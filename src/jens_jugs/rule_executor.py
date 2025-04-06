import copy

def apply_rules(state: dict, rules: list) -> tuple[dict, list]:
    """Apply a list of rules to a given state."""
    updated_state = copy.deepcopy(state)
    logs = []

    for rule in rules:
        if 'condition' in rule and not evaluate_condition(rule['condition'], updated_state):
            continue

        for action in rule.get('actions', []):
            action_type = action.get('type')
            match action_type:
                case "set":
                    key, value = action["key"], action["value"]
                    updated_state[key] = value
                    logs.append(f"Set {key} to {value}")
                case "increase":
                    key, amount = action["key"], action["amount"]
                    updated_state[key] = updated_state.get(key, 0) + amount
                    logs.append(f"Increased {key} by {amount}")
                case "decrease":
                    key, amount = action["key"], action["amount"]
                    updated_state[key] = updated_state.get(key, 0) - amount
                    logs.append(f"Decreased {key} by {amount}")
                case "unlockClue":
                    clue = action["clue"]
                    updated_state.setdefault("unlocked_clues", []).append(clue)
                    logs.append(f"Unlocked clue: {clue}")
                case "addNarrative":
                    flag = action["flag"]
                    updated_state.setdefault("narrative_flags", {})[flag] = True
                    logs.append(f"Narrative flag added: {flag}")
                case _:
                    logs.append(f"Unknown action: {action_type}")

    return updated_state, logs


def evaluate_condition(condition: dict, state: dict) -> bool:
    """Basic evaluator for rule conditions."""
    key = condition.get("key")
    op = condition.get("op")
    value = condition.get("value")

    current = state.get(key)

    match op:
        case "==": return current == value
        case "!=": return current != value
        case ">": return current > value
        case "<": return current < value
        case ">=": return current >= value
        case "<=": return current <= value
        case _: return False
