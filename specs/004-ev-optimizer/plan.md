# Implementation Plan: Expected Value Decision Engine

**Branch**: `004-ev-optimizer` | **Date**: 2026-06-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/004-ev-optimizer/spec.md`

## Summary

Implement a mathematical Expected Value (EV) Decision Engine utilizing vectorized operations (NumPy). It will take a 2D probability matrix (Phase 2 output), dynamically build a corresponding point-reward matrix based on the competition's non-linear scoring rules (5 for exact score, 3 for goal difference, 1 for outcome), compute EV for all possible outcomes, and recommend the exact scoreline (from 0-0 to 5-5) that maximizes the Expected Value. Tie-breaking logic will prefer the scoreline with the highest absolute baseline probability.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: NumPy (for vectorized cross-multiplication)

**Storage**: N/A (Stateless mathematical engine)

**Testing**: pytest

**Target Platform**: Local execution (Workstation)

**Project Type**: Python core library / simulation component

**Performance Goals**: <5ms per matrix calculation

**Constraints**: Must strictly use vectorized computations (no Python loops for matrix evaluation), must be 100% local.

**Scale/Scope**: Matrix size dynamically adapting (e.g. 6x6 to 10x10). Computations done efficiently to support tournament scales.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. 100% Local Execution**: Passes. Operations are strictly local NumPy processing.
- **II. EV-Centric Decision Making (EV Maximization)**: Passes. This feature explicitly implements this principle.
- **III. Multi-Bookmaker Consensus & Overround Correction**: N/A (Handled upstream).
- **IV. Vectorized Computation**: Passes. The engine uses NumPy matrix broadcasting.
- **V. Interactive Streamlit UI & SQLite Storage**: N/A for this backend logic component.

## Project Structure

### Documentation (this feature)

```text
specs/004-ev-optimizer/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output
```

### Source Code (repository root)

```text
src/
└── model/
    ├── optimizer.py         # Core EV decision logic
    └── scoring.py           # (Optional) Separated scoring rule definitions

tests/
└── model/
    └── test_optimizer.py    # Unit tests covering EV logic and ties
```

**Structure Decision**: The EV Engine will reside in `src/model/optimizer.py`, parallel to `simulation.py`, as it serves as the mathematical recommendation engine acting upon the simulation/model probabilities.
