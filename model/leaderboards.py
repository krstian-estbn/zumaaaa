import json
from pathlib import Path
from typing import List, Dict, TypedDict, Optional

from utils import Mode

LEADERBOARD = "leaderboard.json"

class LeaderboardEntry(TypedDict):
    name: str
    exp: int
    rounds: int

def load_leaderboard() -> Dict[str, List[Optional[LeaderboardEntry]]]:
    path = Path(LEADERBOARD)
    
    if not path.exists():
        return {
            "campaign_normal": [],
            "campaign_hard": [],
            "endless_normal": [],
            "endless_hard": []
        }
    
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)
    
def save_score(mode: Mode, name: str, exp: int, rounds: int) -> None:
    leaderboard: Dict[str, List[Optional[LeaderboardEntry]]] = load_leaderboard()
    mode_key = mode.name.lower()
    
    leaderboard[mode_key].append({
        "name": name,
        "exp": exp,
        "rounds": rounds
    })
    
    leaderboard[mode_key].sort(
        key=lambda x: (x["rounds"], x["exp"]),
        reverse=True        
        )
    leaderboard[mode_key] = leaderboard[mode_key][:10] # keep 10 lang muna
    
    with open(LEADERBOARD, "w", encoding="utf-8") as file:
        json.dump(leaderboard, file, indent=4)
    
     