import unittest
from unittest.mock import patch, MagicMock
from flask import Flask

from jens_jugs import relay_server  # Correct import path

class TestRelayServer(unittest.TestCase):
    def setUp(self):
        # Set up the Flask test client
        self.app = relay_server.app
        self.client = self.app.test_client()

    @patch("jens_jugs.relay_server.run_game_rules")
    @patch("jens_jugs.relay_server.build_augmented_prompt")
    def test_valid_request(self, mock_build_prompt, mock_run_rules):
        # Mock dependencies
        mock_redis_gamestate = MagicMock()
        mock_redis_gamestate.get_or_create_game_state.return_value = {"trust": 50}
        mock_redis_gamestate.set_game_state.return_value = None
        mock_run_rules.return_value = {"trust": 60}
        mock_build_prompt.return_value = "Augmented prompt"

        # Simulate a valid request
        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json)
        self.assertEqual(response.json["response"], "Mock response")
        mock_redis_gamestate.get_or_create_game_state.assert_called_once_with("user123")
        mock_run_rules.assert_called_once_with({"trust": 50}, [{"rule": "increase trust"}])
        mock_redis_gamestate.set_game_state.assert_called_once_with("user123", {"trust": 60})
        mock_build_prompt.assert_called_once_with("Hello", {"trust": 60})

    @patch("jens_jugs.relay_server.build_augmented_prompt")
    def test_valid_request_with_mock_prompt(self, mock_build_prompt):
        # Mock the build_augmented_prompt function
        mock_build_prompt.return_value = "Mocked augmented prompt"

        # Simulate a valid request
        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("response", response.json)
        self.assertEqual(response.json["response"], "Mock response")
        mock_build_prompt.assert_called_once_with("Hello", {"trust": 50})

    def test_missing_user_id(self):
        # Simulate a request with missing userId
        response = self.client.post(
            "/api/chat",
            json={
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Missing userId")

    def test_missing_messages(self):
        # Simulate a request with missing messages
        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Missing messages")

    def test_invalid_json(self):
        # Simulate a request with invalid JSON
        response = self.client.post(
            "/api/chat",
            data="Invalid JSON",
            headers={"Authorization": "Bearer valid-token", "Content-Type": "application/json"},
        )

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Invalid JSON format")

    @patch("relay_server.get_or_create_game_state", side_effect=Exception("Game state error"))
    def test_game_state_error(self, mock_get_state):
        # Simulate a request that triggers a game state error
        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to retrieve or create game state")
        mock_get_state.assert_called_once_with("user123")

    @patch("relay_server.OpenAI")
    def test_openai_api_error(self, mock_openai):
        # Simulate an OpenAI API error
        mock_openai.return_value.chat.completions.create.side_effect = Exception("OpenAI error")

        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Unexpected error while calling OpenAI API")
        mock_openai.return_value.chat.completions.create.assert_called_once()

    @patch("relay_server.build_augmented_prompt", side_effect=Exception("Augmentation error"))
    def test_augmentation_error(self, mock_build_prompt):
        # Simulate an error during message augmentation
        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
            headers={"Authorization": "Bearer valid-token"},
        )

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertIn("error", response.json)
        self.assertEqual(response.json["error"], "Failed to augment system message")
        mock_build_prompt.assert_called_once_with("Hello", {"trust": 50})

    def test_missing_authorization_header(self):
        # Simulate a request without an Authorization header
        response = self.client.post(
            "/api/chat",
            json={
                "userId": "user123",
                "messages": [{"role": "system", "content": "Hello"}],
                "rules": [{"rule": "increase trust"}],
            },
        )

        # Assertions
        self.assertEqual(response.status_code, 401)
        self.assertIn("message", response.json)
        self.assertEqual(response.json["message"], "Authorization token is missing")

if __name__ == "__main__":
    unittest.main()
