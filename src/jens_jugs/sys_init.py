import os
import json
from jsonschema import validate, ValidationError
from jens_jugs.logger import get_logger

# Load the Redis schema
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../../schema/redis.schema.json")
with open(SCHEMA_PATH, "r") as schema_file:
    REDIS_SCHEMA = json.load(schema_file)

# Load the default Redis data
DEFAULT_DATA_PATH = os.path.join(os.path.dirname(__file__), "../../data/game-state.default.json")
with open(DEFAULT_DATA_PATH, "r") as default_file:
    DEFAULT_REDIS_DATA = json.load(default_file)

logger = get_logger(log_name="sys_init")

# def load_external_default(file_path):
#     """
#     Load the external default file.

#     Args:
#         file_path (str): Path to the external default file.

#     Returns:
#         dict: The loaded default data.

#     Raises:
#         FileNotFoundError: If the file does not exist.
#         ValueError: If the file contains invalid JSON.
#     """
#     if not os.path.exists(file_path):
#         raise FileNotFoundError(f"Default file not found: {file_path}")

#     with open(file_path, "r") as file:
#         try:
#             return json.load(file)
#         except json.JSONDecodeError as e:
#             raise ValueError(f"Invalid JSON in default file: {file_path}") from e

def populate_redis_with_defaults(redis_client, logger=logger):
    """
    Populate Redis with default values if keys are missing.

    Args:
        redis_client: Redis client instance.
        logger: Logger instance (optional).
    """
    try:
        # Validate the loaded default data against the schema
        for key, value in DEFAULT_REDIS_DATA.items():
            schema_section = "gamestate:default" if key == "gamestate:default" else "gamestate:<user_id>"
            try:
                validate(instance=value, schema=REDIS_SCHEMA["properties"][schema_section])
                logger.debug(f"Default data for key '{key}' is schema-compliant.")
            except ValidationError as e:
                logger.error(f"Validation error for key '{key}': {e.message}")
                raise ValueError(f"Default data for key '{key}' is not schema-compliant: {e.message}")

            # Add the default value to Redis if the key does not exist
            if not redis_client.exists(key):
                logger.info(f"Key '{key}' not found in Redis. Adding default value.")
                redis_client.set(key, json.dumps(value))
            else:
                logger.debug(f"Key '{key}' already exists in Redis. Skipping.")
    except Exception as e:
        logger.error(f"Error populating Redis with default values: {e}", exc_info=True)
        raise