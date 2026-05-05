#!/usr/bin/env python
"""Open launcher support for saved URLs and local files."""

from __future__ import annotations

import datetime as dt
import json
import os
import re
import shlex
import shutil

# fx open intentionally runs vetted argv commands with shell disabled.
import subprocess  # nosec B404
import sys
import tempfile
import time
import tomllib
import unicodedata
from contextlib import contextmanager
from dataclasses import dataclass, field, replace
from pathlib import Path
from typing import Callable, Iterator, Mapping, Optional, Sequence, TypeGuard
from urllib.parse import urlparse

from .errors import OpenError

SLUG_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,63}$")
TOML_BARE_KEY_RE = re.compile(r"^[A-Za-z0-9_-]+$")
NEWLY_RESERVED_SLUGS = {"disable", "enable"}
RESERVED_SLUGS = {
    "add",
    "remove",
    "rm",
    "edit",
    "list",
    "delete",
    "help",
    *NEWLY_RESERVED_SLUGS,
}
ALLOWED_ITEM_KEYS = {
    "name",
    "slug",
    "target",
    "order",
    "tags",
    "browser",
    "app",
    "disabled",
}
AI_ALLOWED_FIELDS = {"name", "slug", "tags"}
LOCK_STALE_SECONDS = 600
WINDOWS_EXECUTABLE_SUFFIXES = (".exe", ".bat", ".cmd", ".com", ".ps1")
UNSUPPORTED_TARGET_SCHEMES = {
    "about",
    "chrome",
    "data",
    "file",
    "ftp",
    "javascript",
    "mailto",
    "sftp",
    "ssh",
}
BARE_DOMAIN_RE = re.compile(
    r"^[A-Za-z0-9](?:[A-Za-z0-9.-]*[A-Za-z0-9])?\.[A-Za-z]{2,}(?::[0-9]+)?$"
)


@dataclass(frozen=True)
class OpenItem:
    """A saved launcher item."""

    name: str
    slug: str
    target: str
    order: int = 0
    tags: tuple[str, ...] = ()
    browser: Optional[str] = None
    app: Optional[str] = None
    disabled: bool = False


@dataclass(frozen=True)
class OpenConfig:
    """Parsed launcher config."""

    items: list[OpenItem]
    extra: Mapping[str, object] = field(default_factory=dict)


@dataclass(frozen=True)
class LaunchTarget:
    """A resolved target ready for dispatch planning."""

    label: str
    target: str
    slug: Optional[str] = None
    browser: Optional[str] = None
    app: Optional[str] = None


@dataclass(frozen=True)
class DispatchPlan:
    """A safe opener dispatch plan."""

    args: tuple[str, ...]
    method: str = "subprocess"
    shell: bool = False


def default_config_path(
    platform_name: Optional[str] = None,
    environ: Optional[Mapping[str, str]] = None,
    home: Optional[Path] = None,
) -> Path:
    """Return the default fx open config path."""

    platform_value = platform_name or sys.platform
    env = environ if environ is not None else os.environ
    home_path = home or Path.home()

    if platform_value.startswith("win"):
        appdata = env.get("APPDATA")
        if appdata:
            return Path(appdata) / "fx-bin" / "open.toml"
        return home_path / ".config" / "fx-bin" / "open.toml"

    xdg_config_home = env.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        return Path(xdg_config_home) / "fx-bin" / "open.toml"
    return home_path / ".config" / "fx-bin" / "open.toml"


def resolve_config_path(config_path: Optional[str]) -> Path:
    """Resolve an optional CLI config path."""

    if config_path:
        return Path(config_path).expanduser()
    return default_config_path()


def load_config(config_path: Path) -> OpenConfig:
    """Load and validate launcher config."""

    if not config_path.exists():
        return OpenConfig([])

    try:
        text = config_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise OpenError(f"Could not read config {config_path}: {exc}") from exc

    return _parse_config_text(text, config_path)


def _parse_config_text(text: str, config_path: Path) -> OpenConfig:
    try:
        raw_config = tomllib.loads(text) if text.strip() else {}
    except tomllib.TOMLDecodeError as exc:
        raise OpenError(f"Malformed TOML in {config_path}: {exc}") from exc

    raw_items = raw_config.get("items", [])
    if not isinstance(raw_items, list):
        raise OpenError("Config field 'items' must be a list of tables")

    items: list[OpenItem] = []
    seen_slugs: set[str] = set()
    for index, raw_item in enumerate(raw_items, start=1):
        if not isinstance(raw_item, dict):
            raise OpenError(f"Item {index} must be a TOML table")
        items.append(_parse_item(raw_item, index, seen_slugs))

    extra = {key: value for key, value in raw_config.items() if key != "items"}
    return OpenConfig(_sort_items(items), extra)


