"""CLI orchestration helpers for fx organize."""

import dataclasses
from datetime import datetime
from typing import TYPE_CHECKING, Tuple

import click
from returns.io import IOResult

from .errors import OrganizeError
from .lib import unsafe_ioresult_unwrap
from .organize import ConflictMode, OrganizeContext, generate_organize_plan
from .organize_functional import get_file_date, move_file_safe, remove_empty_dirs

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
    scan_result: "IOResult[list[str], OrganizeError]",
    context: "OrganizeContext",
) -> "tuple[list[str], dict[str, datetime], list[FileOrganizeResult], list[tuple[str, Exception]]]":  # noqa: E501
    """Unwrap a scan result, read file dates, and generate the organize plan.

    The caller obtains `scan_result` itself by calling `scan_files(...)`
    (kept outside this function) so the exception boundary matches the
    pre-refactor structure: a raw scan failure propagates from the
    caller's `scan_files()` call, while a scan *failure result* (unwrap
    raising) is caught by whatever try/except the caller wraps this call
    in -- mirroring the old per-call-site boundary exactly.

    Per-file date-read errors are never raised here -- this matches the
    historical swallow-always behavior of the preview and ASK-mode
    conflict-detection scans (`# nosec B110`-equivalent). Failures are
    collected in `date_failures`, in encounter order, so a caller that
    needs the old ASK-mode *execution* fail-fast behavior (raise/report on
    the first date-read failure) can replicate it itself, at the point in
    the flow where that used to happen.

    Returns:
        Tuple of (scanned files, file->date mapping, organize plan,
        date_failures as (file_path, exception) pairs in encounter order)
    """
    files = unsafe_ioresult_unwrap(scan_result)

    dates: "dict[str, datetime]" = {}
    date_failures: "list[tuple[str, Exception]]" = []
    for file_path in files:
        date_result = get_file_date(file_path, context.date_source)
        try:
            dates[file_path] = unsafe_ioresult_unwrap(date_result)
        except Exception as e:  # nosec B110 - collected, not silently dropped
            date_failures.append((file_path, e))

    plan = generate_organize_plan(files, dates, context)
    return files, dates, plan, date_failures


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
