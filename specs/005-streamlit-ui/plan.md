# Implementation Plan: Streamlit UI

**Branch**: `005-streamlit-ui` | **Date**: 2026-06-11 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/005-streamlit-ui/spec.md`

## Summary

Build a lightweight local presentation layer using Streamlit (`app.py`). The application will provide a large Text Area for pasting multiline bookmaker odds, trigger the existing data parsing (`src/data/parser.py`) and EV optimization (`src/model/optimizer.py`) backend pipeline, and render the recommended predictions in a clean, scannable Markdown/HTML table for easy manual entry.

## Technical Context

**Language/Version**: Python 3.11+

**Primary Dependencies**: Streamlit, pandas

**Storage**: SQLite (Matches/Odds historical storage integration if required by the data pipeline, otherwise stateless inference)

**Testing**: pytest (unit testing UI helper functions) and Streamlit AppTest framework

**Target Platform**: Local execution (Windows)

**Project Type**: Local Web Application (Streamlit)

**Performance Goals**: UI responsive in <3 seconds, parsing and optimization pipelines execute synchronously without freezing the browser.

**Constraints**: 100% Local Execution (No external API calls), fully vectorized processing in the backend.

**Scale/Scope**: ~20 matches processed in a single batch pasting action.

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **I. 100% Local Execution**: Passes. Streamlit runs entirely on the local workstation on `localhost`.
- **II. EV-Centric Decision Making**: Passes. The UI directly triggers the EV optimizer and highlights its recommendations.
- **III. Multi-Bookmaker Consensus**: Passes. The UI relies on the backend parsers which handle this.
- **IV. Vectorized Computation**: Passes. The UI is just a presentation layer for the vectorized backend.
- **V. Interactive Streamlit UI & SQLite Storage**: Passes. This feature explicitly satisfies the Streamlit UI mandate.

## Project Structure

### Documentation (this feature)

```text
specs/005-streamlit-ui/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── quickstart.md        # Phase 1 output
```

### Source Code (repository root)

```text
app.py                   # Main Streamlit application entry point

src/
├── data/
│   └── parser.py        # Existing parsers
├── model/
│   └── optimizer.py     # Existing EV engine
└── ui/                  # New UI module for helper functions (optional)
    └── components.py    # Reusable Streamlit render functions

tests/
└── ui/
    └── test_app.py      # Streamlit AppTest coverage
```

**Structure Decision**: A root-level `app.py` will serve as the Streamlit entry point to allow simple execution via `streamlit run app.py`. Any complex rendering logic can be encapsulated in `src/ui/` to keep the main script clean.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

No violations.
