# Purpose: Manages per-user game state persistence using Redis

import redis
import json

r = redis.Redis(host="localhost", port=6379, db=0)


def get_game_state(user_id: str):
    key = f"gamestate:{user_id}"
    data = r.get(key)
    return json.loads(data) if data else None


def set_game_state(user_id: str, state: dict):
    key = f"gamestate:{user_id}"
    r.set(key, json.dumps(state))
