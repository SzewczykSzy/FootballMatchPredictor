import os
import math
import argparse
import numpy as np
from typing import Tuple, Optional

from src.model.contracts import ScoreMatrix, TeamParameters
from src.model.parameters import get_team_parameters, get_model_config
from src.data.database import get_db_connection

def poisson_pdf(k: int, mu: float) -> float:
    """
    Calculates the Poisson probability mass function for k events with rate mu.
    """
    return (mu ** k) * math.exp(-mu) / math.factorial(k)

def tau_adjustment(x: int, y: int, lambda_h: float, mu_a: float, rho: float) -> float:
    """
    Dixon-Coles correlation adjustment factor for low scores.
    """
    if x == 0 and y == 0:
        return 1.0 - lambda_h * mu_a * rho
    elif x == 0 and y == 1:
        return 1.0 + lambda_h * rho
    elif x == 1 and y == 0:
        return 1.0 + mu_a * rho
    elif x == 1 and y == 1:
        return 1.0 - rho
    return 1.0

def generate_score_matrix(
    home_alpha: float,
    home_beta: float,
    away_alpha: float,
    away_beta: float,
    gamma: float,
    rho: float,
    consensus_prior: Optional[Tuple[float, float, float]] = None
) -> np.ndarray:
    """
    Calculates the 6x6 score probability matrix based on Dixon-Coles expected goals
    and applies consensus prior correction if provided. Normalizes output to sum to 1.0.
    """
    lambda_h = home_alpha * away_beta * gamma
    mu_a = away_alpha * home_beta
    
    # Bound expected goals to prevent division by zero or negative probabilities
    lambda_h = max(lambda_h, 1e-12)
    mu_a = max(mu_a, 1e-12)
    
    matrix = np.zeros((6, 6))
    for x in range(6):
        for y in range(6):
            p_x = poisson_pdf(x, lambda_h)
            p_y = poisson_pdf(y, mu_a)
            tau = tau_adjustment(x, y, lambda_h, mu_a, rho)
            # Ensure adjustment factor does not force probability negative
            tau = max(tau, 0.0)
            matrix[x, y] = tau * p_x * p_y
            
    # Normalize initial Dixon-Coles matrix
    matrix_sum = np.sum(matrix)
    if matrix_sum > 0:
        matrix = matrix / matrix_sum
        
    # Apply bookmaker consensus prior via outcome-conditional scaling
    if consensus_prior is not None:
        p_prior_home, p_prior_draw, p_prior_away = consensus_prior
        
        # Calculate raw outcome sums from matrix
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
                    
        # Apply scaling factors
        adjusted_matrix = np.zeros((6, 6))
        for x in range(6):
            for y in range(6):
                if x > y:
                    factor = (p_prior_home / p_home) if p_home > 0 else 0.0
                elif x == y:
                    factor = (p_prior_draw / p_draw) if p_draw > 0 else 0.0
                else:
                    factor = (p_prior_away / p_away) if p_away > 0 else 0.0
                adjusted_matrix[x, y] = matrix[x, y] * factor
                
        matrix = adjusted_matrix
        
    # Final normalization to ensure sum is exactly 1.0
    final_sum = np.sum(matrix)
    if final_sum > 0:
        matrix = matrix / final_sum
        
    return matrix

def predict_matchup(home: str, away: str, db_path: str = "matches.db") -> ScoreMatrix:
    """
    Predicts the 6x6 score matrix for a specific home vs away matchup,
    loading parameters and consensus prior from the database.
    """
    home_alpha, home_beta = 1.0, 1.0
    away_alpha, away_beta = 1.0, 1.0
    gamma, rho = 1.0, 0.0
    consensus_prior = None
    
    db_exists = os.path.exists(db_path)
    
    if db_exists:
        with get_db_connection(db_path) as conn:
            # 1. Fetch team parameters
            h_params = get_team_parameters(conn, home)
            if h_params:
                home_alpha, home_beta = h_params.alpha, h_params.beta
            else:
                print(f"Warning: Parameters for home team '{home}' not found in database. Using defaults.")
                
            a_params = get_team_parameters(conn, away)
            if a_params:
                away_alpha, away_beta = a_params.alpha, a_params.beta
            else:
                print(f"Warning: Parameters for away team '{away}' not found in database. Using defaults.")
                
            # 2. Fetch global model config
            config = get_model_config(conn)
            if config:
                gamma, rho = config["gamma"], config["rho"]
            else:
                print("Warning: Model config not found in database. Using defaults.")
                
            # 3. Fetch consensus prior if an upcoming match exists
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT consensus_p_home, consensus_p_draw, consensus_p_away 
                FROM matches 
                WHERE home_team = ? AND away_team = ? AND home_goals IS NULL
                ORDER BY id DESC LIMIT 1
                """,
                (home, away)
            )
            row = cursor.fetchone()
            if row:
                consensus_prior = (row[0], row[1], row[2])
                print(f"Consensus prior loaded from database: H={consensus_prior[0]:.4f}, D={consensus_prior[1]:.4f}, A={consensus_prior[2]:.4f}")
    else:
        print(f"Warning: Database '{db_path}' not found. Predicting matchup using default parameters.")
        
    # Generate the score matrix
    matrix = generate_score_matrix(
        home_alpha=home_alpha,
        home_beta=home_beta,
        away_alpha=away_alpha,
        away_beta=away_beta,
        gamma=gamma,
        rho=rho,
        consensus_prior=consensus_prior
    )
    
    return ScoreMatrix(home_team=home, away_team=away, matrix=matrix)

def main():
    parser = argparse.ArgumentParser(description="Dixon-Coles Match Probability Generator")
    parser.add_argument("--home", type=str, required=True, help="Home team name")
    parser.add_argument("--away", type=str, required=True, help="Away team name")
    parser.add_argument("--db", type=str, default="matches.db", help="Path to SQLite database")
    
    args = parser.parse_args()
    
    print(f"\nAnalyzing Matchup: {args.home} vs {args.away}...")
    score_matrix = predict_matchup(args.home, args.away, args.db)
    
    # Print the matrix
    print("\n--- 6x6 Score Probability Matrix (Home Goals vs Away Goals) ---")
    print("      Away Goals ->")
    print("      " + " ".join(f"   {y}   " for y in range(6)))
    for x in range(6):
        row_str = f"H:{x} | " + " ".join(f"{score_matrix.matrix[x, y]*100:6.2f}%" for y in range(6))
        print(row_str)
        
    # Calculate and print outcome summaries
    p_home = 0.0
    p_draw = 0.0
    p_away = 0.0
    for x in range(6):
        for y in range(6):
            if x > y:
                p_home += score_matrix.matrix[x, y]
            elif x == y:
                p_draw += score_matrix.matrix[x, y]
            else:
                p_away += score_matrix.matrix[x, y]
                
    print("\n--- Summarized Match Probabilities ---")
    print(f"  Home Win: {p_home*100:6.2f}%")
    print(f"  Draw:     {p_draw*100:6.2f}%")
    print(f"  Away Win: {p_away*100:6.2f}%")
    print(f"  Total:    {np.sum(score_matrix.matrix)*100:6.2f}%")

if __name__ == "__main__":
    main()
