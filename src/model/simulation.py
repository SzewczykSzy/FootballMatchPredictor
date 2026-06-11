"""
Vectorized tournament simulation engine for the 2026 World Cup.
This module handles loading parameters, simulating group and knockout stages stochastically,
and calculating aggregated probabilities and goal concentration indices.
"""

import os
import sqlite3
import numpy as np
import pandas as pd
from typing import Dict, Tuple, List, Optional

from src.model.bracket import TEAMS, GROUPS, GROUP_MATCHES, ROUND_OF_32_MATCHUPS
from src.model.parameters import get_all_team_parameters, get_model_config

DEFAULT_DB_PATH = "matches.db"

def load_simulation_parameters(db_path: str = DEFAULT_DB_PATH) -> Tuple[np.ndarray, np.ndarray, float, float]:
    """
    Loads alpha and beta parameters for all 48 teams, along with global gamma and rho.
    Returns:
        alphas: np.ndarray of shape (48,) containing attack parameters for each team.
        betas: np.ndarray of shape (48,) containing defense parameters for each team.
        gamma: float, home advantage parameter (will be set to 1.0 during match sampling since neutral ground).
        rho: float, Dixon-Coles low-score correlation parameter.
    """
    alphas = np.ones(len(TEAMS), dtype=np.float64)
    betas = np.ones(len(TEAMS), dtype=np.float64)
    gamma = 1.0
    rho = 0.0
    
    if os.path.exists(db_path):
        try:
            # Use connection context
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            
            # Load team parameters
            team_params = get_all_team_parameters(conn)
            for idx, team_name in enumerate(TEAMS):
                if team_name in team_params:
                    alphas[idx] = team_params[team_name].alpha
                    betas[idx] = team_params[team_name].beta
                else:
                    # Case-insensitive check fallback
                    matched = False
                    for db_name, param in team_params.items():
                        if db_name.lower().strip() == team_name.lower().strip():
                            alphas[idx] = param.alpha
                            betas[idx] = param.beta
                            matched = True
                            break
            
            # Load model config
            config = get_model_config(conn)
            if config:
                gamma = config.get("gamma", 1.0)
                rho = config.get("rho", 0.0)
                
            conn.close()
        except Exception as e:
            print(f"Warning: Failed to load parameters from database: {e}. Using defaults.")
    else:
        print(f"Warning: Database '{db_path}' not found. Using default team parameters.")
        
    return alphas, betas, gamma, rho

# Mapping from team name to global index (0 to 47)
TEAM_TO_IDX = {name: idx for idx, name in enumerate(TEAMS)}

# Pre-compute match indices for group stage (72 matches)
GROUP_MATCH_INDICES = np.array([
    (TEAM_TO_IDX[h], TEAM_TO_IDX[a]) for h, a in GROUP_MATCHES
], dtype=np.int32)

# Pre-compute team-to-match mapping matrices of shape (48, 72)
H_MASK = np.zeros((len(TEAMS), len(GROUP_MATCHES)), dtype=np.float64)
A_MASK = np.zeros((len(TEAMS), len(GROUP_MATCHES)), dtype=np.float64)
for m_idx, (h, a) in enumerate(GROUP_MATCHES):
    H_MASK[TEAM_TO_IDX[h], m_idx] = 1.0
    A_MASK[TEAM_TO_IDX[a], m_idx] = 1.0

