# Tasks: Data Ingestion and Local Storage

**Input**: Design documents from `specs/001-data-ingestion-and-sqlite/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/schema.sql

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure (`src/data/` and `tests/data/`) per implementation plan
- [ ] T002 [P] Initialize Python project and configure `pytest` environment

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T003 Setup SQLite database connection manager and schema initialization in `src/data/database.py` using `contracts/schema.sql`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Parse and Consolidate Odds (Priority: P1) 🎯 MVP

**Goal**: Users paste a block of raw, multi-line text containing odds. System extracts odds, applies strict team name matching, resolves duplicates by taking the last occurrence, removes margin proportionally, and outputs the average consensus probability.

**Independent Test**: Can be fully tested by parsing a mock text block and verifying the output consensus mathematically without needing the database.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T004 [P] [US1] Integration test for parsing raw odds text in `tests/data/test_ingestion.py`
- [ ] T005 [P] [US1] Unit test for proportional margin math in `tests/data/test_math.py`

### Implementation for User Story 1

- [ ] T006 [P] [US1] Implement proportional margin removal logic in `src/data/math_utils.py`
- [ ] T007 [US1] Implement multi-line text parsing logic to extract odds in `src/data/parser.py`
- [ ] T008 [US1] Integrate parser with math utils to generate match consensus in `src/data/parser.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Store Match Data (Priority: P2)

**Goal**: Users can save the parsed match data and raw bookmaker odds into the SQLite database.

**Independent Test**: Can be fully tested by triggering a save operation for a parsed match and then retrieving the exact same match data from the local database.

### Tests for User Story 2

- [ ] T009 [P] [US2] Integration test for saving and retrieving match data in `tests/data/test_database.py`

### Implementation for User Story 2

- [ ] T010 [P] [US2] Define internal Python data models for MatchRecord and MatchOdds in `src/data/models.py`
- [ ] T011 [US2] Implement insert and update logic for `matches` and `match_odds` tables in `src/data/database.py`
- [ ] T012 [US2] Implement query functions to retrieve saved matches in `src/data/database.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T013 Create an executable example script `run_quickstart.py` in project root based on `quickstart.md`
- [ ] T014 Run `run_quickstart.py` to validate end-to-end integration

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories proceed sequentially in priority order (US1 → US2)
- **Polish (Final Phase)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Depends on US1 completing to have parsed Match objects available to test the insertion logic.

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch test and math logic together:
Task: "Unit test for proportional margin math in tests/data/test_math.py"
Task: "Implement proportional margin removal logic in src/data/math_utils.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1 (Parsing and Math)
4. **STOP and VALIDATE**: Test User Story 1 parsing independently.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test parsing logic → MVP
3. Add User Story 2 → Test SQLite storage → Phase 2 MVP
