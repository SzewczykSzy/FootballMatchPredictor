# Phase 1: Data Model

**Feature**: Expected Value Decision Engine

## Core Data Structures

### 1. `ProbabilityMatrix`
- **Type**: 2D `numpy.ndarray`
- **Description**: An $M \times N$ matrix representing the probability of all possible match outcomes. `matrix[i, j]` represents the probability that the Home team scores $i$ goals and the Away team scores $j$ goals.
- **Constraints**: Sum of all elements in the matrix should equal $1.0$ (normalized).
- **Source**: Passed dynamically from the Phase 2 Dixon-Coles model.

### 2. `PointRewardMatrix`
- **Type**: 2D `numpy.ndarray`
- **Description**: An $M \times N$ matrix dynamically constructed for each candidate prediction pair $(U, V)$. Each cell `[i, j]` maps out how many points the user receives if the actual outcome is $i-j$.
- **Values**:
  - `5`: If $i = U$ and $j = V$ (Exact Score)
  - `3`: If $i - j = U - V$ but $(i, j) \neq (U, V)$ (Exact Goal Difference)
  - `1`: If $sign(i - j) = sign(U - V)$ and $i - j \neq U - V$ (Correct Outcome)
  - `0`: Otherwise

### 3. `ExpectedValueVector`
- **Type**: Struct / Scalar dictionary or 2D mapped array
- **Description**: Stores the scalar EV calculation for every evaluated candidate pair $(U, V)$.
- **Selection**: `argmax(EV)` across the evaluation domain ($0-0$ to $5-5$).
