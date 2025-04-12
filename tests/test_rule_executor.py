import pytest
from jens_jugs.rule_executor import apply_rules, evaluate_condition


def test_apply_rules_set_action():
    state = {"health": 50}
    rules = [
        {
            "id": "rule1",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "set", "field": "health", "value": 100}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["health"] == 100
    assert "Set health to 100" in logs


def test_apply_rules_increase_action():
    state = {"score": 10}
    rules = [
        {
            "id": "rule2",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "increase", "field": "score", "amount": 5}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["score"] == 15
    assert "Increased score by 5" in logs


def test_apply_rules_decrease_action():
    state = {"score": 10}
    rules = [
        {
            "id": "rule3",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "decrease", "field": "score", "amount": 3}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["score"] == 7
    assert "Decreased score by 3" in logs


def test_apply_rules_unlock_clue_action():
    state = {}
    rules = [
        {
            "id": "rule4",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "unlockClue", "clue": "clue1"}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert "clue1" in updated_state["unlocked_clues"]
    assert "Unlocked clue: clue1" in logs


def test_apply_rules_add_narrative_action():
    state = {}
    rules = [
        {
            "id": "rule5",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "addNarrative", "scene": "scene1"}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["narrativeEvents"] == ["scene1"]
    assert "Narrative scene added: scene1" in logs


def test_apply_rules_with_condition_true():
    state = {"health": 50}
    rules = [
        {
            "id": "rule6",
            "condition": {"all": [{"field": "health", "operator": ">", "value": 40}]},
            "actions": [{"type": "set", "field": "health", "value": 100}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["health"] == 100
    assert "Set health to 100" in logs


def test_apply_rules_with_condition_false():
    state = {"health": 30}
    rules = [
        {
            "id": "rule7",
            "condition": {"all": [{"field": "health", "operator": ">", "value": 40}]},
            "actions": [{"type": "set", "field": "health", "value": 100}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["health"] == 30
    assert "Set health to 100" not in logs


def test_apply_rules_unknown_action():
    state = {}
    rules = [
        {
            "id": "rule8",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "unknownAction"}]
        }
    ]
    with pytest.raises(ValueError, match="Invalid rule: 'unknownAction' is not one of"):
        apply_rules(state, rules)


def test_evaluate_condition_equal():
    state = {"score": 10}
    condition = {"field": "score", "operator": "==", "value": 10}
    result = evaluate_condition(condition, state)
    assert result is True


def test_evaluate_condition_not_equal():
    state = {"score": 10}
    condition = {"field": "score", "operator": "!=", "value": 5}
    result = evaluate_condition(condition, state)
    assert result is True


def test_evaluate_condition_greater_than():
    state = {"score": 10}
    condition = {"field": "score", "operator": ">", "value": 5}
    result = evaluate_condition(condition, state)
    assert result is True


def test_evaluate_condition_less_than():
    state = {"score": 10}
    condition = {"field": "score", "operator": "<", "value": 15}
    result = evaluate_condition(condition, state)
    assert result is True


def test_evaluate_condition_invalid_operator():
    state = {"score": 10}
    condition = {"field": "score", "operator": "invalid", "value": 10}
    result = evaluate_condition(condition, state)
    assert result is False


def test_valid_rule_with_condition_and_action():
    state = {"health": 50, "score": 10, "inventory": ["sword"]}
    rules = [
        {
            "id": "rule1",
            "condition": {"field": "health", "operator": ">", "value": 40},
            "actions": [{"type": "set", "field": "health", "value": 100}]
        },
        {
            "id": "rule2",
            "condition": {"field": "score", "operator": "==", "value": 10},
            "actions": [{"type": "increase", "field": "score", "amount": 5}]
        },
        {
            "id": "rule3",
            "condition": {"field": "inventory", "operator": "includes", "value": "sword"},
            "actions": [{"type": "addNarrative", "scene": "scene1"}]
        }
    ]
    updated_state, logs = apply_rules(state, rules)
    assert updated_state["health"] == 100
    assert updated_state["score"] == 15
    assert updated_state["narrativeEvents"] == ["scene1"]
    assert "Set health to 100" in logs
    assert "Increased score by 5" in logs
    assert "Narrative scene added: scene1" in logs


def test_invalid_rule_missing_id():
    state = {"health": 50}
    rules = [
        {
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"type": "set", "field": "health", "value": 100}]
        }
    ]
    with pytest.raises(ValueError, match="Invalid rule: 'id' is a required property"):
        apply_rules(state, rules)


def test_invalid_condition_missing_field():
    state = {"health": 50}
    rules = [
        {
            "id": "rule1",
            "condition": {"all": [{"operator": ">", "value": 40}]},  # Missing 'field'
            "actions": [{"type": "set", "field": "health", "value": 100}]
        }
    ]
    with pytest.raises(ValueError, match="Invalid rule: 'field' is a required property"):
        apply_rules(state, rules)


def test_invalid_action_missing_type():
    state = {"health": 50}
    rules = [
        {
            "id": "rule1",
            "condition": {"all": []},  # Empty condition to always execute
            "actions": [{"field": "health", "value": 100}]  # Missing 'type'
        }
    ]
    with pytest.raises(ValueError, match="Invalid rule: 'type' is a required property"):
        apply_rules(state, rules)