import json
from pathlib import Path
from typing import List, Dict, TypedDict, cast

from utils import Mode

LEADERBOARD = "leaderboard.json"

class LeaderboardEntry(TypedDict):
    name: str
    exp: int
    rounds: int

def load_leaderboard() -> Dict[str, List[LeaderboardEntry]]:
    path = Path(LEADERBOARD)
    
    default: Dict[str, List[LeaderboardEntry]] = {
        "campaign_normal": [],
        "campaign_hard": [],
        "endless_normal": [],
        "endless_hard": []
    }
    
    if not path.exists():
        return default

    if path.stat().st_size == 0:
        return default
    
    with open(path, "r", encoding="utf-8") as file:
        data = json.load(file)
        return cast(Dict[str, List[LeaderboardEntry]], data)
    
def save_score(mode: Mode, name: str, exp: int, rounds: int) -> None:
    leaderboard: Dict[str, List[LeaderboardEntry]] = load_leaderboard()
    mode_key = mode.name.lower()
    
    entries: List[LeaderboardEntry] = leaderboard[mode_key]
    existing_entry: None | LeaderboardEntry = None
    
    for entry in entries:
        if entry["name"].lower() == name.lower():
            existing_entry = entry
            break
    
    if existing_entry:
        better_rounds: bool = rounds > existing_entry["rounds"]
        better_exp: bool = (rounds == existing_entry["rounds"] and exp > existing_entry["exp"])
        
        if better_rounds or better_exp:
            existing_entry["rounds"] = rounds
            existing_entry["exp"] = exp
    else:
        entries.append({
            "name": name,
            "exp": exp,
            "rounds": rounds
        })
    

    entries.sort(key=lambda x: (x["rounds"], x["exp"]), reverse=True)
    leaderboard[mode_key] = entries[:10] # keep 10 lang muna
    
    with open(LEADERBOARD, "w", encoding="utf-8") as file:
        json.dump(leaderboard, file, indent=4)
    
     