def sample_dixon_coles_vectorized(lambda_h: np.ndarray, mu_a: np.ndarray, rho: float) -> Tuple[np.ndarray, np.ndarray]:
    """
    Vectorized Dixon-Coles match score sampler.
    Args:
        lambda_h: np.ndarray of shape (N, M) containing home expected goals
        mu_a: np.ndarray of shape (N, M) containing away expected goals
        rho: float, low-score correlation adjustment factor
    Returns:
        home_goals, away_goals: np.ndarray of shape (N, M) with sampled goals
    """
    N, M = lambda_h.shape
    total_matches = N * M
    
    # 6x6 score grid (capped at 5 goals per team)
    x_grid, y_grid = np.meshgrid(np.arange(6), np.arange(6), indexing='ij')
    
    # Pre-compute factorials for Poisson PDF
    facts = np.array([1, 1, 2, 6, 24, 120], dtype=np.float64)
    
    # Flatten expected goals to 1D array of shape (N*M, 1, 1) for broadcasting
    lh_flat = np.maximum(lambda_h.reshape(-1, 1, 1), 1e-12)
    mu_flat = np.maximum(mu_a.reshape(-1, 1, 1), 1e-12)
    
    # Calculate Poisson probabilities for home (x) and away (y) goals
    p_x = (lh_flat ** x_grid[None, :, :]) * np.exp(-lh_flat) / facts[x_grid[None, :, :]]
    p_y = (mu_flat ** y_grid[None, :, :]) * np.exp(-mu_flat) / facts[y_grid[None, :, :]]
    
    # Apply Dixon-Coles tau adjustment for low scores (x <= 1, y <= 1)
    tau = np.ones((total_matches, 6, 6), dtype=np.float64)
    tau[:, 0, 0] = 1.0 - lh_flat.reshape(-1) * mu_flat.reshape(-1) * rho
    tau[:, 0, 1] = 1.0 + lh_flat.reshape(-1) * rho
    tau[:, 1, 0] = 1.0 + mu_flat.reshape(-1) * rho
    tau[:, 1, 1] = 1.0 - rho
    
    # Ensure adjustment factor is non-negative
    tau = np.maximum(tau, 0.0)
    
    # Joint probabilities matrix of shape (N*M, 6, 6)
    probs = tau * p_x * p_y
    
    # Normalize probabilities for each match
    probs_sum = probs.sum(axis=(1, 2), keepdims=True)
    probs = np.where(probs_sum > 0, probs / probs_sum, 0.0)
    
    # Flatten to (N*M, 36) for sampling
    probs_flat = probs.reshape(-1, 36)
    cdf = np.cumsum(probs_flat, axis=1)
    
    # Generate uniform random variables
    U = np.random.rand(total_matches)
    
    # Sample outcomes vectorially
    idx = (U[:, None] > cdf).sum(axis=1)
    idx = np.clip(idx, 0, 35)
    
    home_goals = idx // 6
    away_goals = idx % 6
    
    return home_goals.reshape(N, M), away_goals.reshape(N, M)

