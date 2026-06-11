import pytest
import numpy as np
import os
from src.model.simulation import (
    load_simulation_parameters,
    sample_dixon_coles_vectorized,
    simulate_group_stage,
    simulate_tournament
)
from src.model.bracket import TEAMS

def test_load_simulation_parameters():
    # Test loading parameters. Since matches.db might be empty or filled, we check defaults/types.
    alphas, betas, gamma, rho = load_simulation_parameters("non_existent_db.db")
    
    assert len(alphas) == len(TEAMS)
    assert len(betas) == len(TEAMS)
    assert np.all(alphas == 1.0)
    assert np.all(betas == 1.0)
    assert gamma == 1.0
    assert rho == 0.0

def test_sample_dixon_coles_vectorized():
    # Test vectorized sampler
    runs = 100
    matches = 10
    lambda_h = np.ones((runs, matches)) * 1.5
    mu_a = np.ones((runs, matches)) * 1.0
    rho = 0.05
    
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    assert h_goals.shape == (runs, matches)
    assert a_goals.shape == (runs, matches)
    assert np.all(h_goals >= 0) and np.all(h_goals <= 5)
    assert np.all(a_goals >= 0) and np.all(a_goals <= 5)

def test_simulate_group_stage():
    # Test group stage simulation
    runs = 10
    alphas = np.ones(len(TEAMS))
    betas = np.ones(len(TEAMS))
    rho = 0.0
    
    winners, runners_up, third_slots, group_goals = simulate_group_stage(alphas, betas, rho, runs)
    
    assert winners.shape == (runs, 12)
    assert runners_up.shape == (runs, 12)
    assert third_slots.shape == (runs, 8)
    assert group_goals.shape == (runs, 72, 2)
    
    # Check that in every run, the 32 advancing teams are unique
    for r in range(runs):
        w_set = set(winners[r])
        ru_set = set(runners_up[r])
        t3_set = set(third_slots[r])
        
        # Top 2 teams from each group cannot overlap
        assert len(w_set) == 12
        assert len(ru_set) == 12
        assert len(w_set.intersection(ru_set)) == 0
        
        # 3rd place teams cannot overlap with top 2
        assert len(t3_set) == 8
        assert len(t3_set.intersection(w_set)) == 0
        assert len(t3_set.intersection(ru_set)) == 0
        
        # In total, 32 distinct advancing teams
        all_advancers = w_set.union(ru_set).union(t3_set)
        assert len(all_advancers) == 32

def test_simulate_tournament():
    # Run the full tournament simulation on a mock database (or non-existent, falling back to defaults)
    runs = 100
    df = simulate_tournament(runs=runs, db_path="non_existent_db.db")
    
    # Verify shape
    assert df.shape == (48, 9)
    
    # Verify columns
    expected_cols = [
        "team", "p_group_winner", "p_advance", "p_r16", "p_qf", "p_sf", "p_final", "p_champion", "avg_gci"
    ]
    assert list(df.columns) == expected_cols
    
    # Verify probability bounds and championship sum
    assert pytest.approx(df["p_champion"].sum()) == 1.0
    for col in expected_cols[1:8]:
        assert np.all(df[col] >= 0.0)
        assert np.all(df[col] <= 1.0)
        
    # Verify progression monotonicity: e.g. p_advance >= p_r16 >= ... >= p_champion
    for idx, row in df.iterrows():
        assert row["p_advance"] >= row["p_r16"]
        assert row["p_r16"] >= row["p_qf"]
        assert row["p_qf"] >= row["p_sf"]
        assert row["p_sf"] >= row["p_final"]
        assert row["p_final"] >= row["p_champion"]

    # Verify GCI properties (HHI is between 0 and 1, except if they scored 0 goals, which GCI defaults to 0.0)
    assert np.all(df["avg_gci"] >= 0.0)
    assert np.all(df["avg_gci"] <= 1.0)

