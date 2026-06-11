# Feature Specification: Expected Value Decision Engine

**Feature Branch**: `004-ev-optimizer`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "Develop the Expected Value (EV) Decision Engine based on the non-linear scoring rules of the competition. The script must take the 2D probability matrix from Phase 2 and cross-multiply it against a static 2D matrix representing the point-reward matrix (5 points for exact score/draw, 3 points for exact goal difference, 1 point for correct outcome tendency, 0 points otherwise). The engine must iterate through all plausible prediction pairs (U, V) from 0-0 to 5-5 and recommend the exact scoreline that maximizes the mathematical Expected Value, rather than just selecting the highest single-outcome probability."

## Clarifications

### Session 2026-06-11
- Q: How should the engine resolve exact ties if multiple scorelines yield the identical maximum Expected Value? → A: Break ties by selecting the scoreline with the highest single-outcome probability
- Q: If the input probability matrix exceeds 6x6 (e.g., 8x8), how should the engine construct the EV calculation scope? → A: Dynamically size point-reward matrix to input dimensions, capturing all probability mass for EV computation (restrict recommendations to 0-0 to 5-5)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Recommend Prediction for a Given Match (Priority: P1)

As a tournament participant, I want the system to recommend an exact scoreline prediction based on expected tournament points, so that I can maximize my score in the competition over the long term.

**Why this priority**: The core purpose of the system is to provide mathematical advantages in predictions. Recommending the highest EV prediction is fundamental to achieving this goal based on the non-linear point system.

**Independent Test**: Can be fully tested by providing a known probability matrix and verifying that the recommended prediction correctly maximizes the 5/3/1/0 point reward structure.

**Acceptance Scenarios**:

1. **Given** a match's 2D probability matrix with a clear heavy favorite but high variance, **When** the EV Decision Engine is invoked, **Then** it recommends a prediction that mathematically maximizes expected points, even if it differs from the absolute highest single-cell probability.
2. **Given** an evenly matched game with a high probability of a draw, **When** the EV Decision Engine is invoked, **Then** it correctly considers the 5 points for an exact score and outputs the optimal prediction.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST accept a 2D probability matrix (e.g., from the Dixon-Coles model) representing the likelihood of various scorelines (home goals vs. away goals).
- **FR-002**: System MUST define a scoring rule representation where: Exact Score = 5 points, Exact Goal Difference = 3 points, Correct Outcome (Win/Loss/Draw) = 1 point, Incorrect Outcome = 0 points.
- **FR-003**: System MUST iterate through all plausible score prediction combinations `(U, V)` from 0-0 up to 5-5.
- **FR-004**: System MUST calculate the mathematical Expected Value (EV) for each candidate prediction `(U, V)` by cross-multiplying the candidate's point rewards against the true 2D probability matrix. The point-reward matrix MUST be dynamically sized to match the exact dimensions of the input probability matrix to capture all probability mass in the EV computation.
- **FR-005**: System MUST select and recommend the exact scoreline `(U, V)` that yields the highest Expected Value.
- **FR-006**: System MUST utilize vectorized computations (e.g., NumPy) to perform the EV matrix calculations efficiently, conforming to the project Constitution Principle IV.
- **FR-007**: In the event of exact Expected Value ties between multiple candidate scorelines, the system MUST recommend the tied scoreline that possesses the highest single-outcome probability.

### Key Entities *(include if feature involves data)*

- **Probability Matrix**: A 2D array where cell `(i, j)` represents the probability of the home team scoring `i` goals and the away team scoring `j` goals.
- **Point-Reward Matrix**: A 2D array for a specific candidate prediction `(U, V)` that maps out how many points would be awarded for every possible actual match outcome `(i, j)`.
- **Expected Value**: A scalar value representing the sum of `(Probability of Outcome * Points for Outcome)` across all possible outcomes for a given prediction.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: The engine identifies the highest EV score prediction in 100% of test cases compared to manual/brute-force validation.
- **SC-002**: The engine processes the EV calculation for a single match probability matrix in under 5 milliseconds, ensuring it can scale to entire tournament rounds without lag.
- **SC-003**: The engine successfully iterates over the standard domain of scores (0-0 to 5-5) as candidate predictions.

## Assumptions

- Plausible prediction pairs `(U, V)` up to 5-5 (6x6 matrix domain) are sufficient to capture the vast majority of football matches and maximize EV.
- The 2D probability matrix passed to the engine is already normalized and accounts for overround and other necessary prior adjustments.
- The scoring rules (5, 3, 1, 0) are static for this competition.
