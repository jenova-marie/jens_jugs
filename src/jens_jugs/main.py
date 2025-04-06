import click
import subprocess
from pathlib import Path
import os
import json
from dotenv import load_dotenv
import boto3

def get_aws_secret_manager_value(secret_name):
    """Retrieve a secret value from AWS Secrets Manager."""
    client = boto3.client("secretsmanager")
    try:
        response = client.get_secret_value(SecretId=secret_name)
        return response["SecretString"]
    except Exception as e:
        raise RuntimeError(f"Failed to retrieve secret: {e}")

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
@click.option("--secret", default="RecoverySky/Core/Prod", help="AWS Secrets Manager secret name.")
@click.pass_context
def start(ctx, secret):
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

    relay_path = Path(__file__).parent / "relay_server.py"
    if not relay_path.exists():
        click.echo(f"❌ relay_server.py not found at {relay_path}")
        raise click.ClickException("File not found")

    click.echo("🚀 Starting relay server...")
    subprocess.run(["python", str(relay_path)], check=True)

if __name__ == "__main__":
    cli()
