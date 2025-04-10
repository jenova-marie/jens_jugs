import os
import json
from jens_jugs.logger import get_logger
from jsonschema import validate, ValidationError

def populate_redis_with_defaults(redis_client, logger=None):
    """
    Populate Redis with default values from redis.json if keys are missing.

    Args:
        redis_client: Redis client instance.
        logger: Logger instance (optional).
    """
    if logger is None:
        logger = get_logger(log_name="sys_init")

    # Correct the path to the redis.json file
    base_dir = os.path.dirname(os.path.abspath(__file__))
    redis_json_path = os.path.join(base_dir, "defaults", "redis.json")
    logger.info(f"Loading default Redis data from {redis_json_path}...")

    # Load the Redis schema
    SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../../schema/redis.schema.json")
    with open(SCHEMA_PATH, "r") as schema_file:
        REDIS_SCHEMA = json.load(schema_file)

    def validate_redis_data(data, schema_section):
        """Validate Redis data against the schema."""
        try:
            validate(instance=data, schema=REDIS_SCHEMA["properties"][schema_section])
        except ValidationError as e:
            logger.error(f"Redis data validation error: {e.message}")
            raise ValueError(f"Invalid Redis data: {e.message}")

    try:
        with open(redis_json_path, "r") as f:
            default_redis_data = json.load(f)

        # Iterate through the keys and populate Redis
        for key, value in default_redis_data.items():
            if not redis_client.exists(key):
                logger.info(f"Key '{key}' not found in Redis. Adding default value.")
                schema_section = "gamestate:default" if key == "gamestate:default" else "gamestate:<user_id>"
                validate_redis_data(value, schema_section)
                if isinstance(value, dict):
                    # Serialize the dictionary to a JSON string
                    redis_client.set(key, json.dumps(value))
                else:
                    redis_client.set(key, value)
            else:
                logger.debug(f"Key '{key}' already exists in Redis. Skipping.")

    except Exception as e:
        logger.error(f"Error populating Redis with default values: {e}", exc_info=True)