# Implementation Plan: Dixon-Coles Probabilistic Prediction Engine

**Branch**: `002-dixon-coles-model` | **Date**: 2026-06-11 | **Spec**: [specs/002-dixon-coles-model/spec.md](spec.md)

**Input**: Feature specification from `specs/002-dixon-coles-model/spec.md`

## Summary

Implement a local MLE parameter fitting engine using `scipy.optimize` to calculate time-weighted attack and defense strengths for 48 national teams. Additionally, generate a 6x6 discrete probability score matrix incorporating a low-score dependency adjustment ($\tau$).

## Technical Context

**Language/Version**: Python 3.x

**Primary Dependencies**: `scipy` (for optimize), `numpy` (for vectorized math/matrices), `sqlite3`

**Storage**: SQLite (storing calculated team parameters)

**Testing**: `pytest`

**Target Platform**: Local execution (Windows/Linux/Mac)

**Project Type**: Backend Python module

**Performance Goals**: Parameter estimation < 30 seconds, Matrix generation < 500 ms.

**Constraints**: 100% offline, must sum to 1.0, 6x6 capping, fallback for convergence failure.

**Scale/Scope**: 48 national teams, historical match database

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **100% Local Execution**: PASS - All processing done locally via SciPy.
- **EV-Centric Decision Making**: PASS - Matrix generation is the foundation for EV.
- **Multi-Bookmaker Consensus & Overround Correction**: PASS - Engine uses the consensus prior.
- **Vectorized Computation**: PASS - Heavy reliance on `numpy` and `scipy`.
- **Interactive Streamlit UI & SQLite Storage**: PASS - Model parameters will be persisted in SQLite.

## Project Structure

### Documentation (this feature)

```text
specs/002-dixon-coles-model/
├── plan.md              # This file
├── research.md          # Math formulation choices
├── data-model.md        # Entities and Schema additions
├── quickstart.md        # How to run parameter fitting
└── contracts/           # API and data classes
```

### Source Code (repository root)

```text
src/
├── model/
│   ├── dixon_coles.py    # MLE optimization and tau adjustment logic
│   ├── matrix.py         # 2D Probability matrix generation
│   └── parameters.py     # SQLite persistence for alpha/beta parameters
tests/
├── model/
│   ├── test_dixon_coles.py
│   └── test_matrix.py
```

**Structure Decision**: Added a new `model/` package in `src/` to separate the statistical modeling from the purely data ingestion/parsing logic developed in phase 1.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

(No violations)
