"""
CLI tool to execute the Monte Carlo World Cup 2026 Tournament Simulator.
"""

import argparse
import sys
import time
import os
import pandas as pd
from src.model.simulation import simulate_tournament

def format_as_table(df: pd.DataFrame) -> str:
    """
    Formats the probability DataFrame as a premium ASCII table.
    """
    header = (
        f"{'Team':<16} | {'Group Win':<9} | {'Advance':<7} | {'R16':<6} | "
        f"{'QF':<6} | {'SF':<6} | {'Final':<6} | {'Champion':<8} | {'Avg GCI':<7}"
    )
    divider = "-" * len(header)
    lines = [header, divider]
    
    for _, row in df.iterrows():
        line = (
            f"{row['team']:<16} | "
            f"{row['p_group_winner']:<9.4f} | "
            f"{row['p_advance']:<7.4f} | "
            f"{row['p_r16']:<6.4f} | "
            f"{row['p_qf']:<6.4f} | "
            f"{row['p_sf']:<6.4f} | "
            f"{row['p_final']:<6.4f} | "
            f"{row['p_champion']:<8.4f} | "
            f"{row['avg_gci']:<7.4f}"
        )
        lines.append(line)
        
    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(
        description="Vectorized Monte Cup World Cup 2026 Tournament Simulator"
    )
    parser.add_argument(
        "--runs", "-n",
        type=int,
        default=10000,
        help="Number of simulations to run (default: 10000)"
    )
    parser.add_argument(
        "--db", "-d",
        type=str,
        default="matches.db",
        help="Path to the SQLite database (default: matches.db)"
    )
    parser.add_argument(
        "--format", "-f",
        type=str,
        choices=["table", "csv", "json"],
        default="table",
        help="Output format: table, csv, or json (default: table)"
    )
    parser.add_argument(
        "--output", "-o",
        type=str,
        default=None,
        help="Optional file path to export results (default: stdout)"
    )

    args = parser.parse_args()
    
    # 1. Print progress info to stderr so stdout redirection stays clean
    sys.stderr.write(f"Running {args.runs:,} tournament simulations using database '{args.db}'...\n")
    sys.stderr.flush()
    
    start_time = time.perf_counter()
    
    # 2. Run simulation
    try:
        df = simulate_tournament(runs=args.runs, db_path=args.db)
    except Exception as e:
        sys.stderr.write(f"Error executing simulation: {e}\n")
        sys.exit(1)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    sys.stderr.write(f"Simulation completed in {duration:.2f} seconds.\n\n")
    sys.stderr.flush()
    
    # 3. Format output
    if args.format == "csv":
        output_str = df.to_csv(index=False)
    elif args.format == "json":
        output_str = df.to_json(orient="records", indent=2)
    else:  # table
        output_str = format_as_table(df)
        
    # 4. Write output to file or stdout
    if args.output:
        try:
            # Ensure output directories exist
            out_dir = os.path.dirname(args.output)
            if out_dir:
                os.makedirs(out_dir, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(output_str)
            sys.stderr.write(f"Results successfully exported to '{args.output}'.\n")
        except Exception as e:
            sys.stderr.write(f"Error writing output to file: {e}\n")
            sys.exit(1)
    else:
        sys.stdout.write(output_str + "\n")
        sys.stdout.flush()

if __name__ == "__main__":
    main()
