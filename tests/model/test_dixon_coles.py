import pytest
import numpy as np
from src.data.models import MatchRecord
from src.model.dixon_coles import fit_dixon_coles, calculate_days_since

def test_calculate_days_since():
    # Test date difference calculations
    assert calculate_days_since("2026-06-11", "2026-06-11") == 0
    assert calculate_days_since("2026-06-01", "2026-06-11") == 10
    assert calculate_days_since("2025-06-11", "2026-06-11") == 365

def test_fit_dixon_coles_basic():
    # Create a mock dataset with 3 teams
    # Team A is strong, Team B is average, Team C is weak
    matches = [
        # Recent matches (day diff = 0)
        MatchRecord("TeamA", "TeamB", 0.0, 0.0, 0.0, match_date="2026-06-11", home_goals=3, away_goals=0),
        MatchRecord("TeamB", "TeamC", 0.0, 0.0, 0.0, match_date="2026-06-11", home_goals=2, away_goals=0),
        MatchRecord("TeamA", "TeamC", 0.0, 0.0, 0.0, match_date="2026-06-11", home_goals=4, away_goals=0),
        
        # Older matches (decayed weight)
        MatchRecord("TeamC", "TeamA", 0.0, 0.0, 0.0, match_date="2025-06-11", home_goals=0, away_goals=1),
        MatchRecord("TeamB", "TeamA", 0.0, 0.0, 0.0, match_date="2025-06-11", home_goals=0, away_goals=2),
    ]
    
    # Fit Dixon-Coles
    team_params, gamma, rho = fit_dixon_coles(matches, reference_date="2026-06-11")
    
    # Check that we have parameters for all 3 teams
    assert len(team_params) == 3
    assert "TeamA" in team_params
    assert "TeamB" in team_params
    assert "TeamC" in team_params
    
    # Identifiability constraint: average alpha = 1.0
    alphas = [p.alpha for p in team_params.values()]
    assert pytest.approx(np.mean(alphas)) == 1.0
    
    # Team A is strongest -> highest alpha, lowest beta
    assert team_params["TeamA"].alpha > team_params["TeamB"].alpha
    assert team_params["TeamB"].alpha > team_params["TeamC"].alpha
    
    assert team_params["TeamA"].beta < team_params["TeamB"].beta
    assert team_params["TeamB"].beta < team_params["TeamC"].beta
    
    # Basic bounds checking
    for p in team_params.values():
        assert p.alpha > 0
        assert p.beta > 0
        
    assert gamma > 0
    assert -1.0 <= rho <= 1.0

def test_fit_dixon_coles_retry_logic():
    # If optimization fails, the retry logic should be invoked and succeed
    # We can create a degenerate dataset (e.g. only 1 match or mismatched teams) 
    # to trigger numerical challenges or see if the solver handles it
    matches = [
        MatchRecord("TeamA", "TeamB", 0.0, 0.0, 0.0, match_date="2026-06-11", home_goals=1, away_goals=1),
    ]
    
    # Should fit successfully even on minimal/degenerate data due to robust fallbacks
    team_params, gamma, rho = fit_dixon_coles(matches, reference_date="2026-06-11")
    assert len(team_params) == 2
    assert pytest.approx(np.mean([p.alpha for p in team_params.values()])) == 1.0
