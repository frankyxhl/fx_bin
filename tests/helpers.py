"""Shared test helpers."""


def table_cells(row: str) -> list[str]:
    """Return stripped cells from an ASCII table row."""

    return [cell.strip() for cell in row.strip().strip("|").split("|")]
