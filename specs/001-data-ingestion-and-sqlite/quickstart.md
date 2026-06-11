# Quickstart: Data Ingestion and SQLite Module

This module is responsible for parsing pasted text containing football odds, neutralizing the bookmaker margin, calculating the consensus, and saving the data to SQLite.

## Prerequisites
- Python 3.11+
- No external packages required for ingestion (only standard `re` and `sqlite3`). `pytest` needed for tests.

## Local Setup

1. **Initialize the database**:
   Run the database setup script (to be implemented) which will execute `contracts/schema.sql` against a local file `matches.db`.

2. **Parsing Odds**:
   Pass a string containing the copied odds to the `Parser` class.
   ```python
   from src.data.parser import parse_odds_text
   from src.data.math_utils import calculate_consensus

   raw_text = """
   Arsenal - Chelsea
   Bet365 2.10 3.40 3.20
   Pinnacle 2.15 3.35 3.30
   """
   
   # Parse to raw objects
   matches = parse_odds_text(raw_text)
   
   # Calculate consensus
   for match in matches:
       consensus = calculate_consensus(match)
       print(consensus)
   ```

3. **Running Tests**:
   Execute `pytest tests/data` to ensure regex parsing and math calculations are functioning as expected.
