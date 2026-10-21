"""Markdown report generation."""

from __future__ import annotations

from pathlib import Path

from physlab_qa.fit import LinearFitResult


def _fmt(value: float) -> str:
    return "undefined" if value != value else f"{value:.8g}"


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
