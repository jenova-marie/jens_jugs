import unittest
from jens_jugs.rule_executor import apply_rules

class RuleExecutorTest(unittest.TestCase):
    def test_set_and_increase(self):
        state = {"score": 5}
        rules = [
            {
                "actions": [
                    {"type": "set", "key": "level", "value": "Detective"},
                    {"type": "increase", "key": "score", "amount": 3}
                ]
            }
        ]
        updated, logs = apply_rules(state, rules)
        self.assertEqual(updated["level"], "Detective")
        self.assertEqual(updated["score"], 8)
        self.assertIn("Set rank to Detective", logs)

if __name__ == '__main__':
    unittest.main()
