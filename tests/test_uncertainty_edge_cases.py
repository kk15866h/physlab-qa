import math

import pytest

from physlab_qa.uncertainty import propagate_uncertainty


def test_linear_function_propagates_uncertainty():
    result = propagate_uncertainty(lambda x: 3.0 * x[0] - 2.0, [4.0], [0.25])

    assert result.value == pytest.approx(10.0)
    assert result.sensitivities[0] == pytest.approx(3.0, rel=1e-7)
    assert result.standard_uncertainty == pytest.approx(0.75, rel=1e-7)


def test_zero_input_uncertainty_gives_zero_output_uncertainty():
    result = propagate_uncertainty(lambda x: x[0] ** 2, [2.0], [0.0])

    assert result.standard_uncertainty == 0.0


def test_nonfinite_function_output_is_rejected():
    with pytest.raises(ValueError, match="finite scalar"):
        propagate_uncertainty(lambda x: math.inf, [1.0], [0.1])


def test_invalid_finite_difference_step_is_rejected():
    with pytest.raises(ValueError, match="steps"):
        propagate_uncertainty(lambda x: x[0], [1.0], [0.1], steps=[0.0])
