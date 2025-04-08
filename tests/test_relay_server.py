import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from jens_jugs.relay_server import create_app
from tests.test_base import BaseTestCase  # Import BaseTestCase

class TestRelayServer(BaseTestCase):  # Derive from BaseTestCase
    def setUp(self):
        super().setUp()  # Call BaseTestCase's setUp to initialize mocks

    @patch("jens_jugs.redis_gamestate.set_game_state")
    @patch("jens_jugs.redis_gamestate.get_game_state")
    @patch("jens_jugs.rule_evaluator.run_game_rules")
    @patch("jens_jugs.prompt_augmentation.build_prompt")
    def test_valid_request(self, mock_build_prompt, mock_run_game_rules, mock_get_game_state, mock_set_game_state):
        # Configure the mocks
        mock_get_game_state.return_value = {"trust": 50}
        mock_set_game_state.return_value = None
        mock_run_game_rules.return_value = {"trust": 60}
        mock_build_prompt.return_value = "Augmented prompt"

        # Create a mock OpenAI client
        mock_openai_client = MagicMock()
        mock_response = MagicMock()
        mock_choice = MagicMock()
        mock_message = MagicMock()

        # Set up the mock response structure
        mock_message.content = "This is a valid response from OpenAI."
        mock_choice.message = mock_message
        mock_response.choices = [mock_choice]
        mock_openai_client.chat.completions.create.return_value = mock_response

        # Create the app using the mocks from BaseTestCase
        self.app = create_app(
            jwt_verify=self.mock_jwt_verify,
            auth_bp=self.mock_auth_bp,
            run_game_rules=self.mock_run_game_rules,
            get_logger=lambda log_name, **kwargs: self.local_logger,
            build_prompt=self.mock_build_prompt,
            redis_gamestate=self.mock_redis_gamestate,
            openai_client=mock_openai_client,
        )
        self.client = self.app.test_client()

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

        # Debugging output
        self.local_logger.info(f"Response status code: {response.status_code}")
        self.local_logger.info(f"Response JSON: {response.json}")

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json,
            {"response": "This is a valid response from OpenAI."},
        )


if __name__ == "__main__":
    unittest.main()