def _parse_item(
    raw_item: dict[str, object],
    index: int,
    seen_slugs: set[str],
) -> OpenItem:
    unknown_keys = set(raw_item) - ALLOWED_ITEM_KEYS
    if unknown_keys:
        keys = ", ".join(sorted(unknown_keys))
        raise OpenError(f"Item {index} has unknown field(s): {keys}")

    name = _required_string(raw_item, "name", index)
    slug = _required_string(raw_item, "slug", index)
    target = _required_string(raw_item, "target", index)
    order = _optional_non_negative_int(raw_item.get("order"), "order", index)
    tags = _optional_string_tuple(raw_item.get("tags"), "tags", index)
    browser = _optional_string(raw_item.get("browser"), "browser", index)
    app = _optional_string(raw_item.get("app"), "app", index)
    disabled = _optional_bool(raw_item.get("disabled"), "disabled", index)

    validate_slug(slug)
    if slug in seen_slugs:
        raise OpenError(f"Duplicate slug in config: {slug}")
    seen_slugs.add(slug)

    _validate_target_string(target)
    _validate_opener_name(browser, "browser")
    _validate_opener_name(app, "app")

    target_kind = classify_target_kind(target)
    if browser and target_kind != "url":
        raise OpenError(f"Item {slug} uses browser for a non-URL target")
    if app and target_kind != "path":
        raise OpenError(f"Item {slug} uses app for a URL target")

    return OpenItem(
        name=name,
        slug=slug,
        target=target,
        order=order,
        tags=tags,
        browser=browser,
        app=app,
        disabled=disabled,
    )


def _required_string(raw_item: dict[str, object], key: str, index: int) -> str:
    value = raw_item.get(key)
    if not isinstance(value, str) or value == "":
        raise OpenError(f"Item {index} field '{key}' must be a non-empty string")
    _reject_nul(value, f"Item {index} field '{key}'")
    return value


def _optional_string(value: object, key: str, index: int) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str) or value == "":
        raise OpenError(f"Item {index} field '{key}' must be a non-empty string")
    _reject_nul(value, f"Item {index} field '{key}'")
    return value


def _optional_non_negative_int(value: object, key: str, index: int) -> int:
    if value is None:
        return 0
    if type(value) is not int or value < 0:
        raise OpenError(f"Item {index} field '{key}' must be a non-negative integer")
    return value


def _optional_bool(value: object, key: str, index: int) -> bool:
    if value is None:
        return False
    if type(value) is not bool:
        raise OpenError(f"Item {index} field '{key}' must be a boolean")
    return value


def _optional_string_tuple(value: object, key: str, index: int) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise OpenError(f"Item {index} field '{key}' must be a list of strings")
    result: list[str] = []
    for tag in value:
        if not isinstance(tag, str) or tag == "":
            raise OpenError(f"Item {index} field '{key}' must be a list of strings")
        _reject_nul(tag, f"Item {index} tag")
        result.append(tag)
    return tuple(result)


def _sort_items(items: Sequence[OpenItem]) -> list[OpenItem]:
    return sorted(items, key=lambda item: (item.order, item.name.lower(), item.slug))


def format_items(
    items: Sequence[OpenItem],
    terminal_width: Optional[int] = None,
) -> str:
    """Format launcher items for CLI display."""

    if not items:
        return "No saved open targets. Add one with: fx open add https://example.com"

    width = terminal_width
    if width is None:
        width = shutil.get_terminal_size(fallback=(80, 24)).columns
    return _format_items_table(items, max(width, 1))


def _format_items_table(items: Sequence[OpenItem], terminal_width: int) -> str:
    include_state = any(item.disabled for item in items)
    columns: list[tuple[str, list[str], int, int]] = []

    index_values = [str(index) for index, _ in enumerate(items, start=1)]
    index_width = max(_display_width(value) for value in [*index_values, "#"])
    columns.append(("#", index_values, index_width, index_width))

    if include_state:
        state_values = ["disabled" if item.disabled else "" for item in items]
        columns.append(("State", state_values, 8, 5))

    name_values = [item.name for item in items]
    slug_values = [item.slug for item in items]
    tag_values = [", ".join(item.tags) for item in items]
    target_values = [item.target for item in items]
    columns.extend(
        [
            ("Name", name_values, 24, 4),
            ("Slug", slug_values, 20, 4),
            ("Tags", tag_values, 24, 4),
            ("Target", target_values, 10_000, 6),
        ]
    )

    sanitized = [
        (header, [_sanitize_table_cell(value) for value in values], cap, min_width)
        for header, values, cap, min_width in columns
    ]
    widths = [
        min(
            max([_display_width(header), *(_display_width(value) for value in values)]),
            cap,
        )
        for header, values, cap, _min_width in sanitized
    ]
    min_widths = [
        min(max(_display_width(header), min_width), width)
        for (header, _values, _cap, min_width), width in zip(sanitized, widths)
    ]
    widths = _fit_column_widths(widths, min_widths, terminal_width)

    border = _table_border(widths)
    header = _table_row([header for header, _values, _cap, _min in sanitized], widths)
    rows = [
        _table_row([values[index] for _header, values, _cap, _min in sanitized], widths)
        for index in range(len(items))
    ]
    return "\n".join([border, header, border, *rows, border])


