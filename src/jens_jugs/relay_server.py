# Purpose: Acts as the API gateway between the client app and OpenAI
from flask import Flask, request, jsonify
from openai import OpenAI, OpenAIError
import os
import logging

# Additional imports for operation
from jens_jugs.jwt_auth import jwt_verify  # For JWT verification
from jens_jugs.auth_service import auth_bp  # For authentication blueprint
from jens_jugs.rule_evaluator import run_game_rules  # For game state rule evaluation
from jens_jugs.cloudwatch_logger import get_logger  # For logging to CloudWatch
import jens_jugs.redis_gamestate as redis_gamestate  # For managing game state
from jens_jugs.rule_executor import apply_rules  # For applying triggered rules
from jens_jugs.prompt_augmentation import build_prompt  # For augmenting system messages
from jens_jugs.sys_init import populate_redis_with_defaults  # For initializing system defaults in Redis

def create_app(jwt_verify, auth_bp, run_game_rules, get_logger, build_prompt, redis_gamestate, openai_client):
    logger = get_logger(log_name="relay_server")
    logger.info("Starting the relay server...")

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
            game_state = redis_gamestate.get_game_state(user_id)
            logger.debug(f"Initial game state: {game_state}")

            logger.debug(f"Game state: {game_state}")
            logger.debug(f"Messages: {messages}")

            game_state = run_game_rules(game_state, rules)
            logger.debug(f"Updated game state after applying rules: {game_state}")

            redis_gamestate.set_game_state(user_id, game_state)
            logger.info(f"Game state updated for userId: {user_id}")

            # Augment system message if applicable
            if messages[0]["role"] == "system":
                logger.info("Augmenting system message with game state.")
                try:
                    logger.debug(f"Calling build_prompt with content: {messages[0]['content']} and game_state: {game_state}")
                    messages[0]["content"] = build_prompt(
                        messages[0]["content"], game_state
                    )
                except Exception as e:
                    logger.error(f"Failed to augment system message: {e}")
                    return jsonify({"error": "Failed to augment system message"}), 500
                logger.debug(f"Augmented system message: {messages[0]['content']}")

            # Call OpenAI API
            logger.info("Sending request to OpenAI API.")
            response = openai_client.chat.completions.create(
                model=request_data.get("model", "gpt-4"),
                temperature=request_data.get("temperature", 0.7),
                max_tokens=request_data.get("max_tokens", 1000),
                messages=messages,
            )
            logger.info("Received response from OpenAI API.")

            # Extract response content
            response_content = response.choices[0].message.content
            logger.debug(f"OpenAI response content: {response_content}")

            # Check for triggered rules in the response metadata
            triggered_rules = getattr(response, "triggered_rules", [])
            if triggered_rules:
                logger.info(f"Applying triggered rules: {triggered_rules}")
                state, logs = apply_rules(game_state, triggered_rules)
                logger.info(f"Triggered rules applied. Logs: {logs}")

            return jsonify({"response": response_content})

        except OpenAIError as e:
            logger.error(f"OpenAI API error: {e}", exc_info=True)
            return jsonify({"error": "Error communicating with OpenAI API"}), 500
        except Exception as e:
            logger.error(f"Unexpected error processing /api/chat request: {e}", exc_info=True)
            return jsonify({"error": "Unexpected error occurred"}), 500

    return app

if __name__ == "__main__":
    port = int(os.getenv("API_PORT_HTTP", 6000))  # Default to port 6000 if API_PORT_HTTP is not set
    logger = get_logger(log_name="relay_server")
    logger.info(f"Starting Flask app on port {port}...")

    # Retrieve the OpenAI API key from the environment
    openai_api_key = os.getenv("OPENAPI_KEY")
    if not openai_api_key:
        logger.critical("OPENAPI_KEY is not set in the environment variables.")
        raise EnvironmentError("OPENAPI_KEY is not set in the environment variables.")

    # Instantiate the OpenAI client
    openai_client = OpenAI(api_key=openai_api_key)

    # Create and run the app
    app = create_app(
        jwt_verify=jwt_verify,
        auth_bp=auth_bp,
        run_game_rules=run_game_rules,
        get_logger=get_logger,
        build_prompt=build_prompt,
        redis_gamestate=redis_gamestate,
        openai_client=openai_client,
    )
    app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
