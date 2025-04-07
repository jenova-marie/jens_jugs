# Purpose: Manages per-user game state persistence using Redis

import redis
import json
import os

# Retrieve Redis host and port from environment variables
redis_host = os.getenv("REDIS_HOST", "localhost")  # Default to "localhost"
redis_port = int(os.getenv("REDIS_PORT", 6379))    # Default to 6379

# Initialize Redis client
r = redis.Redis(host=redis_host, port=redis_port, db=0)

default_gamestate = None  # Initialize as a global variable

def load_default_gamestate(redis_client):
    """
    Load the default game state from Redis if not already loaded.

    Args:
        redis_client: Redis client instance.

    Returns:
        dict: The default game state.

    Raises:
        ValueError: If the default game state is not found in Redis.
    """
    global default_gamestate

    # Return immediately if default_gamestate is already loaded
    if default_gamestate is not None:
        return default_gamestate

    default_gamestate_key = "gamestate:default"
    default_gamestate_data = redis_client.get(default_gamestate_key)

    if default_gamestate_data:
        default_gamestate = json.loads(default_gamestate_data)
        return default_gamestate
    else:
        raise ValueError(f"Default game state not found in Redis under key '{default_gamestate_key}'. Please initialize Redis with default values.")
        
def get_game_state(user_id: str):
    """
    Retrieve the game state for a user from Redis. If no game state is found,
    load and return the default game state, and update Redis with the default data.

    Args:
        user_id (str): The ID of the user.

    Returns:
        dict: The game state for the user or the default game state.
    """
    key = f"gamestate:{user_id}"
    data = r.get(key)

    if data:
        return json.loads(data)
    else:
        # If no game state is found, ensure the default game state is loaded
        default_state = load_default_gamestate(r)
        # Update Redis with the default game state for the user
        r.set(key, json.dumps(default_state))
        return default_state

def set_game_state(user_id: str, state: dict):
    key = f"gamestate:{user_id}"
    r.set(key, json.dumps(state))
