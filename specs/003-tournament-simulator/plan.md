# Implementation Plan: Vectorized Tournament Simulator

**Branch**: `003-monte-carlo-simulation` | **Date**: 2026-06-11 | **Spec**: [specs/003-tournament-simulator/spec.md](file:///C:/Users/szyme/Documents/Coding/Projects/FootbalMatchPredictor/specs/003-tournament-simulator/spec.md)

**Input**: Feature specification from `specs/003-tournament-simulator/spec.md`

## Summary

Build a 100% vectorized Monte Carlo tournament simulator using NumPy and Pandas to simulate the 2026 World Cup 10,000 times in under 5 seconds. The simulator will load parameters from the local SQLite database, resolve group stages and knockout brackets (including 3rd-place advancement logic and 50/50 tie-breakers), compute goal concentration indexes (GCI), and expose a CLI tool to output probabilities for long-term questions.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: NumPy, Pandas, sqlite3

**Storage**: SQLite (`matches.db`) for reading parameters. Results computed on-the-fly (in-memory only).

**Testing**: pytest

**Target Platform**: Local Workstation

**Project Type**: Backend Simulation Engine & CLI

**Performance Goals**: < 5 seconds for 10,000 full tournament simulations.

**Constraints**: 100% vectorized computation (no Python loops over simulation runs), 100% local execution.

**Scale/Scope**: 48 teams, 12 groups, 32-team knockout bracket, 10,000 stochastic runs per batch.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. 100% Local Execution**: Pass. All calculations occur locally; SQLite is used for reads.
- **II. EV-Centric Decision Making**: Pass. Accurate probability distributions generated here serve as the foundation for EV maximization.
- **IV. Vectorized Computation**: Pass. Strict constraint to use NumPy/Pandas for all 10,000 runs without looping.
- **V. Interactive Streamlit UI & SQLite Storage**: Pass. Streamlit UI deferred; SQLite used exclusively for storage.

## Project Structure

### Documentation (this feature)

```text
specs/003-tournament-simulator/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
    └── cli_contract.md
```

### Source Code (repository root)

```text
src/
├── model/
│   ├── simulation.py       # Core vectorized tournament simulation logic
│   └── bracket.py          # Deterministic 3rd-place to knockout mapping
├── cli/
│   └── simulate.py         # CLI entry point to run simulations
```

**Structure Decision**: The project uses a single Python package structure. Simulation logic is placed in `src/model/` where the Dixon-Coles model resides, and the CLI tool is placed in `src/cli/`.

## Complexity Tracking

No violations.
