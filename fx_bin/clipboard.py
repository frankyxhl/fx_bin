"""Shared system-clipboard helpers.

Extracted from open_launcher (CHG-2115) so any subcommand can copy text
without importing the fx open machinery. open_launcher re-exports these
names for backward compatibility.
"""

from __future__ import annotations

import os
import shutil
import subprocess  # nosec B404
import sys
from typing import Callable, Mapping, Optional

from .errors import ClipboardError
from .shared_types import DispatchPlan

WAYLAND_CLIPBOARD = ("wl-copy", ())
X11_CLIPBOARD = ("xclip", ("-selection", "clipboard"))


def build_clipboard_plan(
    platform_name: Optional[str] = None,
    opener_lookup: Callable[[str], Optional[str]] = shutil.which,
    environ: Optional[Mapping[str, str]] = None,
) -> DispatchPlan:
    """Build the clipboard-write command for this platform."""

    platform_value = platform_name or sys.platform
    if platform_value == "darwin":
        return DispatchPlan(("pbcopy",))
    if platform_value.startswith("win"):
        return DispatchPlan(("clip",))
    if platform_value.startswith("linux"):
        env = environ if environ is not None else os.environ
        # Wayland and X11 have separate clipboards and each tool only talks to
        # its own display server. wl-clipboard is pulled in as a dependency on
        # many X11 installs, so order by session type rather than by whichever
        # binary happens to be present; fall back to the other when the
        # preferred one is not installed.
        candidates = (
            (WAYLAND_CLIPBOARD, X11_CLIPBOARD)
            if env.get("WAYLAND_DISPLAY")
            else (X11_CLIPBOARD, WAYLAND_CLIPBOARD)
        )
        for name, extra_args in candidates:
            found = opener_lookup(name)
            if found:
                return DispatchPlan((found, *extra_args))
        raise ClipboardError("No clipboard tool found. Install wl-clipboard or xclip.")
    raise ClipboardError(f"Unsupported platform for clipboard copy: {platform_value}")


def copy_to_clipboard(text: str, plan: Optional[DispatchPlan] = None) -> None:
    """Write text to the system clipboard."""

    resolved = plan or build_clipboard_plan()
    result = subprocess.run(  # nosec B603
        resolved.args,
        input=text.encode(),
        shell=False,
        check=False,
    )
    if result.returncode != 0:
        raise ClipboardError(
            f"Clipboard command failed with exit code {result.returncode}"
        )
