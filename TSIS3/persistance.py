import json
import os

LEADERBOARD_FILE = "leaderboard.json"
SETTINGS_FILE    = "settings.json"

DEFAULT_SETTINGS = {
    "sound":      True,
    "car_color":  "Blue",
    "difficulty": "Normal",  
}

DIFFICULTY_PARAMS = {
    "Easy":   {"base_speed": 3, "enemy_interval": 120, "coin_interval": 120},
    "Normal": {"base_speed": 4, "enemy_interval": 90,  "coin_interval": 150},
    "Hard":   {"base_speed": 6, "enemy_interval": 60,  "coin_interval": 180},
}

def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE) as f:
                data = json.load(f)
            for k, v in DEFAULT_SETTINGS.items():
                data.setdefault(k, v)
            return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict) -> None:
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)


def load_leaderboard() -> list:
    if os.path.exists(LEADERBOARD_FILE):
        try:
            with open(LEADERBOARD_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return []


def save_score(name: str, score: int, distance: int, coins: int) -> None:
    board = load_leaderboard()
    board.append({"name": name, "score": score,
                  "distance": distance, "coins": coins})
    board.sort(key=lambda e: e["score"], reverse=True)
    board = board[:10]
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(board, f, indent=2)
