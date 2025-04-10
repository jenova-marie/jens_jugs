import os
import pytest

def setup_test_environment():
    """Set up environment variables for testing."""
    os.environ["APP_ENV"] = "Test"
    os.environ["CLOUDWATCH_GROUP_NAME"] = "Test/Group"
    os.environ["LOG_STREAM"] = "test_logger_stream"
    os.environ["DEBUG_MODE"] = "True"
    os.environ["CLOUDWATCH_STREAM_DURATION"] = "7"
    os.environ["LOG_RESET"] = "False"
    os.environ["AWS_REGION"] = "us-east-1"
    os.environ["OPENAPI_KEY"] = "abc123"
    os.environ["API_PORT_HTTP"] = "6000"
    os.environ["API_AUTH_KEY"] = "1234567890"

@pytest.fixture(scope="session", autouse=True)
def test_environment():
    """Fixture to set up the test environment."""
    from .test_env_setup import setup_test_environment
    setup_test_environment()