def _fit_column_widths(
    widths: list[int],
    min_widths: list[int],
    terminal_width: int,
) -> list[int]:
    available = terminal_width - (3 * len(widths) + 1)
    if available < len(widths):
        available = len(widths)
        min_widths = [1 for _ in widths]

    result = list(widths)
    for index in range(len(result) - 2, -1, -1):
        while sum(result) > available and result[index] > min_widths[index]:
            result[index] -= 1
    target_index = len(result) - 1
    while sum(result) > available and result[target_index] > min_widths[target_index]:
        result[target_index] -= 1
    for index in range(len(result) - 2, -1, -1):
        while sum(result) > available and result[index] > 1:
            result[index] -= 1
    while sum(result) > available and result[target_index] > 1:
        result[target_index] -= 1
    return result


def _table_border(widths: Sequence[int]) -> str:
    return "+" + "+".join("-" * (width + 2) for width in widths) + "+"


def _table_row(values: Sequence[str], widths: Sequence[int]) -> str:
    cells = [
        _pad_display(_truncate_display(value, width), width)
        for value, width in zip(values, widths)
    ]
    return "| " + " | ".join(cells) + " |"


def _sanitize_table_cell(value: str) -> str:
    result: list[str] = []
    previous_space = False
    for char in value:
        if unicodedata.category(char) == "Cc":
            if not previous_space:
                result.append(" ")
                previous_space = True
            continue
        result.append(char)
        previous_space = char == " "
    return "".join(result).strip()


def _display_width(value: str) -> int:
    width = 0
    for char in value:
        if unicodedata.combining(char):
            continue
        width += 2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1
    return width


def _truncate_display(value: str, width: int) -> str:
    if width <= 0:
        return ""
    if _display_width(value) <= width:
        return value
    marker = "..." if width >= 3 else "." * width
    content_width = width - len(marker)
    result: list[str] = []
    current_width = 0
    for char in value:
        char_width = (
            0
            if unicodedata.combining(char)
            else (2 if unicodedata.east_asian_width(char) in {"F", "W"} else 1)
        )
        if current_width + char_width > content_width:
            break
        result.append(char)
        current_width += char_width
    return "".join(result) + marker


def _pad_display(value: str, width: int) -> str:
    padding = max(width - _display_width(value), 0)
    return value + (" " * padding)


def filter_items(
    items: Sequence[OpenItem],
    filter_tags: Sequence[str] = (),
    visibility: str = "enabled",
) -> list[OpenItem]:
    """Return sorted items that include all requested tags."""

    sorted_items = _sort_items(items)
    if visibility == "enabled":
        sorted_items = [item for item in sorted_items if not item.disabled]
    elif visibility == "disabled":
        sorted_items = [item for item in sorted_items if item.disabled]
    elif visibility != "all":
        raise OpenError(f"Unknown visibility mode: {visibility}")
    if not filter_tags:
        return sorted_items
    tag_set = set(filter_tags)
    return [item for item in sorted_items if tag_set.issubset(set(item.tags))]


def resolve_launch_target(
    token: str,
    items: Sequence[OpenItem],
    filter_tags: Sequence[str] = (),
    cwd: Optional[Path] = None,
    platform_name: Optional[str] = None,
) -> LaunchTarget:
    """Resolve a selector token to a launch target."""

    if not token:
        raise OpenError("Missing open target")

    platform_value = platform_name or sys.platform
    cwd_path = cwd or Path.cwd()

    if _is_http_url(token):
        return LaunchTarget(label=token, target=token)

    if _has_unsupported_scheme(token):
        scheme = urlparse(token).scheme
        raise OpenError(f"Unsupported target scheme: {scheme}")

    if _is_explicit_path_token(token, platform_value):
        return LaunchTarget(label=token, target=token)

    visible_items = filter_items(items, filter_tags)

    if _looks_like_index(token):
        index = int(token)
        if index <= 0:
            raise OpenError("Index must be a positive 1-based number")
        if index > len(visible_items):
            raise OpenError(f"Index {index} is out of range")
        item = visible_items[index - 1]
        return _launch_target_from_item(item)

    for item in visible_items:
        if item.slug == token:
            return _launch_target_from_item(item)

    if filter_tags and any(item.slug == token for item in items):
        tags = ", ".join(filter_tags)
        raise OpenError(f"Slug '{token}' does not match filter tag(s): {tags}")

    bare_path = cwd_path / token
    if bare_path.exists():
        return LaunchTarget(label=token, target=str(bare_path))

    if any(item.slug == token and item.disabled for item in items):
        raise OpenError(f"Slug '{token}' is disabled")

    raise OpenError(f"Open target not found: {token}. Run 'fx open' to list targets.")


