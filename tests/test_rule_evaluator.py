import unittest
from jens_jugs.rule_evaluator import apply_action, evaluate_condition, run_game_rules
from tests.test_base import BaseTestCase

class TestRuleEvaluator(BaseTestCase):

    def test_apply_action_set(self):
        game_state = {"health": 50}
        action = {"type": "set", "field": "health", "value": 100}
        apply_action(game_state, action)
        self.assertEqual(game_state["health"], 100)

    def test_apply_action_increase(self):
        game_state = {"score": 10}
        action = {"type": "increase", "field": "score", "amount": 5}
        apply_action(game_state, action)
        self.assertEqual(game_state["score"], 15)

    def test_apply_action_decrease(self):
        game_state = {"score": 10}
        action = {"type": "decrease", "field": "score", "amount": 3}
        apply_action(game_state, action)
        self.assertEqual(game_state["score"], 7)

    def test_apply_action_add_narrative(self):
        game_state = {}
        action = {"type": "addNarrative", "scene": "scene1"}
        apply_action(game_state, action)
        self.assertIn("scene1", game_state["narrativeEvents"])

    def test_apply_action_add_to_array(self):
        game_state = {}
        action = {"type": "addToArray", "field": "inventory", "value": "sword"}
        apply_action(game_state, action)
        self.assertIn("sword", game_state["inventory"])

    def test_apply_action_unknown_type(self):
        game_state = {}
        action = {"type": "unknown", "field": "health", "value": 100}
        apply_action(game_state, action)
        self.assertNotIn("health", game_state)  # No changes should be made

    def test_evaluate_condition_all_true(self):
        game_state = {"health": 50, "score": 10}
        condition = {"all": [{"field": "health", "operator": ">", "value": 40}, {"field": "score", "operator": "==", "value": 10}]}
        result = evaluate_condition(game_state, condition)
        self.assertTrue(result)

    def test_evaluate_condition_all_false(self):
        game_state = {"health": 30, "score": 10}
        condition = {"all": [{"field": "health", "operator": ">", "value": 40}, {"field": "score", "operator": "==", "value": 10}]}
        result = evaluate_condition(game_state, condition)
        self.assertFalse(result)

    def test_evaluate_condition_any_true(self):
        game_state = {"health": 30, "score": 10}
        condition = {"any": [{"field": "health", "operator": ">", "value": 40}, {"field": "score", "operator": "==", "value": 10}]}
        result = evaluate_condition(game_state, condition)
        self.assertTrue(result)

    def test_evaluate_condition_any_false(self):
        game_state = {"health": 30, "score": 5}
        condition = {"any": [{"field": "health", "operator": ">", "value": 40}, {"field": "score", "operator": "==", "value": 10}]}
        result = evaluate_condition(game_state, condition)
        self.assertFalse(result)

    def test_evaluate_condition_includes(self):
        game_state = {"inventory": ["sword", "shield"]}
        condition = {"all": [{"field": "inventory", "operator": "includes", "value": "sword"}]}
        result = evaluate_condition(game_state, condition)
        self.assertTrue(result)

    def test_run_game_rules(self):
        game_state = {"health": 50, "score": 10}
        rules = [
            {
                "condition": {"all": [{"field": "health", "operator": ">", "value": 40}]},
                "actions": [{"type": "increase", "field": "score", "amount": 5}]
            },
            {
                "condition": {"all": [{"field": "score", "operator": "==", "value": 15}]},
                "actions": [{"type": "set", "field": "health", "value": 100}]
            }
        ]
        run_game_rules(game_state, rules)
        self.assertEqual(game_state["health"], 100)
        self.assertEqual(game_state["score"], 15)


if __name__ == "__main__":
    unittest.main()