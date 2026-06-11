# Phase 0: Research & Architecture Decisions

## Vectorization of the 2026 World Cup Simulation

- **Decision**: Represent the simulation state as large 3D/2D NumPy arrays `(10000_runs, n_matches)` and compute the entire group stage mathematically using matrix operations (grouping by `reshape` and using `np.argsort` for standings).
- **Rationale**: Strict performance requirements (< 5 seconds for 10,000 runs) and the project's vectorization constraint mandate the avoidance of Python loops across runs. Pandas will be used for final aggregation of the 10,000 runs into exact probabilities.
- **Alternatives considered**:
  - *Standard looping in Python*: Rejected due to severe performance degradation (would likely take >30s for 10,000 full runs).
  - *Numba/Cython/Rust extensions*: Rejected as they introduce unnecessary complexity. Pure NumPy vectorization is sufficient for this scale.

## 3rd-Place Team Advancement Logic

- **Decision**: Pre-compute a static lookup table that maps the 15 possible combinations of advancing 3rd-place teams (from 12 groups) to their knockout bracket slots. During simulation, vectorized boolean masks will select the correct matchups from this lookup table.
- **Rationale**: The official 2026 World Cup uses a complex assignment table based on which specific groups the best 3rd-place teams come from. A vectorized lookup is the fastest way to route these teams without loops.
- **Alternatives considered**: Iterative conditional logic in a loop (rejected due to vectorization constraint).

## Knockout Stage Tie-Breaker (50/50 Stochastic Resolution)

- **Decision**: If a knockout match ends in a draw, sample from a uniform binomial distribution `np.random.randint(0, 2, size=num_ties)` to pick the advancing team.
- **Rationale**: It perfectly models a penalty shootout where both teams have roughly equal chances (50/50), aligning with Option A from the specification.

## Goal Concentration Index (GCI) Calculation

- **Decision**: Use the Herfindahl-Hirschman Index (HHI) calculated across matches. For a team in a single run: `sum(goals_in_match^2) / (total_goals^2)`. This will be computed efficiently over the 2D arrays.
- **Rationale**: Selected as the standard approach in the specification (Option A) to measure variance and concentration of goals.
