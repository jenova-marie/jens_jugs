import unittest
from unittest.mock import MagicMock, patch, mock_open
from jens_jugs.sys_init import populate_redis_with_defaults
from tests.test_base import BaseTestCase

class TestSysInit(BaseTestCase):
    @patch("jens_jugs.sys_init.get_logger")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1", "key2": {"nested_key": "nested_value"}}')
    @patch("jens_jugs.sys_init.os.path.join", return_value="/mock/path/redis.json")
    @patch("jens_jugs.sys_init.os.path.dirname", return_value="/mock/path")
    def test_populate_redis_with_defaults(self, mock_dirname, mock_join, mock_open_file, mock_get_logger):
        # Mock Redis client
        mock_redis_client = MagicMock()
        mock_redis_client.exists.side_effect = lambda key: key == "key1"  # Simulate "key1" already exists

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Call the function
        populate_redis_with_defaults(mock_redis_client, logger=mock_logger)

        # Assertions for Redis interactions
        mock_redis_client.exists.assert_any_call("key1")
        mock_redis_client.exists.assert_any_call("key2")
        mock_redis_client.set.assert_called_once_with("key2", '{"nested_key": "nested_value"}')

        # Assertions for logger interactions
        mock_logger.info.assert_any_call("Key 'key2' not found in Redis. Adding default value.")
        mock_logger.debug.assert_any_call("Key 'key1' already exists in Redis. Skipping.")

    @patch("jens_jugs.sys_init.get_logger")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
    @patch("jens_jugs.sys_init.os.path.join", return_value="/mock/path/redis.json")
    @patch("jens_jugs.sys_init.os.path.dirname", return_value="/mock/path")
    def test_populate_redis_with_defaults_file_not_found(self, mock_dirname, mock_join, mock_open_file, mock_get_logger):
        # Mock Redis client
        mock_redis_client = MagicMock()

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Simulate file not found
        mock_open_file.side_effect = FileNotFoundError

        # Call the function
        populate_redis_with_defaults(mock_redis_client, logger=mock_logger)

        # Assertions for logger interactions
        mock_logger.error.assert_called_once_with(
            "Error populating Redis with default values: ",
            exc_info=True
        )

    @patch("jens_jugs.sys_init.get_logger")
    @patch("builtins.open", new_callable=mock_open, read_data='{"key1": "value1"}')
    @patch("jens_jugs.sys_init.os.path.join", return_value="/mock/path/redis.json")
    @patch("jens_jugs.sys_init.os.path.dirname", return_value="/mock/path")
    def test_populate_redis_with_defaults_invalid_json(self, mock_dirname, mock_join, mock_open_file, mock_get_logger):
        # Mock Redis client
        mock_redis_client = MagicMock()

        # Mock logger
        mock_logger = MagicMock()
        mock_get_logger.return_value = mock_logger

        # Simulate invalid JSON
        mock_open_file.return_value.read.side_effect = ValueError("Invalid JSON")

        # Call the function
        populate_redis_with_defaults(mock_redis_client, logger=mock_logger)

        # Assertions for logger interactions
        mock_logger.error.assert_called_once()
        logged_message = mock_logger.error.call_args[0][0]
        self.assertTrue(logged_message.startswith("Error populating Redis with default values: "))
        self.assertIn("Invalid JSON", logged_message)


if __name__ == "__main__":
    unittest.main()