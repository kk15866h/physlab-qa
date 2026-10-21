"""Optional diagnostic plots for fitted linear models."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from physlab_qa.fit import LinearFitResult


def save_fit_plot(
    x: Sequence[float],
    y: Sequence[float],
    result: LinearFitResult,
    *,
    x_label: str,
    y_label: str,
    output_path: str | Path,
    title: str = "Linear fit and residuals",
) -> Path:
    """Save observed data, fitted line, and residuals to an image file."""
    try:
        import matplotlib.pyplot as plt
    except ImportError as exc:
        raise RuntimeError(
            "Plotting requires Matplotlib; install with `pip install -e '.[plot]'`."
        ) from exc

    x_values = list(map(float, x))
    y_values = list(map(float, y))
    if not x_values:
        raise ValueError("x and y must contain at least one observation")
    if len(x_values) != len(y_values):
        raise ValueError("x and y must have the same number of observations")
    if len(result.fitted) != len(x_values) or len(result.residuals) != len(x_values):
        raise ValueError("fit result length does not match the supplied observations")

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    order = sorted(range(len(x_values)), key=x_values.__getitem__)

    figure, (fit_axis, residual_axis) = plt.subplots(
        2,
        1,
        figsize=(7.2, 6.4),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    fit_axis.scatter(x_values, y_values, label="Observed data")
    fit_axis.plot(
        [x_values[index] for index in order],
        [result.fitted[index] for index in order],
        label="Linear fit",
    )
    fit_axis.set_ylabel(y_label)
    fit_axis.set_title(title)
    fit_axis.legend()
    fit_axis.grid(True, alpha=0.25)

    residual_axis.axhline(0.0, linewidth=1.0)
    residual_axis.scatter(x_values, result.residuals)
    residual_axis.set_xlabel(x_label)
    residual_axis.set_ylabel("Residual")
    residual_axis.grid(True, alpha=0.25)

    figure.tight_layout()
    figure.savefig(output, dpi=180, bbox_inches="tight")
    plt.close(figure)
    return output
