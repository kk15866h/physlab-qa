import pytest
from physlab_qa.uncertainty import propagate_uncertainty

def test_product_uncertainty():
    r=propagate_uncertainty(lambda x:x[0]*x[1],[2,3],[0.1,0.2])
    assert r.value == pytest.approx(6)
    assert r.standard_uncertainty == pytest.approx((3**2*0.1**2+2**2*0.2**2)**0.5,rel=1e-5)

def test_bad_uncertainty_rejected():
    with pytest.raises(ValueError):
        propagate_uncertainty(lambda x:x[0],[1],[-1])
