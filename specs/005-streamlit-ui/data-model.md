# Phase 1: Data Model

**Feature**: Streamlit UI

## Core Data Structures

### 1. `PredictionOutputRow` (View Model)
- **Type**: Struct / Dictionary / Pandas DataFrame Row
- **Description**: The formatted output representation of a successfully processed match prediction.
- **Fields**:
  - `MatchID` (String): Identifier or title for the match (e.g., "Arsenal vs Chelsea").
  - `Recommended Prediction` (String): The exact score prediction (e.g., "2-1").
  - `Expected Value` (Float/String): The calculated EV, formatted to 2-4 decimal places (e.g., "3.42").
  - `Status` (String): Success or error state for that specific match parsing.

### 2. `RawOddsInput` (Input Model)
- **Type**: String
- **Description**: The raw multi-line string pasted by the user containing the team names, times, and bookmaker odds. It is passed directly to the `src/data/parser.py` module.

## Relationships
The UI acts as a pure conduit. It accepts `RawOddsInput`, delegates to the backend, and iterates over the backend responses to construct a list of `PredictionOutputRow` objects, which are then rendered directly to the screen via `st.table` or `st.dataframe`.
