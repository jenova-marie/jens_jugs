import pytest
from unittest.mock import patch
from src.jens_jugs.game_logic_injection import evaluate_game_state_for_triggers
from tests.test_base import BaseTestCase

class TestGameLogicInjection(BaseTestCase):
    @patch("jens_jugs.game_logic_injection.get_logger")
    def test_no_triggers_or_secrets(self, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        game_state = {"trustLevel": 10}
        results = evaluate_game_state_for_triggers(game_state)
        assert results == {"secretsUnlocked": [], "eventsTriggered": []}
        assert "hiddenMemory" not in game_state

    @patch("jens_jugs.game_logic_injection.get_logger")
    def test_unlock_hidden_memory(self, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        game_state = {"trustLevel": 60}
        results = evaluate_game_state_for_triggers(game_state)
        assert results == {
            "secretsUnlocked": ["Claudette's past revealed"],
            "eventsTriggered": ["New dialogue unlocked for Claudette"],
        }
        assert game_state["hiddenMemory"] is True