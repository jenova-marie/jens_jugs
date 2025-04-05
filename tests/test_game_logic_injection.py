import unittest
from game_logic_injection import evaluate_game_state_for_triggers

class TestGameLogicInjection(unittest.TestCase):

    def test_trigger_unlocked(self):
        game_state = {
            "trust": 80,
            "visited": True,
            "clues": ["code_sheet"]
        }
        result = evaluate_game_state_for_triggers(game_state)
        self.assertIn("unlockedMemory", result)

if __name__ == '__main__':
    unittest.main()