def resolve_saved_item_selector(
    token: str,
    items: Sequence[OpenItem],
    filter_tags: Sequence[str] = (),
    visibility: str = "enabled",
    action: str = "select",
) -> OpenItem:
    """Resolve a saved-item slug or visible index for config mutations."""

    if not token:
        raise OpenError(f"Missing {action} selector")
    if _is_http_url(token) or _is_explicit_path_token(token, sys.platform):
        raise OpenError(f"{action.title()} selector must be a slug or index")

    visible_items = filter_items(items, filter_tags, visibility=visibility)
    if _looks_like_index(token):
        index = int(token)
        if index <= 0:
            raise OpenError("Index must be a positive 1-based number")
        if index > len(visible_items):
            raise OpenError(f"Index {index} is out of range")
        return visible_items[index - 1]

    for item in visible_items:
        if item.slug == token:
            return item

    if filter_tags and any(item.slug == token for item in items):
        tags = ", ".join(filter_tags)
        raise OpenError(f"Slug '{token}' does not match filter tag(s): {tags}")
    if visibility == "enabled" and any(
        item.slug == token and item.disabled for item in items
    ):
        raise OpenError(f"Slug '{token}' is disabled")
    raise OpenError(
        f"{action.title()} target not found: {token}. Run 'fx open' to list targets."
    )


def _launch_target_from_item(item: OpenItem) -> LaunchTarget:
    return LaunchTarget(
        label=item.name,
        target=item.target,
        slug=item.slug,
        browser=item.browser,
        app=item.app,
    )


def build_new_item(
    target: str,
    existing_items: Sequence[OpenItem],
    name: Optional[str] = None,
    slug: Optional[str] = None,
    tags: Sequence[str] = (),
    browser: Optional[str] = None,
    app: Optional[str] = None,
    ai_metadata: Optional[Mapping[str, object]] = None,
) -> OpenItem:
    """Build and validate a new item for the add workflow."""

    normalized_target = normalize_add_target(target)
    _validate_target_string(normalized_target)
    target_kind = classify_target_kind(normalized_target)
    _validate_opener_name(browser, "browser")
    _validate_opener_name(app, "app")
    if browser and target_kind != "url":
        raise OpenError("--browser can only be stored for URL targets")
    if app and target_kind != "path":
        raise OpenError("--app can only be stored for local path targets")

    ai_name, ai_slug, ai_tags = _validated_ai_metadata(ai_metadata)
    if slug == "":
        raise OpenError("Slug must be non-empty when provided")
    if name == "":
        raise OpenError("Name must be non-empty when provided")
    final_slug = slug or ai_slug or generate_slug(normalized_target)
    final_name = name or ai_name or _name_from_slug(final_slug)
    final_tags = tuple(tags) if tags else ai_tags

    existing_slugs = {item.slug for item in existing_items}
    validate_slug(final_slug, existing_slugs)
    _reject_nul(final_name, "name")
    for tag in final_tags:
        if not tag:
            raise OpenError("Tags must be non-empty strings")
        _reject_nul(tag, "tag")

    return OpenItem(
        name=final_name,
        slug=final_slug,
        target=normalized_target,
        order=0,
        tags=tuple(final_tags),
        browser=browser,
        app=app,
    )


def normalize_add_target(target: str) -> str:
    """Normalize add-workflow targets into stable URL or absolute file targets."""

    stripped = target.strip()
    _validate_target_string(stripped)
    if _is_http_url(stripped):
        return stripped

    if _is_explicit_path_token(stripped, sys.platform) or Path(stripped).exists():
        return _normalize_local_path(stripped)

    if BARE_DOMAIN_RE.fullmatch(stripped):
        return f"https://{stripped}"

    raise OpenError(
        "Add target must be an http(s) URL, bare domain, or existing local file"
    )


def _validated_ai_metadata(
    ai_metadata: Optional[Mapping[str, object]],
) -> tuple[Optional[str], Optional[str], tuple[str, ...]]:
    if ai_metadata is None:
        return (None, None, ())

    unknown = set(ai_metadata) - AI_ALLOWED_FIELDS
    if unknown:
        unknown_fields = ", ".join(sorted(unknown))
        raise OpenError(f"AI returned unsupported field(s): {unknown_fields}")

    name = ai_metadata.get("name")
    slug = ai_metadata.get("slug")
    tags = ai_metadata.get("tags", [])

    if name is not None and not isinstance(name, str):
        raise OpenError("AI field 'name' must be a string")
    if slug is not None and not isinstance(slug, str):
        raise OpenError("AI field 'slug' must be a string")
    if not isinstance(tags, list) or any(not isinstance(tag, str) for tag in tags):
        raise OpenError("AI field 'tags' must be a list of strings")
    return (name, slug, tuple(tags))


def _next_order(items: Sequence[OpenItem]) -> int:
    current_max = max((item.order for item in items), default=0)
    return current_max + 10


def generate_slug(target: str) -> str:
    """Generate a deterministic slug from a target."""

    if _is_http_url(target):
        parsed = urlparse(target)
        base = (parsed.hostname or parsed.netloc).lower()
        if base.startswith("www."):
            base = base[4:]
    else:
        path = Path(target).expanduser()
        base = path.stem or path.name or "link"

    normalized = unicodedata.normalize("NFKD", base)
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    candidate = re.sub(r"[^a-z0-9_-]+", "-", ascii_text)
    candidate = re.sub(r"-{2,}", "-", candidate)
    candidate = re.sub(r"^[^a-z]+", "", candidate)
    if not candidate:
        candidate = "link"
    candidate = candidate[:64].rstrip("-_")
    if not candidate:
        candidate = "link"
    return candidate


def _name_from_slug(slug: str) -> str:
    return re.sub(r"[-_]+", " ", slug).strip().title()


