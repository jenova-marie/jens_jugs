import copy
import json
import os
from jsonschema import validate, ValidationError

# Load the schema once as a global variable
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "../../schema/game-rule.schema.json")
with open(SCHEMA_PATH, "r") as schema_file:
    RULE_SCHEMA = json.load(schema_file)


def apply_rules(state: dict, rules: list) -> tuple[dict, list]:
    """Apply a list of rules to a given state."""
    updated_state = copy.deepcopy(state)
    logs = []

    for rule in rules:
        # Validate the rule against the schema
        try:
            validate(instance=rule, schema=RULE_SCHEMA)
        except ValidationError as e:
            raise ValueError(f"Invalid rule: {e.message}")

        # Evaluate the condition (if present)
        if "condition" in rule and not evaluate_condition(rule["condition"], updated_state):
            continue

        # Apply actions
        for action in rule.get("actions", []):
            action_type = action["type"]
            match action_type:
                case "set":
                    field, value = action["field"], action["value"]
                    updated_state[field] = value
                    logs.append(f"Set {field} to {value}")
                case "increase":
                    field, amount = action["field"], action["amount"]
                    updated_state[field] = updated_state.get(field, 0) + amount
                    logs.append(f"Increased {field} by {amount}")
                case "decrease":
                    field, amount = action["field"], action["amount"]
                    updated_state[field] = updated_state.get(field, 0) - amount
                    logs.append(f"Decreased {field} by {amount}")
                case "unlockClue":
                    clue = action["clue"]
                    updated_state.setdefault("unlocked_clues", []).append(clue)
                    logs.append(f"Unlocked clue: {clue}")
                case "addNarrative":
                    scene = action["scene"]
                    updated_state.setdefault("narrativeEvents", []).append(scene)
                    logs.append(f"Narrative scene added: {scene}")
                case _:
                    logs.append(f"Unknown action: {action_type}")

    return updated_state, logs


def evaluate_condition(condition: dict, state: dict) -> bool:
    """Basic evaluator for rule conditions."""
    field = condition.get("field")
    operator = condition.get("operator")
    value = condition.get("value")

    current = state.get(field)

    match operator:
        case "==": return current == value
        case "!=": return current != value
        case ">": return current > value
        case "<": return current < value
        case ">=": return current >= value
        case "<=": return current <= value
        case "includes": return isinstance(current, list) and value in current
        case _: return False
