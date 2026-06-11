# Feature Specification: Data Ingestion and Local Storage

**Feature Branch**: `001-data-ingestion-and-sqlite`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "I want to build a data parsing module (Data Ingestion) and a local SQLite database in accordance with CONSTITUTION.md. The module must use multi-line regular expressions (Regex) to extract team names and odds from multiple bookmakers from the pasted text. It must then calculate implied probabilities, adjust them for the margin using the proportional method, and determine the average market consensus. The SQLite database is to store matches, statistics, and generated parameters."

## Clarifications

### Session 2026-06-11
- Q: How should the system handle team name unification to aggregate odds correctly? → A: Strict exact matching
- Q: Should the local database store every individual bookmaker's raw odds for a match, or just the final calculated Consensus probabilities? → A: Store all individual bookmaker odds AND the consensus
- Q: If the text contains multiple odds lines for the same bookmaker for a single match, how should the system handle it? → A: Use the last occurrence and ignore previous ones

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Parse and Consolidate Odds (Priority: P1)

Users paste a block of raw, multi-line text containing odds from various bookmakers into the system. The system processes this text and displays the averaged, margin-adjusted market consensus probabilities for the match.

**Why this priority**: Parsing odds and calculating the pure consensus probabilities is the foundational step required before any EV optimization or predictions can be made.

**Independent Test**: Can be fully tested by pasting a sample block of text containing odds from 3 different bookmakers and verifying that the output consensus probabilities are correct and sum to 100%.

**Acceptance Scenarios**:

1. **Given** a valid block of text with bookmaker odds, **When** the user submits the text, **Then** the system extracts the odds, removes the margin proportionally, and outputs the average consensus probability.
2. **Given** text with some malformed lines alongside valid ones, **When** the text is submitted, **Then** the system ignores the malformed lines and calculates the consensus based on the valid bookmaker data.

---

### User Story 2 - Store Match Data (Priority: P2)

Users can save the processed match data, including the consensus probabilities and calculated statistics, into a local database.

**Why this priority**: Storing data allows the system to build a historical dataset necessary for later generating parameters (like attack/defense strengths) for the probabilistic model.

**Independent Test**: Can be fully tested by triggering a save operation for a parsed match and then retrieving the exact same match data from the local database.

**Acceptance Scenarios**:

1. **Given** a successfully parsed match with consensus probabilities, **When** the system saves the record, **Then** the data is securely persisted in the local database.
2. **Given** an attempt to save a match that already exists in the database for the same teams and date, **When** the system saves the record, **Then** it updates the existing entry rather than creating a duplicate.

## Edge Cases

- What happens when the pasted text contains odds for outcomes other than Home, Draw, Away (e.g., Over/Under)?
- **Duplicate Bookmakers**: If the same bookmaker appears multiple times for a single match, the system MUST use the last occurrence and ignore any previous ones.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST extract team names and 3-way odds (Home, Draw, Away) from multi-line text using text pattern matching, enforcing strict exact matching of team names across bookmakers to aggregate their odds.
- **FR-002**: System MUST calculate implied probabilities from the extracted odds.
- **FR-003**: System MUST remove the bookmaker margin (overround) from the implied probabilities using the proportional method.
- **FR-004**: System MUST calculate the arithmetic mean of the pure probabilities across all detected bookmakers to form the market consensus.
- **FR-005**: System MUST store extracted match data, every individual bookmaker's raw odds, consensus probabilities, and associated statistics in a local database.
- **FR-006**: System MUST gracefully ignore lines in the pasted text that do not match the expected odds format without failing the entire parsing process.
- **FR-007**: System MUST provide a mechanism to query previously saved matches and their parameters from the database.

### Key Entities

- **MatchOdds**: Represents raw odds extracted from a single bookmaker (Home odds, Draw odds, Away odds).
- **Consensus**: Represents the aggregated, margin-free probabilities (P_home, P_draw, P_away) for a specific match.
- **MatchRecord**: Represents a database entry containing team names, match date, all associated individual bookmaker odds, the consensus probabilities, and generated model parameters.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Text containing odds from at least 10 different bookmakers is parsed and consolidated in under 1 second.
- **SC-002**: Margin removal calculations reliably produce pure probabilities that sum to exactly 1.0 (100%) across the Home/Draw/Away outcomes for every parsed bookmaker.
- **SC-003**: 100% of successfully parsed matches can be saved to and retrieved from the local database without data loss or corruption.
- **SC-004**: System correctly ignores 100% of invalid text lines (e.g., ads, blank lines) intermixed with valid odds data without throwing errors.

## Assumptions

- The pasted text contains a recognizable and relatively consistent pattern for odds that can be targeted by text pattern matching.
- All inputted matches involve standard 3-way outcomes (Home Win, Draw, Away Win).
- The local database is a single file managed by the system, requiring no separate database server installation or credentials by the user.
- The proportional method is mathematically sufficient for margin distribution.
