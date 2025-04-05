# Purpose: Acts as the API gateway between the client app and OpenAI
from flask import Flask, request, jsonify
from prompt_augmentation import build_augmented_prompt
from redis_gamestate import get_game_state, set_game_state
from rule_evaluator import run_game_rules
from openai import OpenAI

app = Flask(__name__)
client = OpenAI()


def create_default_game_state():
    return {
        "rank": "Beat Cop",
        "points": 0,
        "trustLevel": 0,
        "emotionalEchoes": [],
        "narrativeEvents": [],
    }


@app.route("/api/chat", methods=["POST"])
def chat():
    user_id = request.json.get("userId")
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    messages = request.json.get("messages")
    if not messages:
        return jsonify({"error": "Missing messages"}), 400

    rules = request.json.get("rules", [])
    game_state = get_game_state(user_id)

    if not game_state:
        game_state = create_default_game_state()
        set_game_state(user_id, game_state)

    game_state = run_game_rules(game_state, rules)
    set_game_state(user_id, game_state)

    if messages[0]["role"] == "system":
        messages[0]["content"] = build_augmented_prompt(
            messages[0]["content"], game_state
        )

    response = client.chat.completions.create(
        model=request.json.get("model", "gpt-4"),
        temperature=request.json.get("temperature", 0.7),
        max_tokens=request.json.get("max_tokens", 1000),
        messages=messages,
    )
    return jsonify({"response": response.choices[0].message.content})


if __name__ == "__main__":
    app.run(debug=True)
