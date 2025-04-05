import unittest
from unittest.mock import patch, AsyncMock
import relay_server

class TestRelayServer(unittest.IsolatedAsyncioTestCase):

    @patch("relay_server.get_game_state", new_callable=AsyncMock)
    @patch("relay_server.set_game_state", new_callable=AsyncMock)
    async def test_relay_process(self, mock_set, mock_get):
        mock_get.return_value = {"trust": 50}

        # Simulate input/output of relay (details will vary)
        user_id = "user123"
        message = "Ask about the scene"
        response = await relay_server.handle_chat(user_id, message)

        self.assertIn("response", response)
        mock_get.assert_called_once()
        mock_set.assert_called_once()

if __name__ == '__main__':
    unittest.main()