def validate_slug(slug: str, existing_slugs: Optional[set[str]] = None) -> None:
    """Validate slug grammar, reserved words, and optional uniqueness."""

    if not SLUG_RE.fullmatch(slug):
        raise OpenError(
            "Slug must match ^[A-Za-z][A-Za-z0-9_-]{0,63}$. "
            "Provide --slug with a valid value."
        )
    if slug.lower() in NEWLY_RESERVED_SLUGS:
        raise OpenError(
            f"Rename slug '{slug}' before using this fx open version; "
            f"'{slug}' is reserved for a command."
        )
    if slug.lower() in RESERVED_SLUGS:
        raise OpenError(f"Slug is reserved: {slug}")
    if existing_slugs is not None and slug in existing_slugs:
        raise OpenError(f"Slug already exists: {slug}. Provide --slug.")


def append_item(config_path: Path, item: OpenItem) -> OpenItem:
    """Append an item to a TOML config using a lock and atomic replace."""

    config_path.parent.mkdir(parents=True, exist_ok=True)

    with _config_lock(config_path):
        existing_text = ""
        if config_path.exists():
            existing_text = config_path.read_text(encoding="utf-8")

        existing_config = _parse_config_text(existing_text, config_path)
        item_to_write = item
        if item_to_write.order == 0:
            item_to_write = replace(
                item_to_write,
                order=_next_order(existing_config.items),
            )

        candidate = _append_toml(existing_text, item_to_write)
        _parse_config_text(candidate, config_path)

        with tempfile.NamedTemporaryFile(
            "w",
            encoding="utf-8",
            dir=str(config_path.parent),
            delete=False,
        ) as temp_file:
            temp_file.write(candidate)
            temp_name = temp_file.name

        try:
            os.replace(temp_name, config_path)
        except OSError as exc:
            try:
                os.unlink(temp_name)
            except OSError:
                pass
            raise OpenError(f"Could not update config {config_path}: {exc}") from exc

    return item_to_write


def delete_item(
    config_path: Path,
    selector: str,
    filter_tags: Sequence[str] = (),
    visibility: str = "enabled",
) -> OpenItem:
    """Delete a saved item from a TOML config using a lock and atomic replace."""

    with _mutate_config(config_path) as config:
        deleted = resolve_saved_item_selector(
            selector,
            config.items,
            filter_tags=filter_tags,
            visibility=visibility,
            action="delete",
        )
        config.items[:] = [item for item in config.items if item.slug != deleted.slug]
        yield_item = deleted
    return yield_item


def disable_item(
    config_path: Path,
    selector: str,
    filter_tags: Sequence[str] = (),
) -> OpenItem:
    """Mark a saved item disabled using a lock and atomic replace."""

    with _mutate_config(config_path) as config:
        selected = resolve_saved_item_selector(
            selector,
            config.items,
            filter_tags=filter_tags,
            visibility="enabled",
            action="disable",
        )
        disabled = replace(selected, disabled=True)
        config.items[:] = [
            disabled if item.slug == selected.slug else item for item in config.items
        ]
        yield_item = disabled
    return yield_item


def enable_item(
    config_path: Path,
    selector: str,
    filter_tags: Sequence[str] = (),
) -> OpenItem:
    """Mark a saved item enabled using a lock and atomic replace."""

    with _mutate_config(config_path) as config:
        selected = resolve_saved_item_selector(
            selector,
            config.items,
            filter_tags=filter_tags,
            visibility="disabled",
            action="enable",
        )
        enabled = replace(selected, disabled=False)
        config.items[:] = [
            enabled if item.slug == selected.slug else item for item in config.items
        ]
        yield_item = enabled
    return yield_item


@contextmanager
def _mutate_config(config_path: Path) -> Iterator[OpenConfig]:
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with _config_lock(config_path):
        existing_text = ""
        if config_path.exists():
            existing_text = config_path.read_text(encoding="utf-8")

        config = _parse_config_text(existing_text, config_path)
        yield config
        candidate = _config_to_toml(config)
        _parse_config_text(candidate, config_path)
        _atomic_replace_config(config_path, candidate)


def _atomic_replace_config(config_path: Path, text: str) -> None:
    with tempfile.NamedTemporaryFile(
        "w",
        encoding="utf-8",
        dir=str(config_path.parent),
        delete=False,
    ) as temp_file:
        temp_file.write(text)
        temp_name = temp_file.name

    try:
        os.replace(temp_name, config_path)
    except OSError as exc:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise OpenError(f"Could not update config {config_path}: {exc}") from exc


