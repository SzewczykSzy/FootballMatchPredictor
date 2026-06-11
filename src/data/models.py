from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class MatchOdds:
    bookmaker_name: str
    odds_home: float
    odds_draw: float
    odds_away: float
    p_true_home: float
    p_true_draw: float
    p_true_away: float
    id: Optional[int] = None
    match_id: Optional[int] = None

@dataclass
class MatchRecord:
    home_team: str
    away_team: str
    consensus_p_home: float
    consensus_p_draw: float
    consensus_p_away: float
    match_date: Optional[str] = None
    created_at: Optional[str] = None
    id: Optional[int] = None
    odds: List[MatchOdds] = field(default_factory=list)
