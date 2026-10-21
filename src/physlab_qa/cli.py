"""Command-line interface for PhysLab QA."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Sequence

from physlab_qa.csvio import read_numeric_columns, validate_csv
from physlab_qa.fit import LinearFitResult, linear_fit
from physlab_qa.report import write_fit_report


def _comma_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="physlab-qa",
        description="Validate experimental CSV data and generate reproducible linear-fit reports.",
    )
    parser.add_argument("--version", action="version", version="physlab-qa 0.1.0")
    commands = parser.add_subparsers(dest="command", required=True)

    validate = commands.add_parser("validate", help="audit a CSV without modifying it")
    validate.add_argument("csv")
    validate.add_argument("--required-cols")
    validate.add_argument("--numeric-cols")
    validate.add_argument("--delimiter", default=",")
    validate.add_argument("--json", action="store_true", help="emit machine-readable JSON")

    fit = commands.add_parser("fit", help="fit a linear model and write a Markdown report")
    fit.add_argument("csv")
    fit.add_argument("--x", required=True)
    fit.add_argument("--y", required=True)
    fit.add_argument("--sigma-y")
    fit.add_argument("--delimiter", default=",")
    fit.add_argument("--output", default="fit-report.md")
    fit.add_argument("--plot")
    fit.add_argument("--title", default="Linear fit report")
    fit.add_argument("--x-label")
    fit.add_argument("--y-label")
    fit.add_argument("--json", action="store_true", help="emit fit result as JSON")
    return parser


def _write_optional_plot(args: argparse.Namespace, result: LinearFitResult, x, y) -> str | None:
    if not args.plot:
        return None

    from physlab_qa.plotting import save_fit_plot

    save_fit_plot(
        x,
        y,
        result,
        x_label=args.x_label or args.x,
        y_label=args.y_label or args.y,
        output_path=args.plot,
        title=args.title,
    )
    return os.path.relpath(
        Path(args.plot).resolve(),
        Path(args.output).resolve().parent,
    ).replace(os.sep, "/")


def _run_validate(args: argparse.Namespace) -> int:
    report = validate_csv(
        args.csv,
        required_columns=_comma_list(args.required_cols),
        numeric_columns=_comma_list(args.numeric_cols),
        delimiter=args.delimiter,
    )
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(f"{'PASS' if report.ok else 'FAIL'}: {report.path}")
        print(f"Rows: {report.rows}; columns: {', '.join(report.columns)}")
        print(
            "Missing cells: "
            f"{len(report.missing_cells)}; non-numeric cells: {len(report.non_numeric_cells)}"
        )
        print(f"Duplicate rows: {len(report.duplicate_rows)} (reported, never auto-removed)")
    return 0 if report.ok else 2


def _run_fit(args: argparse.Namespace) -> int:
    columns = read_numeric_columns(
        args.csv,
        x_column=args.x,
        y_column=args.y,
        sigma_y_column=args.sigma_y,
        delimiter=args.delimiter,
    )
    result = linear_fit(columns.x, columns.y, sigma_y=columns.sigma_y)
    plot_path = _write_optional_plot(args, result, columns.x, columns.y)
    write_fit_report(
        result,
        x_name=args.x,
        y_name=args.y,
        source_path=args.csv,
        output_path=args.output,
        title=args.title,
        plot_path=plot_path,
    )

    if args.json:
        payload = result.to_dict()
        payload["source_csv"] = args.csv
        payload["x_column"] = args.x
        payload["y_column"] = args.y
        payload["report_path"] = args.output
        print(json.dumps(payload, allow_nan=True, indent=2))
    else:
        print(f"Slope: {result.slope:.8g} +/- {result.slope_stderr:.3g}")
        print(f"Intercept: {result.intercept:.8g} +/- {result.intercept_stderr:.3g}")
        print(f"R2: {result.r_squared:.8g}; RMSE: {result.rmse:.8g}")
        print(f"Report: {args.output}")
        if args.plot:
            print(f"Plot: {args.plot}")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate":
            return _run_validate(args)
        return _run_fit(args)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"physlab-qa: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
