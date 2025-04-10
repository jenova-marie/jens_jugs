import pytest
from jens_jugs.rule_evaluator import apply_action, evaluate_condition, run_game_rules


def test_apply_action_set():
    game_state = {"health": 50}
    action = {"type": "set", "field": "health", "value": 100}
    apply_action(game_state, action)
    assert game_state["health"] == 100


def test_apply_action_increase():
    game_state = {"score": 10}
    action = {"type": "increase", "field": "score", "amount": 5}
    apply_action(game_state, action)
    assert game_state["score"] == 15


def test_apply_action_decrease():
    game_state = {"score": 10}
    action = {"type": "decrease", "field": "score", "amount": 3}
    apply_action(game_state, action)
    assert game_state["score"] == 7


def test_apply_action_add_narrative():
    game_state = {}
    action = {"type": "addNarrative", "scene": "scene1"}
    apply_action(game_state, action)
    assert "scene1" in game_state["narrativeEvents"]


def test_apply_action_add_to_array():
    game_state = {}
    action = {"type": "addToArray", "field": "inventory", "value": "sword"}
    apply_action(game_state, action)
    assert "sword" in game_state["inventory"]


def test_apply_action_unknown_type():
    game_state = {}
    action = {"type": "unknown", "field": "health", "value": 100}
    apply_action(game_state, action)
    assert "health" not in game_state  # No changes should be made


def test_evaluate_condition_all_true():
    game_state = {"health": 50, "score": 10}
    condition = {
        "all": [
            {"field": "health", "operator": ">", "value": 40},
            {"field": "score", "operator": "==", "value": 10},
        ]
    }
    result = evaluate_condition(game_state, condition)
    assert result is True


def test_evaluate_condition_all_false():
    game_state = {"health": 30, "score": 10}
    condition = {
        "all": [
            {"field": "health", "operator": ">", "value": 40},
            {"field": "score", "operator": "==", "value": 10},
        ]
    }
    result = evaluate_condition(game_state, condition)
    assert result is False


def test_evaluate_condition_any_true():
    game_state = {"health": 30, "score": 10}
    condition = {
        "any": [
            {"field": "health", "operator": ">", "value": 40},
            {"field": "score", "operator": "==", "value": 10},
        ]
    }
    result = evaluate_condition(game_state, condition)
    assert result is True


def test_evaluate_condition_any_false():
    game_state = {"health": 30, "score": 5}
    condition = {
        "any": [
            {"field": "health", "operator": ">", "value": 40},
            {"field": "score", "operator": "==", "value": 10},
        ]
    }
    result = evaluate_condition(game_state, condition)
    assert result is False


def test_evaluate_condition_includes():
    game_state = {"inventory": ["sword", "shield"]}
    condition = {
        "all": [{"field": "inventory", "operator": "includes", "value": "sword"}]
    }
    result = evaluate_condition(game_state, condition)
    assert result is True


def test_run_game_rules():
    game_state = {"health": 50, "score": 10}
    rules = [
        {
            "id": "rule1",  # Added unique identifier
            "condition": {"all": [{"field": "health", "operator": ">", "value": 40}]},
            "actions": [{"type": "increase", "field": "score", "amount": 5}],
        },
        {
            "id": "rule2",  # Added unique identifier
            "condition": {"all": [{"field": "score", "operator": "==", "value": 15}]},
            "actions": [{"type": "set", "field": "health", "value": 100}],
        },
    ]
    run_game_rules(game_state, rules)
    assert game_state["health"] == 100
    assert game_state["score"] == 15