@contextmanager
def _config_lock(config_path: Path) -> Iterator[None]:
    lock_path = config_path.with_name(f"{config_path.name}.lock")
    fd: Optional[int] = None
    owns_lock = False
    try:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            owns_lock = True
            os.write(fd, f"{os.getpid()}\n{time.time()}\n".encode("utf-8"))
        except FileExistsError as exc:
            if _lock_is_stale(lock_path):
                try:
                    os.unlink(lock_path)
                except OSError as unlink_exc:
                    raise OpenError(f"Config is locked: {lock_path}") from unlink_exc
                try:
                    fd = os.open(
                        str(lock_path),
                        os.O_CREAT | os.O_EXCL | os.O_WRONLY,
                    )
                except FileExistsError as race_exc:
                    raise OpenError(f"Config is locked: {lock_path}") from race_exc
                owns_lock = True
                os.write(fd, f"{os.getpid()}\n{time.time()}\n".encode("utf-8"))
            else:
                raise OpenError(f"Config is locked: {lock_path}") from exc
        yield
    finally:
        if fd is not None:
            os.close(fd)
        if owns_lock:
            try:
                os.unlink(lock_path)
            except FileNotFoundError:
                pass


def _lock_is_stale(lock_path: Path) -> bool:
    try:
        return time.time() - lock_path.stat().st_mtime > LOCK_STALE_SECONDS
    except OSError:
        return False


def _append_toml(existing_text: str, item: OpenItem) -> str:
    blocks: list[str] = []
    if existing_text.strip():
        blocks.append(existing_text.rstrip())
    blocks.append(_item_to_toml(item))
    return "\n\n".join(blocks) + "\n"


def _config_to_toml(config: OpenConfig) -> str:
    blocks: list[str] = []
    extra_text = _extra_config_to_toml(config.extra)
    if extra_text:
        blocks.append(extra_text)
    items_text = _items_to_toml(config.items).rstrip()
    if items_text:
        blocks.append(items_text)
    if not blocks:
        return ""
    return "\n\n".join(blocks) + "\n"


def _extra_config_to_toml(extra: Mapping[str, object]) -> str:
    scalar_lines: list[str] = []
    table_blocks: list[str] = []
    for key, value in extra.items():
        if isinstance(value, dict):
            table_blocks.extend(
                _toml_table_blocks(
                    (key,),
                    _string_keyed_mapping(value, key),
                    array_table=False,
                )
            )
        elif _is_array_of_tables(value):
            table_blocks.extend(_toml_array_table_blocks((key,), value))
        else:
            scalar_lines.append(f"{_toml_key(key)} = {_toml_value(value)}")

    blocks: list[str] = []
    if scalar_lines:
        blocks.append("\n".join(scalar_lines))
    blocks.extend(table_blocks)
    return "\n\n".join(blocks)


def _items_to_toml(items: Sequence[OpenItem]) -> str:
    if not items:
        return ""
    return "\n\n".join(_item_to_toml(item) for item in items) + "\n"


def _item_to_toml(item: OpenItem) -> str:
    lines = [
        "[[items]]",
        f"order = {item.order}",
        f"name = {_toml_basic_string(item.name)}",
        f"slug = {_toml_basic_string(item.slug)}",
        f"target = {_toml_basic_string(item.target)}",
    ]
    if item.tags:
        lines.append(
            "tags = [" + ", ".join(_toml_basic_string(tag) for tag in item.tags) + "]"
        )
    if item.browser:
        lines.append(f"browser = {_toml_basic_string(item.browser)}")
    if item.app:
        lines.append(f"app = {_toml_basic_string(item.app)}")
    if item.disabled:
        lines.append("disabled = true")
    return "\n".join(lines)


def _toml_table_blocks(
    path: Sequence[str],
    table: Mapping[str, object],
    array_table: bool,
) -> list[str]:
    scalar_lines: list[str] = []
    nested_blocks: list[str] = []
    for key, value in table.items():
        child_path = (*path, key)
        if isinstance(value, dict):
            nested_blocks.extend(
                _toml_table_blocks(
                    child_path,
                    _string_keyed_mapping(value, _toml_dotted_key(child_path)),
                    array_table=False,
                )
            )
        elif _is_array_of_tables(value):
            nested_blocks.extend(_toml_array_table_blocks(child_path, value))
        else:
            scalar_lines.append(f"{_toml_key(key)} = {_toml_value(value)}")

    header = (
        f"[[{_toml_dotted_key(path)}]]"
        if array_table
        else f"[{_toml_dotted_key(path)}]"
    )
    blocks = [header]
    if scalar_lines:
        blocks[0] = "\n".join([header, *scalar_lines])
    blocks.extend(nested_blocks)
    return blocks


def _toml_array_table_blocks(
    path: Sequence[str],
    values: Sequence[object],
) -> list[str]:
    blocks: list[str] = []
    for value in values:
        if not isinstance(value, dict):
            raise OpenError(
                f"TOML array table {_toml_dotted_key(path)} must contain tables"
            )
        blocks.extend(
            _toml_table_blocks(
                path,
                _string_keyed_mapping(value, _toml_dotted_key(path)),
                array_table=True,
            )
        )
    return blocks


def _is_array_of_tables(value: object) -> TypeGuard[list[object]]:
    return (
        isinstance(value, list)
        and bool(value)
        and all(isinstance(item, dict) for item in value)
    )


def _string_keyed_mapping(
    value: Mapping[object, object],
    context: str,
) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, item in value.items():
        if not isinstance(key, str):
            raise OpenError(f"TOML table {context} contains a non-string key")
        result[key] = item
    return result


