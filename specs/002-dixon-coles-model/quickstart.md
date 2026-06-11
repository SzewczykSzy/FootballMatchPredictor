# Quickstart: Dixon-Coles Prediction Engine

## Running Parameter Fitting

To run the MLE optimization on the historical match database and save parameters:
```bash
python -m src.model.dixon_coles --fit
```

## Generating a Match Matrix

To test the 6x6 probability output for a specific matchup:
```bash
python -m src.model.matrix --home "France" --away "Germany"
```
