import copy
import json
import os
from jsonschema import validate, ValidationError, RefResolver

# Load the schema once as a global variable
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), "../../schema")
SCHEMA_PATH = os.path.join(SCHEMA_DIR, "game-rule.schema.json")
with open(SCHEMA_PATH, "r") as schema_file:
    RULE_SCHEMA = json.load(schema_file)

# Create a RefResolver for resolving $ref in the schema
RESOLVER = RefResolver(base_uri=f"file://{SCHEMA_DIR}/", referrer=RULE_SCHEMA)


def apply_rules(state: dict, rules: list) -> tuple[dict, list]:
    """Apply a list of rules to a given state."""
    updated_state = copy.deepcopy(state)
    logs = []

    for rule in rules:
        # Validate the rule against the schema using the resolver
        try:
            validate(instance=rule, schema=RULE_SCHEMA, resolver=RESOLVER)
        except ValidationError as e:
            logs.append(f"Invalid rule: {e.message}")
            continue  # Skip invalid rules

        # Evaluate the condition (if present)
        if "condition" in rule and not evaluate_condition(rule["condition"], updated_state):
            continue

        # Apply actions
        for action in rule.get("actions", []):
            if "type" not in action:
                raise ValueError("Invalid rule: 'type' is a required property in action")
            
            action_type = action["type"]
            if action_type not in ["set", "increase", "decrease", "unlockClue", "addNarrative"]:
                raise ValueError(f"Invalid rule: '{action_type}' is not one of ['addNarrative', 'assign', 'decrease', 'increase', 'reward', 'set', 'trust', 'unlockClue']")
            
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

    return updated_state, logs


def evaluate_condition(condition: dict, state: dict) -> bool:
    """Enhanced evaluator for rule conditions."""
    if "all" in condition:
        # Evaluate all subconditions and return True only if all are True
        return all(evaluate_condition(sub_condition, state) for sub_condition in condition["all"])
    elif "any" in condition:
        # Evaluate all subconditions and return True if any are True
        return any(evaluate_condition(sub_condition, state) for sub_condition in condition["any"])
    elif "not" in condition:
        # Negate the result of the subcondition
        return not evaluate_condition(condition["not"], state)

    # Handle simple conditions
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
