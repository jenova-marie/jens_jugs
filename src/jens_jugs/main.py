import click
import os
import json
import redis
from dotenv import load_dotenv
import boto3
import sys
from jens_jugs.relay_server import create_app
from jens_jugs.logger import get_logger
from jens_jugs.sys_init import populate_redis_with_defaults
from openai import OpenAI  # Assuming OpenAI is the correct client library

# Initialize the logger
logger = get_logger(log_name="main", streams=["console", "cloudwatch", "file"], config={
    "file": {
        "path": "./logs",
        "max_bytes": 10 * 1024 * 1024,  # 10 MB
        "backup_count": 5
    }
})

def get_aws_secret_manager_value(secret_name):
    """
    Retrieve a secret value from AWS Secrets Manager.

    Args:
        secret_name (str): The name of the secret in AWS Secrets Manager.

    Returns:
        str: The secret value as a JSON string.

    Raises:
        RuntimeError: If the secret cannot be retrieved.
    """
    logger.debug(f"Attempting to retrieve secret: {secret_name}")
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
        logger.debug(f"Successfully retrieved secret: {secret_name}")
        return response["SecretString"]
    except Exception as e:
        logger.error(f"Failed to retrieve secret: {e}")
        raise RuntimeError(f"Failed to retrieve secret: {e}")

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """
    Log uncaught exceptions to CloudWatch.

    Args:
        exc_type: Exception type.
        exc_value: Exception value.
        exc_traceback: Exception traceback.
    """
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the global exception handler
sys.excepthook = log_uncaught_exceptions

@click.group()
@click.option("--local-env", is_flag=True, help="Use local environment variables.")
@click.pass_context
def cli(ctx, local_env):
    """
    CLI entry point for Jens Jugs.

    Args:
        ctx: Click context object.
        local_env (bool): Whether to use local environment variables.
    """
    ctx.ensure_object(dict)
    ctx.obj["local_env"] = local_env

    # Load .env file for local development
    logger.debug("Loading environment variables from .env file")
    load_dotenv()

@cli.command()
@click.option("--secret", default="JensJugs/Api/Local/Dev", help="AWS Secrets Manager secret name.")
@click.option("--log-reset", is_flag=True, help="Reset the CloudWatch log stream.")
@click.option("--debug", is_flag=True, help="Enable debug mode for the relay server.")
@click.pass_context
def start(ctx, secret, log_reset, debug):
    """
    Start the relay server.

    Args:
        ctx: Click context object.
        secret (str): AWS Secrets Manager secret name.
        log_reset (bool): Whether to reset the CloudWatch log stream.
        debug (bool): Whether to enable debug mode.
    """
    local_env = ctx.obj["local_env"]
    secret_name = secret

    if not local_env:
        try:
            logger.debug(f"Loading secrets from AWS Secrets Manager: {secret_name}")
            secret_json = get_aws_secret_manager_value(secret_name)
            secret = json.loads(secret_json)
            # Convert all values to strings before updating os.environ
            secret = {key: str(value) for key, value in secret.items()}
            os.environ.update(secret)
            click.echo(f"ENV: AWS Secret Manager - {secret_name} LOADED: {len(secret)} env vars")
        except Exception as e:
            logger.error(f"Failed to load secrets from AWS Secrets Manager: {e}")
            raise click.ClickException("Failed to load secrets from AWS Secrets Manager")
    else:
        os.environ["SECRET_NAME"] = secret_name

    # Pass the log-reset flag to the logger
    os.environ["LOG_RESET"] = str(log_reset)
    logger.debug(f"LOG_RESET set to: {log_reset}")

    # Pass the debug flag to the relay server
    os.environ["DEBUG_MODE"] = str(debug)
    logger.debug(f"DEBUG_MODE set to: {debug}")

    # Create required logger
    logger.info("Populating Redis with default values...")

    # Initialize Redis and populate defaults
    try:
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = int(os.getenv("REDIS_PORT", 6379))
        logger.debug(f"Connecting to Redis at {redis_host}:{redis_port}")
        redis_client = redis.Redis(host=redis_host, port=redis_port, decode_responses=True)
        # Test Redis connection
        redis_client.ping()
        logger.debug("Successfully connected to Redis")
    except redis.ConnectionError as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise click.ClickException("Redis connection failed. Ensure Redis is running and accessible.")

    try:
        # Populate Redis with default or updated data if required
        logger.debug("Populating Redis with default values")
        populate_redis_with_defaults(redis_client, logger)
    except Exception as e:
        logger.error(f"Failed to populate Redis with default values: {e}")
        raise click.ClickException("Failed to populate Redis with default values.")

    # Create the OpenAI client
    try:
        openai_api_key = os.getenv("OPENAPI_KEY")
        if not openai_api_key:
            raise EnvironmentError("OPENAPI_KEY is not set in the environment variables.")
        logger.debug("Initializing OpenAI client")
        openai_client = OpenAI(api_key=openai_api_key)
    except Exception as e:
        logger.error(f"Failed to initialize OpenAI client: {e}")
        raise click.ClickException("Failed to initialize OpenAI client. Check your API key.")

    # Create the Flask app with the OpenAI client
    try:
        logger.debug("Creating Flask app")
        app = create_app(openai_client, redis_client, get_logger)
    except Exception as e:
        logger.error(f"Failed to create the Flask app: {e}")
        raise click.ClickException("Failed to create the Flask app.")

    # Start the Flask app
    try:
        port = int(os.getenv("API_PORT_HTTP", 6000))  # Default to port 6000 if API_PORT_HTTP is not set
        logger.debug(f"Starting Flask app on port {port}")
        click.echo(f"🚀 Starting relay server on port {port}...")
        app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    except Exception as e:
        logger.error(f"Failed to start the Flask app: {e}")
        raise click.ClickException("Failed to start the Flask app.")

if __name__ == "__main__":
    cli()
