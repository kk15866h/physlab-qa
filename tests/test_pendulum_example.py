import math
from pathlib import Path

import pytest

from physlab_qa.csvio import read_numeric_columns
from physlab_qa.fit import linear_fit
from physlab_qa.uncertainty import propagate_uncertainty


def test_synthetic_pendulum_example_gives_plausible_gravity():
    root = Path(__file__).resolve().parents[1]
    data = root / "examples" / "pendulum.csv"
    columns = read_numeric_columns(
        data,
        x_column="length_m",
        y_column="period_squared_s2",
    )
    fit = linear_fit(columns.x, columns.y)
    gravity = propagate_uncertainty(
        lambda values: 4.0 * math.pi**2 / values[0],
        [fit.slope],
        [fit.slope_stderr],
    )

    assert fit.slope == pytest.approx(4.03, abs=0.02)
    assert gravity.value == pytest.approx(9.80, abs=0.1)
    assert gravity.standard_uncertainty > 0
    assert gravity.standard_uncertainty < 0.2
