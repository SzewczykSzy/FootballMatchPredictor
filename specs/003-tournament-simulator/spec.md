# Feature Specification: Vectorized Tournament Simulator

**Feature Branch**: `003-monte-carlo-simulation`

**Created**: 2026-06-11

**Status**: Draft

**Input**: User description: "Create a 100% vectorized tournament simulator using NumPy and Pandas to address long-term tournament questions (Champion, Finalists, Group Winners). Fully map the official 2026 World Cup structure: 12 groups of 4 teams, top 2 teams + 8 best 3rd-placed teams advancing, followed by a knockout bracket starting from the Round of 32. Run 10,000 stochastic simulations per batch by sampling match outcomes from the Phase 2 Poisson distributions. Aggregate results to determine exact probabilities for long-term questions, including team goal-concentration indexes for top scorer predictions."

## Clarifications

### Session 2026-06-11
- Q: Does this feature include creating a Streamlit UI page to visualize the simulation results, or should it focus exclusively on building the backend simulation engine and CLI tool for now? → A: Backend and CLI only (Defer Streamlit UI to a future feature)
- Q: Should the aggregated simulation results (team probabilities, GCI) be permanently saved to the SQLite database, or computed on-the-fly and kept in memory? → A: Compute on-the-fly (In-memory only, re-run simulation when needed by CLI or future UI)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Group Stage Simulation (Priority: P1) 🎯 MVP

Users run the simulator on the 12 groups of 4 teams to determine which teams are most likely to win their group, finish in the top 2, or advance as one of the 8 best 3rd-placed teams.

**Why this priority**: Simulating the group stage and executing the advancement logic is the mathematical foundation of the entire tournament simulator. Without group stage sorting, no knockout bracket can be constructed.

**Independent Test**: Can be fully tested by running the group stage simulator on a mock set of 12 groups with fixed team parameters, verifying that:
1. Each group is correctly simulated (6 matches per group, 72 matches total per run).
2. Group standings are calculated using points, goal difference, and goals scored.
3. Exactly 24 teams (top 2 from each group) plus the 8 best 3rd-placed teams advance.

**Acceptance Scenarios**:

1. **Given** 12 groups of 4 teams and their attack/defense strengths, **When** the group stage is simulated 10,000 times, **Then** the system outputs a probability table for each team's finish position (1st, 2nd, 3rd, 4th) and their likelihood of advancing.
2. **Given** the 3rd-place team rankings across all 12 groups, **When** selecting the best 8 teams to advance, **Then** the tie-breakers (points, goal difference, goals scored) are applied stochastically/vectorized to rank the 12 teams.

---

### User Story 2 - Knockout Stage & Champion Prediction (Priority: P2)

Users predict the exact probabilities of each team reaching successive rounds (Round of 16, Quarter-finals, Semi-finals, Final) and winning the tournament.

**Why this priority**: Predicting the final champion and bracket progression is the primary end-user value for long-term tournament wagering and sweepstakes.

**Independent Test**: Can be tested by feeding a list of 32 advancing teams into the knockout simulator and verifying that:
1. The bracket matches the standard 2026 World Cup Round of 32 progression.
2. Knockout matches result in exactly one team advancing per match.
3. The final aggregated probability of all teams winning the championship sums to exactly 1.0 (100%).

**Acceptance Scenarios**:

1. **Given** the 32 qualified teams from the group stage, **When** the knockout bracket is simulated 10,000 times, **Then** the system outputs the percentage of runs in which each team reaches the Round of 16, Quarter-finals, Semi-finals, Final, and wins the Championship.
2. **Given** a draw in a knockout match after 90 minutes, **When** resolving the tie, **Then** the system stochastically decides which team advances using the defined tie-breaker logic.

---

### User Story 3 - Goal Concentration Indexing (Priority: P3)

Users analyze the distribution of goals scored by each team to determine which teams are most likely to produce the tournament's top goalscorer.

**Why this priority**: Top scorer markets are highly popular but depend heavily on goal concentration (e.g., a player scoring a hat-trick in a high-yield match vs. goals distributed across many players/matches).

