# ⚽ Football Match Predictor & World Cup 2026 Simulator

A local, high-performance, EV-centric prediction engine and tournament simulator for the 2026 FIFA World Cup, built using the modified Dixon-Coles model. All calculations, database storage, and presentation layers run 100% locally on your machine.

---

## 🚀 Quick Start & Setup

First, make sure you are in the project root directory and your local virtual environment is active or used directly.

**Command execution environment variable check (Windows PowerShell):**
Before running python CLI commands that import modules from `src/`, always ensure `PYTHONPATH` is set to the project root:
```powershell
$env:PYTHONPATH="."
```

---

## 📋 Execution Scripts Reference

Here is the list of all executable commands in this project, categorized by utility.

### 1. Interactive Predictions UI (Streamlit)
Launches the web-based presentation layer to generate EV-optimized exact score predictions by pasting raw odds text.
```powershell
.venv\Scripts\streamlit run app.py
```
* **How to use**: 
  - Open the browser at `http://localhost:8501`.
  - Paste multi-line bookmaker odds (e.g. from Bet365/Pinnacle) into the large text box.
  - Click **Generate Predictions** to calculate optimal exact score predictions based on EV maximization and non-linear contest scoring rules.

---

### 2. Upload Match Day Results (Interactive or CLI)
Allows adding new match results as the tournament progresses. It automatically standardizes team names and offers to re-calibrate the model parameters immediately.
```powershell
# Interactive wizard mode (Recommended):
.venv\Scripts\python src/data/upload_match_day.py

# Direct command line flag mode:
.venv\Scripts\python src/data/upload_match_day.py --home "France" --away "Germany" --home-goals 2 --away-goals 1 --date "2026-06-12"
```
* **Options**:
  - `--home`: Name of the home team.
  - `--away`: Name of the away team.
  - `--home-goals`: Goals scored by the home team.
  - `--away-goals`: Goals scored by the away team.
  - `--date`: Date of the match (format: `YYYY-MM-DD`, defaults to today).
  - `--db`: Path to the database file (defaults to `matches.db`).

---

### 3. Dixon-Coles Parameter Fitting (MLE Calibration)
Calibrates attack and defense parameters (`alpha` and `beta`) for all 48 tournament teams using SciPy Maximum Likelihood Estimation (MLE) based on the match history stored in your database.
```powershell
.venv\Scripts\python -m src.model.dixon_coles --fit
```
* **Options**:
  - `--fit`: Triggers the optimization process.
  - `--db`: Path to the SQLite database file (defaults to `matches.db`).

---

### 4. Import Historical Match Data (CSV Ingestion)
Parses international match history from the provided CSV file and uploads it into the database to build a base for model fitting.
```powershell
.venv\Scripts\python src/data/import_real_data.py --since 2021-01-01
```
* **Options**:
  - `--csv`: Path to the results CSV file (defaults to `src/data/real_data/results.csv`).
  - `--since`: Date threshold (defaults to `2021-01-01` to filter for recent matches).
  - `--db`: Path to the SQLite database file (defaults to `matches.db`).

---

### 5. Monte Carlo Tournament Simulator (10,000 Runs)
Runs a 100% vectorized Monte Carlo simulation of the entire 2026 World Cup bracket (Group Stage + Knockout Stage) to calculate advance probabilities and Goal Concentration Indices (GCI) for top scorer evaluation.
```powershell
.venv\Scripts\python -m src.cli.simulate --runs 10000
```
* **Options**:
  - `--runs` / `-n`: Number of full tournament simulations to perform (default: `10000`).
  - `--db` / `-d`: Path to the SQLite database file (default: `matches.db`).

---

## 🧪 Running Tests
To run the automated test suite verifying both the backend math engines and the Streamlit frontend AppTests:
```powershell
.venv\Scripts\python -m pytest
```
