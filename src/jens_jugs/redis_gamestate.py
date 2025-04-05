# Purpose: Manages per-user game state persistence using Redis

import redis
import json
import os

r = redis.Redis(host="localhost", port=6379, db=0)

# Load default game state from file
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
default_gamestate_path = os.path.join(base_dir, "jens_jugs", "default_gamestate.json")
print(default_gamestate_path)
with open(default_gamestate_path, "r") as f:
    default_gamestate = json.load(f)

def get_game_state(user_id: str):
    key = f"gamestate:{user_id}"
    data = r.get(key)
    return json.loads(data) if data else None

def set_game_state(user_id: str, state: dict):
    key = f"gamestate:{user_id}"
    r.set(key, json.dumps(state))

def get_or_create_game_state(user_id: str):
    state = get_game_state(user_id)
    if not state:
        set_game_state(user_id, default_gamestate)
        return default_gamestate
    return state
