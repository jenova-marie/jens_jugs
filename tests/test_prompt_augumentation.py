import unittest
from prompt_augmentation import build_augmented_prompt

class TestPromptAugmentation(unittest.TestCase):

    def test_prompt_builds_with_state(self):
        base_prompt = "Describe the scene."
        game_state = {
            "playerName": "Jenova",
            "cluesFound": ["rose_petals", "broken_glass"],
            "narrativeEvents": ["found_body"]
        }
        result = build_augmented_prompt(base_prompt, game_state)
        self.assertIn("Jenova", result)
        self.assertIn("rose_petals", result)
        self.assertIn("found_body", result)

if __name__ == '__main__':
    unittest.main()