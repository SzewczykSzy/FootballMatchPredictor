# Tasks: Streamlit UI

**Input**: Design documents from `/specs/005-streamlit-ui/`

**Prerequisites**: plan.md, spec.md, data-model.md, research.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Streamlit entry point in `app.py`
- [X] T002 [P] Create UI components module in `src/ui/components.py`
- [X] T003 [P] Create UI test suite in `tests/ui/test_app.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create backend integration functions/wrappers connecting `src/data/parser.py` and `src/model/optimizer.py` inside `src/ui/components.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Paste Odds and Generate Predictions (Priority: P1) 🎯 MVP

**Goal**: As a tournament participant, I want to paste raw bookmaker odds into a simple web interface and instantly receive a formatted table of exact score predictions.

**Independent Test**: Can be fully tested by launching the application via `streamlit run app.py`, pasting a known sample of odds, clicking the button, and verifying that the output table renders the correct recommendations and metrics.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Create Streamlit AppTest asserting Text Area existence and table rendering on submit in `tests/ui/test_app.py`
- [X] T006 [P] [US1] Create AppTest asserting error message appears on invalid input in `tests/ui/test_app.py`

### Implementation for User Story 1

- [X] T007 [P] [US1] Implement large Text Area input and "Generate Predictions" button in `app.py`
- [X] T008 [P] [US1] Implement parsing error handling and user-friendly error messages in `app.py`
- [X] T009 [US1] Implement table rendering logic formatting `PredictionOutputRow` data into a Markdown/HTML table in `src/ui/components.py`
- [X] T010 [US1] Wire the input text to the backend integration functions and pass the resulting data to the table renderer in `app.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently via the browser.

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T011 Validate execution via `streamlit run app.py` and ensure UI responsiveness (<3s)
- [X] T012 Run quickstart.md validation locally

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

- Tests MUST be written and FAIL before implementation
- UI inputs before rendering logic
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All tests for a user story marked [P] can run in parallel
- Independent UI component implementation can run in parallel with backend integration

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Create Streamlit AppTest asserting Text Area existence and table rendering on submit in tests/ui/test_app.py"
Task: "Create AppTest asserting error message appears on invalid input in tests/ui/test_app.py"

# Launch UI structure tasks together:
Task: "Implement large Text Area input and "Generate Predictions" button in app.py"
Task: "Implement parsing error handling and user-friendly error messages in app.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently using `pytest tests/ui/test_app.py` and `streamlit run app.py`
5. Polish codebase
