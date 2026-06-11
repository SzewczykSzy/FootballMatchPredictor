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
    if not isinstance(prob_matrix, np.ndarray):
        raise TypeError("prob_matrix must be a numpy.ndarray")
    if prob_matrix.ndim != 2:
        raise ValueError("prob_matrix must be 2D")
    
    M, N = prob_matrix.shape
    if M < max_score + 1 or N < max_score + 1:
        raise ValueError(f"prob_matrix dimensions {prob_matrix.shape} must be at least ({max_score + 1}, {max_score + 1})")

    # Generate all candidate prediction coordinates (U, V) from 0-0 to max_score-max_score
    u_grid, v_grid = np.meshgrid(np.arange(max_score + 1), np.arange(max_score + 1), indexing='ij')
    U = u_grid.ravel()
    V = v_grid.ravel()
    num_candidates = len(U)

    # Reshape candidate predictions for broadcasting: (num_candidates, 1, 1)
    U_c = U[:, None, None]
    V_c = V[:, None, None]

    # Coordinate matrices for actual outcomes: (1, M, N)
    i = np.arange(M)[None, :, None]
    j = np.arange(N)[None, None, :]
    diff_matrix = i - j  # actual goal differences

    pred_diff = U_c - V_c  # predicted goal differences

    # Compute point reward matrix dynamically of shape (num_candidates, M, N)
    # Rules:
    # 5 points for exact score (i == U and j == V)
    # 3 points for exact goal difference (diff_matrix == pred_diff), except the exact score cell
    # 1 point for correct outcome tendency (same sign of goal diff), except where diff_matrix == pred_diff
    # 0 points otherwise
    rewards = np.zeros((num_candidates, M, N), dtype=float)

    # 1. Correct Outcome (1 point)
    # True if signs of differences match, and goal difference is not equal to predicted difference
    outcome_match = (np.sign(diff_matrix) == np.sign(pred_diff)) & (diff_matrix != pred_diff)
    rewards = np.where(outcome_match, 1.0, rewards)

    # 2. Exact Goal Difference (3 points)
    # True if goal difference matches predicted difference
    rewards = np.where(diff_matrix == pred_diff, 3.0, rewards)

    # 3. Exact Score (5 points)
    # Assign 5 points directly to the cell (U_k, V_k) for each candidate prediction k
    k_indices = np.arange(num_candidates)
    rewards[k_indices, U, V] = 5.0

    # Calculate EV for each candidate prediction: sum over outcome dimensions (M, N)
    # rewards is (num_candidates, M, N), prob_matrix is (M, N)
    evs = np.sum(rewards * prob_matrix[None, :, :], axis=(1, 2))

    # Retrieve the baseline probabilities for each candidate
    probs = prob_matrix[U, V]

    # To ensure machine precision issues don't disrupt exact ties, we round the EV values
    # before tie-breaking. 12 decimal places is highly precise but robust to floating point noise.
    evs_rounded = np.round(evs, decimals=12)

    # Sort candidates: primary key is EV (rounded), secondary key is baseline probability
    idx = np.lexsort((probs, evs_rounded))
    best_idx = idx[-1]

    best_prediction = (int(U[best_idx]), int(V[best_idx]))
    # Return the unrounded EV for maximum precision
    best_ev = float(evs[best_idx])

    return best_prediction, best_ev
