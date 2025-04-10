import os
import pytest
from unittest.mock import patch, MagicMock
from jens_jugs.relay_server import create_app
from jens_jugs.logger import get_logger


@pytest.fixture
def openai_client():
    """Fixture to create a mocked OpenAI client."""
    mock_openai_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [
        MagicMock(message=MagicMock(content="This is a valid response from OpenAI."))
    ]
    mock_openai_client.chat.completions.create.return_value = mock_completion
    return mock_openai_client

logger = get_logger(log_name="test", streams=["console", "file"], config={
            "file": {
                "path": "./tests/logs",
                "max_bytes": 10 * 1024 * 1024,  # 10 MB
                "backup_count": 5
            }
        });

def get_logger(log_name=None, streams=["console"], level="INFO", config=None):
    """Fixture to create a logger for testing."""
    # All code under test should use this logger for appropriate logging of test data.
    return logger


@pytest.fixture
def app(openai_client):
    """Fixture to create the Flask app for testing."""
    with patch("jens_jugs.relay_server.jwt_verify", lambda f: f), \
         patch("jens_jugs.relay_server.auth_bp"), \
         patch("jens_jugs.relay_server.apply_rules", return_value=(None, [])), \
         patch("jens_jugs.rule_evaluator.run_game_rules", return_value={"trust": 60}):

        # Create the app with the mocked OpenAI client
        app = create_app(openai_client, get_logger)
        yield app


@pytest.fixture
def client(app):
    """Fixture to create a test client for the Flask app."""
    return app.test_client()


@patch("jens_jugs.redis_gamestate.get_game_state")
@patch("jens_jugs.redis_gamestate.set_game_state")
def test_missing_user_id(mock_set_game_state, mock_get_game_state, client):
    """Test a request with a missing userId."""
    mock_get_game_state.return_value = None

    response = client.post(
        "/api/chat",
        json={
            "messages": [{"role": "system", "content": "Hello"}],
            "rules": [{"rule": "increase trust"}],
        },
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 400
    assert response.json == {"error": "Missing userId"}


@patch("jens_jugs.redis_gamestate.get_game_state")
@patch("jens_jugs.redis_gamestate.set_game_state")
def test_redis_connection_failure(mock_set_game_state, mock_get_game_state, client):
    """Test a Redis connection failure."""
    mock_get_game_state.side_effect = Exception("Redis connection error")

    response = client.post(
        "/api/chat",
        json={
            "userId": "user123",
            "messages": [{"role": "system", "content": "Hello"}],
            "rules": [{"rule": "increase trust"}],
        },
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 500
    assert response.json == {"error": "Failed to retrieve game state"}


@patch("jens_jugs.redis_gamestate.get_game_state")
@patch("jens_jugs.redis_gamestate.set_game_state")
@patch("jens_jugs.build_prompt")
def test_build_prompt_failure(mock_build_prompt, mock_set_game_state, mock_get_game_state, client):
    """Test a failure in the build_prompt function."""
    mock_get_game_state.return_value = {"trust": 50}
    mock_build_prompt.side_effect = Exception("Build prompt error")

    response = client.post(
        "/api/chat",
        json={
            "userId": "user123",
            "messages": [{"role": "system", "content": "Hello"}],
            "rules": [{"rule": "increase trust"}],
        },
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 500
    assert response.json == {"error": "Failed to augment system message"}


@patch("jens_jugs.redis_gamestate.get_game_state")
@patch("jens_jugs.redis_gamestate.set_game_state")
def test_valid_request(mock_get_game_state, mock_set_game_state, client):
    """Test a valid request to the /api/chat endpoint."""
    mock_get_game_state.return_value = {"trust": 50}

    response = client.post(
        "/api/chat",
        json={
            "userId": "user123",
            "messages": [{"role": "system", "content": "Hello"}],
            "rules": [
                {
                    "condition": {"field": "trust", "operator": ">", "value": 40},
                    "actions": [{"type": "increase", "key": "trust", "amount": 10}],
                }
            ],
        },
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 200
    assert response.json == {"response": "This is a valid response from OpenAI."}
    mock_set_game_state.assert_called_once_with("user123", {"trust": 60})

@patch("jens_jugs.relay_server.OpenAIError")
def test_openai_error_handling(mock_openai_error, client):
    """Test handling of OpenAI API errors."""
    mock_openai_error.side_effect = Exception("Mocked OpenAIError")

    response = client.post(
        "/api/chat",
        json={
            "userId": "user123",
            "messages": [{"role": "system", "content": "Hello"}],
            "rules": [{"rule": "increase trust"}],
        },
        headers={"Authorization": "Bearer valid-token"},
    )

    assert response.status_code == 500
    assert response.json == {"error": "Mocked OpenAIError"}
