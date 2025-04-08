import unittest
from unittest.mock import MagicMock
from flask import Blueprint
from jens_jugs.relay_server import create_app
from jens_jugs.logger import get_logger  # Use the real RedNeckLogger
import os  # Import os to set environment variables

class BaseTestCase(unittest.TestCase):
    def setUp(self):
        # Set required environment variables for the logger
        os.environ["APP_ENV"] = "test"
        os.environ["CLOUDWATCH_GROUP_NAME"] = "Test/Group"
        os.environ["LOG_STREAM"] = "test_logger_stream"
        os.environ["DEBUG_MODE"] = "True"
        os.environ["CLOUDWATCH_STREAM_DURATION"] = "7"
        os.environ["LOG_RESET"] = "True"
        os.environ["AWS_REGION"] = "us-east-1"
        os.environ["OPENAPI_KEY"] = "abc123"
        os.environ["API_PORT_HTTP"] = "6000"  # Set to "local" for local-only logging
        os.environ["API_AUTH_KEY"] = "1234567890"
        # os.environ["LOG_CONFIG"] = ""

        # Mock dependencies
        self.mock_jwt_verify = MagicMock()
        self.mock_jwt_verify.__name__ = "jwt_verify"  # Add __name__ attribute to the mock

        # Mock jwt_verify to behave as a pass-through decorator
        def jwt_verify_decorator(func):
            def wrapper(*args, **kwargs):
                return func(*args, **kwargs)
            wrapper.__name__ = func.__name__
            return wrapper

        self.mock_jwt_verify.side_effect = jwt_verify_decorator

        # Mock Redis GameState
        self.mock_redis_gamestate = MagicMock()
        self.mock_redis_gamestate.get_game_state = MagicMock()
        self.mock_redis_gamestate.set_game_state = MagicMock()

        # Mock run_game_rules and build_prompt
        self.mock_run_game_rules = MagicMock()
        self.mock_build_prompt = MagicMock()

        # Mock OpenAI client
        self.mock_openai_client = MagicMock()
        self.mock_openai_client.return_value = self.mock_openai_client

        # Mock Flask Blueprint
        self.mock_auth_bp = Blueprint("auth", __name__)  # Use a real Flask Blueprint

        # Use the real RedNeckLogger with local-only logging
        self.local_logger = get_logger(log_name="test", streams=["console", "file"], config={
                    "file": {
                        "path": "./tests/logs",
                        "max_bytes": 10 * 1024 * 1024,  # 10 MB
                        "backup_count": 5
                    }
                })


if __name__ == "__main__":
    unittest.main()
