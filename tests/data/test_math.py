import pytest
from src.data.math_utils import remove_margin, calculate_consensus

def test_remove_margin():
    # Example 1: Fair odds with no margin (1/2 + 1/4 + 1/4 = 1.0)
    # Odds: 2.0, 4.0, 4.0
    p1, px, p2 = remove_margin(2.0, 4.0, 4.0)
    assert pytest.approx(p1 + px + p2) == 1.0
    assert pytest.approx(p1) == 0.5
    assert pytest.approx(px) == 0.25
    assert pytest.approx(p2) == 0.25

    # Example 2: Bookmaker odds with margin (e.g. 2.10 3.40 3.20)
    o_h, o_d, o_a = 2.10, 3.40, 3.20
    ph, pd, pa = remove_margin(o_h, o_d, o_a)
    assert pytest.approx(ph + pd + pa) == 1.0
    
    imp_h = 1.0 / o_h
    imp_d = 1.0 / o_d
    imp_a = 1.0 / o_a
    margin = imp_h + imp_d + imp_a
    
    assert pytest.approx(ph) == imp_h / margin
    assert pytest.approx(pd) == imp_d / margin
    assert pytest.approx(pa) == imp_a / margin

def test_remove_margin_invalid_odds():
    # Odds must be > 1.0
    with pytest.raises(ValueError):
        remove_margin(1.0, 2.0, 3.0)
    with pytest.raises(ValueError):
        remove_margin(2.0, 0.5, 3.0)
