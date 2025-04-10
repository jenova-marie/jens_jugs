import pytest
from unittest.mock import MagicMock, patch
from jens_jugs.redis_gamestate import load_default_gamestate, get_game_state, set_game_state


@patch("jens_jugs.redis_gamestate.json.loads")
@patch("jens_jugs.redis_gamestate.redis.Redis")
def test_load_default_gamestate_success(mock_redis, mock_json_loads):
    """Test loading the default game state successfully."""
    # Mock Redis client and default game state
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = '{"health": 100, "score": 0}'
    mock_json_loads.return_value = {"health": 100, "score": 0}

    # Call the function
    result = load_default_gamestate(mock_redis_client)

    # Assertions
    mock_redis_client.get.assert_called_once_with("gamestate:default")
    mock_json_loads.assert_called_once_with('{"health": 100, "score": 0}')
    assert result == {"health": 100, "score": 0}

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


@patch("jens_jugs.redis_gamestate.load_default_gamestate")
@patch("jens_jugs.redis_gamestate.redis.Redis")
def test_get_game_state_new_user(mock_redis, mock_load_default_gamestate):
    """Test retrieving the game state for a new user."""
    # Mock Redis client and default game state
    mock_redis_client = MagicMock()
    mock_redis_client.get.return_value = None
    mock_load_default_gamestate.return_value = {"health": 100, "score": 0}

    # Call the function
    with patch("jens_jugs.redis_gamestate.r", mock_redis_client):
        result = get_game_state("new_user")

    # Assertions
    mock_redis_client.get.assert_called_once_with("gamestate:new_user")
    mock_load_default_gamestate.assert_called_once_with(mock_redis_client)
    mock_redis_client.set.assert_called_once_with("gamestate:new_user", '{"health": 100, "score": 0}')
    assert result == {"health": 100, "score": 0}


@patch("jens_jugs.redis_gamestate.redis.Redis")
def test_set_game_state(mock_redis):
    """Test setting the game state for a user."""
    # Mock Redis client
    mock_redis_client = MagicMock()

    # Call the function
    with patch("jens_jugs.redis_gamestate.r", mock_redis_client):
        set_game_state("user123", {"health": 90, "score": 20})

    # Assertions
    mock_redis_client.set.assert_called_once_with("gamestate:user123", '{"health": 90, "score": 20}')