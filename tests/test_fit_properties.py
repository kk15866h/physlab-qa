import pytest

from physlab_qa.fit import linear_fit


def test_vertical_translation_changes_only_intercept():
    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 2.2, 4.1, 5.9]
    original = linear_fit(x, y)
    shifted = linear_fit(x, [value + 7.0 for value in y])

    assert shifted.intercept == pytest.approx(original.intercept + 7.0)
    assert shifted.slope == pytest.approx(original.slope)
    assert shifted.r_squared == pytest.approx(original.r_squared)


def test_observation_order_does_not_change_fit():
    x = [0.0, 1.0, 2.0, 3.0]
    y = [1.0, 2.2, 4.1, 5.9]
    original = linear_fit(x, y)
    permuted = linear_fit([x[i] for i in (2, 0, 3, 1)], [y[i] for i in (2, 0, 3, 1)])

    assert permuted.intercept == pytest.approx(original.intercept)
    assert permuted.slope == pytest.approx(original.slope)
    assert permuted.r_squared == pytest.approx(original.r_squared)
