# Phase 0: Research

**Feature**: Expected Value Decision Engine

## Unknowns and Decisions

All implementation details were explicitly outlined in the project Constitution and Technical Context. No formal research agents were necessary to dispatch.

### 1. Vectorized Cross-Multiplication (NumPy)
- **Decision**: Use NumPy's 2D array broadcasting to construct the point-reward matrix dynamically and compute the Hadamard product (element-wise multiplication) against the probability matrix, followed by a sum.
- **Rationale**: Meets Constitution Principle IV (Vectorized Computation) and easily achieves the <5ms performance goal.
- **Alternatives considered**: Python standard nested loops were considered but strictly rejected due to performance constraints and constitution violations.

### 2. Tie-Breaking Strategy
- **Decision**: Select the scoreline with the highest baseline absolute probability when EV is identical.
- **Rationale**: Statistically soundest approach when expected rewards are perfectly equal.
- **Alternatives considered**: Random selection, which introduces non-deterministic outputs.
