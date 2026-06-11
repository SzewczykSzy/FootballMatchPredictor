# Implementation Plan: Data Ingestion and Local Storage

**Branch**: `001-data-ingestion-and-sqlite` | **Date**: 2026-06-11 | **Spec**: [specs/001-data-ingestion-and-sqlite/spec.md](spec.md)

**Input**: Feature specification from `specs/001-data-ingestion-and-sqlite/spec.md`

## Summary

Build a data parsing module using text pattern matching to extract 1X2 odds from multi-line text, apply the proportional margin method to find the market consensus, and persist both raw and consensus data to a local SQLite database.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: `sqlite3` (built-in), `re` (built-in)

**Storage**: SQLite (`matches.db`)

**Testing**: `pytest`

**Target Platform**: Local Windows execution

**Project Type**: Library / Data Pipeline module

**Performance Goals**: Parse odds from at least 10 bookmakers in < 1 second

**Constraints**: 100% offline, zero cloud dependencies

**Scale/Scope**: Historical and live match storage (est. 10,000+ records)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- [x] **100% Local Execution**: Data ingestion relies purely on pasted text and local regex matching. No external API calls are made. Storage is handled via local SQLite.
- [x] **Maximizing EV**: This module forms the foundation of EV by determining the true probability (market consensus) via the proportional margin removal method.
- [x] **Tech Stack Alignment**: Uses Python, standard libraries (`re`, `sqlite3`), and vectorized/efficient patterns where applicable.

## Project Structure

### Documentation (this feature)

```text
specs/001-data-ingestion-and-sqlite/
├── plan.md              # This file
├── research.md          # Parsing and math strategies
├── data-model.md        # Database schema and entities
├── quickstart.md        # Developer setup and execution
├── contracts/           # Database schema SQL files
└── tasks.md             # To be created later
```

### Source Code (repository root)

```text
src/
├── data/
│   ├── __init__.py
│   ├── parser.py        # Text pattern matching logic
│   ├── math_utils.py    # Proportional margin removal
│   └── database.py      # SQLite operations and context managers
tests/
└── data/
    └── test_ingestion.py
```

**Structure Decision**: A modular Python package structure (`src/data`) isolating the parsing logic, mathematical operations, and storage mechanism, keeping them independently testable.
