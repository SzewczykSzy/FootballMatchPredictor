import re
from typing import List, Dict, Any
from src.data.math_utils import calculate_consensus

def parse_odds_text(text: str) -> List[Dict[str, Any]]:
    """
    Parses a block of text containing odds.
    """
    # Regex to match a bookmaker line: Name followed by 3 float/int odds
    bookmaker_pattern = re.compile(
        r'^\s*([a-zA-Z][a-zA-Z0-9\s\.\-_]+?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)\s*$'
    )
    
    # Regex to match match header: Team A - Team B or Team A vs Team B
    match_header_pattern = re.compile(
        r'^\s*(?P<home>.+?)\s+(?:-|vs\.?|v\.?)\s+(?P<away>.+?)\s*$'
    )
    
    # Regex for a date: YYYY-MM-DD
    date_pattern = re.compile(r'^\s*(\d{4}-\d{2}-\d{2})\s*$')
    
    matches = []
    current_match = None
    odds_dict = {}
    last_seen_date = None
    
    lines = text.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # 1. Try to match date
        date_match = date_pattern.match(line)
        if date_match:
            last_seen_date = date_match.group(1)
            continue
            
        # 2. Try to match bookmaker odds
        bookmaker_match = bookmaker_pattern.match(line)
        if bookmaker_match:
            if current_match is not None:
                bookmaker_name = bookmaker_match.group(1).strip()
                odds_h = float(bookmaker_match.group(2))
                odds_d = float(bookmaker_match.group(3))
                odds_a = float(bookmaker_match.group(4))
                
                # Check that odds are > 1.0
                if odds_h > 1.0 and odds_d > 1.0 and odds_a > 1.0:
                    odds_dict[bookmaker_name] = {
                        "bookmaker_name": bookmaker_name,
                        "odds_home": odds_h,
                        "odds_draw": odds_d,
                        "odds_away": odds_a
                    }
            continue
            
        # 3. Try to match match header
        header_match = match_header_pattern.match(line)
        if header_match:
            # Save the current match if we have one
            if current_match is not None:
                current_match["odds"] = list(odds_dict.values())
                matches.append(current_match)
                
            home = header_match.group("home").strip()
            away = header_match.group("away").strip()
            
            # Re-initialize current match
            current_match = {
                "home_team": home,
                "away_team": away,
                "match_date": last_seen_date,
                "odds": []
            }
            odds_dict = {}
            
    # Save the final match if exists
    if current_match is not None:
        current_match["odds"] = list(odds_dict.values())
        matches.append(current_match)
        
    return matches

def parse_odds_with_consensus(text: str) -> List[Dict[str, Any]]:
    """
    Parses a block of text containing odds and calculates the consensus for each match.
    """
    matches = parse_odds_text(text)
    for match in matches:
        if match["odds"]:
            consensus = calculate_consensus(match)
            match.update(consensus)
    return matches
