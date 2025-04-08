import unittest
from jens_jugs.rule_executor import apply_rules, evaluate_condition
from tests.test_base import BaseTestCase

class TestRuleExecutor(BaseTestCase):

    def test_apply_rules_set_action(self):
        state = {"health": 50}
        rules = [
            {"actions": [{"type": "set", "key": "health", "value": 100}]}
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertEqual(updated_state["health"], 100)
        self.assertIn("Set health to 100", logs)

    def test_apply_rules_increase_action(self):
        state = {"score": 10}
        rules = [
            {"actions": [{"type": "increase", "key": "score", "amount": 5}]}
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertEqual(updated_state["score"], 15)
        self.assertIn("Increased score by 5", logs)

    def test_apply_rules_decrease_action(self):
        state = {"score": 10}
        rules = [
            {"actions": [{"type": "decrease", "key": "score", "amount": 3}]}
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertEqual(updated_state["score"], 7)
        self.assertIn("Decreased score by 3", logs)

    def test_apply_rules_unlock_clue_action(self):
        state = {}
        rules = [
            {"actions": [{"type": "unlockClue", "clue": "clue1"}]}
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertIn("clue1", updated_state["unlocked_clues"])
        self.assertIn("Unlocked clue: clue1", logs)

    def test_apply_rules_add_narrative_action(self):
        state = {}
        rules = [
            {"actions": [{"type": "addNarrative", "flag": "flag1"}]}
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertTrue(updated_state["narrative_flags"]["flag1"])
        self.assertIn("Narrative flag added: flag1", logs)

    def test_apply_rules_with_condition_true(self):
        state = {"health": 50}
        rules = [
            {
                "condition": {"key": "health", "op": ">", "value": 40},
                "actions": [{"type": "set", "key": "health", "value": 100}]
            }
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertEqual(updated_state["health"], 100)
        self.assertIn("Set health to 100", logs)

    def test_apply_rules_with_condition_false(self):
        state = {"health": 30}
        rules = [
            {
                "condition": {"key": "health", "op": ">", "value": 40},
                "actions": [{"type": "set", "key": "health", "value": 100}]
            }
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertEqual(updated_state["health"], 30)
        self.assertNotIn("Set health to 100", logs)

    def test_apply_rules_unknown_action(self):
        state = {}
        rules = [
            {"actions": [{"type": "unknownAction"}]}
        ]
        updated_state, logs = apply_rules(state, rules)
        self.assertEqual(updated_state, state)
        self.assertIn("Unknown action: unknownAction", logs)

    def test_evaluate_condition_equal(self):
        state = {"score": 10}
        condition = {"key": "score", "op": "==", "value": 10}
        result = evaluate_condition(condition, state)
        self.assertTrue(result)

    def test_evaluate_condition_not_equal(self):
        state = {"score": 10}
        condition = {"key": "score", "op": "!=", "value": 5}
        result = evaluate_condition(condition, state)
        self.assertTrue(result)

    def test_evaluate_condition_greater_than(self):
        state = {"score": 10}
        condition = {"key": "score", "op": ">", "value": 5}
        result = evaluate_condition(condition, state)
        self.assertTrue(result)

    def test_evaluate_condition_less_than(self):
        state = {"score": 10}
        condition = {"key": "score", "op": "<", "value": 15}
        result = evaluate_condition(condition, state)
        self.assertTrue(result)

    def test_evaluate_condition_invalid_operator(self):
        state = {"score": 10}
        condition = {"key": "score", "op": "invalid", "value": 10}
        result = evaluate_condition(condition, state)
        self.assertFalse(result)


if __name__ == "__main__":
    unittest.main()