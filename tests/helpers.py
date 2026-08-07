"""Shared test helpers."""


class ExecvGuardViolation(BaseException):
    """Raised by the block_exec_shell guard in conftest.

    Deliberately a BaseException subclass: CLI code (fx_bin/today.py) wraps
    os.execv in `except Exception`, which would swallow an ordinary
    AssertionError and turn it into exit code 1 — letting an offending test
    pass silently. BaseException escapes that handler and Click's CliRunner,
    erroring the test instead.
    """


def table_cells(row: str) -> list[str]:
    """Return stripped cells from an ASCII table row."""

    return [cell.strip() for cell in row.strip().strip("|").split("|")]
