import os
import sqlite3
import numpy as np
from typing import List, Dict, Any, Tuple, Optional

from src.data.parser import parse_odds_with_consensus
from src.model.matrix import generate_score_matrix
from src.model.optimizer import calculate_best_ev
from src.model.parameters import get_team_parameters, get_model_config

def process_odds_and_predict(odds_text: str, db_path: str = "matches.db") -> List[Dict[str, Any]]:
    """
    Connects the regex parser and EV optimization pipeline.
    Parses raw odds text, loads parameters from matches.db, generates score matrices,
    runs EV optimization, and returns formatted prediction rows.
    """
    if not odds_text or not odds_text.strip():
        raise ValueError("Input odds text is empty.")

    matches = parse_odds_with_consensus(odds_text)
    if not matches:
        raise ValueError("No matches or bookmaker odds could be parsed from the input text.")

    results = []

    # Connect to SQLite database if it exists
    has_db = os.path.exists(db_path)
    conn = None
    if has_db:
        try:
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
        except Exception:
            pass

    try:
        for match in matches:
            home = match["home_team"]
            away = match["away_team"]
            
            # Default model parameters if not found in DB
            home_alpha, home_beta = 1.0, 1.0
            away_alpha, away_beta = 1.0, 1.0
            gamma, rho = 1.0, 0.0

            if conn:
                try:
                    h_params = get_team_parameters(conn, home)
                    if h_params:
                        home_alpha, home_beta = h_params.alpha, h_params.beta
                    
                    a_params = get_team_parameters(conn, away)
                    if a_params:
                        away_alpha, away_beta = a_params.alpha, a_params.beta

                    config = get_model_config(conn)
                    if config:
                        gamma, rho = config["gamma"], config["rho"]
                except Exception:
                    # Fail silently and fall back to default parameters if database queries fail
                    pass

            # Prepare consensus prior from parsed odds if available
            consensus_prior = None
            if "consensus_p_home" in match and match["consensus_p_home"] is not None:
                consensus_prior = (
                    match["consensus_p_home"],
                    match["consensus_p_draw"],
                    match["consensus_p_away"]
                )

            # Generate the 6x6 score probability matrix
            matrix = generate_score_matrix(
                home_alpha=home_alpha,
                home_beta=home_beta,
                away_alpha=away_alpha,
                away_beta=away_beta,
                gamma=gamma,
                rho=rho,
                consensus_prior=consensus_prior
            )

            # Compute optimal EV prediction
            best_prediction, best_ev = calculate_best_ev(matrix, max_score=5)

            results.append({
                "MatchID": f"{home} vs {away}",
                "Recommended Prediction": f"{best_prediction[0]}-{best_prediction[1]}",
                "Expected Value": best_ev,
                "Status": "Success"
            })
    finally:
        if conn:
            conn.close()

    return results

def render_predictions_table(prediction_rows: List[Dict[str, Any]]) -> None:
    """
    Renders the prediction results as a scannable Streamlit table.
    """
    import streamlit as st
    import pandas as pd
    
    if not prediction_rows:
        st.info("No predictions to display.")
        return

    # Convert to DataFrame for rendering
    df = pd.DataFrame(prediction_rows)
    
    # Format EV to 4 decimal places for UI readability
    if "Expected Value" in df.columns:
        df["Expected Value"] = df["Expected Value"].map(lambda val: f"{val:.4f}" if isinstance(val, (int, float)) else val)
        
    st.table(df)
