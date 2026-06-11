import pytest
from src.data.database import initialize_db, get_db_connection, save_match, get_match, get_all_matches
from src.data.models import MatchRecord, MatchOdds

def test_initialize_db(tmp_path):
    db_file = tmp_path / "test_matches.db"
    db_path = str(db_file)
    
    # Initialize the database
    initialize_db(db_path)
    
    # Verify tables exist
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row["name"] for row in cursor.fetchall()]
        
    assert "matches" in tables
    assert "match_odds" in tables

def test_save_and_retrieve_match(tmp_path):
    db_file = tmp_path / "test_matches.db"
    db_path = str(db_file)
    initialize_db(db_path)
    
    # Create MatchRecord
    odds_bet365 = MatchOdds(
        bookmaker_name="Bet365",
        odds_home=2.10,
        odds_draw=3.40,
        odds_away=3.20,
        p_true_home=0.44,
        p_true_draw=0.27,
        p_true_away=0.29
    )
    odds_pinnacle = MatchOdds(
        bookmaker_name="Pinnacle",
        odds_home=2.15,
        odds_draw=3.35,
        odds_away=3.30,
        p_true_home=0.43,
        p_true_draw=0.28,
        p_true_away=0.29
    )
    
    match = MatchRecord(
        home_team="Arsenal",
        away_team="Chelsea",
        consensus_p_home=0.435,
        consensus_p_draw=0.275,
        consensus_p_away=0.290,
        match_date="2026-06-12",
        odds=[odds_bet365, odds_pinnacle]
    )
    
    # Save match
    with get_db_connection(db_path) as conn:
        match_id = save_match(conn, match)
        
    assert match_id is not None
    
    # Retrieve match
    with get_db_connection(db_path) as conn:
        retrieved = get_match(conn, match_id)
        
    assert retrieved is not None
    assert retrieved.id == match_id
    assert retrieved.home_team == "Arsenal"
    assert retrieved.away_team == "Chelsea"
    assert retrieved.match_date == "2026-06-12"
    assert retrieved.consensus_p_home == pytest.approx(0.435)
    assert len(retrieved.odds) == 2
    
    bet365_retrieved = next(o for o in retrieved.odds if o.bookmaker_name == "Bet365")
    assert bet365_retrieved.odds_home == 2.10
    assert bet365_retrieved.p_true_home == pytest.approx(0.44)
    assert bet365_retrieved.match_id == match_id

def test_upsert_match_behavior(tmp_path):
    db_file = tmp_path / "test_matches.db"
    db_path = str(db_file)
    initialize_db(db_path)
    
    match1 = MatchRecord(
        home_team="Real Madrid",
        away_team="Barcelona",
        consensus_p_home=0.50,
        consensus_p_draw=0.25,
        consensus_p_away=0.25,
        match_date="2026-06-15",
        odds=[
            MatchOdds("Bet365", 1.80, 3.60, 3.60, 0.50, 0.25, 0.25)
        ]
    )
    
    # First save
    with get_db_connection(db_path) as conn:
        id1 = save_match(conn, match1)
        
    # Create an updated MatchRecord (same teams and date)
    match2 = MatchRecord(
        home_team="Real Madrid",
        away_team="Barcelona",
        consensus_p_home=0.52,
        consensus_p_draw=0.24,
        consensus_p_away=0.24,
        match_date="2026-06-15",
        odds=[
            # Overwrite Bet365 and add Pinnacle
            MatchOdds("Bet365", 1.75, 3.70, 3.70, 0.52, 0.24, 0.24),
            MatchOdds("Pinnacle", 1.80, 3.60, 3.60, 0.51, 0.25, 0.24)
        ]
    )
    
    # Second save (should update the existing)
    with get_db_connection(db_path) as conn:
        id2 = save_match(conn, match2)
        
    assert id1 == id2  # IDs must match
    
    # Check that there is only 1 match in DB
    with get_db_connection(db_path) as conn:
        all_matches = get_all_matches(conn)
        retrieved = get_match(conn, id1)
        
    assert len(all_matches) == 1
    assert retrieved is not None
    assert retrieved.consensus_p_home == pytest.approx(0.52)
    assert len(retrieved.odds) == 2
    
    bet365_odds = next(o for o in retrieved.odds if o.bookmaker_name == "Bet365")
    assert bet365_odds.odds_home == 1.75

