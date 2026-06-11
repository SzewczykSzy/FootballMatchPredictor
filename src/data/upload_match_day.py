import os
import sys
from datetime import date

# Add the project root to python path to ensure imports work correctly when run from anywhere
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from src.data.models import MatchRecord
from src.data.database import get_db_connection, save_match
from src.model.bracket import TEAMS

def run_interactive():
    print("\n==============================================")
    print("      ⚽  Upload Match Day Results  ⚽")
    print("==============================================\n")
    
    # Sort teams for display
    tournament_teams = sorted(TEAMS)
    
    # 1. Get home team
    while True:
        home = input("Enter Home Team Name: ").strip()
        matched_home = [t for t in tournament_teams if t.lower() == home.lower()]
        if matched_home:
            home = matched_home[0]
            print(f"-> Standardized to: {home}")
            break
        print(f"Error: '{home}' is not a valid tournament team. Please check the list of teams.")
        print(f"Available Teams: {', '.join(tournament_teams)}\n")
        
    # 2. Get away team
    while True:
        away = input("Enter Away Team Name: ").strip()
        matched_away = [t for t in tournament_teams if t.lower() == away.lower()]
        if matched_away:
            away = matched_away[0]
            if away != home:
                print(f"-> Standardized to: {away}")
                break
            print("Error: Away team cannot be the same as the home team.")
        else:
            print(f"Error: '{away}' is not a valid tournament team. Please check the list of teams.\n")
            
    # 3. Get match date
    default_date = date.today().isoformat()
    match_date = input(f"Enter Match Date (YYYY-MM-DD) [default: {default_date}]: ").strip()
    if not match_date:
        match_date = default_date
    else:
        try:
            date.fromisoformat(match_date)
        except ValueError:
            print(f"Invalid format. Falling back to default date: {default_date}")
            match_date = default_date
            
    # 4. Get scores
    while True:
        try:
            home_goals = int(input(f"Enter goals scored by {home}: "))
            if home_goals >= 0:
                break
            print("Error: Goals must be a non-negative integer.")
        except ValueError:
            print("Error: Please enter a valid number.")
            
    while True:
        try:
            away_goals = int(input(f"Enter goals scored by {away}: "))
            if away_goals >= 0:
                break
            print("Error: Goals must be a non-negative integer.")
        except ValueError:
            print("Error: Please enter a valid number.")
            
    return home, away, match_date, home_goals, away_goals

def upload_result(home, away, match_date, home_goals, away_goals, db_path="matches.db"):
    match_record = MatchRecord(
        home_team=home,
        away_team=away,
        consensus_p_home=0.0,
        consensus_p_draw=0.0,
        consensus_p_away=0.0,
        match_date=match_date,
        home_goals=home_goals,
        away_goals=away_goals
    )
    
    print(f"\nConnecting to database '{db_path}'...")
    with get_db_connection(db_path) as conn:
        match_id = save_match(conn, match_record)
        print(f"✓ Success! Saved match to DB (ID: {match_id})")
        print(f"  Result: {home} {home_goals} - {away_goals} {away} (Date: {match_date})")
        
    # Ask if the user wants to re-fit team parameters
    refit = input("\nDo you want to re-fit the Dixon-Coles model parameters? (y/n) [default: y]: ").strip().lower()
    if not refit or refit in ['y', 'yes']:
        print("\nRe-fitting parameters on all matches in database...")
        try:
            from src.model.dixon_coles import run_fitting
            run_fitting(db_path)
            print("\n✓ Model parameters updated successfully!")
        except Exception as e:
            print(f"Error during fitting: {e}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Upload match results to SQLite database")
    parser.add_argument("--home", type=str, help="Home team name")
    parser.add_argument("--away", type=str, help="Away team name")
    parser.add_argument("--date", type=str, help="Match date (YYYY-MM-DD)")
    parser.add_argument("--home-goals", type=int, help="Home team goals")
    parser.add_argument("--away-goals", type=int, help="Away team goals")
    parser.add_argument("--db", type=str, default="matches.db", help="Path to database")
    
    args = parser.parse_args()
    
    # Check if CLI arguments were provided
    if args.home and args.away and args.home_goals is not None and args.away_goals is not None:
        tournament_teams = set(TEAMS)
        home = args.home.strip()
        away = args.away.strip()
        
        # Case-insensitive validation against tournament teams
        matched_home = [t for t in tournament_teams if t.lower() == home.lower()]
        matched_away = [t for t in tournament_teams if t.lower() == away.lower()]
        
        if not matched_home:
            print(f"Error: '{home}' is not a valid tournament team.")
            sys.exit(1)
        if not matched_away:
            print(f"Error: '{away}' is not a valid tournament team.")
            sys.exit(1)
            
        home = matched_home[0]
        away = matched_away[0]
        match_date = args.date.strip() if args.date else date.today().isoformat()
        
        upload_result(home, away, match_date, args.home_goals, args.away_goals, args.db)
    else:
        # Run interactive prompt
        home, away, match_date, home_goals, away_goals = run_interactive()
        upload_result(home, away, match_date, home_goals, away_goals, args.db)
