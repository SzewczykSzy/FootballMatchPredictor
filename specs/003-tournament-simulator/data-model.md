# Data Model: Vectorized Tournament Simulator

The simulation is executed fully in-memory using vectorized NumPy arrays and Pandas DataFrames. There is no new persistent schema added to SQLite, but the shapes and structures of the matrices are strictly defined here.

## Core In-Memory Entities

### 1. Match Configuration Matrix
- **Shape**: `(72, 4)` for the Group Stage (72 matches).
- **Columns**: `[home_team_id, away_team_id, alpha_home, beta_home, alpha_away, beta_away]`.
- **Purpose**: Feeds into the Dixon-Coles random sample generator.

### 2. Simulation Results Tensor
- **Shape**: `(10000, 72, 2)` for Group Stage.
- **Dimensions**: Runs $\times$ Matches $\times$ (Home Goals, Away Goals).
- **Purpose**: Stores the stochastically sampled goals for every match in every simulation run.

### 3. Group Standings Tensor
- **Shape**: `(10000, 12, 4, 4)`
- **Dimensions**: Runs $\times$ Groups $\times$ Teams $\times$ (Points, Goal Diff, Goals Scored, Random Tiebreaker).
- **Purpose**: Used to `np.lexsort` teams within their groups across all 10,000 runs simultaneously.

### 4. Aggregated Team Probabilities (Output)
A Pandas DataFrame presented to the user at the end of the simulation.
- **Index**: `team_id` / `team_name`
- **Columns**:
  - `p_group_winner`: Float (0.0 to 1.0)
  - `p_advance`: Float (0.0 to 1.0)
  - `p_r16`: Float (0.0 to 1.0)
  - `p_qf`: Float (0.0 to 1.0)
  - `p_sf`: Float (0.0 to 1.0)
  - `p_final`: Float (0.0 to 1.0)
  - `p_champion`: Float (0.0 to 1.0)
  - `avg_gci`: Float (Herfindahl-Hirschman Index representing goal concentration)

## External Dependencies (Read-Only)

- **Database**: `matches.db`
- **Tables**:
  - `teams` (Provides `alpha`, `beta`, `rho` parameters)
  - `groups` (Provides the 12 World Cup group configurations)
  - `matches` (Used to configure the schedule)

## State Transitions
1. **Init**: Load parameters from SQLite and initialize empty tensors.
2. **Phase 1 (Group)**: Sample 72 matches $\rightarrow$ Calculate Points $\rightarrow$ Sort Groups $\rightarrow$ Identify 24 direct advancers + 8 best 3rd-place teams.
3. **Phase 2 (Knockout)**: Route teams through the deterministic lookup table $\rightarrow$ Sample R32 $\rightarrow$ Resolve ties $\rightarrow$ Sample R16 $\rightarrow$ ... $\rightarrow$ Final.
4. **Phase 3 (Aggregate)**: Flatten tensors into Pandas DataFrame $\rightarrow$ Compute means $\rightarrow$ Output.
