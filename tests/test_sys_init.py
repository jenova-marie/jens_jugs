import pytest
from unittest.mock import MagicMock, patch, mock_open
from jens_jugs.sys_init import populate_redis_with_defaults


@patch("jens_jugs.sys_init.get_logger")
@patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1", "key2": {"nested_key": "nested_value"}}')
@patch("jens_jugs.sys_init.os.path.join", return_value="/mock/path/redis.json")
@patch("jens_jugs.sys_init.os.path.dirname", return_value="/mock/path")
def test_populate_redis_with_defaults(mock_dirname, mock_join, mock_open_file, mock_get_logger):
    """Test that missing keys are added to Redis with default values."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_redis_client = MagicMock()
    mock_redis_client.exists.side_effect = lambda key: key == "key1"

    populate_redis_with_defaults(mock_redis_client, logger=mock_logger)

    mock_redis_client.exists.assert_any_call("key1")
    mock_redis_client.exists.assert_any_call("key2")
    mock_redis_client.set.assert_called_once_with("key2", '{"nested_key": "nested_value"}')
    mock_logger.info.assert_any_call("Key 'key2' not found in Redis. Adding default value.")


@patch("jens_jugs.sys_init.get_logger")
@patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
@patch("jens_jugs.sys_init.os.path.join", return_value="/mock/path/redis.json")
@patch("jens_jugs.sys_init.os.path.dirname", return_value="/mock/path")
def test_populate_redis_with_defaults_file_not_found(mock_dirname, mock_join, mock_open_file, mock_get_logger):
    """Test that a FileNotFoundError is logged when the defaults file is missing."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_redis_client = MagicMock()

    # Simulate file not found
    mock_open_file.side_effect = FileNotFoundError

    populate_redis_with_defaults(mock_redis_client, logger=mock_logger)

    mock_logger.error.assert_called_once_with(
        "Error populating Redis with default values: ",
        exc_info=True
    )


@patch("jens_jugs.sys_init.get_logger")
@patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
@patch("jens_jugs.sys_init.os.path.join", return_value="/mock/path/redis.json")
@patch("jens_jugs.sys_init.os.path.dirname", return_value="/mock/path")
def test_populate_redis_with_defaults_invalid_json(mock_dirname, mock_join, mock_open_file, mock_get_logger):
    """Test that invalid JSON in the defaults file is logged as an error."""
    mock_logger = MagicMock()
    mock_get_logger.return_value = mock_logger
    mock_redis_client = MagicMock()

    # Simulate invalid JSON
    mock_open_file.return_value.read.side_effect = ValueError("Invalid JSON")

    populate_redis_with_defaults(mock_redis_client, logger=mock_logger)

    mock_logger.error.assert_called_once()
    logged_message = mock_logger.error.call_args[0][0]
    assert logged_message.startswith("Error populating Redis with default values: ")
    assert "Invalid JSON" in logged_message