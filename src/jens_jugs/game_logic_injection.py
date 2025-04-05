# Purpose: Evaluates custom procedural logic (early phase)


def evaluate_game_state_for_triggers(game_state: dict) -> dict:
    results = {"secretsUnlocked": [], "eventsTriggered": []}

    if game_state.get("trustLevel", 0) > 50 and "hiddenMemory" not in game_state:
        game_state["hiddenMemory"] = True
        results["secretsUnlocked"].append("Claudette's past revealed")

    if "Claudette's past revealed" in results["secretsUnlocked"]:
        results["eventsTriggered"].append("New dialogue unlocked for Claudette")

    return results
