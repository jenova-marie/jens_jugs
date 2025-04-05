# Applies a single action to mutate the game state based on rule logic
def apply_action(game_state: dict, action: dict) -> None:
    action_type = action["type"]

    # Sets a game state field to a specific value
    if action_type == "set":
        field = action["field"]
        value = action["value"]
        game_state[field] = value

    # Decreases a numeric field by an amount (default 1)
    elif action_type == "decrease":
        field = action["field"]
        amount = action.get("amount", 1)
        game_state[field] = game_state.get(field, 0) - amount

    # Increases a numeric field by an amount (default 1)
    elif action_type == "increase":
        field = action["field"]
        amount = action.get("amount", 1)
        game_state[field] = game_state.get(field, 0) + amount

    # Adds a narrative scene identifier to the narrativeEvents array
    elif action_type == "addNarrative":
        scene = action.get("scene")
        if scene:
            game_state.setdefault("narrativeEvents", []).append(scene)

    # Appends a value to an array field in game state, creates array if missing
    elif action_type == "addToArray":
        field = action["field"]
        value = action["value"]
        if field not in game_state:
            game_state[field] = []
        if isinstance(game_state[field], list):
            game_state[field].append(value)

    else:
        print(f"Unknown action type: {action_type}")

# Evaluates a condition block ("all" or "any") to determine rule triggering
def evaluate_condition(game_state: dict, condition: dict) -> bool:
    def evaluate_clause(clause: dict) -> bool:
        field = clause["field"]
        operator = clause["operator"]
        value = clause["value"]
        actual = game_state.get(field)

        # Compare based on supported operators
        if operator == "==":
            return actual == value
        elif operator == "!=":
            return actual != value
        elif operator == "<":
            return actual < value
        elif operator == "<=":
            return actual <= value
        elif operator == ">":
            return actual > value
        elif operator == ">=":
            return actual >= value
        elif operator == "includes":
            return isinstance(actual, list) and value in actual
        else:
            return False

    all_clauses = condition.get("all")
    any_clauses = condition.get("any")

    # Evaluate all conditions (AND)
    if all_clauses:
        return all(evaluate_clause(clause) for clause in all_clauses)
    # Evaluate any condition (OR)
    if any_clauses:
        return any(evaluate_clause(clause) for clause in any_clauses)
    return False

# Runs a set of rules, applying actions if conditions evaluate to True
def run_game_rules(game_state: dict, rules: list[dict]) -> None:
    for rule in rules:
        if evaluate_condition(game_state, rule["condition"]):
            for action in rule["actions"]:
                apply_action(game_state, action)
