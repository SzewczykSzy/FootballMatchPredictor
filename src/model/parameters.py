import sqlite3
from typing import Dict, List, Optional
from src.model.contracts import TeamParameters

def save_team_parameters(conn: sqlite3.Connection, params: List[TeamParameters]) -> None:
    """
    Saves a list of TeamParameters to the team_parameters table, upserting if team_id exists.
    """
    cursor = conn.cursor()
    cursor.executemany(
        """
        INSERT INTO team_parameters (team_id, alpha, beta, last_updated)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(team_id) DO UPDATE SET
            alpha = excluded.alpha,
            beta = excluded.beta,
            last_updated = CURRENT_TIMESTAMP;
        """,
        [(p.team_id, p.alpha, p.beta) for p in params]
    )

def get_team_parameters(conn: sqlite3.Connection, team_id: str) -> Optional[TeamParameters]:
    """
    Retrieves the parameters for a specific team.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT team_id, alpha, beta FROM team_parameters WHERE team_id = ?",
        (team_id,)
    )
    row = cursor.fetchone()
    if not row:
        return None
    return TeamParameters(team_id=row["team_id"], alpha=row["alpha"], beta=row["beta"])

def get_all_team_parameters(conn: sqlite3.Connection) -> Dict[str, TeamParameters]:
    """
    Retrieves all team parameters as a dictionary mapping team_id to TeamParameters.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT team_id, alpha, beta FROM team_parameters")
    rows = cursor.fetchall()
    result = {}
    for row in rows:
        team_id = row["team_id"]
        result[team_id] = TeamParameters(team_id=team_id, alpha=row["alpha"], beta=row["beta"])
    return result

def save_model_config(conn: sqlite3.Connection, gamma: float, rho: float) -> None:
    """
    Saves the global model configuration (gamma, rho) into model_config table.
    """
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO model_config (gamma, rho, last_updated) VALUES (?, ?, CURRENT_TIMESTAMP)",
        (gamma, rho)
    )

def get_model_config(conn: sqlite3.Connection) -> Optional[Dict[str, float]]:
    """
    Retrieves the latest global model configuration.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT gamma, rho FROM model_config ORDER BY id DESC LIMIT 1"
    )
    row = cursor.fetchone()
    if not row:
        return None
    return {"gamma": row["gamma"], "rho": row["rho"]}
