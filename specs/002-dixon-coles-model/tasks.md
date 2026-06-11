# Tasks: Dixon-Coles Probabilistic Prediction Engine

**Input**: Design documents from `specs/002-dixon-coles-model/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/python_api.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create `ScoreMatrix` and `TeamParameters` dataclasses in `src/model/contracts.py`
- [x] T002 [P] Update database schema with `TeamParameters` and `ModelConfig` tables in `contracts/schema.sql`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T003 Implement database repository for TeamParameters and ModelConfig in `src/model/parameters.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Model Parameter Estimation (Priority: P1) 🎯 MVP

**Goal**: Fit MLE to historical data for 48 teams to estimate time-weighted attack ($\alpha$) and defense ($\beta$) strengths.

**Independent Test**: Can be fully tested by running the parameter estimation on a mock dataset of historical matches and verifying that the solver converges to produce sensible values.

### Tests for User Story 1

- [x] T004 [US1] Write test for parameter fitting and exponential decay in `tests/model/test_dixon_coles.py`

### Implementation for User Story 1

- [x] T005 [US1] Implement Dixon-Coles MLE optimization logic with tau adjustment, using ModelConfig for global parameters, in `src/model/dixon_coles.py`
- [x] T006 [US1] Add convergence failure retry logic with relaxed tolerances in `src/model/dixon_coles.py`
- [x] T007 [US1] Implement CLI for running the fitting process in `src/model/dixon_coles.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Match Probability Generation (Priority: P2)

**Goal**: Generate a discrete 6x6 probability matrix for any given match based on calculated parameters.

**Independent Test**: Can be tested by providing mock attack/defense parameters and verifying the output is a valid 6x6 matrix summing to exactly 1.0.

### Tests for User Story 2

- [x] T008 [US2] Write test verifying 6x6 matrix generation sums to 1.0 in `tests/model/test_matrix.py`

### Implementation for User Story 2

- [x] T009 [US2] Implement 6x6 probability matrix calculation logic, integrating Phase 1 bookmaker consensus prior, in `src/model/matrix.py`
- [x] T010 [US2] Implement CLI for predicting a specific matchup in `src/model/matrix.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase N: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T011 Run quickstart.md validation by testing the new CLI commands
- [x] T012 Code cleanup and refactoring across the `src/model` module

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational
- **User Story 2 (P2)**: Can start after Foundational

### Parallel Opportunities

- T002 can run in parallel with T001
- User Story 1 and User Story 2 could be implemented in parallel since they don't block each other if mock data is used for US2.

---

## Parallel Example: User Story 1

```bash
# Launch test and implementation for User Story 1
Task: "[US1] Write test for parameter fitting and exponential decay in tests/model/test_dixon_coles.py"
Task: "[US1] Implement Dixon-Coles MLE optimization logic with tau adjustment in src/model/dixon_coles.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently

### Incremental Delivery

1. Complete Setup + Foundational
2. Add User Story 1 → Test independently
3. Add User Story 2 → Test independently
