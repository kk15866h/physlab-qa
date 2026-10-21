"""End-to-end example: estimate g from synthetic pendulum data.

The CSV is synthetic teaching data, not a real measurement. This example
propagates only the regression slope's standard error; it does not include
length uncertainty, timing uncertainty, correlations, or systematic effects.
Run from the repository root after installing the package.
"""
from __future__ import annotations

import math
from pathlib import Path

from physlab_qa.csvio import read_numeric_columns
from physlab_qa.fit import linear_fit
from physlab_qa.report import write_fit_report
from physlab_qa.uncertainty import propagate_uncertainty

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "examples" / "pendulum.csv"
OUTPUT = ROOT / "build" / "pendulum-report.md"


def main() -> int:
    columns = read_numeric_columns(
        DATA,
        x_column="length_m",
        y_column="period_squared_s2",
    )
    fit = linear_fit(columns.x, columns.y)

    # For a simple pendulum at small angles: T² = (4π²/g)L + intercept.
    if fit.slope <= 0:
        raise ValueError("the fitted slope must be positive to estimate g")
    gravity = propagate_uncertainty(
        lambda values: 4.0 * math.pi**2 / values[0],
        [fit.slope],
        [fit.slope_stderr],
    )
    write_fit_report(
        fit,
        x_name="length_m",
        y_name="period_squared_s2",
        source_path=str(DATA.relative_to(ROOT)),
        output_path=OUTPUT,
        title="Simple pendulum: synthetic demonstration",
    )

    print("Synthetic demonstration only; do not cite as experimental evidence.")
    print(f"Fit slope: {fit.slope:.5f} ± {fit.slope_stderr:.5f} s²/m")
    print(f"Estimated g: {gravity.value:.4f} ± {gravity.standard_uncertainty:.4f} m/s²")
    print(f"Markdown report: {OUTPUT.relative_to(ROOT)}")
    print("Uncertainty includes the fitted slope's statistical standard error only.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