def simulate_group_stage(
    alphas: np.ndarray,
    betas: np.ndarray,
    rho: float,
    runs: int = 10000
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """
    Simulates the group stage stochastically for the given number of runs.
    Returns:
        winners: np.ndarray of shape (runs, 12) containing winner team indices
        runners_up: np.ndarray of shape (runs, 12) containing runner-up team indices
        third_slots_teams: np.ndarray of shape (runs, 8) containing 3rd-place advancer team indices
        group_goals: np.ndarray of shape (runs, 72, 2) containing home and away goals scored in group stage
    """
    # 1. Prepare expected goals for all 72 matches
    home_idx = GROUP_MATCH_INDICES[:, 0]
    away_idx = GROUP_MATCH_INDICES[:, 1]
    
    # Neutral ground: home advantage gamma is 1.0
    lambda_h = alphas[home_idx][None, :] * betas[away_idx][None, :]
    mu_a = alphas[away_idx][None, :] * betas[home_idx][None, :]
    
    # Broadcast to (runs, 72)
    lambda_h = lambda_h * np.ones((runs, 1))
    mu_a = mu_a * np.ones((runs, 1))
    
    # 2. Sample goals scored
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    # Keep track of goals
    group_goals = np.stack([h_goals, a_goals], axis=-1)  # shape (runs, 72, 2)
    
    # 3. Calculate match points
    # 3 points for win, 1 for draw, 0 for loss
    h_pts = np.where(h_goals > a_goals, 3, np.where(h_goals == a_goals, 1, 0))
    a_pts = np.where(a_goals > h_goals, 3, np.where(h_goals == a_goals, 1, 0))
    
    # 4. Accumulate points, goal difference, goals scored for each team
    # Matrix multiplication achieves this vectorially: shape (runs, 48)
    points = h_pts @ H_MASK.T + a_pts @ A_MASK.T
    gf = h_goals @ H_MASK.T + a_goals @ A_MASK.T
    ga = a_goals @ H_MASK.T + h_goals @ A_MASK.T
    gd = gf - ga
    
    # 5. Reshape to group level: shape (runs, 12, 4)
    points_group = points.reshape(runs, 12, 4)
    gd_group = gd.reshape(runs, 12, 4)
    gf_group = gf.reshape(runs, 12, 4)
    
    # Stochastic tiebreaker
    rand_tiebreaker = np.random.rand(runs, 12, 4)
    
    # Sort groups: np.lexsort sorts in ascending order.
    # We sort by: points (desc), GD (desc), GF (desc), random (desc).
    # So we use negative values.
    idx = np.lexsort((-rand_tiebreaker, -gf_group, -gd_group, -points_group), axis=-1)
    
    # 6. Retrieve global team IDs of sorted group teams
    # base_indices[g, t] = 4*g + t
    sorted_global_teams = 4 * np.arange(12)[None, :, None] + idx
    
    # Winners (rank 0) and Runners-up (rank 1)
    winners = sorted_global_teams[:, :, 0]
    runners_up = sorted_global_teams[:, :, 1]
    
    # 7. Identify the 8 best 3rd-placed teams
    third_placed_teams = sorted_global_teams[:, :, 2]  # shape (runs, 12)
    
    # Extract statistics for the 3rd-placed teams
    run_indices = np.arange(runs)[:, None]
    third_pts = points[run_indices, third_placed_teams]
    third_gd = gd[run_indices, third_placed_teams]
    third_gf = gf[run_indices, third_placed_teams]
    third_rand = np.random.rand(runs, 12)
    
    # Sort the 12 third-placed teams stochastically
    third_idx = np.lexsort((-third_rand, -third_gf, -third_gd, -third_pts), axis=-1)
    
    # Select top 8 advancing group indices, sorted by group index to match knockout slots
    advancing_group_indices_sorted = np.sort(third_idx[:, :8], axis=-1)
    
    # Map back to global team IDs
    third_slots_teams = third_placed_teams[run_indices, advancing_group_indices_sorted]
    
    return winners, runners_up, third_slots_teams, group_goals

def setup_round_of_32(
    winners: np.ndarray,
    runners_up: np.ndarray,
    third_slots: np.ndarray
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Sets up the Round of 32 matchups for all runs.
    """
    runs = winners.shape[0]
    home_teams = np.zeros((runs, 16), dtype=np.int32)
    away_teams = np.zeros((runs, 16), dtype=np.int32)
    
    for m, (h_src, a_src) in enumerate(ROUND_OF_32_MATCHUPS):
        h_type, h_val = h_src
        if h_type == 'winner':
            home_teams[:, m] = winners[:, h_val]
        elif h_type == 'runner_up':
            home_teams[:, m] = runners_up[:, h_val]
        elif h_type == 'third_place':
            home_teams[:, m] = third_slots[:, h_val]
            
        a_type, a_val = a_src
        if a_type == 'winner':
            away_teams[:, m] = winners[:, a_val]
        elif a_type == 'runner_up':
            away_teams[:, m] = runners_up[:, a_val]
        elif a_type == 'third_place':
            away_teams[:, m] = third_slots[:, a_val]
            
    return home_teams, away_teams

def simulate_knockout_stage(
    winners: np.ndarray,
    runners_up: np.ndarray,
    third_slots: np.ndarray,
    alphas: np.ndarray,
    betas: np.ndarray,
    rho: float,
    runs: int = 10000
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, List]:
    """
    Simulates the knockout stage stochastically for all runs.
    """
    reached_r32 = np.zeros((runs, 48), dtype=bool)
    run_idx_arr = np.arange(runs)[:, None]
    reached_r32[run_idx_arr, winners] = True
    reached_r32[run_idx_arr, runners_up] = True
    reached_r32[run_idx_arr, third_slots] = True
    
    knockout_match_records = []
    
    # 1. Round of 32
    home_teams, away_teams = setup_round_of_32(winners, runners_up, third_slots)
    lambda_h = alphas[home_teams] * betas[away_teams]
    mu_a = alphas[away_teams] * betas[home_teams]
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    # Tie-breakers: 50/50 coin flip for draws
    coin_flips = np.random.randint(0, 2, size=(runs, 16))
    r32_winners = np.where(h_goals > a_goals, home_teams,
                           np.where(h_goals < a_goals, away_teams,
                                    np.where(coin_flips == 0, home_teams, away_teams)))
    
    knockout_match_records.append((home_teams, away_teams, h_goals, a_goals))
    
    reached_r16 = np.zeros((runs, 48), dtype=bool)
    reached_r16[run_idx_arr, r32_winners] = True
    
    # 2. Round of 16
    home_teams = r32_winners[:, 0::2]
    away_teams = r32_winners[:, 1::2]
    lambda_h = alphas[home_teams] * betas[away_teams]
    mu_a = alphas[away_teams] * betas[home_teams]
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    coin_flips = np.random.randint(0, 2, size=(runs, 8))
    r16_winners = np.where(h_goals > a_goals, home_teams,
                           np.where(h_goals < a_goals, away_teams,
                                    np.where(coin_flips == 0, home_teams, away_teams)))
    
    knockout_match_records.append((home_teams, away_teams, h_goals, a_goals))
    
    reached_qf = np.zeros((runs, 48), dtype=bool)
    reached_qf[np.arange(runs)[:, None], r16_winners] = True
    
    # 3. Quarter-finals
    home_teams = r16_winners[:, 0::2]
    away_teams = r16_winners[:, 1::2]
    lambda_h = alphas[home_teams] * betas[away_teams]
    mu_a = alphas[away_teams] * betas[home_teams]
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    coin_flips = np.random.randint(0, 2, size=(runs, 4))
    qf_winners = np.where(h_goals > a_goals, home_teams,
                           np.where(h_goals < a_goals, away_teams,
                                    np.where(coin_flips == 0, home_teams, away_teams)))
    
    knockout_match_records.append((home_teams, away_teams, h_goals, a_goals))
    
    reached_sf = np.zeros((runs, 48), dtype=bool)
    reached_sf[np.arange(runs)[:, None], qf_winners] = True
    
    # 4. Semi-finals
    home_teams = qf_winners[:, 0::2]
    away_teams = qf_winners[:, 1::2]
    lambda_h = alphas[home_teams] * betas[away_teams]
    mu_a = alphas[away_teams] * betas[home_teams]
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    coin_flips = np.random.randint(0, 2, size=(runs, 2))
    sf_winners = np.where(h_goals > a_goals, home_teams,
                           np.where(h_goals < a_goals, away_teams,
                                    np.where(coin_flips == 0, home_teams, away_teams)))
    
    knockout_match_records.append((home_teams, away_teams, h_goals, a_goals))
    
    reached_final = np.zeros((runs, 48), dtype=bool)
    reached_final[np.arange(runs)[:, None], sf_winners] = True
    
    # 5. Final
    home_teams = sf_winners[:, 0:1]
    away_teams = sf_winners[:, 1:2]
    lambda_h = alphas[home_teams] * betas[away_teams]
    mu_a = alphas[away_teams] * betas[home_teams]
    h_goals, a_goals = sample_dixon_coles_vectorized(lambda_h, mu_a, rho)
    
    coin_flips = np.random.randint(0, 2, size=(runs, 1))
    final_winner = np.where(h_goals > a_goals, home_teams,
                            np.where(h_goals < a_goals, away_teams,
                                     np.where(coin_flips == 0, home_teams, away_teams)))
    
    final_winner = final_winner.squeeze(axis=-1)
    
    knockout_match_records.append((home_teams, away_teams, h_goals, a_goals))
    
    champion = np.zeros((runs, 48), dtype=bool)
    champion[np.arange(runs), final_winner] = True
    
    return reached_r32, reached_r16, reached_qf, reached_sf, reached_final, champion, knockout_match_records

def calculate_gci(
    group_goals: np.ndarray,
    knockout_match_records: List,
    runs: int = 10000
) -> np.ndarray:
    """
    Calculates the Goal Concentration Index (GCI) using HHI for all teams stochastically.
    GCI = sum(goals_in_match^2) / (total_goals^2) for each team in each run.
    """
    h_goals = group_goals[:, :, 0]
    a_goals = group_goals[:, :, 1]
    
    # 1. Group stage goals contribution: shape (runs, 48)
    sum_goals = h_goals @ H_MASK.T + a_goals @ A_MASK.T
    sum_squared_goals = (h_goals ** 2) @ H_MASK.T + (a_goals ** 2) @ A_MASK.T
    
    # 2. Knockout stage goals contribution
    team_indices = np.arange(48)[np.newaxis, :, np.newaxis]
    
    for home_teams, away_teams, h_g, a_g in knockout_match_records:
        # home_teams, away_teams: (runs, M)
        # h_g, a_g: (runs, M)
        h_mask = (home_teams[:, np.newaxis, :] == team_indices)
        a_mask = (away_teams[:, np.newaxis, :] == team_indices)
        
        sum_goals += np.sum(h_g[:, np.newaxis, :] * h_mask, axis=2)
        sum_goals += np.sum(a_g[:, np.newaxis, :] * a_mask, axis=2)
        
        sum_squared_goals += np.sum((h_g[:, np.newaxis, :] ** 2) * h_mask, axis=2)
        sum_squared_goals += np.sum((a_g[:, np.newaxis, :] ** 2) * a_mask, axis=2)
        
    # GCI using HHI formula (using np.divide to prevent division-by-zero warnings)
    gci = np.divide(sum_squared_goals, sum_goals ** 2, out=np.zeros_like(sum_squared_goals), where=sum_goals > 0)
    return gci

def simulate_tournament(
    runs: int = 10000,
    db_path: str = DEFAULT_DB_PATH
) -> pd.DataFrame:
    """
    Simulates the full tournament multiple times and computes aggregated team statistics.
    """
    # 1. Load team parameters
    alphas, betas, gamma, rho = load_simulation_parameters(db_path)
    
    # 2. Simulate Group Stage
    winners, runners_up, third_slots, group_goals = simulate_group_stage(alphas, betas, rho, runs)
    
    # 3. Simulate Knockout Stage
    reached_r32, reached_r16, reached_qf, reached_sf, reached_final, champion, knockout_match_records = simulate_knockout_stage(
        winners, runners_up, third_slots, alphas, betas, rho, runs
    )
    
    # 4. Calculate GCI
    gci = calculate_gci(group_goals, knockout_match_records, runs)
    
    # 5. Compute aggregated probabilities
    p_group_winner = np.mean(np.any(winners[:, :, np.newaxis] == np.arange(48)[np.newaxis, np.newaxis, :], axis=1), axis=0)
    p_advance = np.mean(reached_r32, axis=0)
    p_r16 = np.mean(reached_r16, axis=0)
    p_qf = np.mean(reached_qf, axis=0)
    p_sf = np.mean(reached_sf, axis=0)
    p_final = np.mean(reached_final, axis=0)
    p_champion = np.mean(champion, axis=0)
    avg_gci = np.mean(gci, axis=0)
    
    # Build result DataFrame
    df = pd.DataFrame({
        "team": TEAMS,
        "p_group_winner": p_group_winner,
        "p_advance": p_advance,
        "p_r16": p_r16,
        "p_qf": p_qf,
        "p_sf": p_sf,
        "p_final": p_final,
        "p_champion": p_champion,
        "avg_gci": avg_gci
    })
    
    # Sort results
    df = df.sort_values(
        by=["p_champion", "p_final", "p_sf", "p_qf", "p_r16", "p_advance", "p_group_winner", "team"],
        ascending=[False, False, False, False, False, False, False, True]
    )
    df = df.reset_index(drop=True)
    
    return df


