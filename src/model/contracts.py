from dataclasses import dataclass
import numpy as np

@dataclass
class ScoreMatrix:
    home_team: str
    away_team: str
    matrix: np.ndarray  # 6x6 float array summing to 1.0

@dataclass
class TeamParameters:
    team_id: str
    alpha: float
    beta: float
