# Quickstart: Vectorized Tournament Simulator

This guide shows how to run the Monte Carlo tournament simulator from the command line once the database is populated with team parameters.

## Prerequisites

1. Ensure Python 3.11+ is installed.
2. Ensure you have installed the required dependencies:
   ```bash
   pip install numpy pandas scipy
   ```
3. Ensure that `matches.db` is present in the project root and populated with at least one set of team parameters (e.g., after running the Dixon-Coles model fitter).

## Running the Simulator

To run the default 10,000 stochastic simulations and view the aggregated probability table in your console:

```bash
python -m src.cli.simulate
```

You should see an output similar to this:

```text
Running 10,000 simulations...
Simulation completed in 3.42 seconds.

Team        | p_group_winner | p_advance | p_r16 | ... | p_champion | avg_gci
-----------------------------------------------------------------------------
Brazil      | 0.85           | 0.98      | 0.98  | ... | 0.15       | 0.234
Argentina   | 0.82           | 0.95      | 0.95  | ... | 0.12       | 0.221
France      | 0.79           | 0.92      | 0.92  | ... | 0.10       | 0.210
...
```

## Exporting Results

If you want to use the results in a spreadsheet or another script, export the data to CSV:

```bash
python -m src.cli.simulate --format csv --output results.csv
```
