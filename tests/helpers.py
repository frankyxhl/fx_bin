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


def stderr_capturing_runner():
    """CliRunner whose Result exposes stderr separately from stdout.

    Click < 8.2 needs mix_stderr=False for that; Click >= 8.2 removed the
    kwarg and always captures stderr separately. The project allows both
    (click = ^8.1.3), so pick by signature.
    """
    import inspect

    from click.testing import CliRunner

    if "mix_stderr" in inspect.signature(CliRunner.__init__).parameters:
        return CliRunner(mix_stderr=False)
    return CliRunner()
