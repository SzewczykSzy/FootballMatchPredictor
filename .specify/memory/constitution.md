<!--
Sync Impact Report:
- Version change: 1.0.0 -> 1.0.1
- List of modified principles:
  - Translated all principles and sections to English
- Added sections: None
- Removed sections: None
- Templates requiring updates: ✅ updated
- Follow-up TODOs: None
-->

# FootballMatchPredictor Constitution

## Core Principles

### I. 100% Local Execution
All calculations, data storage, and the user interface MUST operate 100% locally on a single workstation. Introducing dependencies on external cloud infrastructure during the application's inference and operation processes is strictly prohibited.
**Rationale**: Ensuring maximum performance, network independence, and instantaneous operation in daily mode (0 minutes before kickoff).

### II. EV-Centric Decision Making (EV Maximization)
The system recommending predictions MUST base its decisions on maximizing the Expected Value (EV) of tournament points, rather than simply pointing to the most probable match outcome.
**Rationale**: The contest features a non-linear scoring structure (e.g., 5 points for exact score, 3 for goal difference). Optimizing for EV considers the full probability distribution from the model and the points from the rules, providing a mathematical long-term advantage.

### III. Multi-Bookmaker Consensus & Overround Correction
Input data MUST be acquired by aggregating odds from multiple bookmakers (using multiline regular expressions). Implied probabilities MUST be cleaned of bookmaker margin (overround) using the proportional method before being averaged into a stable market consensus.
**Rationale**: The bookmaker market as a whole is more accurate than individual companies. A consensus prevents anomalies from skewing results and provides a stable prior for the probabilistic model.

### IV. Vectorized Computation
All operations on probability matrices and Monte Carlo simulations MUST be fully vectorized using NumPy and Pandas libraries. The use of standard Python loops for large-scale numerical operations is strictly prohibited.
**Rationale**: Conducting 10,000 simulations of the entire tournament (48 teams) on a local laptop in a matter of seconds requires strict vectorized optimization.

### V. Interactive Streamlit UI & SQLite Storage
The presentation layer MUST be built using the lightweight Streamlit framework, featuring a dedicated large text area for pasting raw bookmaker odds. Match data and statistics MUST be stored in a serverless SQLite database.
**Rationale**: Streamlit and SQLite perfectly align with the 100% local architecture paradigm, avoiding the overhead of external server configurations or background processes.

## Technology Stack & Local Environment Constraints

The system is implemented using Python 3.11+. The core libraries include NumPy and Pandas for vectorized simulations, SciPy (`scipy.optimize` module) for local Maximum Likelihood Estimation (MLE) parameter fitting, the built-in `re` module for multiline odds parsing, and Streamlit for rendering the GUI. The database is a single-file SQLite database. Everything operates "in-memory" and on the laptop's local disk.

## Tournament Simulation & Parameter Calibration

The analytical core of the system is the modified Dixon-Coles model, which addresses the issue of low-score correlation. Its parameters (attack strength $\alpha$, defense strength $\beta$) are estimated locally (MLE) using SciPy. To answer long-term questions (e.g., Champion, Top Scorer), 10,000 stochastic simulations of the tournament bracket are performed based on the generated Poisson distributions. The results are aggregated and presented to the user to answer non-match questions.

## Governance

This constitution dictates the system architecture and technological requirements. Any technological changes, including proposals to use non-local tools or modify the evaluation function (EV), require approval and an update to this document. All code deployments must undergo an audit regarding operation vectorization and strict adherence to cloud independence.

**Version**: 1.0.1 | **Ratified**: 2026-06-11 | **Last Amended**: 2026-06-11
