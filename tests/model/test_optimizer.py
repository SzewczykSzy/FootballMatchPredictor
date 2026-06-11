import numpy as np
import pytest
from src.model.optimizer import calculate_best_ev

def test_calculate_best_ev_deterministic():
    """
    Test EV engine with a deterministic 100% outcome at 1-0.
    """
    # 6x6 matrix (representing scores 0-0 to 5-5)
    prob_matrix = np.zeros((6, 6))
    prob_matrix[1, 0] = 1.0  # 100% chance of 1-0
    
    # Best prediction should be 1-0, which gets 5 points
    pred, ev = calculate_best_ev(prob_matrix, max_score=5)
    assert pred == (1, 0)
    assert pytest.approx(ev) == 5.0

    # Let's check a prediction like 2-1, which should get 3 points (same goal difference)
    # Since we only evaluate max_ev, let's verify that predicting 2-1 would get 3.
    # To test this, we can temporarily put 100% on 1-0, but set max_score to a value where
    # we can verify other outcomes. The primary test verifies the argmax is correct.

def test_calculate_best_ev_tie_breaker():
    """
    Test edge case for exact EV ties resolving by single-outcome probability.
    
    Probability distribution:
    - 1-0: prob = 0.2
    - 2-0: prob = 0.3
    - 2-1: prob = 0.2
    - 0-3: prob = 0.3
    
    EV calculations:
    - Predict 1-0:
      - actual 1-0 (exact score) -> 5 * 0.2 = 1.0
      - actual 2-0 (tendency) -> 1 * 0.3 = 0.3
      - actual 2-1 (goal diff) -> 3 * 0.2 = 0.6
      - actual 0-3 (incorrect) -> 0 * 0.3 = 0.0
      - Total EV = 1.9
      - Baseline prob = 0.2
      
    - Predict 2-0:
      - actual 1-0 (tendency) -> 1 * 0.2 = 0.2
      - actual 2-0 (exact score) -> 5 * 0.3 = 1.5
      - actual 2-1 (tendency) -> 1 * 0.2 = 0.2
      - actual 0-3 (incorrect) -> 0 * 0.3 = 0.0
      - Total EV = 1.9
      - Baseline prob = 0.3
      
    - Predict 2-1:
      - actual 1-0 (goal diff) -> 3 * 0.2 = 0.6
      - actual 2-0 (tendency) -> 1 * 0.3 = 0.3
      - actual 2-1 (exact score) -> 5 * 0.2 = 1.0
      - actual 0-3 (incorrect) -> 0 * 0.3 = 0.0
      - Total EV = 1.9
      - Baseline prob = 0.2
      
    All three (1-0, 2-0, 2-1) have the identical EV of 1.9.
    The tie-breaker must pick 2-0 because its baseline probability (0.3) is highest.
    """
    prob_matrix = np.zeros((6, 6))
    prob_matrix[1, 0] = 0.2
    prob_matrix[2, 0] = 0.3
    prob_matrix[2, 1] = 0.2
    prob_matrix[0, 3] = 0.3
    
    pred, ev = calculate_best_ev(prob_matrix, max_score=5)
    assert pred == (2, 0)
    assert pytest.approx(ev) == 1.9

def test_calculate_best_ev_large_matrix():
    """
    Test that the engine dynamically adapts to input probability matrices
    larger than 6x6 (e.g. 10x10) to capture all probability mass,
    while restricting recommendations to 0-0 to 5-5.
    
    Probability distribution:
    - 5-4: prob = 0.1  (within 5-5 domain)
    - 8-7: prob = 0.9  (outside 5-5 domain, goal diff = 1)
    
    EV calculations:
    - Predict 5-4 (diff = 1):
      - actual 5-4 (exact score) -> 5 * 0.1 = 0.5
      - actual 8-7 (goal diff = 1) -> 3 * 0.9 = 2.7
      - Total EV = 3.2
      
    - Predict 1-0 (diff = 1):
      - actual 5-4 (tendency) -> 1 * 0.1 = 0.1
      - actual 8-7 (goal diff = 1) -> 3 * 0.9 = 2.7
      - Total EV = 2.8
      
    - Predict 5-0 (diff = 5):
      - actual 5-4 (tendency) -> 1 * 0.1 = 0.1
      - actual 8-7 (tendency) -> 1 * 0.9 = 0.9
      - Total EV = 1.0
      
    The optimal recommendation must be 5-4 because it captures the massive probability
    weight of 8-7 at goal diff = 1 and gains exact score points at 5-4, yielding EV = 3.2.
    """
    prob_matrix = np.zeros((10, 10))
    prob_matrix[5, 4] = 0.1
    prob_matrix[8, 7] = 0.9
    
    pred, ev = calculate_best_ev(prob_matrix, max_score=5)
    assert pred == (5, 4)
    assert pytest.approx(ev) == 3.2

def test_calculate_best_ev_invalid_inputs():
    """
    Test that the engine raises appropriate errors for invalid inputs.
    """
    # 1. Non-numpy array
    with pytest.raises(TypeError):
        calculate_best_ev([[1, 0], [0, 1]]) # type: ignore
        
    # 2. Non-2D array
    with pytest.raises(ValueError):
        calculate_best_ev(np.array([1, 2, 3]))
        
    # 3. Too small matrix
    with pytest.raises(ValueError):
        calculate_best_ev(np.zeros((5, 5)), max_score=5)
