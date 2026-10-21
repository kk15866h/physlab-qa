import math

import numpy as np
import pytest

from physlab_qa.fit import linear_fit
from physlab_qa.uncertainty import propagate_uncertainty


def _closed_form_ols(x: np.ndarray, y: np.ndarray):
    n = len(x)
    x_mean = float(np.mean(x))
    y_mean = float(np.mean(y))
    sxx = float(np.sum((x - x_mean) ** 2))
    sxy = float(np.sum((x - x_mean) * (y - y_mean)))
    slope = sxy / sxx
    intercept = y_mean - slope * x_mean
    residuals = y - (intercept + slope * x)
    residual_variance = float(np.sum(residuals**2)) / (n - 2)
    slope_stderr = math.sqrt(residual_variance / sxx)
    intercept_stderr = math.sqrt(
        residual_variance * (1.0 / n + x_mean**2 / sxx)
    )
    return intercept, slope, intercept_stderr, slope_stderr


def _closed_form_wls(x: np.ndarray, y: np.ndarray, sigma: np.ndarray):
    weights = 1.0 / sigma**2
    sw = float(np.sum(weights))
    sx = float(np.sum(weights * x))
    sy = float(np.sum(weights * y))
    sxx = float(np.sum(weights * x * x))
    sxy = float(np.sum(weights * x * y))
    delta = sw * sxx - sx**2
    intercept = (sxx * sy - sx * sxy) / delta
    slope = (sw * sxy - sx * sy) / delta
    intercept_stderr = math.sqrt(sxx / delta)
    slope_stderr = math.sqrt(sw / delta)
    fitted = intercept + slope * x
    weighted_mean = float(np.sum(weights * y) / sw)
    weighted_residual_ss = float(np.sum(weights * (y - fitted) ** 2))
    weighted_total_ss = float(np.sum(weights * (y - weighted_mean) ** 2))
    r_squared = 1.0 - weighted_residual_ss / weighted_total_ss
    return intercept, slope, intercept_stderr, slope_stderr, r_squared


def test_ordinary_fit_matches_closed_form_reference():
    x = np.array([-1.0, 0.0, 1.0, 2.0, 4.0])
    y = np.array([0.2, 0.9, 2.1, 3.3, 5.8])
    expected = _closed_form_ols(x, y)
    result = linear_fit(x, y)

    assert result.intercept == pytest.approx(expected[0], rel=1e-12, abs=1e-12)
    assert result.slope == pytest.approx(expected[1], rel=1e-12, abs=1e-12)
    assert result.intercept_stderr == pytest.approx(expected[2], rel=1e-12)
    assert result.slope_stderr == pytest.approx(expected[3], rel=1e-12)


def test_weighted_fit_matches_closed_form_reference():
    x = np.array([0.0, 1.0, 2.0, 3.0, 5.0])
    y = np.array([0.9, 2.2, 3.7, 5.1, 8.0])
    sigma = np.array([0.10, 0.15, 0.20, 0.30, 0.45])
    expected = _closed_form_wls(x, y, sigma)
    result = linear_fit(x, y, sigma_y=sigma)

    assert result.intercept == pytest.approx(expected[0], rel=1e-12, abs=1e-12)
    assert result.slope == pytest.approx(expected[1], rel=1e-12, abs=1e-12)
    assert result.intercept_stderr == pytest.approx(expected[2], rel=1e-12)
    assert result.slope_stderr == pytest.approx(expected[3], rel=1e-12)
    assert result.r_squared == pytest.approx(expected[4], rel=1e-12)


def test_uncertainty_matches_analytic_derivatives():
    values = np.array([2.0, 0.4])
    uncertainties = np.array([0.03, 0.02])

    result = propagate_uncertainty(
        lambda x: x[0] ** 2 * math.sin(x[1]),
        values,
        uncertainties,
    )

    derivatives = np.array(
        [
            2.0 * values[0] * math.sin(values[1]),
            values[0] ** 2 * math.cos(values[1]),
        ]
    )
    expected_uncertainty = math.sqrt(float(np.sum((derivatives * uncertainties) ** 2)))

    assert result.sensitivities[0] == pytest.approx(derivatives[0], rel=1e-7)
    assert result.sensitivities[1] == pytest.approx(derivatives[1], rel=1e-7)
    assert result.standard_uncertainty == pytest.approx(expected_uncertainty, rel=1e-7)
