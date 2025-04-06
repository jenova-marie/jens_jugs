import click
import subprocess
from pathlib import Path
import os
import json
from dotenv import load_dotenv
import boto3
import sys
from jens_jugs.relay_server import create_app
from jens_jugs.prompt_augmentation import build_augmented_prompt
import jens_jugs.redis_gamestate as redis_gamestate
from jens_jugs.jwt_auth import jwt_verify  # Import jwt_verify
from jens_jugs.auth_service import auth_bp  # Import auth_bp
from jens_jugs.rule_evaluator import run_game_rules  # Import run_game_rules
from jens_jugs.cloudwatch_logger import get_logger  # Import get_logger

def get_aws_secret_manager_value(secret_name):
    """Retrieve a secret value from AWS Secrets Manager."""
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")

def log_uncaught_exceptions(exc_type, exc_value, exc_traceback):
    """Log uncaught exceptions to CloudWatch."""
    logger = get_logger(log_name="global")
    logger.error("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))

# Set the global exception handler
sys.excepthook = log_uncaught_exceptions

@click.group()
@click.option("--local-env", is_flag=True, help="Use local environment variables.")
@click.pass_context
def cli(ctx, local_env):
    """Jens Jugs CLI 💋"""
    ctx.ensure_object(dict)
    ctx.obj["local_env"] = local_env

    # Load .env file for local development
    load_dotenv()

@cli.command()
@click.option("--secret", default="JensJugs/Api/Local/Dev", help="AWS Secrets Manager secret name.")
@click.option("--log-reset", is_flag=True, help="Reset the CloudWatch log stream.")
@click.option("--debug", is_flag=True, help="Enable debug mode for the relay server.")
@click.pass_context
def start(ctx, secret, log_reset, debug):
    """Start the relay server."""
    local_env = ctx.obj["local_env"]
    secret_name = secret

    if not local_env:
        try:
            secret_json = get_aws_secret_manager_value(secret_name)
            secret = json.loads(secret_json)
            # Convert all values to strings before updating os.environ
            secret = {key: str(value) for key, value in secret.items()}
            os.environ.update(secret)
            click.echo(
                f"ENV: AWS Secret Manager - {secret_name} LOADED: {len(secret)} env vars"
            )
        except Exception as e:
            click.echo(
                f"ENV: AWS Secret Manager - {secret_name} ERROR: {e}", err=True
            )
            raise click.ClickException("Failed to load secrets from AWS Secrets Manager")
    else:
        os.environ["SECRET_NAME"] = secret_name

    # Pass the log-reset flag to the logger
    os.environ["LOG_RESET"] = str(log_reset)

    # Pass the debug flag to the relay server
    os.environ["DEBUG_MODE"] = str(debug)

    # Create the Flask app with dependencies
    app = create_app(
        jwt_verify=jwt_verify,
        auth_bp=auth_bp,
        run_game_rules=run_game_rules,
        get_logger=get_logger,
        build_prompt=build_augmented_prompt,
        redis_gamestate=redis_gamestate,
    )

    # Start the Flask app
    port = int(os.getenv("API_PORT_HTTP", 6000))  # Default to port 6000 if API_PORT_HTTP is not set
    click.echo(f"🚀 Starting relay server on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=debug, use_reloader=False)

if __name__ == "__main__":
    cli()
