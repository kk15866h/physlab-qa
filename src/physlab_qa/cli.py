"""Command-line interface for PhysLab QA."""

from __future__ import annotations

import argparse
import json
import math
import os

import numpy as np
import sys
from pathlib import Path
from typing import Sequence

from physlab_qa import __version__
from physlab_qa.csvio import read_numeric_columns, validate_csv
from physlab_qa.fit import LinearFitResult, linear_fit
from physlab_qa.nonlinear import NonlinearFitResult, nonlinear_fit
from physlab_qa.report import write_fit_report, write_nonlinear_fit_report


def _comma_list(value: str | None) -> list[str]:
    if not value:
        return []
    return [part.strip() for part in value.split(",") if part.strip()]


def _json_safe(value: object) -> object:
    """Convert non-finite floats to null-compatible values recursively."""
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return value



def _comma_floats(value: str) -> list[float]:
    parts = [part.strip() for part in value.split(",")]
    if not parts or any(not part for part in parts):
        raise ValueError("--p0 must be a comma-separated list of finite numbers")
    try:
        values = [float(part) for part in parts]
    except ValueError as exc:
        raise ValueError("--p0 must be a comma-separated list of finite numbers") from exc
    if not all(math.isfinite(item) for item in values):
        raise ValueError("--p0 values must be finite")
    return values


def _exponential_decay_model(x, amplitude, decay_rate, offset):
    return amplitude * np.exp(-decay_rate * x) + offset


def _quadratic_model(x, quadratic, linear, offset):
    return quadratic * x**2 + linear * x + offset


_NONLINEAR_MODELS = {
    "exponential-decay": (
        _exponential_decay_model,
        ("amplitude", "decay_rate", "offset"),
        "y = A exp(−k x) + C",
    ),
    "quadratic": (
        _quadratic_model,
        ("quadratic", "linear", "offset"),
        "y = a x² + b x + c",
    ),
}


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="physlab-qa",
        description="Validate experimental CSV data and generate reproducible linear-fit reports.",
    )
    parser.add_argument("--version", action="version", version=f"physlab-qa {__version__}")
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

    nonlinear = commands.add_parser(
        "fit-nonlinear",
        help="fit an explicit nonlinear model (requires the SciPy extra)",
    )
    nonlinear.add_argument("csv")
    nonlinear.add_argument("--x", required=True)
    nonlinear.add_argument("--y", required=True)
    nonlinear.add_argument("--model", choices=tuple(_NONLINEAR_MODELS), required=True)
    nonlinear.add_argument(
        "--p0",
        required=True,
        help="comma-separated initial parameters in the selected model's documented order",
    )
    nonlinear.add_argument("--sigma-y")
    nonlinear.add_argument("--delimiter", default=",")
    nonlinear.add_argument("--output", default="nonlinear-fit-report.md")
    nonlinear.add_argument("--plot")
    nonlinear.add_argument("--title", default="Nonlinear fit report")
    nonlinear.add_argument("--x-label")
    nonlinear.add_argument("--y-label")
    nonlinear.add_argument("--maxfev", type=int, default=10000)
    nonlinear.add_argument("--json", action="store_true", help="emit fit result as JSON")

    return parser


def _write_optional_plot(
    args: argparse.Namespace,
    result: LinearFitResult | NonlinearFitResult,
    x,
    y,
) -> str | None:
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
        print(json.dumps(_json_safe(report.to_dict()), ensure_ascii=False, indent=2, allow_nan=False))
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
        print(json.dumps(_json_safe(payload), allow_nan=False, indent=2))
    else:
        print(f"Slope: {result.slope:.8g} +/- {result.slope_stderr:.3g}")
        print(f"Intercept: {result.intercept:.8g} +/- {result.intercept_stderr:.3g}")
        print(f"R2: {result.r_squared:.8g}; RMSE: {result.rmse:.8g}")
        print(f"Report: {args.output}")
        if args.plot:
            print(f"Plot: {args.plot}")
    return 0



def _run_nonlinear_fit(args: argparse.Namespace) -> int:
    columns = read_numeric_columns(
        args.csv,
        x_column=args.x,
        y_column=args.y,
        sigma_y_column=args.sigma_y,
        delimiter=args.delimiter,
    )
    model, parameter_names, model_equation = _NONLINEAR_MODELS[args.model]
    p0 = _comma_floats(args.p0)
    if len(p0) != len(parameter_names):
        expected = ", ".join(parameter_names)
        raise ValueError(
            f"--p0 for {args.model} requires {len(parameter_names)} values in this order: {expected}"
        )
    result = nonlinear_fit(
        columns.x,
        columns.y,
        model=model,
        p0=p0,
        parameter_names=parameter_names,
        model_name=args.model,
        sigma_y=columns.sigma_y,
        maxfev=args.maxfev,
    )
    plot_path = _write_optional_plot(args, result, columns.x, columns.y)
    write_nonlinear_fit_report(
        result,
        x_name=args.x,
        y_name=args.y,
        source_path=args.csv,
        model_equation=model_equation,
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
        print(json.dumps(_json_safe(payload), allow_nan=False, indent=2))
    else:
        print(f"Converged: {result.converged} (optimizer status {result.optimizer_status})")
        for name, value, stderr in zip(
            result.parameter_names, result.parameters, result.parameter_stderr
        ):
            print(f"{name}: {value:.8g} +/- {stderr:.3g}")
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
        if args.command == "fit":
            return _run_fit(args)
        return _run_nonlinear_fit(args)
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"physlab-qa: error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
