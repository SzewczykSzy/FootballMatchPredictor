# Tasks: Expected Value Decision Engine

**Input**: Design documents from `/specs/004-ev-optimizer/`

**Prerequisites**: plan.md, spec.md, data-model.md, contracts/ev_engine.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the EV Engine module.

- [x] T001 Create `src/model/optimizer.py`
- [x] T002 [P] Create `tests/model/test_optimizer.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete.

- [x] T003 Define `ProbabilityMatrix` handling logic and standard `PointRewardMatrix` constants/generators in `src/model/optimizer.py` based on `data-model.md`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recommend Prediction for a Given Match (Priority: P1) 🎯 MVP

**Goal**: As a tournament participant, I want the system to recommend an exact scoreline prediction based on expected tournament points.

**Independent Test**: Can be fully tested by providing a known probability matrix and verifying that the recommended prediction correctly maximizes the 5/3/1/0 point reward structure.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T004 [P] [US1] Integration test for matrix cross-multiplication EV calculation in `tests/model/test_optimizer.py`
- [x] T005 [P] [US1] Edge case test for exact EV ties resolving by single-outcome probability in `tests/model/test_optimizer.py`

### Implementation for User Story 1

- [x] T006 [US1] Implement `calculate_best_ev` public contract in `src/model/optimizer.py` utilizing vectorized computations
- [x] T007 [US1] Add logic to dynamically size the point-reward matrix based on input matrix dimensions in `src/model/optimizer.py`
- [x] T008 [US1] Implement exact tie-breaking logic in `src/model/optimizer.py` preferring the highest baseline probability

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T009 Refactor any complex broadcasting logic in `src/model/optimizer.py` for performance (<5ms target)
- [x] T010 [P] Ensure type hinting and docstrings align with `contracts/ev_engine.md` in `src/model/optimizer.py`
- [x] T011 Validate execution of `tests/model/test_optimizer.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tests (if included) MUST be written and FAIL before implementation
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All tests for a user story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Integration test for matrix cross-multiplication EV calculation in tests/model/test_optimizer.py"
Task: "Edge case test for exact EV ties resolving by single-outcome probability in tests/model/test_optimizer.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently using `pytest tests/model/test_optimizer.py`
5. Polish code

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP Ready
