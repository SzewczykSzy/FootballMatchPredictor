import os
import argparse
import sqlite3
import numpy as np
from datetime import date
from typing import Dict, List, Tuple, Optional
from scipy.optimize import minimize

from src.data.models import MatchRecord
from src.model.contracts import TeamParameters
from src.model.parameters import save_team_parameters, save_model_config
from src.data.database import get_db_connection, get_all_matches

DECAY_RATE = 0.0065  # Standard Dixon-Coles exponential decay rate

def calculate_days_since(match_date_str: Optional[str], reference_date_str: str) -> int:
    """
    Calculates the number of days between the match date and a reference date.
    If match date is missing, returns a high number (e.g., 10000) to downweight it to 0.
    """
    if not match_date_str:
        return 10000
    try:
        match_dt = date.fromisoformat(match_date_str)
        ref_dt = date.fromisoformat(reference_date_str)
        delta = ref_dt - match_dt
        return max(0, delta.days)
    except (ValueError, TypeError):
        return 10000

def fit_dixon_coles(
    matches: List[MatchRecord], 
    reference_date: Optional[str] = None
) -> Tuple[Dict[str, TeamParameters], float, float]:
    """
    Fits the Dixon-Coles model to historical match data to calculate attack/defense
    strengths for all unique teams, as well as home advantage (gamma) and low-score adjustment (rho).
    
    Returns:
        tuple: (dict of team_name -> TeamParameters, gamma, rho)
    """
    # Filter matches with actual scores
    valid_matches = [m for m in matches if m.home_goals is not None and m.away_goals is not None]
    
    if not valid_matches:
        raise ValueError("Cannot fit model: No matches with scores found in the dataset.")
        
    # Determine reference date if not provided
    if not reference_date:
        # Use the latest match date in the dataset
        dates = [m.match_date for m in valid_matches if m.match_date]
        if dates:
            reference_date = max(dates)
        else:
            reference_date = date.today().isoformat()
            
    # Collect all unique teams
    unique_teams = set()
    for m in valid_matches:
        unique_teams.add(m.home_team)
        unique_teams.add(m.away_team)
        
    teams_list = sorted(list(unique_teams))
    N = len(teams_list)
    team_to_idx = {team: idx for idx, team in enumerate(teams_list)}
    
    # Pre-process match data for speed in likelihood evaluation
    matches_data = []
    for m in valid_matches:
        home_idx = team_to_idx[m.home_team]
        away_idx = team_to_idx[m.away_team]
        x = m.home_goals
        y = m.away_goals
        days = calculate_days_since(m.match_date, reference_date)
        weight = np.exp(-DECAY_RATE * days)
        matches_data.append((home_idx, away_idx, x, y, weight))
        
    # Initial parameters:
    # N alphas, N betas, 1 gamma, 1 rho
    init_alphas = np.ones(N)
    init_betas = np.ones(N)
    init_gamma = 1.0
    init_rho = 0.0
    
    init_params = np.concatenate([init_alphas, init_betas, [init_gamma, init_rho]])
    
    # Bounds: alpha > 0, beta > 0, gamma > 0, rho in [-1.0, 1.0]
    bounds = []
    for _ in range(N):
        bounds.append((1e-4, 10.0))  # alpha bounds
    for _ in range(N):
        bounds.append((1e-4, 10.0))  # beta bounds
    bounds.append((1e-4, 5.0))       # gamma bounds
    bounds.append((-1.0, 1.0))       # rho bounds
    
    # Identifiability constraint: average alpha = 1.0
    def constraint_mean_alpha(params):
        return np.mean(params[0:N]) - 1.0
        
    constraints = [{'type': 'eq', 'fun': constraint_mean_alpha}]
    
    # Negative Log-Likelihood objective function
    def neg_log_likelihood(params):
        alphas = params[0:N]
        betas = params[N:2*N]
        gamma = params[2*N]
        rho = params[2*N+1]
        
        nll = 0.0
        for home_idx, away_idx, x, y, w in matches_data:
            lambda_h = alphas[home_idx] * betas[away_idx] * gamma
            mu_a = alphas[away_idx] * betas[home_idx]
            
            # Avoid numerical issues with extremely small expected goals
            if lambda_h <= 1e-12 or mu_a <= 1e-12:
                nll += w * 1e4
                continue
                
            # Tau adjustment for low scores
            tau_val = 1.0
            if x == 0 and y == 0:
                tau_val = 1.0 - lambda_h * mu_a * rho
            elif x == 0 and y == 1:
                tau_val = 1.0 + lambda_h * rho
            elif x == 1 and y == 0:
                tau_val = 1.0 + mu_a * rho
            elif x == 1 and y == 1:
                tau_val = 1.0 - rho
                
            # Avoid invalid log(<=0)
            if tau_val <= 1e-12:
                nll += w * 1e4
                continue
                
            log_prob = np.log(tau_val) + x * np.log(lambda_h) - lambda_h + y * np.log(mu_a) - mu_a
            nll -= w * log_prob
            
        return nll
        
    # Attempt 1: Standard SLSQP
    res = minimize(
        neg_log_likelihood, 
        init_params, 
        method='SLSQP', 
        bounds=bounds, 
        constraints=constraints,
        options={'ftol': 1e-6, 'maxiter': 200}
    )
    
    # Attempt 2 (Fallback Retry): SLSQP with relaxed tolerances
    if not res.success:
        print(f"Warning: Standard optimization did not converge ({res.message}). Retrying with relaxed tolerances...")
        res = minimize(
            neg_log_likelihood, 
            init_params, 
            method='SLSQP', 
            bounds=bounds, 
            constraints=constraints,
            options={'ftol': 1e-4, 'maxiter': 500}
        )
        
    # Attempt 3 (Fallback Retry 2): L-BFGS-B (no constraint) and post-normalize
    if not res.success:
        print("Warning: SLSQP failed to converge. Attempting L-BFGS-B solver...")
        res = minimize(
            neg_log_likelihood,
            init_params,
            method='L-BFGS-B',
            bounds=bounds,
            options={'ftol': 1e-5, 'maxiter': 300}
        )
        
    final_params = res.x
    alphas = final_params[0:N]
    betas = final_params[N:2*N]
    gamma = final_params[2*N]
    rho = final_params[2*N+1]
    
    # Enforce identifiability constraint: mean(alpha) = 1.0
    mean_alpha = np.mean(alphas)
    if not np.isclose(mean_alpha, 1.0, atol=1e-5):
        alphas = alphas / mean_alpha
        betas = betas * mean_alpha
        
    # Build result dictionaries
    team_parameters = {}
    for idx, team_name in enumerate(teams_list):
        team_parameters[team_name] = TeamParameters(
            team_id=team_name,
            alpha=float(alphas[idx]),
            beta=float(betas[idx])
        )
        
    return team_parameters, float(gamma), float(rho)

