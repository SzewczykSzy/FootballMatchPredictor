import pytest
import numpy as np
from src.model.matrix import generate_score_matrix

def test_generate_score_matrix_no_prior():
    # Test matrix generation without prior
    home_alpha, home_beta = 1.2, 0.8
    away_alpha, away_beta = 1.0, 1.1
    gamma, rho = 1.1, 0.05
    
    matrix = generate_score_matrix(
        home_alpha=home_alpha,
        home_beta=home_beta,
        away_alpha=away_alpha,
        away_beta=away_beta,
        gamma=gamma,
        rho=rho
    )
    
    # Verify shape
    assert matrix.shape == (6, 6)
    
    # Verify sum to 1.0
    assert pytest.approx(np.sum(matrix)) == 1.0
    
    # Verify all probabilities are non-negative
    assert np.all(matrix >= 0.0)

def test_generate_score_matrix_with_prior():
    # Test matrix generation incorporating consensus prior
    home_alpha, home_beta = 1.2, 0.8
    away_alpha, away_beta = 1.0, 1.1
    gamma, rho = 1.1, 0.05
    
    # Prior: 50% Home win, 30% Draw, 20% Away win
    prior = (0.50, 0.30, 0.20)
    
    matrix = generate_score_matrix(
        home_alpha=home_alpha,
        home_beta=home_beta,
        away_alpha=away_alpha,
        away_beta=away_beta,
        gamma=gamma,
        rho=rho,
        consensus_prior=prior
    )
    
    # Verify shape and sum
    assert matrix.shape == (6, 6)
    assert pytest.approx(np.sum(matrix)) == 1.0
    
    # Verify outcome probabilities match prior
    p_home = 0.0
    p_draw = 0.0
    p_away = 0.0
    
    for x in range(6):
        for y in range(6):
            if x > y:
                p_home += matrix[x, y]
            elif x == y:
                p_draw += matrix[x, y]
            else:
                p_away += matrix[x, y]
                
    assert pytest.approx(p_home) == 0.50
    assert pytest.approx(p_draw) == 0.30
    assert pytest.approx(p_away) == 0.20
