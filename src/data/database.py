import sqlite3
import os
from contextlib import contextmanager
from typing import List, Optional
from src.data.models import MatchRecord, MatchOdds

DEFAULT_DB_PATH = "matches.db"
DEFAULT_SCHEMA_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..",
    "specs", "001-data-ingestion-and-sqlite", "contracts", "schema.sql"
)

@contextmanager
def get_db_connection(db_path: str = DEFAULT_DB_PATH):
    """
    Context manager for SQLite database connections.
    Enables foreign keys and handles transactions.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

def initialize_db(db_path: str = DEFAULT_DB_PATH, schema_path: str = None):
    """
    Initializes the SQLite database with the schema defined in schema.sql.
    """
    if schema_path is None:
        schema_path = os.path.abspath(DEFAULT_SCHEMA_PATH)
        
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found at {schema_path}")
        
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
        
    with get_db_connection(db_path) as conn:
        conn.executescript(schema_sql)


def save_match(conn: sqlite3.Connection, match: MatchRecord) -> int:
    """
    Saves a MatchRecord and its MatchOdds to the database.
    If a match with the same home_team, away_team, and match_date already exists,
    it updates the consensus probabilities and replaces the bookmaker odds.
    """
    cursor = conn.cursor()
    
    # Check if match already exists
    if match.match_date is None:
        cursor.execute(
            "SELECT id FROM matches WHERE home_team = ? AND away_team = ? AND match_date IS NULL",
            (match.home_team, match.away_team)
        )
    else:
        cursor.execute(
            "SELECT id FROM matches WHERE home_team = ? AND away_team = ? AND match_date = ?",
            (match.home_team, match.away_team, match.match_date)
        )
        
    row = cursor.fetchone()
    if row:
        match_id = row[0]
        # Update existing match consensus and goals
        cursor.execute(
            """
            UPDATE matches 
            SET consensus_p_home = ?, consensus_p_draw = ?, consensus_p_away = ?, home_goals = ?, away_goals = ?
            WHERE id = ?
            """,
            (match.consensus_p_home, match.consensus_p_draw, match.consensus_p_away, match.home_goals, match.away_goals, match_id)
        )
        
        # Delete old odds
        cursor.execute("DELETE FROM match_odds WHERE match_id = ?", (match_id,))
    else:
        # Insert new match
        cursor.execute(
            """
            INSERT INTO matches (home_team, away_team, match_date, consensus_p_home, consensus_p_draw, consensus_p_away, home_goals, away_goals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (match.home_team, match.away_team, match.match_date, 
             match.consensus_p_home, match.consensus_p_draw, match.consensus_p_away, match.home_goals, match.away_goals)
        )
        match_id = cursor.lastrowid
        
    # Insert new odds
    for o in match.odds:
        cursor.execute(
            """
            INSERT INTO match_odds (match_id, bookmaker_name, odds_home, odds_draw, odds_away, p_true_home, p_true_draw, p_true_away)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (match_id, o.bookmaker_name, o.odds_home, o.odds_draw, o.odds_away, o.p_true_home, o.p_true_draw, o.p_true_away)
        )
        
    return match_id

def get_match(conn: sqlite3.Connection, match_id: int) -> Optional[MatchRecord]:
    """
    Retrieves a MatchRecord by ID, along with its MatchOdds.
    """
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, home_team, away_team, match_date, consensus_p_home, consensus_p_draw, consensus_p_away, home_goals, away_goals, created_at FROM matches WHERE id = ?",
        (match_id,)
    )
    m_row = cursor.fetchone()
    if not m_row:
        return None
        
    # Query match_odds
    cursor.execute(
        "SELECT id, match_id, bookmaker_name, odds_home, odds_draw, odds_away, p_true_home, p_true_draw, p_true_away FROM match_odds WHERE match_id = ?",
        (match_id,)
    )
    odds_rows = cursor.fetchall()
    
    odds_list = []
    for r in odds_rows:
        odds_list.append(MatchOdds(
            id=r["id"],
            match_id=r["match_id"],
            bookmaker_name=r["bookmaker_name"],
            odds_home=r["odds_home"],
            odds_draw=r["odds_draw"],
            odds_away=r["odds_away"],
            p_true_home=r["p_true_home"],
            p_true_draw=r["p_true_draw"],
            p_true_away=r["p_true_away"]
        ))
        
    return MatchRecord(
        id=m_row["id"],
        home_team=m_row["home_team"],
        away_team=m_row["away_team"],
        match_date=m_row["match_date"],
        consensus_p_home=m_row["consensus_p_home"],
        consensus_p_draw=m_row["consensus_p_draw"],
        consensus_p_away=m_row["consensus_p_away"],
        home_goals=m_row["home_goals"],
        away_goals=m_row["away_goals"],
        created_at=m_row["created_at"],
        odds=odds_list
    )

def get_all_matches(conn: sqlite3.Connection) -> List[MatchRecord]:
    """
    Retrieves all matches in the database.
    """
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM matches")
    ids = [row[0] for row in cursor.fetchall()]
    
    matches = []
    for m_id in ids:
        match = get_match(conn, m_id)
        if match:
            matches.append(match)
    return matches

