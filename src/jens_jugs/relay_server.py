# Purpose: Acts as the API gateway between the client app and OpenAI
import os
import logging  # For configuring Werkzeug logger
from flask import Flask, request, jsonify
from openai import OpenAIError

# Additional imports for operation
from jens_jugs.jwt_auth import jwt_verify  # For JWT verification
from jens_jugs.auth_service import auth_bp  # For authentication blueprint
from jens_jugs.rule_evaluator import run_game_rules  # For game state rule evaluation
import jens_jugs.redis_gamestate as redis_gamestate  # For managing game state
from jens_jugs.rule_executor import apply_rules  # For applying triggered rules
from jens_jugs.build_prompt import build_prompt  # For augmenting system messages

def create_app(openai_client, get_logger):
    # Initialize the logger
    logger = get_logger(log_name="relay_server", streams=["console", "cloudwatch", "file"], config={
                    "file": {
                        "path": "./logs",
                        "max_bytes": 10 * 1024 * 1024,  # 10 MB
                        "backup_count": 5
                    }
                })
    logger.info("Starting the relay server...")

    # Configure Werkzeug to use the same logger
    werkzeug_logger = logging.getLogger("werkzeug")
    werkzeug_logger.setLevel(logging.INFO)  # Set the desired log level
    for handler in logger.handlers:
        werkzeug_logger.addHandler(handler)

    app = Flask(__name__)
    app.register_blueprint(auth_bp)  # Register the auth blueprint here

    @app.errorhandler(Exception)
    def handle_exception(e):
        """Log all exceptions to CloudWatch."""
        logger.error(f"Unhandled exception occurred: {e}", exc_info=True)
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    @app.route("/api/chat", methods=["POST"])
    @jwt_verify
    def chat():
        logger.info("Received request at /api/chat endpoint.")
        try:
            # Parse JSON request body
            try:
                request_data = request.get_json()
            except Exception as e:
                logger.warning(f"Invalid JSON format: {e}")
                return jsonify({"error": "Invalid JSON format"}), 400

            if not request_data:
                logger.warning("Request body is empty or not valid JSON.")
                return jsonify({"error": "Request body must be valid JSON"}), 400

            logger.debug(f"Request data: {request_data}")

            # Extract userId
            user_id = request_data.get("userId")
            if not user_id:
                logger.warning("Missing userId in request body.")
                return jsonify({"error": "Missing userId"}), 400
            logger.debug(f"Extracted userId: {user_id}")

            # Extract messages
            messages = request_data.get("messages")
            if not messages:
                logger.warning("Missing messages in request body.")
                return jsonify({"error": "Missing messages"}), 400
            logger.debug(f"Extracted messages: {messages}")

            # Extract rules
            rules = request_data.get("rules", [])
            logger.debug(f"Extracted rules: {rules}")

            # Retrieve and update game state
            logger.info(f"Retrieving game state for userId: {user_id}")
            try:
                game_state = redis_gamestate.get_game_state(user_id)
                if game_state is None:
                    logger.warning(f"Game state not found for userId: {user_id}. Initializing default state.")
                    game_state = {"trust": 50}  # Default game state
            except Exception as e:
                logger.error(f"Redis connection error: {e}")
                return jsonify({"error": "Failed to retrieve game state"}), 500

            logger.debug(f"Game state: {game_state}")

            try:
                game_state = run_game_rules(game_state, rules)
                logger.debug(f"Updated game state after applying rules: {game_state}")
            except Exception as e:
                logger.error(f"Error applying game rules: {e}")
                return jsonify({"error": "Failed to apply game rules"}), 500

            try:
                redis_gamestate.set_game_state(user_id, game_state)
                logger.info(f"Game state updated for userId: {user_id}")
            except Exception as e:
                logger.error(f"Error saving game state: {e}")
                return jsonify({"error": "Failed to save game state"}), 500

            # Augment system message if applicable
            if messages[0]["role"] == "system":
                logger.info("Augmenting system message with game state.")
                try:
                    messages[0]["content"] = build_prompt(messages[0]["content"], game_state)
                except Exception as e:
                    logger.error(f"Failed to augment system message: {e}")
                    return jsonify({"error": "Failed to augment system message"}), 500

            # Call OpenAI API
            logger.info("Sending request to OpenAI API.")
            try:
                response = openai_client.chat.completions.create(
                    model=request_data.get("model", "gpt-4"),
                    temperature=request_data.get("temperature", 0.7),
                    max_tokens=request_data.get("max_tokens", 1000),
                    messages=messages,
                )
                logger.info("Received response from OpenAI API.")

                # Validate response structure
                if not response.choices or not response.choices[0].message.content:
                    logger.error("Invalid response structure from OpenAI API.")
                    return jsonify({"error": "Invalid response from OpenAI API"}), 500

                response_content = response.choices[0].message.content
                logger.debug(f"OpenAI response content: {response_content}")

                return jsonify({"response": response_content})

            except OpenAIError as e:
                logger.error(f"OpenAI API error: {e}", exc_info=True)
                return jsonify({"error": "Error communicating with OpenAI API"}), 500
            except Exception as e:
                logger.error(f"Unexpected error processing /api/chat request: {e}", exc_info=True)
                return jsonify({"error": "Unexpected error occurred"}), 500

        except Exception as e:
            logger.error(f"Unhandled exception in /api/chat: {e}", exc_info=True)
            return jsonify({"error": "An unexpected error occurred"}), 500

    return app

if __name__ == "__main__":
    port = int(os.getenv("API_PORT_HTTP", 6000))  # Default to port 6000 if API_PORT_HTTP is not set
    print(f"Starting Flask app on port {port}...")

    # Create and run the app
    app = create_app()
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
