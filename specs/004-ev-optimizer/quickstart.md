# Quickstart: Expected Value Decision Engine

## Overview
The EV engine is a core mathematical module that takes the output of the Dixon-Coles simulation (a 2D probability matrix) and maps it against the competition's scoring rules to find the mathematically optimal prediction.

## Usage Example

```python
import numpy as np
from src.model.optimizer import calculate_best_ev

# 1. Obtain your probability matrix (e.g., from phase 2 model)
# Here is a mock 6x6 matrix with some probabilities
prob_matrix = np.zeros((6, 6))
prob_matrix[1, 1] = 0.20
prob_matrix[2, 1] = 0.15
prob_matrix[0, 0] = 0.10
# ... ensure matrix sum() == 1.0

# 2. Feed it into the EV Decision Engine
best_prediction, max_ev = calculate_best_ev(prob_matrix, max_score=5)

# 3. Output the result
print(f"Recommended Prediction: {best_prediction[0]}-{best_prediction[1]}")
print(f"Expected Value: {max_ev:.4f} points")
```

## Running Tests
To verify the vectorized logic and non-linear rule scoring, run the pytest suite:
```bash
pytest tests/model/test_optimizer.py -v
```