def run_fitting(db_path: str = "matches.db") -> None:
    """
    Main function to load matches from database, fit the parameters,
    and save them back to the database.
    """
    if not os.path.exists(db_path):
        print(f"Error: Database file not found at '{db_path}'")
        return
        
    print(f"Loading matches from database: {db_path}...")
    with get_db_connection(db_path) as conn:
        matches = get_all_matches(conn)
        
    print(f"Total matches retrieved: {len(matches)}")
    valid_matches = [m for m in matches if m.home_goals is not None and m.away_goals is not None]
    print(f"Matches with valid scores for fitting: {len(valid_matches)}")
    
    if len(valid_matches) < 2:
        print("Error: Need at least 2 scored matches to fit the Dixon-Coles model.")
        return
        
    print("Fitting Dixon-Coles model parameters via local MLE...")
    team_params, gamma, rho = fit_dixon_coles(valid_matches)
    
    print(f"Fitting completed. home_advantage (gamma) = {gamma:.4f}, correlation (rho) = {rho:.4f}")
    
    print("Saving parameters and model config to database...")
    with get_db_connection(db_path) as conn:
        save_team_parameters(conn, list(team_params.values()))
        save_model_config(conn, gamma, rho)
        
    print("Success! Saved parameters for all teams:")
    sorted_teams = sorted(team_params.keys())
    for t in sorted_teams:
        p = team_params[t]
        print(f"  - {p.team_id}: alpha = {p.alpha:.4f}, beta = {p.beta:.4f}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Dixon-Coles Parameter Fitting Engine")
    parser.add_argument("--fit", action="store_true", help="Run Maximum Likelihood Estimation parameter fitting")
    parser.add_argument("--db", type=str, default="matches.db", help="Path to SQLite database")
    
    args = parser.parse_args()
    if args.fit:
        run_fitting(args.db)
    else:
        parser.print_help()
