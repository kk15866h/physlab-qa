"""Markdown report generation."""

from __future__ import annotations

import math
from pathlib import Path

from physlab_qa.fit import LinearFitResult
from physlab_qa.nonlinear import NonlinearFitResult

# Keep formatting consistent for NaN and infinity in every report.


def _fmt(value: float) -> str:
    return "undefined" if not math.isfinite(value) else f"{value:.8g}"


def write_fit_report(
    result: LinearFitResult,
    *,
    x_name: str,
    y_name: str,
    source_path: str,
    output_path: str | Path,
    title: str = "Linear fit report",
    plot_path: str | None = None,
) -> Path:
    """Write a report that records fit type, metrics, provenance, and limitations."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fit_type = "weighted least squares" if result.weighted else "ordinary least squares"
    lines = [
        f"# {title}",
        "",
        "## Provenance",
        "",
        f"- Source CSV: `{source_path}`",
        f"- x column: `{x_name}`",
        f"- y column: `{y_name}`",
        f"- Fit type: {fit_type}",
        f"- Observations: {len(result.fitted)}",
        "",
        "## Model",
        "",
        f"`{y_name} = intercept + slope × {x_name}`",
        "",
        "| Quantity | Estimate | Standard error |",
        "|---|---:|---:|",
        f"| Intercept | {_fmt(result.intercept)} | {_fmt(result.intercept_stderr)} |",
        f"| Slope | {_fmt(result.slope)} | {_fmt(result.slope_stderr)} |",
        "",
        "## Diagnostics",
        "",
        f"- R²: {_fmt(result.r_squared)}",
        f"- RMSE (unweighted): {_fmt(result.rmse)}",
        f"- Residual sum of squares (unweighted): {_fmt(result.residual_sum_squares)}",
        f"- Degrees of freedom: {result.degrees_of_freedom}",
    ]
    if result.chi_square is not None:
        lines.extend(
            [
                f"- Chi-square: {_fmt(result.chi_square)}",
                (
                    f"- Reduced chi-square: {_fmt(result.reduced_chi_square)}"
                    if result.reduced_chi_square is not None
                    else "- Reduced chi-square: undefined (zero residual degrees of freedom)"
                ),
            ]
        )
    if plot_path:
        lines.extend(["", "## Plot", "", f"![Fit plot]({plot_path})"])
    lines.extend(
        [
            "",
            "## Interpretation notes",
            "",
            (
                "- R² is computed with weighted sums for weighted fits and ordinary sums "
                "for unweighted fits."
            ),
            "- RMSE and residual sum of squares are unweighted summaries, including for weighted fits.",
            "- These statistics do not establish that the selected model is physically appropriate.",
            "- Inspect residual structure and experimental assumptions before drawing conclusions.",
            "- Standard errors do not include every possible systematic uncertainty.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def write_nonlinear_fit_report(
    result: NonlinearFitResult,
    *,
    x_name: str,
    y_name: str,
    source_path: str,
    model_equation: str,
    output_path: str | Path,
    title: str = "Nonlinear fit report",
    plot_path: str | None = None,
) -> Path:
    """Write nonlinear parameter estimates, covariance, convergence, and limitations."""
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# {title}",
        "",
        "## Provenance",
        "",
        f"- Source data: {source_path}",
        f"- x variable: {x_name}",
        f"- y variable: {y_name}",
        f"- Model identifier: {result.model_name}",
        f"- Fit type: {'weighted least squares' if result.weighted else 'ordinary least squares'}",
        f"- Observations: {len(result.fitted)}",
        f"- Degrees of freedom: {result.degrees_of_freedom}",
        "",
        "## Model",
        "",
        model_equation,
        "",
        "## Parameters",
        "",
        "| Parameter | Estimate | Standard error |",
        "|---|---:|---:|",
    ]
    for name, value, stderr in zip(
        result.parameter_names, result.parameters, result.parameter_stderr
    ):
        lines.append(f"| {name} | {_fmt(value)} | {_fmt(stderr)} |")
    lines.extend(
        [
            "",
            "## Parameter covariance matrix",
            "",
            "| Parameter | " + " | ".join(result.parameter_names) + " |",
            "|---|" + "---:|" * len(result.parameter_names),
        ]
    )
    for name, row in zip(result.parameter_names, result.parameter_covariance):
        lines.append(f"| {name} | " + " | ".join(_fmt(value) for value in row) + " |")
    lines.extend(
        [
            "",
            "## Diagnostics",
            "",
            f"- Converged: {'yes' if result.converged else 'no'}",
            f"- Optimizer status: {result.optimizer_status}",
            f"- Optimizer message: {result.optimizer_message.replace(chr(10), ' ')}",
            f"- R²: {_fmt(result.r_squared)}",
            f"- RMSE (unweighted): {_fmt(result.rmse)}",
            f"- Residual sum of squares (unweighted): {_fmt(result.residual_sum_squares)}",
        ]
    )
    if result.chi_square is not None:
        lines.extend(
            [
                f"- Chi-square: {_fmt(result.chi_square)}",
                f"- Reduced chi-square: {_fmt(result.reduced_chi_square)}",
            ]
        )
    if plot_path:
        lines.extend(["", "## Plot", "", f"![Fit plot]({plot_path})"])
    lines.extend(
        [
            "",
            "## Interpretation notes",
            "",
            "- Parameter standard errors and covariance are local approximations around the fitted solution.",
            "- Optimizer convergence does not establish that the selected model is physically valid.",
            "- No observations are automatically removed as outliers.",
            "- Weighted fits treat supplied sigma_y values as known, independent absolute standard uncertainties.",
            "- Systematic errors, correlated observations, and model discrepancy are not automatically included.",
            "",
        ]
    )
    output.write_text("\n".join(lines), encoding="utf-8")
    return output
