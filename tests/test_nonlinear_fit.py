import math

import numpy as np
import pytest

from physlab_qa.nonlinear import NonlinearFitError, nonlinear_fit


def _exponential_decay(x, amplitude, decay_rate, offset):
    return amplitude * np.exp(-decay_rate * x) + offset


def _quadratic(x, quadratic, linear, offset):
    return quadratic * x**2 + linear * x + offset


def test_exponential_fit_recovers_known_synthetic_parameters():
    x = np.linspace(0.0, 5.0, 31)
    y = _exponential_decay(x, 2.5, 0.8, 0.3) + 0.015 * np.sin(2.7 * x)

    result = nonlinear_fit(
        x,
        y,
        model=_exponential_decay,
        p0=[2.0, 0.5, 0.1],
        parameter_names=("amplitude", "decay_rate", "offset"),
    )

    assert result.converged
    assert result.optimizer_status in (1, 2, 3, 4)
    assert result.parameters == pytest.approx((2.5, 0.8, 0.3), abs=0.02)
    assert all(math.isfinite(value) and value > 0 for value in result.parameter_stderr)
    assert len(result.parameter_covariance) == 3
    assert result.r_squared > 0.999
    assert result.degrees_of_freedom == len(x) - 3


def test_nonlinear_fit_matches_independent_ordinary_least_squares_reference():
    x = np.linspace(-1.5, 2.0, 17)
    y = _quadratic(x, 1.2, -0.7, 2.5) + 0.02 * np.sin(2.0 * x)
    design = np.column_stack((x**2, x, np.ones_like(x)))
    reference_parameters, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    assert rank == 3
    reference_residuals = y - design @ reference_parameters
    rss = float(np.dot(reference_residuals, reference_residuals))
    reference_covariance = rss / (len(x) - 3) * np.linalg.inv(design.T @ design)

    result = nonlinear_fit(
        x,
        y,
        model=_quadratic,
        p0=[1.0, -0.5, 2.0],
        parameter_names=("quadratic", "linear", "offset"),
    )

    assert result.parameters == pytest.approx(reference_parameters, rel=1e-8, abs=1e-9)
    np.testing.assert_allclose(
        result.parameter_covariance, reference_covariance, rtol=1e-7, atol=1e-10
    )
    np.testing.assert_allclose(
        result.parameter_stderr, np.sqrt(np.diag(reference_covariance)), rtol=1e-7
    )


def test_weighted_nonlinear_covariance_uses_absolute_sigma():
    x = np.linspace(-1.5, 2.0, 17)
    y = _quadratic(x, 1.2, -0.7, 2.5) + 0.02 * np.sin(2.0 * x)
    sigma = np.linspace(0.02, 0.06, len(x))
    design = np.column_stack((x**2, x, np.ones_like(x)))
    weighted_design = design / sigma[:, None]
    reference_parameters, _, rank, _ = np.linalg.lstsq(
        weighted_design, y / sigma, rcond=None
    )
    assert rank == 3
    reference_covariance = np.linalg.inv(weighted_design.T @ weighted_design)

    result = nonlinear_fit(
        x,
        y,
        model=_quadratic,
        p0=[1.0, -0.5, 2.0],
        parameter_names=("quadratic", "linear", "offset"),
        sigma_y=sigma,
    )

    assert result.weighted
    assert result.parameters == pytest.approx(reference_parameters, rel=1e-8, abs=1e-9)
    np.testing.assert_allclose(
        result.parameter_covariance, reference_covariance, rtol=1e-7, atol=1e-10
    )
    assert result.chi_square is not None
    assert result.reduced_chi_square is not None


def test_rank_deficient_model_jacobian_is_rejected():
    def redundant_model(x, first, second):
        return (first + second) * x

    x = np.linspace(0.0, 3.0, 12)
    y = 2.0 * x
    with pytest.raises(ValueError, match="rank deficient"):
        nonlinear_fit(x, y, model=redundant_model, p0=[1.0, 1.0])


def test_non_convergence_is_reported_without_a_fake_result():
    x = np.linspace(0.0, 5.0, 31)
    y = _exponential_decay(x, 2.5, 0.8, 0.3) + 0.015 * np.sin(2.7 * x)
    with pytest.raises(NonlinearFitError, match="did not converge"):
        nonlinear_fit(x, y, model=_exponential_decay, p0=[2.0, 0.5, 0.1], maxfev=1)


def test_model_shape_and_parameter_names_are_validated():
    x = np.linspace(0.0, 1.0, 5)
    y = x.copy()
    with pytest.raises(ValueError, match="matching x"):
        nonlinear_fit(x, y, model=lambda values, a: a, p0=[1.0])
    with pytest.raises(ValueError, match="parameter_names"):
        nonlinear_fit(
            x,
            y,
            model=lambda values, a, b: a * values + b,
            p0=[1.0, 0.0],
            parameter_names=("duplicate", "duplicate"),
        )
