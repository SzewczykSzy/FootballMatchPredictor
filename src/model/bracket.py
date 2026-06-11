"""
Bracket definitions and configurations for the 2026 World Cup simulator.
This module defines the 48 teams, their groups, the group stage match schedule,
and the Round of 32 knockout matchup logic.
"""

from typing import List, Dict, Tuple

# 48 teams in the tournament
TEAMS: List[str] = [
    # Group A
    "USA", "Mexico", "Canada", "Costa Rica",
    # Group B
    "England", "France", "Germany", "Italy",
    # Group C
    "Spain", "Argentina", "Brazil", "Uruguay",
    # Group D
    "Belgium", "Netherlands", "Portugal", "Croatia",
    # Group E
    "Senegal", "Morocco", "Cameroon", "Ghana",
    # Group F
    "Japan", "South Korea", "Iran", "Australia",
    # Group G
    "Switzerland", "Denmark", "Serbia", "Poland",
    # Group H
    "Colombia", "Peru", "Chile", "Ecuador",
    # Group I
    "Nigeria", "Egypt", "Algeria", "Tunisia",
    # Group J
    "Saudi Arabia", "Qatar", "UAE", "Iraq",
    # Group K
    "Ukraine", "Sweden", "Wales", "Austria",
    # Group L
    "Jamaica", "Panama", "Honduras", "El Salvador"
]

# 12 groups (A to L) of 4 teams each
GROUPS: Dict[str, List[str]] = {
    "A": TEAMS[0:4],
    "B": TEAMS[4:8],
    "C": TEAMS[8:12],
    "D": TEAMS[12:16],
    "E": TEAMS[16:20],
    "F": TEAMS[20:24],
    "G": TEAMS[24:28],
    "H": TEAMS[28:32],
    "I": TEAMS[32:36],
    "J": TEAMS[36:40],
    "K": TEAMS[40:44],
    "L": TEAMS[44:48]
}

def generate_group_stage_matches() -> List[Tuple[str, str]]:
    """
    Generates the 72 group stage matches (6 matches per group).
    Each team in a group plays the other 3 teams exactly once.
    """
    matches = []
    # Loop over groups in sorted order to ensure consistent indexing
    for group_name in sorted(GROUPS.keys()):
        group_teams = GROUPS[group_name]
        # 6 pairwise combinations for 4 teams
        group_matches = [
            (group_teams[0], group_teams[1]),
            (group_teams[2], group_teams[3]),
            (group_teams[0], group_teams[2]),
            (group_teams[1], group_teams[3]),
            (group_teams[0], group_teams[3]),
            (group_teams[1], group_teams[2])
        ]
        matches.extend(group_matches)
    return matches

# 72 group stage matches
GROUP_MATCHES: List[Tuple[str, str]] = generate_group_stage_matches()

# Group names mapping to their index (0 to 11)
GROUP_NAME_TO_IDX: Dict[str, int] = {name: idx for idx, name in enumerate(sorted(GROUPS.keys()))}
IDX_TO_GROUP_NAME: Dict[int, str] = {idx: name for idx, name in enumerate(sorted(GROUPS.keys()))}

# Mapping of the Round of 32 knockout slots
# The 16 matches are represented by their opponents.
# Opponent types:
#   - ('winner', group_idx): Winner of that group index (0-11)
#   - ('runner_up', group_idx): Runner-up of that group index (0-11)
#   - ('third_place', slot_idx): The slot (0-7) assigned to the advancing 3rd place teams
#     sorted by their original group index.
ROUND_OF_32_MATCHUPS: List[Tuple[Tuple[str, int], Tuple[str, int]]] = [
    # Match 1: Runner-up Group A vs Runner-up Group B
    (('runner_up', 0), ('runner_up', 1)),
    # Match 2: Winner Group C vs Runner-up Group F
    (('winner', 2), ('runner_up', 5)),
    # Match 3: Winner Group E vs 3rd Place Slot 0 (E.g., early group)
    (('winner', 4), ('third_place', 0)),
    # Match 4: Winner Group F vs Runner-up Group C
    (('winner', 5), ('runner_up', 2)),
    # Match 5: Runner-up Group E vs Runner-up Group I
    (('runner_up', 4), ('runner_up', 8)),
    # Match 6: Winner Group I vs 3rd Place Slot 1
    (('winner', 8), ('third_place', 1)),
    # Match 7: Winner Group A vs 3rd Place Slot 2
    (('winner', 0), ('third_place', 2)),
    # Match 8: Winner Group L vs 3rd Place Slot 3
    (('winner', 11), ('third_place', 3)),
    # Match 9: Winner Group G vs 3rd Place Slot 4
    (('winner', 6), ('third_place', 4)),
    # Match 10: Winner Group D vs 3rd Place Slot 5
    (('winner', 3), ('third_place', 5)),
    # Match 11: Winner Group H vs Runner-up Group J
    (('winner', 7), ('runner_up', 9)),
    # Match 12: Runner-up Group K vs Runner-up Group L
    (('runner_up', 10), ('runner_up', 11)),
    # Match 13: Winner Group B vs 3rd Place Slot 6
    (('winner', 1), ('third_place', 6)),
    # Match 14: Runner-up Group D vs Runner-up Group G
    (('runner_up', 3), ('runner_up', 6)),
    # Match 15: Winner Group J vs Runner-up Group H
    (('winner', 9), ('runner_up', 7)),
    # Match 16: Winner Group K vs 3rd Place Slot 7
    (('winner', 10), ('third_place', 7))
]
