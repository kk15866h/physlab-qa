import numpy as np
import pytest
from physlab_qa.fit import linear_fit

def test_exact_line():
    r=linear_fit([0,1,2,3],[1,3,5,7])
    assert r.intercept == pytest.approx(1)
    assert r.slope == pytest.approx(2)
    assert r.r_squared == pytest.approx(1)

def test_weighted_fit_reports_chi_square():
    r=linear_fit([0,1,2,3],[1.1,2.9,5.2,6.8],sigma_y=[0.2]*4)
    assert r.weighted
    assert r.chi_square is not None
    assert r.slope_stderr > 0

def test_invalid_inputs_rejected():
    with pytest.raises(ValueError): linear_fit([1,1,1],[2,3,4])
    with pytest.raises(ValueError): linear_fit([1,2],[2,float("nan")])
    with pytest.raises(ValueError): linear_fit([1,2],[2,3],sigma_y=[0,1])