def _toml_dotted_key(path: Sequence[str]) -> str:
    return ".".join(_toml_key(key) for key in path)


def _toml_key(key: str) -> str:
    if TOML_BARE_KEY_RE.fullmatch(key):
        return key
    return _toml_basic_string(key)


def _toml_value(value: object) -> str:
    if isinstance(value, str):
        return _toml_basic_string(value)
    if type(value) is bool:
        return "true" if value else "false"
    if type(value) is int:
        return str(value)
    if isinstance(value, float):
        return repr(value).lower()
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return value.isoformat()
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(item) for item in value) + "]"
    if isinstance(value, dict):
        table = _string_keyed_mapping(value, "inline")
        parts = [
            f"{_toml_key(key)} = {_toml_value(item)}" for key, item in table.items()
        ]
        return "{ " + ", ".join(parts) + " }"
    raise OpenError(f"Unsupported TOML value type: {type(value).__name__}")


def _toml_basic_string(value: str) -> str:
    escaped: list[str] = ['"']
    for char in value:
        codepoint = ord(char)
        if char == "\\":
            escaped.append("\\\\")
        elif char == '"':
            escaped.append('\\"')
        elif char == "\t":
            escaped.append("\\t")
        elif char == "\n":
            escaped.append("\\n")
        elif char == "\r":
            escaped.append("\\r")
        elif char == "\b":
            escaped.append("\\b")
        elif char == "\f":
            escaped.append("\\f")
        elif codepoint < 32:
            raise OpenError(
                "TOML strings cannot contain unsupported control characters"
            )
        else:
            escaped.append(char)
    escaped.append('"')
    return "".join(escaped)


def build_dispatch_plan(
    launch_target: LaunchTarget,
    browser: Optional[str] = None,
    app: Optional[str] = None,
    platform_name: Optional[str] = None,
    opener_lookup: Callable[[str], Optional[str]] = shutil.which,
) -> DispatchPlan:
    """Build a safe dispatch plan for a launch target."""

    platform_value = platform_name or sys.platform
    persisted_browser = launch_target.browser if platform_value == "darwin" else None
    persisted_app = launch_target.app if platform_value == "darwin" else None
    selected_browser = browser or persisted_browser
    selected_app = app or persisted_app
    _validate_opener_name(selected_browser, "browser")
    _validate_opener_name(selected_app, "app")

    target_kind = classify_target_kind(launch_target.target)
    if target_kind == "url":
        if selected_app:
            raise OpenError("--app can only be used with local path targets")
        dispatch_target = launch_target.target
        opener_name = selected_browser
    else:
        if selected_browser:
            raise OpenError("--browser can only be used with URL targets")
        dispatch_target = _normalize_local_path(launch_target.target)
        opener_name = selected_app

    if platform_value == "darwin":
        if opener_name:
            return DispatchPlan(("open", "-a", opener_name, dispatch_target))
        return DispatchPlan(("open", dispatch_target))

    if platform_value.startswith("linux"):
        if opener_name:
            raise OpenError("Explicit app/browser selection is only supported on macOS")
        xdg_open = opener_lookup("xdg-open")
        if not xdg_open:
            raise OpenError("xdg-open is not available on this system")
        return DispatchPlan((xdg_open, dispatch_target))

    if platform_value.startswith("win"):
        if opener_name:
            raise OpenError("Explicit app/browser selection is only supported on macOS")
        return DispatchPlan((dispatch_target,), method="startfile")

    raise OpenError(f"Unsupported platform for fx open: {platform_value}")


def execute_dispatch_plan(plan: DispatchPlan) -> None:
    """Execute a previously built dispatch plan."""

    if plan.method == "startfile":
        startfile = getattr(os, "startfile", None)
        if startfile is None:
            raise OpenError("os.startfile is unavailable on this platform")
        startfile(plan.args[0])
        return

    result = subprocess.run(plan.args, shell=False, check=False)  # nosec B603
    if result.returncode != 0:
        raise OpenError(f"Open command failed with exit code {result.returncode}")


