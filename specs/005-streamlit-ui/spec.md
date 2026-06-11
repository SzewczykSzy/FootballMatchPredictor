# Feature Specification: Streamlit UI

**Feature Branch**: `005-streamlit-ui`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "Build a lightweight, clean local presentation layer using the Streamlit framework, executable via 'streamlit run app.py'. The GUI must feature a large Text Area input field for pasting raw daily match listings and multi-line bookmaker odds. Upon hitting a 'Generate Predictions' button, the UI must trigger the underlying regex parsers, run the EV optimization matrices, and output a highly readable, scannable Markdown table displaying the recommended exact scores (U-V) alongside their calculated EV metrics for easy entry."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Paste Odds and Generate Predictions (Priority: P1)

As a tournament participant, I want to paste raw bookmaker odds into a simple web interface and instantly receive a formatted table of exact score predictions so that I can easily enter the optimal EV recommendations into the competition.

**Why this priority**: This is the primary and sole interaction flow for the daily prediction use case. Without this, the backend engine has no user-facing presentation layer.

**Independent Test**: Can be fully tested by launching the application, pasting a known sample of odds, clicking the button, and verifying that the output table renders the correct recommendations.

**Acceptance Scenarios**:

1. **Given** the application is running locally, **When** the user pastes valid multiline odds into the Text Area and clicks "Generate Predictions", **Then** the UI displays a clean Markdown table with match details, recommended exact scores, and EV metrics.
2. **Given** the application is running locally, **When** the user pastes invalid or unrecognized text into the Text Area and clicks "Generate Predictions", **Then** the UI displays a user-friendly error message indicating that the parsing failed.

### Edge Cases

- What happens when the user pastes odds for a massive number of matches (e.g., 50+)?
- How does the system handle an empty text area submission?
- What happens if the backend EV engine throws a calculation error or receives an incomplete probability matrix?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST provide a web-based presentation layer built with Streamlit, executable via the command `streamlit run app.py`.
- **FR-002**: System MUST display a prominent, large Text Area input component for users to paste raw, multi-line match listings and bookmaker odds.
- **FR-003**: System MUST feature a clear "Generate Predictions" action button to trigger the backend processing workflow.
- **FR-004**: System MUST pass the raw text input to the underlying regex data parsers, trigger the probability matrices generation, and run the EV optimization engine upon button click.
- **FR-005**: System MUST output the final recommended predictions in a highly readable, scannable tabular format (Markdown/HTML table).
- **FR-006**: System MUST display the match identifier, the recommended exact scoreline (e.g., 2-1), and the calculated EV metric for each processed match within the output table.
- **FR-007**: System MUST handle invalid inputs or backend parsing failures gracefully by presenting a user-friendly error message, avoiding application crashes or raw stack traces in the UI.

### Key Entities

- **Prediction Output**: The structured tabular data presented to the user containing the Match Identifier, Recommended Score, and Expected Value (EV).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The user interface launches successfully via `streamlit run app.py` and becomes interactive in under 3 seconds.
- **SC-002**: Users can successfully paste and process at least 20 match listings in a single batch without UI unresponsiveness.
- **SC-003**: 100% of successful processing runs output a visually aligned and formatted table that can be quickly scanned by the user for manual entry.
- **SC-004**: Error scenarios (empty input, unparseable text) result in clear error messages rather than raw Python exceptions in the UI.

## Assumptions

- Users are pasting data in a format compatible with the underlying regex parsers previously developed.
- The user operates the application on a local workstation, aligning with the 100% local execution project principle.
- The existing backend modules (regex parser, Dixon-Coles model, EV optimizer) expose synchronous Python functions that the Streamlit app can import and call directly.
