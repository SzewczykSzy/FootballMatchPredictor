# Research & Technical Decisions: Data Ingestion

## 1. Odds Parsing Strategy

**Decision**: Use Python's `re` module with multi-line capabilities to extract odds blocks. We will structure the pipeline to parse text line-by-line, buffering data until a complete "Match + Bookmaker Odds" block is detected.

**Rationale**: Since users copy-paste odds from various sources (like Oddsportal or Flashscore), the text format can vary. By searching for a specific regex pattern (e.g., `Team A - Team B` followed by three floating point numbers `1.XX 3.XX 4.XX`), we can identify the matches. If the same bookmaker appears twice, we will track bookmaker names in a dictionary per match and overwrite previous entries (so the last occurrence is kept).

**Alternatives considered**: 
- *BeautifulSoup / HTML Parsing*: Rejected because the constitution requires parsing from pasted text, not web scraping.
- *LLM Extraction*: Rejected because it is non-deterministic and requires external API calls, violating the 100% offline constitution rule.

## 2. Proportional Margin Removal

**Decision**: Implement the Proportional Method (Normalization) to calculate true probabilities.

**Math Definition**:
For raw decimal odds $O_1, O_X, O_2$:
1. Implied probabilities: $P_{imp_1} = 1 / O_1$, $P_{imp_X} = 1 / O_X$, $P_{imp_2} = 1 / O_2$
2. Margin (Overround): $M = P_{imp_1} + P_{imp_X} + P_{imp_2}$
3. True Probabilities: $P_{true} = P_{imp} / M$

**Rationale**: It is computationally simple, fast, and satisfies the requirement. It scales easily for aggregating the consensus by simply averaging the $P_{true}$ values across all bookmakers for a given match.

**Alternatives considered**:
- *Shin's Method*: More accurate for identifying insider trading biases, but much more computationally expensive and complex for this initial version. Deferred to later improvements if necessary.

## 3. Database Schema

**Decision**: Use `sqlite3` with two main tables: `matches` (storing the consensus) and `match_odds` (storing the raw bookmaker odds linked via foreign key).

**Rationale**: Storing raw data alongside the consensus is explicitly required by the spec clarifications. A relational approach avoids JSON blobs in SQLite, allowing for easier SQL queries (e.g., `SELECT avg(odds_home) FROM match_odds WHERE match_id = X`).

**Alternatives considered**:
- *JSON column in matches table*: Simpler schema, but harder to query specific bookmaker trends later.
