# Copilot Instructions for `src/` Directory

## General Guidelines
- Follow the **Secure REST API** principles:
  - Ensure all endpoints are protected by authentication and authorization.
  - Validate and sanitize all user inputs to prevent injection attacks.
  - Implement rate limiting and throttling where applicable.
  - Log and monitor all security events.

## Module-Specific Instructions
### `auth_service.py`
- Use JWT for authentication and ensure tokens are validated against Redis-stored keys.
- Rotate RSA key pairs periodically and log key generation events.
- Ensure all endpoints in the `auth_bp` blueprint return meaningful error messages for unauthorized access.

### `relay_server.py`
- Ensure all API routes are protected by the `@jwt_verify` decorator.
- Log all incoming requests, including user IDs and request payloads, but avoid logging sensitive data.
- Validate game state and rules before applying them to prevent invalid state mutations.
- Handle exceptions gracefully and return appropriate HTTP status codes.

### `rule_executor.py` and `rule_evaluator.py`
- Validate all rules against the JSON schema before execution.
- Ensure conditions and actions are applied atomically to avoid partial state updates.
- Log all rule evaluations and state changes for debugging and analytics.

### `logger.py`
- Ensure logs are written to multiple streams (`console`, `file`, `cloudwatch`) as configured.
- Use environment variables to control log levels and enable debug mode during development.

### `main.py`
- Use environment variables for all sensitive configurations (e.g., Redis host, OpenAI API key).
- Ensure Redis is populated with default values on startup using `populate_redis_with_defaults`.
