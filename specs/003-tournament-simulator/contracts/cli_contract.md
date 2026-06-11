# CLI Contract: Simulator

The simulator provides a command-line interface to execute the 10,000 tournament simulations and view the aggregated probabilities.

## Command Syntax

```bash
python -m src.cli.simulate [OPTIONS]
```

## Options

- `--runs`, `-n`: Integer. Number of tournament simulations to run. Default is `10000`.
- `--db`, `-d`: String. Path to the SQLite database. Default is `matches.db`.
- `--format`, `-f`: String. Output format for the final aggregated table. Options: `table`, `csv`, `json`. Default is `table`.
- `--output`, `-o`: String. Optional file path to export the results. If not provided, prints to stdout.

## Examples

Run default simulation (10,000 runs) and print as an ASCII table:
```bash
python -m src.cli.simulate
```

Run a quick test simulation with 100 runs and output to CSV:
```bash
python -m src.cli.simulate -n 100 -f csv -o results.csv
```

## Output Schema (JSON Format)

If `--format json` is used, the output will be a JSON array of objects representing the final aggregated DataFrame:

```json
[
  {
    "team": "Brazil",
    "p_group_winner": 0.85,
    "p_advance": 0.98,
    "p_r16": 0.98,
    "p_qf": 0.75,
    "p_sf": 0.50,
    "p_final": 0.30,
    "p_champion": 0.15,
    "avg_gci": 0.234
  },
  ...
]
```
