# Data Model: Data Ingestion and SQLite

## Entities

### `matches` (MatchRecord)
The primary entity representing a single football match and its aggregated consensus probabilities.

**Fields**:
- `id` (INTEGER PRIMARY KEY)
- `home_team` (TEXT, NOT NULL)
- `away_team` (TEXT, NOT NULL)
- `match_date` (TEXT, ISO 8601 string)
- `consensus_p_home` (REAL, NOT NULL)
- `consensus_p_draw` (REAL, NOT NULL)
- `consensus_p_away` (REAL, NOT NULL)
- `created_at` (DATETIME, default CURRENT_TIMESTAMP)

**Relationships**:
- One `match` has many `match_odds` entries.

**Validation Rules**:
- `home_team` and `away_team` must be strictly matched (e.g., lowercase unified strings).
- `consensus_p_home + consensus_p_draw + consensus_p_away` MUST equal 1.0 (with a small epsilon tolerance for float arithmetic, e.g., ±0.0001).

---

### `match_odds` (MatchOdds)
Represents the raw odds extracted from a single bookmaker for a specific match.

**Fields**:
- `id` (INTEGER PRIMARY KEY)
- `match_id` (INTEGER, FOREIGN KEY to `matches.id`, ON DELETE CASCADE)
- `bookmaker_name` (TEXT, NOT NULL)
- `odds_home` (REAL, NOT NULL)
- `odds_draw` (REAL, NOT NULL)
- `odds_away` (REAL, NOT NULL)
- `p_true_home` (REAL)
- `p_true_draw` (REAL)
- `p_true_away` (REAL)

**Validation Rules**:
- `match_id` and `bookmaker_name` form a UNIQUE constraint (to enforce the "last occurrence wins" or prevent duplicates during save).
- Odds must be > 1.0.

## State Transitions
- **Pasted Text** → **Raw Strings** → **MatchOdds Objects** (Memory) → **Math Normalization** (Memory) → **Consensus Generation** (Memory) → **Persisted to SQLite**.
