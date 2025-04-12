# 🧠 GitHub Copilot Guidance Core
# copilot: please follow these instructions strictly
# - Do NOT remove or alter existing comments
# - Do NOT remove or simplify error handling
# - Prefer async/await over synchronous or callback patterns
# - Do NOT change function signatures without a clear reason
# - Suggest improvements only if explicitly requested
# - Prioritize readability and maintainability
# - Always preserve code structure and intent
# - For any proposed changes:
#   - Include explanatory comments describing what was changed and why

# Best Practices for Jens Jugs Workspace

## General Guidelines
- **Code Consistency**: Follow the existing code style and structure. Use consistent naming conventions, indentation, and formatting.
- **Documentation**: Ensure all functions, classes, and modules have clear and concise docstrings.
- **Error Handling**: Log all errors with sufficient context and handle exceptions gracefully to avoid application crashes.
- **Testing**: Write unit tests for all new features and ensure existing tests pass before committing changes.
- **Environment Variables**: Use environment variables for sensitive configurations (e.g., API keys, database credentials).

## Redis Usage
- **Data Validation**: Always validate data retrieved from Redis against the schema defined in `redis.schema.json`.
- **Type Conversion**: Convert Redis data to the expected types before processing.
- **Shared Client**: Use a shared Redis client instance across modules to improve efficiency and maintain consistency.

## API Development
- **Authentication**: Protect all endpoints with JWT-based authentication.
- **Input Validation**: Validate all incoming requests to ensure they meet the expected format and constraints.
- **Logging**: Log all API requests and responses for debugging and monitoring purposes.

## Rule Engine
- **Schema Compliance**: Validate all rules against `game-rule.schema.json` before execution.
- **Atomic Updates**: Ensure game state updates are atomic to avoid partial state changes.
- **Error Logging**: Log invalid rules or actions for debugging.

## Testing
- **Unit Tests**: Write tests for individual functions and methods.
- **Integration Tests**: Test interactions between modules, especially for Redis and API endpoints.
- **Mocking**: Use mocks for external dependencies (e.g., Redis, OpenAI API) in tests.
- **Test Coverage**: Aim for high test coverage to ensure reliability.

## Logging
- **Centralized Logging**: Use a consistent logging configuration across all modules.
- **Log Levels**: Use appropriate log levels (`DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`) for different types of messages.
- **Sensitive Data**: Avoid logging sensitive information such as passwords or API keys.

## File Organization
- **Schemas**: Store all JSON schemas in the `schema/` directory.
- **Tests**: Keep all test files in the `tests/` directory and follow the naming convention `test_<module>.py`.
- **Logs**: Organize logs by module and ensure old logs are rotated to avoid disk space issues.

## Collaboration
- **Code Reviews**: Submit all changes for peer review before merging.
- **Branching**: Use feature branches for new features and bug fixes.
- **Commit Messages**: Write clear and descriptive commit messages.

## Security
- **Secrets Management**: Store secrets securely using environment variables or a secrets manager.
- **Dependency Updates**: Regularly update dependencies to patch security vulnerabilities.
- **Rate Limiting**: Implement rate limiting on API endpoints to prevent abuse.

## Performance
- **Caching**: Use Redis for caching frequently accessed data.
- **Connection Pooling**: Use connection pooling for Redis and other external services.
- **Profiling**: Profile the application to identify and optimize performance bottlenecks.

# Project Folder Structure

```plaintext
/Users/mikki/projects/jens_jugs
├── copilot/               # Guidance and instructions for using GitHub Copilot effectively.
│   ├── GUIDENCE.md        # Best practices and project-specific guidelines.
│   ├── GUIDENCE.pdf       # PDF version of the guidance document.
├── data/                  # Contains default data and reports.
│   ├── game-state.default.json # Default Redis data for initializing the database.
├── docs/                  # Documentation for the project.
│   ├── AI_Wiki.md         # AI-related documentation.
│   ├── TESTING.md         # Testing strategies and guidelines.
├── logs/                  # Log files organized by module and purpose.
├── narrative/             # Narrative designs for the mystery game.
├── rules/                 # JSON files defining game rules for different stages.
├── schema/                # JSON schemas for validation.
│   ├── game-rule.schema.json # Schema for game rules.
│   ├── redis.schema.json      # Schema for Redis data.
├── src/                   # Source code for the application.
│   ├── jens_jugs/         # Core application logic.
│   │   ├── main.py        # Entry point of the application.
│   │   ├── auth_service.py # Handles authentication and JWTs.
│   │   ├── redis_gamestate.py # Manages Redis interactions for game state.
│   │   ├── rule_executor.py # Executes game rules.
├── tests/                 # Unit and integration tests.
│   ├── test_auth_service.py # Tests for authentication service.
│   ├── test_redis_gamestate.py # Tests for Redis game state management.
│   ├── mocks/             # Mock files for testing external dependencies.
├── uml/                   # UML diagrams for system architecture.
│   ├── game_engine_architecture.puml # PlantUML diagram for the game engine.
```

# Entry Point: main.py

The `main.py` file in the `src/jens_jugs/` directory serves as the entry point for the application. It initializes the application, sets up routes, and starts the server. Ensure that all configurations and dependencies are properly set before running the application.

# 🧠 Copilot Context Reminder:
# This code is copied from [relative/path/to/file.py]
# It is here to help Copilot understand related logic and structure.
# Do NOT execute or edit. This is *reference only*.

# --- BEGIN Copilot Reference Snippet ---
# def log_error(message: str) -> None:
#     print(f"[ERROR]: {message}")
# --- END Copilot Reference Snippet ---