def request_ai_metadata(
    target: str,
    existing_slugs: Sequence[str],
    command: Optional[str],
    platform_name: Optional[str] = None,
) -> dict[str, object]:
    """Request optional AI metadata from an external command."""

    if not command:
        raise OpenError(
            "--ai requires FX_OPEN_AI_COMMAND to point to a metadata provider"
        )

    request = {
        "target": target,
        "existing_slugs": list(existing_slugs),
        "allowed_fields": sorted(AI_ALLOWED_FIELDS),
    }

    argv = _split_ai_command(command, platform_name)
    if not argv:
        raise OpenError("FX_OPEN_AI_COMMAND must include a command")

    try:
        # FX_OPEN_AI_COMMAND is parsed into an argv vector above and shell is
        # disabled, so the provider never executes through shell expansion.
        result = subprocess.run(  # nosec B603
            argv,
            input=json.dumps(request),
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        raise OpenError("AI metadata provider timed out after 10 seconds") from exc
    except OSError as exc:
        raise OpenError(f"AI metadata provider failed to start: {exc}") from exc

    if result.returncode != 0:
        raise OpenError(f"AI metadata provider exited with code {result.returncode}")

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        preview = result.stdout[:120].replace("\n", "\\n")
        raise OpenError(
            f"AI metadata provider returned invalid JSON: {preview}"
        ) from exc

    if not isinstance(parsed, dict):
        raise OpenError("AI metadata provider must return a JSON object")
    _validated_ai_metadata(parsed)
    return parsed


def _split_ai_command(command: str, platform_name: Optional[str] = None) -> list[str]:
    platform_value = platform_name or sys.platform
    try:
        if platform_value.startswith("win"):
            return _split_windows_command(command)
        return shlex.split(command)
    except ValueError as exc:
        raise OpenError(f"FX_OPEN_AI_COMMAND cannot be safely split: {exc}") from exc


def _split_windows_command(command: str) -> list[str]:
    args: list[str] = []
    current: list[str] = []
    in_quotes = False
    arg_started = False
    backslash_count = 0
    index = 0

    while index < len(command):
        char = command[index]
        if char == "\\":
            backslash_count += 1
            index += 1
            continue

        if char == '"':
            current.extend("\\" * (backslash_count // 2))
            if backslash_count % 2:
                current.append('"')
            else:
                in_quotes = not in_quotes
            arg_started = True
            backslash_count = 0
            index += 1
            continue

        if backslash_count:
            current.extend("\\" * backslash_count)
            backslash_count = 0

        if char in {" ", "\t"} and not in_quotes:
            if arg_started:
                args.append("".join(current))
                current = []
                arg_started = False
            index += 1
            continue

        current.append(char)
        arg_started = True
        index += 1

    if backslash_count:
        current.extend("\\" * backslash_count)
    if in_quotes:
        raise ValueError("No closing quotation")
    if arg_started:
        args.append("".join(current))
    return _merge_windows_executable_path(args)


def _merge_windows_executable_path(args: Sequence[str]) -> list[str]:
    if len(args) < 2 or not _starts_windows_path(args[0]):
        return list(args)

    command = args[0]
    if _ends_windows_executable(command):
        return list(args)

    for index, arg in enumerate(args[1:], start=1):
        command = f"{command} {arg}"
        if _ends_windows_executable(command):
            return [command, *args[index + 1 :]]
    return list(args)


def _starts_windows_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:\\", value)) or value.startswith("\\\\")


def _ends_windows_executable(value: str) -> bool:
    return value.lower().endswith(WINDOWS_EXECUTABLE_SUFFIXES)


def classify_target_kind(target: str) -> str:
    """Classify a target as url or path, rejecting unsupported schemes."""

    _validate_target_string(target)
    if _is_http_url(target):
        return "url"
    if _has_unsupported_scheme(target):
        scheme = urlparse(target).scheme
        raise OpenError(f"Unsupported target scheme: {scheme}")
    return "path"


def _validate_target_string(target: str) -> None:
    if not target:
        raise OpenError("Target must be non-empty")
    _reject_nul(target, "target")
    if any(ord(char) < 32 for char in target):
        raise OpenError("target cannot contain control characters")
    if _is_http_url(target):
        parsed = urlparse(target)
        if not parsed.netloc:
            raise OpenError("URL targets must include a host")
        return
    if _has_unsupported_scheme(target):
        scheme = urlparse(target).scheme
        raise OpenError(f"Unsupported target scheme: {scheme}")


def _is_http_url(value: str) -> bool:
    parsed = urlparse(value)
    return parsed.scheme.lower() in {"http", "https"} and bool(parsed.netloc)


def _has_unsupported_scheme(value: str) -> bool:
    parsed = urlparse(value)
    scheme = parsed.scheme.lower()
    if not scheme:
        return False
    if _is_windows_drive_path(value):
        return False
    if scheme in {"http", "https"}:
        return not bool(parsed.netloc)
    if parsed.netloc:
        return True
    return scheme in UNSUPPORTED_TARGET_SCHEMES


def _is_windows_drive_path(value: str) -> bool:
    return bool(re.match(r"^[A-Za-z]:[\\/]", value))


def _is_explicit_path_token(token: str, platform_name: str) -> bool:
    if token.startswith((".", "/", "~")):
        return True
    if platform_name.startswith("win"):
        return "/" in token or "\\" in token or _is_windows_drive_path(token)
    return "/" in token


def _looks_like_index(token: str) -> bool:
    if token.startswith("-"):
        return token[1:].isdigit()
    return token.isdigit()


def _normalize_local_path(target: str) -> str:
    try:
        path = Path(target).expanduser()
        resolved = path.resolve(strict=True)
    except (OSError, RuntimeError) as exc:
        raise OpenError(f"Local path cannot be opened: {target}") from exc
    if not resolved.is_file():
        raise OpenError(f"Local path is not a regular file: {target}")
    return str(resolved)


def _validate_opener_name(value: Optional[str], field: str) -> None:
    if value is None:
        return
    if value == "" or value.startswith("-"):
        raise OpenError(f"{field} name is invalid")
    _reject_nul(value, field)


def _reject_nul(value: str, label: str) -> None:
    if "\x00" in value:
        raise OpenError(f"{label} cannot contain NUL bytes")
