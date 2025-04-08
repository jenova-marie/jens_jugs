import pytest
from src.jens_jugs.game_logic_injection import evaluate_game_state_for_triggers

def test_no_triggers_or_secrets():
    game_state = {"trustLevel": 10}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {"secretsUnlocked": [], "eventsTriggered": []}
    assert "hiddenMemory" not in game_state

def test_unlock_hidden_memory():
    game_state = {"trustLevel": 60}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {
        "secretsUnlocked": ["Claudette's past revealed"],
        "eventsTriggered": ["New dialogue unlocked for Claudette"],
    }
    assert game_state["hiddenMemory"] is True

def test_hidden_memory_already_unlocked():
    game_state = {"trustLevel": 60, "hiddenMemory": True}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {"secretsUnlocked": [], "eventsTriggered": []}
    assert game_state["hiddenMemory"] is True

def test_no_trust_level_key():
    game_state = {}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {"secretsUnlocked": [], "eventsTriggered": []}
    assert "hiddenMemory" not in game_state

def test_trust_level_exactly_50():
    game_state = {"trustLevel": 50}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {"secretsUnlocked": [], "eventsTriggered": []}
    assert "hiddenMemory" not in game_state