import pytest
from src.data.parser import parse_odds_text

def test_parse_odds_text_basic():
    raw_text = """
    Arsenal - Chelsea
    Bet365 2.10 3.40 3.20
    Pinnacle 2.15 3.35 3.30
    """
    matches = parse_odds_text(raw_text)
    assert len(matches) == 1
    
    match = matches[0]
    assert match["home_team"] == "Arsenal"
    assert match["away_team"] == "Chelsea"
    assert len(match["odds"]) == 2
    
    # Check Bet365
    bet365_odds = next(o for o in match["odds"] if o["bookmaker_name"] == "Bet365")
    assert bet365_odds["odds_home"] == 2.10
    assert bet365_odds["odds_draw"] == 3.40
    assert bet365_odds["odds_away"] == 3.20

    # Check Pinnacle
    pinnacle_odds = next(o for o in match["odds"] if o["bookmaker_name"] == "Pinnacle")
    assert pinnacle_odds["odds_home"] == 2.15
    assert pinnacle_odds["odds_draw"] == 3.35
    assert pinnacle_odds["odds_away"] == 3.30

def test_parse_odds_text_with_malformed_and_duplicate():
    raw_text = """
    Some random header line to ignore
    Liverpool - Manchester City
    Bet365 1.90 3.60 4.00
    InvalidLine 1.90 3.60
    Bet365 1.95 3.65 3.80
    Bwin 2.00 3.50 3.75
    """
    matches = parse_odds_text(raw_text)
    assert len(matches) == 1
    
    match = matches[0]
    assert match["home_team"] == "Liverpool"
    assert match["away_team"] == "Manchester City"
    # Bet365 appears twice. The last one (1.95, 3.65, 3.80) must overwrite the first.
    # Bwin has 1 entry.
    # Total bookmakers = 2.
    assert len(match["odds"]) == 2
    
    bet365_odds = next(o for o in match["odds"] if o["bookmaker_name"] == "Bet365")
    assert bet365_odds["odds_home"] == 1.95
    assert bet365_odds["odds_draw"] == 3.65
    assert bet365_odds["odds_away"] == 3.80

    bwin_odds = next(o for o in match["odds"] if o["bookmaker_name"] == "Bwin")
    assert bwin_odds["odds_home"] == 2.00
    assert bwin_odds["odds_draw"] == 3.50
    assert bwin_odds["odds_away"] == 3.75