**Independent Test**: Can be tested by running the simulation and verifying that a Goal Concentration Index (GCI) is calculated for each team, with teams scoring in bursts showing higher concentration indexes than teams scoring consistently but in low volumes.

**Acceptance Scenarios**:

1. **Given** the goals scored by each team across all simulated matches in a tournament run, **When** the simulation completes, **Then** the system outputs the average Goal Concentration Index (GCI) for each of the 48 teams.

---

### Edge Cases

- **Ties in Group Stage Standing**: If two or more teams finish with identical points, goal difference, and goals scored in the group stage, the system stochastically breaks the tie using a random draw (50/50 or equal chance).
- **Ties in 3rd-Place Team Rankings**: If multiple 3rd-place teams have identical group stats, the system stochastically ranks them.
- **Knockout Bracket Matchups**: The system must correctly map the complex official 2026 World Cup Round of 32 matchup structure (allocating the 8 best 3rd-placed teams to specific group winners based on which groups they advance from).

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST simulate a full 2026 World Cup tournament structure containing 12 groups of 4 teams.
- **FR-002**: System MUST run stochastic tournament simulations in batches of 10,000 runs, where each match score is sampled stochastically from the Dixon-Coles Poisson joint probability distribution.
- **FR-003**: System MUST execute the simulation in a 100% vectorized manner using NumPy and Pandas (no nested Python loops over simulation runs).
- **FR-004**: System MUST apply group stage ranking rules: 3 points for a win, 1 point for a draw, 0 points for a loss. Tie-breakers must follow the hierarchy: (1) points, (2) goal difference, (3) goals scored, (4) random draw.
- **FR-005**: System MUST identify the 8 best 3rd-placed teams across the 12 groups based on their group stage statistics to fill the remaining Round of 32 slots.
- **FR-006**: System MUST simulate the knockout bracket from the Round of 32, Round of 16, Quarter-finals, Semi-finals, to the Final, resolving draws stochastically according to a 50/50 coin flip representing a standard penalty shoot-out where team strengths are balanced.
- **FR-007**: System MUST calculate and output the Goal Concentration Index (GCI) for each team stochastically, calculated using the Herfindahl-Hirschman Index (HHI) of goals scored across all matches played by a team in a simulation run (calculated as the sum of squared goals divided by the square of total goals scored).
- **FR-008**: System MUST run entirely offline, loading team parameters and configs from the local SQLite database.
- **FR-009**: System MUST expose the simulator via a CLI tool that outputs aggregated results to the console (Streamlit UI integration is explicitly out of scope for this feature branch).
- **FR-010**: System MUST NOT persist the aggregated simulation results to the SQLite database; results must be computed on-the-fly and kept in memory during execution.

### Key Entities

- **TournamentSimulationBatch**: Represents a batch of 10,000 stochastically simulated tournaments.
- **GroupStandings**: Represents the final calculated standings (points, goal difference, goals scored) for a group in a single simulation run.
- **KnockoutBracket**: Represents the structured progression of the 32 advancing teams through the single-elimination rounds.
- **TeamSimulationStats**: Represents the aggregated outcomes for a team across all 10,000 runs (probabilities of winning group, advancing, reaching each round, and their average GCI).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Running a batch of 10,000 full tournament simulations (group stage + knockout bracket) MUST complete in under 5 seconds on local hardware.
- **SC-002**: The sum of championship probabilities across all 48 teams MUST equal exactly 1.0 (100%) within floating-point tolerance.
- **SC-003**: The simulator MUST run 100% locally with no network calls.
- **SC-004**: All group stage and 3rd-place rankings MUST resolve without manual intervention, even in the event of identical statistics.

## Assumptions

- **Neutral Ground**: All matches in the tournament are assumed to be played on neutral ground, so the home advantage parameter $\gamma$ is set to 1.0 (no home advantage) for all match score calculations.
- **Poisson Capping**: Goal counts in simulated matches are sampled from the 6x6 joint probability matrix (capped at 5 goals per team) to align with Phase 2 capabilities.
- **Knockout Bracket Mapping**: A simplified official 2026 World Cup bracket mapping will be used to assign the 8 best 3rd-placed teams to their knockout opponents, using a deterministic lookup table.


