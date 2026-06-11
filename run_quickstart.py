import os
import time
from src.data.database import initialize_db, get_db_connection, save_match, get_all_matches
from src.data.parser import parse_odds_with_consensus
from src.data.models import MatchRecord, MatchOdds

def main():
    db_path = "matches.db"
    
    # Remove existing db if any, for a clean run
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
        except OSError:
            pass
            
    # 1. Initialize the database
    print("Initializing SQLite database 'matches.db'...")
    initialize_db(db_path)
    
    # 2. Paste text containing odds
    raw_text = """
    Arsenal - Chelsea
    Bet365 2.10 3.40 3.20
    Pinnacle 2.15 3.35 3.30
    
    Liverpool - Manchester City
    Bet365 1.90 3.60 4.00
    Pinnacle 1.95 3.65 3.80
    """
    
    print("\nParsing raw odds text...")
    # 3. Parse to objects with consensus
    matches = parse_odds_with_consensus(raw_text)
    
    # 4. Save to database
    print("\nSaving matches to database...")
    with get_db_connection(db_path) as conn:
        for m_dict in matches:
            odds_list = []
            for o_dict in m_dict.get("odds", []):
                odds_list.append(MatchOdds(
                    bookmaker_name=o_dict["bookmaker_name"],
                    odds_home=o_dict["odds_home"],
                    odds_draw=o_dict["odds_draw"],
                    odds_away=o_dict["odds_away"],
                    p_true_home=o_dict["p_true_home"],
                    p_true_draw=o_dict["p_true_draw"],
                    p_true_away=o_dict["p_true_away"]
                ))
            
            match_record = MatchRecord(
                home_team=m_dict["home_team"],
                away_team=m_dict["away_team"],
                consensus_p_home=m_dict["consensus_p_home"],
                consensus_p_draw=m_dict["consensus_p_draw"],
                consensus_p_away=m_dict["consensus_p_away"],
                match_date=m_dict.get("match_date"),
                odds=odds_list
            )
            
            match_id = save_match(conn, match_record)
            print(f"Saved Match ID: {match_id} | {match_record.home_team} vs {match_record.away_team}")
            print(f"  Consensus: H:{match_record.consensus_p_home:.4f} D:{match_record.consensus_p_draw:.4f} A:{match_record.consensus_p_away:.4f}")
            
    # 5. Retrieve saved matches to validate
    print("\nRetrieving all matches from database to validate...")
    with get_db_connection(db_path) as conn:
        saved_matches = get_all_matches(conn)
        
    print(f"Total matches retrieved: {len(saved_matches)}")
    for m in saved_matches:
        print(f"\nMatch: {m.home_team} - {m.away_team} (Date: {m.match_date})")
        print(f"  Consensus Probability: Home={m.consensus_p_home:.4f}, Draw={m.consensus_p_draw:.4f}, Away={m.consensus_p_away:.4f}")
        print("  Bookmaker Odds:")
        for o in m.odds:
            print(f"    - {o.bookmaker_name}: Odds=[{o.odds_home}, {o.odds_draw}, {o.odds_away}] | True Prob=[{o.p_true_home:.4f}, {o.p_true_draw:.4f}, {o.p_true_away:.4f}]")

    # 6. Benchmark check (SC-001)
    print("\n--- Running SC-001 Performance Benchmark ---")
    benchmark_text = """
    Arsenal - Chelsea
    """
    for i in range(1, 11):
        benchmark_text += f"\nBookmaker{i} {2.0 + i/100:.2f} {3.0 + i/100:.2f} {4.0 + i/100:.2f}"
        
    start_time = time.perf_counter()
    parsed_benchmark = parse_odds_with_consensus(benchmark_text)
    end_time = time.perf_counter()
    elapsed = end_time - start_time
    
    print(f"Parsed and consolidated 1 match with 10 bookmakers in {elapsed:.6f} seconds.")
    assert elapsed < 1.0, f"SC-001 Failed: took {elapsed:.6f}s"
    print("SC-001 PASS")

if __name__ == "__main__":
    main()
