# Feature Specification: Dixon-Coles Probabilistic Prediction Engine

**Feature Branch**: `002-dixon-coles-model`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "Implement the core probabilistic soccer prediction engine based on a modified Dixon-Coles model to account for low-score dependencies (0-0, 1-0, etc.). The module must estimate time-weighted attack parameters (alpha) and defense parameters (beta) for all 48 national teams using past historical matches. Use SciPy's 'scipy.optimize' module to perform local Maximum Likelihood Estimation (MLE) parameter fitting. Combine these parameters with the bookmaker consensus prior from Phase 1 to output a full, discrete 2D probability matrix (up to 6x6 goals) for any given match."

## Clarifications

### Session 2026-06-11
- Q: What half-life should be applied to the exponential time-weighting function for historical matches? → A: Standard Dixon-Coles decay (~18 months / exponential decay $e^{-0.0065 \times \text{days}}$).
- Q: If the MLE optimization fails to converge for a specific dataset, how should the system safely handle the failure? → A: Retry optimization automatically with relaxed convergence tolerances before failing.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Model Parameter Estimation (Priority: P1)

Users initialize the prediction engine to process historical match data for all 48 national teams, producing time-weighted attack and defense strengths for each team.

**Why this priority**: Accurate estimation of attack ($\alpha$) and defense ($\beta$) parameters is the mathematical foundation required before any specific match probabilities can be generated.

**Independent Test**: Can be fully tested by running the parameter estimation on a mock dataset of historical matches and verifying that the solver converges to produce sensible attack and defense values for all participating teams.

**Acceptance Scenarios**:

1. **Given** a dataset of historical matches involving the 48 teams, **When** the system runs the parameter fitting process, **Then** it calculates and outputs time-weighted attack and defense strengths for each team.
2. **Given** the optimization process, **When** calculating parameters, **Then** the modified Dixon-Coles approach correctly applies dependencies for low-score outcomes (like 0-0 or 1-0) to prevent underestimation of draws.

---

### User Story 2 - Match Probability Generation (Priority: P2)

Users select a specific upcoming match (Home vs Away) to analyze. The system takes the previously estimated team parameters, combines them with the bookmaker consensus from Phase 1, and generates a discrete 2D probability matrix for all possible exact scores up to 6x6 goals.

**Why this priority**: Translating the parameters and priors into an actionable probability matrix is the core output required for Expected Value (EV) calculation in later stages.

**Independent Test**: Can be fully tested by providing mock attack/defense parameters and a mock consensus prior, then verifying that the output is a valid 6x6 discrete probability distribution matrix summing to exactly 1.0.

**Acceptance Scenarios**:

1. **Given** estimated attack/defense parameters and a parsed bookmaker consensus, **When** predicting a specific match, **Then** the system outputs a 2D matrix representing exact score probabilities (e.g., P(1-0), P(2-2)) capped at a maximum of 6 goals per team.
2. **Given** the 2D probability matrix, **When** evaluated, **Then** the sum of all cell probabilities must equal 1.0 (100%).

### Edge Cases

- **Optimization failure fallback**: If MLE fails to converge initially, the system automatically retries with relaxed convergence tolerances before throwing an exception.
- How does the system handle a match where one or both teams lack sufficient historical data to securely fit parameters?
- What occurs when the bookmaker consensus prior conflicts drastically with the historically fitted parameters?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST process historical match data for 48 national teams to estimate time-weighted attack ($\alpha$) and defense ($\beta$) parameters.
- **FR-002**: System MUST apply a modified Dixon-Coles model to correctly adjust probability distributions for low-score dependencies (e.g., 0-0, 1-0, 0-1, 1-1).
- **FR-003**: System MUST execute parameter fitting 100% locally using Maximum Likelihood Estimation (MLE).
- **FR-004**: System MUST combine calculated team parameters with the parsed bookmaker consensus (from Phase 1) to inform final match probabilities.
- **FR-005**: System MUST output a 2D probability matrix of exact match scores ranging from 0-0 up to 6-6 goals for any specified match.
- **FR-006**: System MUST ensure that the sum of all probabilities in the 6x6 matrix exactly equals 1.0.

### Key Entities

- **HistoricalMatch**: Represents a past match with scoreline and date, used for time-weighted MLE fitting.
- **TeamParameters**: Represents the estimated attack ($\alpha$) and defense ($\beta$) strengths for a specific national team.
- **ScoreMatrix**: A 2D discrete probability distribution representing the likelihood of exact scorelines (e.g., 2-1) for a specific match.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Parameter estimation (MLE) for all 48 teams completes in under 30 seconds on local hardware.
- **SC-002**: The modified Dixon-Coles model produces a 6x6 score probability matrix for a match in under 500 milliseconds.
- **SC-003**: 100% of generated 2D probability matrices sum to exactly 1.0 (within standard floating point epsilon tolerance).
- **SC-004**: System runs entirely offline with zero external network requests during parameter fitting and matrix generation.

## Assumptions

- A sufficient volume of historical match data is available locally to achieve MLE convergence for all 48 teams.
- "Time-weighted" is defined as using the standard Dixon-Coles exponential decay function (approx. 18-month half-life, $e^{-0.0065 \times \text{days}}$).
- Matches where teams score more than 6 goals are statistically rare enough to be safely grouped into the 6+ bucket or ignored, allowing the matrix to be capped at 6x6.
