# Purpose: Injects dynamic game state into the system prompt


def build_augmented_prompt(base_prompt: str, state: dict) -> str:
    # Sanitize game state (minimal)
    summary_parts = [
        f"Current Rank: {state.get('rank', 'Unknown')}",
        f"Points: {state.get('points', 0)}",
        f"Emotional Echoes: {state.get('emotionalEchoes', [])}",
    ]

    if "narrativeEvents" in state:
        summary_parts.append("Recent Events:")
        summary_parts.extend([f"- {event}" for event in state["narrativeEvents"][-5:]])

    summary = "\n".join(summary_parts)
    return f"""{base_prompt}

---

[Game State Summary]
{summary}

---"""
