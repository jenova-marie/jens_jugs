import pytest
from jens_jugs.build_prompt import build_prompt


def test_build_prompt_with_full_state():
    """Test building a prompt with a full game state."""
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
    assert base_prompt in result
    assert "[Game State Summary]" in result
    assert expected_summary in result


def test_build_prompt_with_partial_state():
    """Test building a prompt with a partial game state."""
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
    assert base_prompt in result
    assert "[Game State Summary]" in result
    assert expected_summary in result


def test_build_prompt_with_empty_state():
    """Test building a prompt with an empty game state."""
    base_prompt = "Welcome to the game!"
    state = {}

    result = build_prompt(base_prompt, state)

    expected_summary = (
        "Current Level: UnknownPoints: 0\n"
        "Emotional Echoes: []"
    )
    assert base_prompt in result
    assert "[Game State Summary]" in result
    assert expected_summary in result


def test_build_prompt_with_none_state():
    """Test building a prompt with a None game state."""
    base_prompt = "Welcome to the game!"

    result = build_prompt(base_prompt, None)

    expected_summary = (
        "Current Level: UnknownPoints: 0\n"
        "Emotional Echoes: []"
    )
    assert base_prompt in result
    assert "[Game State Summary]" in result
    assert expected_summary in result


def test_build_prompt_with_long_narrative_events():
    """Test building a prompt with long narrative events."""
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
    assert base_prompt in result
    assert "[Game State Summary]" in result
    assert expected_events in result


# def test_build_prompt():
#     """Test building a prompt with a simple context."""
#     prompt = "What is the capital of France?"
#     context = {"country": "France"}
#     result = build_prompt(prompt, context)
#     # Example assertion (update based on actual implementation)
#     assert "Paris" in result