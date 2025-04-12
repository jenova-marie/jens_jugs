# Purpose: Manages per-user game state persistence using Redis

import json
import os
from jsonschema import validate, ValidationError
from jsonschema.exceptions import RefResolutionError
from jens_jugs.logger import get_logger

# Load the Redis schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../../schema/redis.schema.json")
with open(SCHEMA_PATH, "r") as schema_file:
    REDIS_SCHEMA = json.load(schema_file)

# Load the default Redis data
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/game-state.default.json")
with open(DEFAULT_DATA_PATH, "r") as default_file:
    DEFAULT_REDIS_DATA = json.load(default_file)

logger = get_logger(log_name="redis_gamestate")


def validate_redis_data(data, schema_section):
    """
    Validate Redis data against the schema.

    Args:
        data (dict): The data to validate.
        schema_section (str): The schema section to validate against.

    Raises:
        ValueError: If the data does not conform to the schema or if a reference cannot be resolved.
    """
    try:
        validate(instance=data, schema=REDIS_SCHEMA["properties"][schema_section])
    except ValidationError as e:
        logger.error(f"Redis data validation error: {e.message}")
        raise ValueError(f"Invalid Redis data: {e.message}")
    except RefResolutionError as e:
        logger.error(f"Schema reference resolution error: {e}")
        raise ValueError(f"Schema reference resolution error: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during validation: {e}")
        raise ValueError(f"Unexpected error during validation: {e}")


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
    try:
        default_gamestate_key = "gamestate:default"
        default_gamestate_data = redis_client.get(default_gamestate_key)

        if default_gamestate_data and default_gamestate_data != "null":
            # Parse the data as JSON
            default_gamestate = json.loads(default_gamestate_data)
            validate_redis_data(default_gamestate, "gamestate:default")
            return default_gamestate
        else:
            logger.warning(f"Default game state not found in Redis under key '{default_gamestate_key}'. Loading from game-state.default.json.")
            # Load default game state from game-state.default.json
            default_gamestate = DEFAULT_REDIS_DATA.get("gamestate:default")
            if not default_gamestate:
                raise ValueError("Default game state is missing in game-state.default.json.")
            # Validate the default game state
            validate_redis_data(default_gamestate, "gamestate:default")
            # Add the default game state to Redis
            redis_client.set(default_gamestate_key, json.dumps(default_gamestate))
            logger.info(f"Default game state added to Redis under key '{default_gamestate_key}'.")
            return default_gamestate
    except Exception as e:
        logger.error(f"Unexpected error in load_default_gamestate: {e}")
        raise ValueError(f"Unexpected error in load_default_gamestate: {e}")


def get_game_state(user_id: str, redis_client):
    """
    Retrieve the game state for a user from Redis. If no game state is found,
    load and return the default game state, and update Redis with the default data.

    Args:
        user_id (str): The ID of the user.
        redis_client: Redis client instance.

    Returns:
        dict: The game state for the user or the default game state.
    """
    try:
        key = f"gamestate:{user_id}"
        data = redis_client.get(key)

        if data and data != "null":  # Check if data exists and is not 'null'
            # Parse the data as JSON
            game_state = json.loads(data)
            validate_redis_data(game_state, "gamestate:<user_id>")
            return game_state
        else:
            # If no game state is found, ensure the default game state is loaded
            default_state = load_default_gamestate(redis_client)
            # Update Redis with the default game state for the user
            redis_client.set(key, json.dumps(default_state))
            logger.info(f"Default game state set for user '{user_id}' in Redis.")
            return default_state
    except Exception as e:
        logger.error(f"Unexpected error in get_game_state: {e}")
        raise ValueError(f"Unexpected error in get_game_state: {e}")


def set_game_state(user_id: str, state: dict, redis_client):
    """
    Set the game state for a user in Redis.

    Args:
        user_id (str): The ID of the user.
        state (dict): The game state to set.
        redis_client: Redis client instance.

    Raises:
        ValueError: If the game state does not conform to the schema.
    """
    try:
        key = f"gamestate:{user_id}"
        validate_redis_data(state, "gamestate:<user_id>")
        redis_client.set(key, json.dumps(state))
        logger.info(f"Game state updated for user '{user_id}' in Redis.")
    except Exception as e:
        logger.error(f"Unexpected error in set_game_state: {e}")
        raise ValueError(f"Unexpected error in set_game_state: {e}")
