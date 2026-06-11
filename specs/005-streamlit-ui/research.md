# Phase 0: Research

**Feature**: Streamlit UI

## Unknowns and Decisions

All architectural decisions and implementation constraints were explicitly outlined in the project Constitution (Principle V) and Technical Context. No formal research agents were necessary to dispatch.

### 1. Presentation Framework
- **Decision**: Use `Streamlit` as the core web framework.
- **Rationale**: Meets Constitution Principle V directly. It supports pure Python implementations, requires no separate Node.js/frontend build step, and runs 100% locally on the workstation.
- **Alternatives considered**: None. Streamlit is strictly mandated by the constitution.

### 2. State Management
- **Decision**: Pure stateless pipeline per submission.
- **Rationale**: Streamlit natively re-runs the entire script upon user interaction (like button clicks). Since the goal is a quick daily "paste and process" loop, saving session state across re-runs is unnecessary unless handling massive batch pagination, which is out of scope.
- **Alternatives considered**: Streamlit `st.session_state`, which was rejected to keep the app complexity minimal.
