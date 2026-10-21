"""CSV loading and data-quality checks."""
import csv, math
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class NumericColumns:
    x: list[float]
    y: list[float]
    sigma_y: list[float] | None = None

@dataclass(frozen=True)
class ValidationReport:
    path: str
    rows: int
    columns: tuple[str,...]
    missing_cells: tuple[str,...]
    non_numeric_cells: tuple[str,...]
    duplicate_rows: tuple[int,...]
    missing_required_columns: tuple[str,...]
    @property
    def ok(self): return not (self.missing_cells or self.non_numeric_cells or self.missing_required_columns)
    def to_dict(self):
        return {"path":self.path,"rows":self.rows,"columns":list(self.columns),"missing_cells":list(self.missing_cells),"non_numeric_cells":list(self.non_numeric_cells),"duplicate_rows":list(self.duplicate_rows),"missing_required_columns":list(self.missing_required_columns),"ok":self.ok}

def _read_table(path, delimiter=","):
    source=Path(path)
    if len(delimiter)!=1: raise ValueError("delimiter must be exactly one character")
    try:
        with source.open("r",encoding="utf-8-sig",newline="") as f:
            reader=csv.DictReader(f,delimiter=delimiter)
            if reader.fieldnames is None: raise ValueError("CSV has no header row")
            headers=[n.strip() if n else "" for n in reader.fieldnames]
            if not headers or any(not n for n in headers): raise ValueError("CSV contains an empty column name")
            if len(set(headers))!=len(headers): raise ValueError("CSV contains duplicate column names")
            rows=[]
            for line,row in enumerate(reader,2):
                if None in row: raise ValueError(f"row {line} has more fields than the header")
                rows.append({headers[i]:(row.get(reader.fieldnames[i]) or "").strip() for i in range(len(headers))})
    except FileNotFoundError as e: raise FileNotFoundError(f"CSV file not found: {source}") from e
    if not rows: raise ValueError("CSV contains a header but no data rows")
    return headers,rows

def read_numeric_columns(path, *, x_column, y_column, sigma_y_column=None, delimiter=","):
    headers,rows=_read_table(path,delimiter); requested=[x_column,y_column]+([sigma_y_column] if sigma_y_column else [])
    absent=[n for n in requested if n not in headers]
    if absent: raise ValueError("column(s) not found: "+", ".join(absent))
    parsed={n:[] for n in requested}
    for line,row in enumerate(rows,2):
        for name in requested:
            try: value=float(row[name])
            except (TypeError,ValueError) as e: raise ValueError(f"row {line}, column '{name}' is not numeric: {row[name]!r}") from e
            if not math.isfinite(value): raise ValueError(f"row {line}, column '{name}' is not finite")
            parsed[name].append(value)
    return NumericColumns(parsed[x_column],parsed[y_column],parsed[sigma_y_column] if sigma_y_column else None)

def validate_csv(path, *, required_columns=(), numeric_columns=(), delimiter=","):
    headers,rows=_read_table(path,delimiter)
    missing_required=tuple(dict.fromkeys([n for n in required_columns if n not in headers]+[n for n in numeric_columns if n not in headers]))
    missing=[]; nonnumeric=[]; seen=set(); duplicates=[]
    for line,row in enumerate(rows,2):
        tup=tuple(row.get(c,"") for c in headers)
        if tup in seen: duplicates.append(line)
        seen.add(tup)
        for c in headers:
            if row.get(c,"")== "": missing.append(f"line {line}, column '{c}'")
        for c in numeric_columns:
            if c not in headers or row.get(c,"")== "": continue
            try: v=float(row[c])
            except ValueError: nonnumeric.append(f"line {line}, column '{c}': {row[c]!r}"); continue
            if not math.isfinite(v): nonnumeric.append(f"line {line}, column '{c}': non-finite")
    return ValidationReport(str(path),len(rows),tuple(headers),tuple(missing),tuple(nonnumeric),tuple(duplicates),missing_required)
