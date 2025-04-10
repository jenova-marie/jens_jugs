import pytest
from src.jens_jugs.game_logic_injection import evaluate_game_state_for_triggers

def test_no_triggers_or_secrets():
    """Test case where no triggers or secrets are unlocked."""
    game_state = {"trustLevel": 10}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {"secretsUnlocked": [], "eventsTriggered": []}
    assert "hiddenMemory" not in game_state

def test_unlock_hidden_memory():
    """Test case where hidden memory is unlocked."""
    game_state = {"trustLevel": 60}
    results = evaluate_game_state_for_triggers(game_state)
    assert results == {
        "secretsUnlocked": ["Claudette's past revealed"],
        "eventsTriggered": ["New dialogue unlocked for Claudette"],
    }
    assert game_state.get("hiddenMemory") is True