# Interface Contract: EV Engine

**File**: `src/model/optimizer.py`

## Public Function `calculate_best_ev`

### Signature
```python
import numpy as np
from typing import Tuple

def calculate_best_ev(prob_matrix: np.ndarray, max_score: int = 5) -> Tuple[Tuple[int, int], float]:
    """
    Evaluates the Expected Value of all score predictions up to max_score-max_score,
    cross-multiplying against the provided probability matrix and non-linear rules.
    
    Args:
        prob_matrix (np.ndarray): The 2D probability matrix of true outcomes.
        max_score (int): The maximum candidate scoreline to evaluate (default 5 for 0-0 to 5-5).
        
    Returns:
        Tuple[Tuple[int, int], float]: A tuple containing the best prediction pair (U, V) 
                                       and its corresponding Expected Value.
    """
```

### Constraints
- The `prob_matrix` must be a 2D NumPy array.
- The `prob_matrix` dimensions must be at least `(max_score + 1, max_score + 1)`.
- If ties exist, the function must use the baseline `prob_matrix` cell values to break the tie, returning the most probable outcome among those with exactly identical maximum EV.
