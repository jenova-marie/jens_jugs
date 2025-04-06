# Purpose: Acts as the API gateway between the client app and OpenAI
from flask import Flask, request, jsonify
from prompt_augmentation import build_augmented_prompt
from redis_gamestate import get_or_create_game_state, set_game_state
from rule_evaluator import run_game_rules
from cloudwatch_logger import get_logger
from openai import OpenAI
import os

logger = get_logger(log_name="relay_server")
logger.info("Starting the relay server...")
# Retrieve the OpenAI API key from the environment
openai_api_key = os.getenv("OPENAPI_KEY")
if not openai_api_key:
    raise EnvironmentError("OPENAPI_KEY is not set in the environment variables.")

app = Flask(__name__)
client = OpenAI(api_key=openai_api_key)

@app.route("/api/chat", methods=["POST"])
def chat():
    user_id = request.json.get("userId")
    if not user_id:
        return jsonify({"error": "Missing userId"}), 400

    messages = request.json.get("messages")
    if not messages:
        return jsonify({"error": "Missing messages"}), 400

    rules = request.json.get("rules", [])
    game_state = get_or_create_game_state(user_id)
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

    response_dict = response if isinstance(response, dict) else response.__dict__

    from jens_jugs.rule_executor import apply_rules

    # If GPT output contains 'triggered_rules', apply them
    triggered_rules = response_dict.get("triggered_rules", [])
    if triggered_rules:
        state, logs = apply_rules(state, triggered_rules)
        print("[RuleExecutor] Applied rules:", logs)

    return jsonify({"response": response.choices[0].message.content})

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
