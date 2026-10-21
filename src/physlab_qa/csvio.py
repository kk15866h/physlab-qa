"""CSV loading and data-quality checks."""

from __future__ import annotations

import csv
import math
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class NumericColumns:
    """Numeric columns extracted from an experimental table."""

    x: list[float]
    y: list[float]
    sigma_y: list[float] | None = None


@dataclass(frozen=True)
class ValidationReport:
    """Non-destructive audit result for a CSV file."""

    path: str
    rows: int
    columns: tuple[str, ...]
    missing_cells: tuple[str, ...]
    non_numeric_cells: tuple[str, ...]
    duplicate_rows: tuple[int, ...]
    missing_required_columns: tuple[str, ...]

    @property
    def ok(self) -> bool:
        """Whether the file is structurally usable for the requested analysis.

        Duplicate rows are reported for human review but do not make the file
        invalid because repeated measurements can be legitimate observations.
        """
        return not (
            self.missing_cells
            or self.non_numeric_cells
            or self.missing_required_columns
        )

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-serializable representation."""
        return {
            "path": self.path,
            "rows": self.rows,
            "columns": list(self.columns),
            "missing_cells": list(self.missing_cells),
            "non_numeric_cells": list(self.non_numeric_cells),
            "duplicate_rows": list(self.duplicate_rows),
            "missing_required_columns": list(self.missing_required_columns),
            "ok": self.ok,
        }


def _read_table(
    path: str | Path,
    delimiter: str = ",",
) -> tuple[list[str], list[dict[str, str]]]:
    """Read a CSV into normalized string rows without altering its data."""
    source = Path(path)
    if len(delimiter) != 1:
        raise ValueError("delimiter must be exactly one character")

    try:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle, delimiter=delimiter)
            if reader.fieldnames is None:
                raise ValueError("CSV has no header row")

            raw_headers = reader.fieldnames
            headers = [header.strip() if header is not None else "" for header in raw_headers]
            if not headers or any(not header for header in headers):
                raise ValueError("CSV contains an empty column name")
            if len(set(headers)) != len(headers):
                raise ValueError("CSV contains duplicate column names")

            rows: list[dict[str, str]] = []
            for line_number, row in enumerate(reader, start=2):
                if None in row:
                    raise ValueError(
                        f"row {line_number} has more fields than the header"
                    )

                normalized: dict[str, str] = {}
                for index, normalized_header in enumerate(headers):
                    raw_header = raw_headers[index]
                    raw_value = row.get(raw_header, "")
                    normalized[normalized_header] = (raw_value or "").strip()
                rows.append(normalized)
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"CSV file not found: {source}") from exc

    if not rows:
        raise ValueError("CSV contains a header but no data rows")
    return headers, rows


def read_numeric_columns(
    path: str | Path,
    *,
    x_column: str,
    y_column: str,
    sigma_y_column: str | None = None,
    delimiter: str = ",",
) -> NumericColumns:
    """Read selected columns and require every selected value to be finite."""
    headers, rows = _read_table(path, delimiter)
    requested = [x_column, y_column]
    if sigma_y_column is not None:
        requested.append(sigma_y_column)

    absent = [name for name in requested if name not in headers]
    if absent:
        raise ValueError("column(s) not found: " + ", ".join(absent))

    parsed: dict[str, list[float]] = {name: [] for name in requested}
    for line_number, row in enumerate(rows, start=2):
        for name in requested:
            raw_value = row[name]
            try:
                value = float(raw_value)
            except ValueError as exc:
                raise ValueError(
                    f"row {line_number}, column '{name}' is not numeric: {raw_value!r}"
                ) from exc
            if not math.isfinite(value):
                raise ValueError(
                    f"row {line_number}, column '{name}' is not finite: {raw_value!r}"
                )
            parsed[name].append(value)

    return NumericColumns(
        x=parsed[x_column],
        y=parsed[y_column],
        sigma_y=parsed[sigma_y_column] if sigma_y_column is not None else None,
    )


def validate_csv(
    path: str | Path,
    *,
    required_columns: Sequence[str] = (),
    numeric_columns: Sequence[str] = (),
    delimiter: str = ",",
) -> ValidationReport:
    """Audit a CSV without deleting rows or changing measurements."""
    headers, rows = _read_table(path, delimiter)

    absent_required = [name for name in required_columns if name not in headers]
    absent_numeric = [name for name in numeric_columns if name not in headers]
    missing_required = tuple(dict.fromkeys([*absent_required, *absent_numeric]))

    missing_cells: list[str] = []
    non_numeric_cells: list[str] = []
    duplicate_rows: list[int] = []
    seen_rows: set[tuple[str, ...]] = set()

    for line_number, row in enumerate(rows, start=2):
        row_signature = tuple(row.get(column, "") for column in headers)
        if row_signature in seen_rows:
            duplicate_rows.append(line_number)
        seen_rows.add(row_signature)

        for column in headers:
            if row.get(column, "") == "":
                missing_cells.append(f"line {line_number}, column '{column}'")

        for column in numeric_columns:
            if column not in headers:
                continue
            raw_value = row.get(column, "")
            if raw_value == "":
                continue
            try:
                value = float(raw_value)
            except ValueError:
                non_numeric_cells.append(
                    f"line {line_number}, column '{column}': {raw_value!r}"
                )
                continue
            if not math.isfinite(value):
                non_numeric_cells.append(
                    f"line {line_number}, column '{column}': non-finite {raw_value!r}"
                )

    return ValidationReport(
        path=str(path),
        rows=len(rows),
        columns=tuple(headers),
        missing_cells=tuple(missing_cells),
        non_numeric_cells=tuple(non_numeric_cells),
        duplicate_rows=tuple(duplicate_rows),
        missing_required_columns=missing_required,
    )
