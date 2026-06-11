---
description: "Task list for Vectorized Tournament Simulator implementation"
---

# Tasks: Vectorized Tournament Simulator

**Input**: Design documents from `specs/003-tournament-simulator/`

**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/cli_contract.md`

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic file structure

- [ ] T001 [P] Initialize simulation file in `src/model/simulation.py`
- [ ] T002 [P] Initialize bracket file in `src/model/bracket.py`
- [ ] T003 [P] Initialize CLI file in `src/cli/simulate.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [ ] T004 Implement SQLite parameter loading (teams, groups, distributions) in `src/model/simulation.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Group Stage Simulation (Priority: P1) 🎯 MVP

**Goal**: Simulate 12 groups, calculate standings, and determine top 2 + 8 best 3rd-placed advancing teams.

**Independent Test**: Run the group stage simulator on a mock set of 12 groups and verify 24 teams + 8 best 3rd-place teams advance correctly based on vectorized sorting rules.

### Implementation for User Story 1

- [ ] T005 [P] [US1] Define deterministic 3rd-place to knockout mapping table in `src/model/bracket.py`
- [ ] T006 [US1] Implement vectorized 72-match group stage sampling logic in `src/model/simulation.py`
- [ ] T007 [US1] Implement vectorized points, goal difference, and goals scored calculation in `src/model/simulation.py`
- [ ] T008 [US1] Implement vectorized group sorting (np.lexsort) and identify top 2 teams per group in `src/model/simulation.py`
- [ ] T009 [US1] Implement vectorized ranking of 3rd-placed teams and select the top 8 in `src/model/simulation.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Knockout Stage & Champion Prediction (Priority: P2)

**Goal**: Simulate the single-elimination bracket from Round of 32 to Final and calculate progression probabilities.

**Independent Test**: Feed 32 advancing teams into the knockout simulator and verify exactly one champion emerges per run, and total probabilities sum to exactly 1.0.

### Implementation for User Story 2

- [ ] T010 [US2] Implement Round of 32 assignment using the lookup table from `bracket.py` in `src/model/simulation.py`
- [ ] T011 [US2] Implement stochastic 50/50 tie-breaker logic for drawn knockout matches in `src/model/simulation.py`
- [ ] T012 [US2] Implement vectorized progression loops (R32, R16, QF, SF, Final) in `src/model/simulation.py`
- [ ] T013 [US2] Aggregate runs into a Pandas DataFrame containing progression probabilities in `src/model/simulation.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Goal Concentration Indexing (Priority: P3)

**Goal**: Calculate the Goal Concentration Index (GCI) using HHI for all teams across simulation runs.

**Independent Test**: Run the simulation and verify that an average GCI is calculated and added to the DataFrame for each team.

### Implementation for User Story 3

- [ ] T014 [US3] Implement vectorized HHI calculation across all simulated matches in `src/model/simulation.py`
- [ ] T015 [US3] Aggregate average GCI into the final probabilities Pandas DataFrame in `src/model/simulation.py`

**Checkpoint**: All user stories should now be independently functional

---

## Phase 6: Polish & CLI Integration

**Purpose**: Expose the simulator to the user via the command-line interface as requested in `cli_contract.md`.

- [ ] T016 Implement argparse/click CLI options (`--runs`, `--db`, `--format`, `--output`) in `src/cli/simulate.py`
- [ ] T017 Integrate the simulation engine execution within `src/cli/simulate.py`
- [ ] T018 Implement output formatting (table, csv, json) in `src/cli/simulate.py`
- [ ] T019 Run validation against `quickstart.md` commands in terminal

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2)
- **User Story 2 (P2)**: Depends on User Story 1 (needs advancing teams to populate the bracket)
- **User Story 3 (P3)**: Can be implemented concurrently with US2 or sequentially, but depends on completed matches.

### Parallel Opportunities

- T001, T002, T003 can be executed in parallel.
- T005 (bracket lookup table) can be executed in parallel with T006 (match sampling).

---

## Parallel Example: User Story 1

```bash
# Define mapping table while implementing sampling logic concurrently:
Task: "T005 Define deterministic 3rd-place to knockout mapping table in src/model/bracket.py"
Task: "T006 Implement vectorized 72-match group stage sampling logic in src/model/simulation.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Verify group stage advancements via unit tests or script before proceeding.
5. Move to Phase 4 (Knockout) to finalize the core MVP capabilities.
