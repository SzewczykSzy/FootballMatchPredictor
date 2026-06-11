# Internal Python API Contracts

## `ScoreMatrix` Data Class
```python
@dataclass
class ScoreMatrix:
    home_team: str
    away_team: str
    matrix: np.ndarray  # 6x6 float array summing to 1.0
```

## `TeamParameters` Data Class
```python
@dataclass
class TeamParameters:
    team_id: str
    alpha: float
    beta: float
```
