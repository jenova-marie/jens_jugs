import click
import subprocess
from pathlib import Path

@click.group()
def cli():
    """Jens Jugs CLI 💋"""
    pass

@cli.command()
def start():
    """Start the relay server."""
    relay_path = Path(__file__).parent / "relay_server.py"
    if not relay_path.exists():
        click.echo(f"❌ relay_server.py not found at {relay_path}")
        raise click.ClickException("File not found")

    click.echo("🚀 Starting relay server...")
    subprocess.run(["python", str(relay_path)], check=True)

if __name__ == "__main__":
    cli()
