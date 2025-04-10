import json
import pytest
from unittest.mock import MagicMock, patch
from jens_jugs.redis_gamestate import load_default_gamestate, get_game_state, set_game_state


@patch("jens_jugs.redis_gamestate.DEFAULT_REDIS_DATA", {"gamestate:default": {"health": 100, "score": 0, "inventory": [], "unlocked_clues": [], "narrativeEvents": []}})
def test_load_default_gamestate():
    """Test loading the default game state successfully."""
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None  # Simulate missing default game state in Redis

    result = load_default_gamestate(mock_redis_client)

    mock_redis_client.set.assert_called_once_with(
        "gamestate:default",
        json.dumps({"health": 100, "score": 0, "inventory": [], "unlocked_clues": [], "narrativeEvents": []}),
    )
    assert result == {"health": 100, "score": 0, "inventory": [], "unlocked_clues": [], "narrativeEvents": []}


@patch("jens_jugs.redis_gamestate.load_default_gamestate")
@patch("jens_jugs.redis_gamestate.redis.Redis")
def test_get_game_state_existing_user(mock_redis, mock_load_default_gamestate):
    """Test retrieving the game state for an existing user."""
    # Mock Redis client and user game state
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = '{"health": 80, "score": 10}'

    # Call the function
    with patch("jens_jugs.redis_gamestate.r", mock_redis_client):
        result = get_game_state("user123")

    # Assertions
    mock_redis_client.get.assert_called_once_with("gamestate:user123")
    assert result == {"health": 80, "score": 10}


def test_get_game_state_new_user():
    """Test retrieving the game state for a new user."""
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None  # Simulate missing user game state in Redis

    result = get_game_state("new_user", mock_redis_client)

    mock_redis_client.set.assert_called_once()
    assert result == {"health": 100, "score": 0, "inventory": [], "unlocked_clues": [], "narrativeEvents": []}


@patch("jens_jugs.redis_gamestate.redis.Redis")
def test_set_game_state(mock_redis):
    """Test setting the game state for a user."""
    mock_redis_client = MagicMock()

    with patch("jens_jugs.redis_gamestate.r", mock_redis_client):
        set_game_state("user123", {"health": 90, "score": 20})

    mock_redis_client.set.assert_called_once_with("gamestate:user123", '{"health": 90, "score": 20}')


def test_set_game_state():
    """Test setting the game state for a user."""
    mock_redis_client = MagicMock()

    valid_game_state = {"health": 90, "score": 20, "inventory": [], "unlocked_clues": [], "narrativeEvents": []}
    set_game_state("user123", valid_game_state, mock_redis_client)

    mock_redis_client.set.assert_called_once_with("gamestate:user123", json.dumps(valid_game_state))