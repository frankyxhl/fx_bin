"""CLI orchestration helpers for fx organize."""

import dataclasses
from datetime import datetime
from typing import TYPE_CHECKING, Tuple

import click

from .lib import unsafe_ioresult_unwrap
from .organize import ConflictMode, OrganizeContext, generate_organize_plan
from .organize_functional import (
    get_file_date,
    move_file_safe,
    remove_empty_dirs,
    scan_files,
)

if TYPE_CHECKING:
    from .organize import FileOrganizeResult


def _confirm_with_user(is_tty: bool) -> bool:
    """Ask user to confirm proceeding with organization.

    Returns:
        True if user confirms or not in TTY mode, False if user cancels.
    """
    if is_tty:
        if not click.confirm("\nProceed?", default=False):
            click.echo("Cancelled.")
            return False
    return True


def _execute_move_with_tracking(
    item: "FileOrganizeResult",
    source: str,
    context: "OrganizeContext",
    conflict_mode: "ConflictMode",
) -> Tuple[int, int, int]:
    """Execute a single file move and track results.

    Returns:
        Tuple of (processed_change, skipped_change, errors_change)
    """
    if context.dry_run:
        return (1, 0, 0)

    move_result = move_file_safe(
        item.source,
        item.target,
        source,  # source_root
        context.output_dir,  # output_root
        conflict_mode,
    )
    try:
        _, dir_created = unsafe_ioresult_unwrap(move_result)
        return (1, 0, 0)
    except Exception as e:
        if context.fail_fast:
            click.echo(
                f"Error: Failed to move {item.source}: {e}",
                err=True,
            )
            raise
        return (0, 0, 1)


def prepare_organize_plan(
    source: str,
    context: "OrganizeContext",
    fail_fast_dates: bool,
) -> "tuple[list[str], dict[str, datetime], list[FileOrganizeResult]]":
    """Scan the source, read file dates, and generate the organize plan.

    Runs the scan -> date-read -> plan sequence exactly once, so callers
    (preview/confirm, ASK-mode conflict detection, ASK-mode execution) can
    share a single result instead of each re-scanning the disk.

    Args:
        source: Source directory to scan
        context: Organization configuration context
        fail_fast_dates: If True, echo and re-raise on the first per-file
            date-read error (matches the historical ASK-mode execution
            behavior). If False, silently skip files whose date can't be
            read; such files surface later as a plan item with action
            "error" (matches the historical preview/confirm behavior).

    Returns:
        Tuple of (scanned files, file->date mapping, organize plan)
    """
    scan_result = scan_files(
        source,
        recursive=context.recursive,
        follow_symlinks=False,
        max_depth=100,
        output_dir=context.output_dir,
    )
    files = unsafe_ioresult_unwrap(scan_result)

    dates: "dict[str, datetime]" = {}
    for file_path in files:
        date_result = get_file_date(file_path, context.date_source)
        try:
            dates[file_path] = unsafe_ioresult_unwrap(date_result)
        except Exception as e:
            if fail_fast_dates:
                click.echo(f"Error: Failed to read date for {file_path}: {e}", err=True)
                raise
            # else: nosec B110 - Intentionally skip files with date errors

    plan = generate_organize_plan(files, dates, context)
    return files, dates, plan


def _execute_ask_plan_item(
    item: "FileOrganizeResult",
    ask_user_choices: "dict[str, str]",
    source: str,
    context: "OrganizeContext",
) -> Tuple[int, int, int]:
    """Execute a single plan item in ASK mode.

    Returns:
        Tuple of (processed_delta, skipped_delta, errors_delta)
    """
    if item.source not in ask_user_choices:
        # No conflict, proceed with normal move
        return _execute_move_with_tracking(item, source, context, ConflictMode.RENAME)

    choice = ask_user_choices[item.source]
    match choice:
        case "skip":
            return (0, 1, 0)
        case "overwrite":
            return _execute_move_with_tracking(
                item, source, context, ConflictMode.OVERWRITE
            )
        case _:
            # Unknown choice - treat as skip
            return (0, 1, 0)


def _execute_ask_mode_with_choices(
    ask_user_choices: "dict[str, str]",
    source: str,
    context: "OrganizeContext",
    plan: "list[FileOrganizeResult]",
) -> Tuple[int, int, int]:
    """Execute organization in ASK mode with user choices.

    Args:
        ask_user_choices: Map of source file -> 'overwrite' or 'skip'
        source: Source directory being organized
        context: Organization configuration context
        plan: Pre-computed organize plan (from `prepare_organize_plan`)

    Returns:
        Tuple of (processed, skipped, errors)
    """
    # Execute plan with ASK mode user choices
    processed = 0
    skipped = 0
    errors = 0

    for item in plan:
        match item.action:
            case "moved":
                proc_delta, skip_delta, err_delta = _execute_ask_plan_item(
                    item, ask_user_choices, source, context
                )
                processed += proc_delta
                skipped += skip_delta
                errors += err_delta
                if err_delta and context.fail_fast:
                    raise

            case "skipped":
                skipped += 1
            case "error":
                errors += 1
                if context.fail_fast:
                    click.echo(f"Error: Planning error for {item.source}", err=True)
                    raise

    # Clean up empty directories if requested
    if context.clean_empty and not context.dry_run:
        remove_empty_dirs(source, source)

    return (processed, skipped, errors)


def _handle_disk_conflicts_interactively(
    disk_conflicts: "list[FileOrganizeResult]",
    context: "OrganizeContext",
    is_tty: bool,
) -> "tuple[dict[str, str], OrganizeContext]":
    """Handle disk conflicts interactively based on TTY availability.

    Returns:
        Tuple of (ask_user_choices, updated_context)
    """
    ask_user_choices = {}

    # Check if we should prompt or auto-skip
    # We check isatty() to distinguish between:
    # - Real terminal: prompt the user
    # - Piped input/non-TTY: auto-skip
    if not is_tty:
        click.echo(
            f"\nFound {len(disk_conflicts)} disk conflict(s). "
            "Skipping (non-interactive mode)."
        )
        for conflict in disk_conflicts:
            ask_user_choices[conflict.source] = "skip"

        # Change conflict_mode to SKIP for non-TTY
        context = dataclasses.replace(context, conflict_mode=ConflictMode.SKIP)
    else:
        # Interactive TTY: prompt for each conflict
        click.echo(f"\nFound {len(disk_conflicts)} disk conflict(s):")
        for conflict in disk_conflicts:
            prompt_msg = f"Overwrite {conflict.target}?"
            if click.confirm(prompt_msg, default=False):
                ask_user_choices[conflict.source] = "overwrite"
            else:
                ask_user_choices[conflict.source] = "skip"

    return (ask_user_choices, context)
