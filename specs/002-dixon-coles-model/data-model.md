# Phase 1: Data Model & SQLite Additions

## New Entities

### TeamParameters (SQLite Table)
Stores the solved parameters for fast prediction lookups without re-running MLE.
- `team_id` (String, PK): Standardized team name
- `alpha` (Float): Attack strength
- `beta` (Float): Defense strength
- `last_updated` (Timestamp): When the MLE was run

### ModelConfig (SQLite Table)
Stores global model parameters.
- `id` (Integer, PK): Single row ID
- `gamma` (Float): Global home advantage parameter
- `rho` (Float): Global low-score dependency parameter
- `last_updated` (Timestamp): When the MLE was run
