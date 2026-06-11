import os
import csv
import sqlite3
import argparse
from src.model.bracket import TEAMS

# Team name mapping to match the bracket definition exactly
TEAM_MAPPING = {
    "United States": "USA",
    "United Arab Emirates": "UAE"
}

def import_csv_to_db(csv_path: str, db_path: str, start_date: str):
    """
    Reads historical matches from the CSV file, filters them for tournament teams,
    standardizes names, and imports them into the SQLite database.
    """
    if not os.path.exists(csv_path):
        print(f"Error: CSV file not found at '{csv_path}'")
        return
        
    print(f"Reading matches from '{csv_path}' since {start_date}...")
    
    # Create a set of tournament teams for O(1) lookup
    tournament_teams = set(TEAMS)
    
    matches_to_insert = []
    skipped_non_tournament = 0
    try:
        with open(csv_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                match_date = row['date']
                if match_date < start_date:
                    continue
                    
                # Skip if score is NA (unplayed/upcoming)
                if row['home_score'] == 'NA' or row['away_score'] == 'NA':
                    continue
                    
                home_team = row['home_team']
                away_team = row['away_team']
                
                # Apply standardizations
                home_team = TEAM_MAPPING.get(home_team, home_team)
                away_team = TEAM_MAPPING.get(away_team, away_team)
                
                # Filter: Keep matches only if BOTH teams are in the 48 tournament teams
                if home_team not in tournament_teams or away_team not in tournament_teams:
                    skipped_non_tournament += 1
                    continue
                    
                home_goals = int(row['home_score'])
                away_goals = int(row['away_score'])
                
                # Default consensus probabilities to 0.0 for completed matches
                matches_to_insert.append((
                    home_team,
                    away_team,
                    match_date,
                    0.0, 0.0, 0.0,  # consensus_p_home, consensus_p_draw, consensus_p_away
                    home_goals,
                    away_goals
                ))
    except Exception as e:
        print(f"Error parsing CSV: {e}")
        return

    total_parsed = len(matches_to_insert)
    print(f"Parsed {total_parsed} completed matches since {start_date} involving tournament teams.")
    print(f"Skipped {skipped_non_tournament} matches involving non-tournament teams.")
    
    if not matches_to_insert:
        print("No matches to import.")
        return
        
    print(f"Connecting to database '{db_path}'...")
    conn = sqlite3.connect(db_path)
    try:
        cursor = conn.cursor()
        
        # We delete existing historical matches first to start with a clean filtered dataset
        # (This is important to clear the previously imported unfiltered 5,683 matches)
        print("Cleaning up old completed matches in the database...")
        cursor.execute("DELETE FROM matches WHERE home_goals IS NOT NULL AND away_goals IS NOT NULL")
        
        # Insert in batches using ON CONFLICT to update scores if matches already exist
        print(f"Inserting {total_parsed} matches...")
        cursor.executemany(
            """
            INSERT INTO matches (home_team, away_team, match_date, consensus_p_home, consensus_p_draw, consensus_p_away, home_goals, away_goals)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(home_team, away_team, match_date) DO UPDATE SET
                home_goals = excluded.home_goals,
                away_goals = excluded.away_goals;
            """,
            matches_to_insert
        )
        conn.commit()
        print(f"Successfully imported/updated {total_parsed} matches in the database.")
    except Exception as e:
        conn.rollback()
        print(f"Error inserting into database: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Import tournament matches from CSV to SQLite database")
    parser.add_argument("--csv", type=str, default="src/data/real_data/results.csv", help="Path to results CSV file")
    parser.add_argument("--db", type=str, default="matches.db", help="Path to SQLite database")
    parser.add_argument("--since", type=str, default="2021-01-01", help="Import matches on or after this ISO date")
    
    args = parser.parse_args()
    import_csv_to_db(args.csv, args.db, args.since)
