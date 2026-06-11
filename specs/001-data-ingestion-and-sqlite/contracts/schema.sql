-- Database Schema: Data Ingestion and Consensus Storage
-- SQLite Compatibility Required

CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    home_team TEXT NOT NULL,
    away_team TEXT NOT NULL,
    match_date TEXT, -- ISO 8601 string
    consensus_p_home REAL NOT NULL,
    consensus_p_draw REAL NOT NULL,
    consensus_p_away REAL NOT NULL,
    home_goals INTEGER, -- Actual home goals (null for upcoming matches)
    away_goals INTEGER, -- Actual away goals (null for upcoming matches)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(home_team, away_team, match_date)
);

CREATE TABLE IF NOT EXISTS match_odds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    bookmaker_name TEXT NOT NULL,
    odds_home REAL NOT NULL,
    odds_draw REAL NOT NULL,
    odds_away REAL NOT NULL,
    p_true_home REAL NOT NULL,
    p_true_draw REAL NOT NULL,
    p_true_away REAL NOT NULL,
    FOREIGN KEY(match_id) REFERENCES matches(id) ON DELETE CASCADE,
    UNIQUE(match_id, bookmaker_name)
);

CREATE TABLE IF NOT EXISTS team_parameters (
    team_id TEXT PRIMARY KEY,
    alpha REAL NOT NULL,
    beta REAL NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS model_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gamma REAL NOT NULL,
    rho REAL NOT NULL,
    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
);
