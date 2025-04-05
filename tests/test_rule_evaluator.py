import unittest
from rule_evaluator import apply_action, evaluate_condition, run_game_rules

class TestRuleEvaluator(unittest.TestCase):

    def test_apply_action_set(self):
        state = {}
        action = {"type": "set", "field": "mood", "value": "curious"}
        apply_action(state, action)
        self.assertEqual(state["mood"], "curious")

    def test_apply_action_increase(self):
        state = {"points": 5}
        action = {"type": "increase", "field": "points", "amount": 10}
        apply_action(state, action)
        self.assertEqual(state["points"], 15)

    def test_apply_action_decrease(self):
        state = {"suspicion": 10}
        action = {"type": "decrease", "field": "suspicion", "amount": 3}
        apply_action(state, action)
        self.assertEqual(state["suspicion"], 7)

    def test_apply_action_add_to_array(self):
        state = {}
        action = {"type": "addToArray", "field": "clues", "value": "bloody_mirror"}
        apply_action(state, action)
        self.assertIn("bloody_mirror", state["clues"])

    def test_apply_action_add_narrative(self):
        state = {}
        action = {"type": "addNarrative", "scene": "bathroom_reveal"}
        apply_action(state, action)
        self.assertIn("bathroom_reveal", state["narrativeEvents"])

    def test_evaluate_condition_all_true(self):
        state = {"trust": 30, "visited": True}
        condition = {
            "all": [
                {"field": "trust", "operator": ">=", "value": 20},
                {"field": "visited", "operator": "==", "value": True}
            ]
        }
        self.assertTrue(evaluate_condition(state, condition))

    def test_evaluate_condition_includes(self):
        state = {"narrativeEvents": ["entry", "questioning"]}
        condition = {
            "all": [
                {"field": "narrativeEvents", "operator": "includes", "value": "questioning"}
            ]
        }
        self.assertTrue(evaluate_condition(state, condition))

    def test_run_game_rules_triggers_action(self):
        state = {"trust": 50}
        rules = [
            {
                "id": "increase_points_if_trust_high",
                "condition": {"all": [{"field": "trust", "operator": ">", "value": 40}]},
                "actions": [
                    {"type": "increase", "field": "points", "amount": 5},
                    {"type": "addToArray", "field": "narrativeEvents", "value": "trust_bonus_triggered"}
                ]
            }
        ]
        run_game_rules(state, rules)
        self.assertEqual(state["points"], 5)
        self.assertIn("trust_bonus_triggered", state["narrativeEvents"])

if __name__ == '__main__':
    unittest.main()
