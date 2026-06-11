from typing import Tuple, Dict, Any, List

def remove_margin(odds_home: float, odds_draw: float, odds_away: float) -> Tuple[float, float, float]:
    """
    Remove bookmaker margin using the proportional method.
    Raises ValueError if any odds are <= 1.0.
    """
    if odds_home <= 1.0 or odds_draw <= 1.0 or odds_away <= 1.0:
        raise ValueError("Odds must be strictly greater than 1.0")
        
    p_imp_home = 1.0 / odds_home
    p_imp_draw = 1.0 / odds_draw
    p_imp_away = 1.0 / odds_away
    
    margin = p_imp_home + p_imp_draw + p_imp_away
    
    p_true_home = p_imp_home / margin
    p_true_draw = p_imp_draw / margin
    p_true_away = p_imp_away / margin
    
    return p_true_home, p_true_draw, p_true_away

def calculate_consensus(match: Dict[str, Any]) -> Dict[str, float]:
    """
    Calculates consensus probabilities for a match by:
    1. Removing margin from each bookmaker's odds.
    2. Calculating the arithmetic mean of the clean probabilities.
    Updates the bookmaker odds dictionary in place with true probabilities.
    Returns a dict with:
      - 'consensus_p_home'
      - 'consensus_p_draw'
      - 'consensus_p_away'
    """
    odds_list = match.get("odds", [])
    if not odds_list:
        raise ValueError("Match must contain at least one bookmaker odds entry")
        
    sum_home = 0.0
    sum_draw = 0.0
    sum_away = 0.0
    
    for entry in odds_list:
        ph, pd, pa = remove_margin(entry["odds_home"], entry["odds_draw"], entry["odds_away"])
        entry["p_true_home"] = ph
        entry["p_true_draw"] = pd
        entry["p_true_away"] = pa
        
        sum_home += ph
        sum_draw += pd
        sum_away += pa
        
    n = len(odds_list)
    consensus = {
        "consensus_p_home": sum_home / n,
        "consensus_p_draw": sum_draw / n,
        "consensus_p_away": sum_away / n
    }
    
    # Ensure they sum exactly to 1.0 (handling float precision)
    total = sum(consensus.values())
    if abs(total - 1.0) > 1e-9:
        for key in consensus:
            consensus[key] /= total
            
    return consensus
