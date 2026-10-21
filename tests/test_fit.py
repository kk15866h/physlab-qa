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


def test_weighted_fit_reports_chi_square():
    result = linear_fit([0, 1, 2, 3], [1.1, 2.9, 5.2, 6.8], sigma_y=[0.2] * 4)
    assert result.weighted
    assert result.chi_square is not None
    assert result.slope_stderr > 0


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        linear_fit([1, 1, 1], [2, 3, 4])
    with pytest.raises(ValueError):
        linear_fit([1, 2], [2, float("nan")])
    with pytest.raises(ValueError):
        linear_fit([1, 2], [2, 3], sigma_y=[0, 1])
