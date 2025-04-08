import unittest
from jens_jugs.prompt_augmentation import build_prompt
from tests.test_base import BaseTestCase

class TestPromptAugmentation(BaseTestCase):

    def test_build_prompt_with_full_state(self):
        base_prompt = "Welcome to the game!"
        state = {
            "level": 5,
            "points": 120,
            "emotionalEchoes": ["joy", "fear"],
            "narrativeEvents": ["Found a key", "Opened a door", "Defeated a monster"]
        }

        result = build_prompt(base_prompt, state)

        expected_summary = (
            "Current Level: 5Points: 120\n"
            "Emotional Echoes: ['joy', 'fear']\n"
            "Recent Events:\n"
            "- Found a key\n"
            "- Opened a door\n"
            "- Defeated a monster"
        )
        self.assertIn(base_prompt, result)
        self.assertIn("[Game State Summary]", result)
        self.assertIn(expected_summary, result)

    def test_build_prompt_with_partial_state(self):
        base_prompt = "Welcome to the game!"
        state = {
            "level": 2,
            "points": 50,
        }

        result = build_prompt(base_prompt, state)

        expected_summary = (
            "Current Level: 2Points: 50\n"
            "Emotional Echoes: []"
        )
        self.assertIn(base_prompt, result)
        self.assertIn("[Game State Summary]", result)
        self.assertIn(expected_summary, result)

    def test_build_prompt_with_empty_state(self):
        base_prompt = "Welcome to the game!"
        state = {}

        result = build_prompt(base_prompt, state)

        expected_summary = (
            "Current Level: UnknownPoints: 0\n"
            "Emotional Echoes: []"
        )
        self.assertIn(base_prompt, result)
        self.assertIn("[Game State Summary]", result)
        self.assertIn(expected_summary, result)

    def test_build_prompt_with_none_state(self):
        base_prompt = "Welcome to the game!"

        result = build_prompt(base_prompt, None)

        expected_summary = (
            "Current Level: UnknownPoints: 0\n"
            "Emotional Echoes: []"
        )
        self.assertIn(base_prompt, result)
        self.assertIn("[Game State Summary]", result)
        self.assertIn(expected_summary, result)

    def test_build_prompt_with_long_narrative_events(self):
        base_prompt = "Welcome to the game!"
        state = {
            "narrativeEvents": [
                "Event 1", "Event 2", "Event 3", "Event 4", "Event 5", "Event 6"
            ]
        }

        result = build_prompt(base_prompt, state)

        expected_events = (
            "- Event 2\n"
            "- Event 3\n"
            "- Event 4\n"
            "- Event 5\n"
            "- Event 6"
        )
        self.assertIn(base_prompt, result)
        self.assertIn("[Game State Summary]", result)
        self.assertIn(expected_events, result)

if __name__ == "__main__":
    unittest.main()