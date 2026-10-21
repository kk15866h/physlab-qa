import numpy as np
import pytest

from physlab_qa.fit import linear_fit


def test_exact_line():
    result = linear_fit([0, 1, 2, 3], [1, 3, 5, 7])
    assert result.intercept == pytest.approx(1)
    assert result.slope == pytest.approx(2)
    assert result.r_squared == pytest.approx(1)


def test_constant_response_has_undefined_r_squared():
    result = linear_fit([0, 1, 2], [5, 5, 5])
    assert np.isnan(result.r_squared)


def test_weighted_fit_reports_chi_square_and_weighted_r_squared():
    result = linear_fit(
        [0, 1, 2, 3],
        [1.1, 2.9, 5.2, 6.8],
        sigma_y=[0.2, 0.2, 0.5, 0.5],
    )
    assert result.weighted
    assert result.chi_square is not None
    assert result.slope_stderr > 0
    assert result.r_squared == pytest.approx(0.9964014618, abs=1e-8)


def test_weighted_exact_line_has_unit_r_squared():
    result = linear_fit([0, 1, 2, 3], [1, 3, 5, 7], sigma_y=[0.1, 0.2, 0.3, 0.4])
    assert result.r_squared == pytest.approx(1.0, abs=1e-12)


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        linear_fit([1, 1, 1], [2, 3, 4])
    with pytest.raises(ValueError):
        linear_fit([1, 2], [2, float("nan")])
    with pytest.raises(ValueError):
        linear_fit([1, 2], [2, 3], sigma_y=[0, 1])


def test_influence_diagnostics_identify_a_synthetic_outlier():
    x = np.arange(10, dtype=float)
    y = 1.0 + 2.0 * x
    y[5] += 10.0

    result = linear_fit(x, y)

    assert sum(result.leverage) == pytest.approx(2.0, abs=1e-12)
    assert len(result.standardized_residuals) == len(x)
    assert len(result.cooks_distance) == len(x)
    assert result.durbin_watson is not None
    assert 0.0 <= result.durbin_watson <= 4.0
    assert int(np.argmax(result.cooks_distance)) == 5
    assert 6 in result.potentially_influential_rows
    assert result.potentially_influential_rows == (6,)


def test_weighted_influence_diagnostics_use_known_sigma_and_omit_durbin_watson():
    x = np.arange(8, dtype=float)
    y = 0.5 + 1.25 * x + np.array([0.01, -0.02, 0.015, -0.01, 0.02, -0.015, 0.005, -0.005])
    sigma = np.linspace(0.02, 0.05, len(x))

    result = linear_fit(x, y, sigma_y=sigma)

    assert result.weighted
    assert sum(result.leverage) == pytest.approx(2.0, abs=1e-12)
    assert result.durbin_watson is None
    assert all(np.isfinite(value) for value in result.standardized_residuals)
    assert all(np.isfinite(value) for value in result.cooks_distance)


def test_exact_line_has_undefined_standardized_residuals_and_durbin_watson():
    result = linear_fit([0, 1, 2, 3], [1, 3, 5, 7])

    assert sum(result.leverage) == pytest.approx(2.0, abs=1e-12)
    assert all(np.isnan(value) for value in result.standardized_residuals)
    assert all(np.isnan(value) for value in result.cooks_distance)
    assert np.isnan(result.durbin_watson)
    assert result.potentially_influential_rows == ()


def test_residual_diagnostics_handle_small_residuals_on_a_large_baseline():
    x = np.arange(8, dtype=float)
    perturbations = np.array([0, 1, -1, 0, 1, -1, 0, 1], dtype=float)
    y = 1e12 + 2.0 * x + perturbations

    result = linear_fit(x, y)

    assert result.residual_sum_squares > 0
    assert np.isfinite(result.durbin_watson)
    assert all(np.isfinite(value) for value in result.standardized_residuals)
