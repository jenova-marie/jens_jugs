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

# 🧠 GitHub Copilot Guidance Project Specific
# copilot: the following an overall technical guild that you should follow at all times, please :-)

This project uses pytest as the testing framework.
This project uses a schema file located at schema/game-rule.schema.json.  Any updates to code that may impact the schema should identified and noted with proposed schema updates, if possible.




# 🧠 Copilot Context Reminder:
# This code is copied from [relative/path/to/file.py]
# It is here to help Copilot understand related logic and structure.
# Do NOT execute or edit. This is *reference only*.

# --- BEGIN Copilot Reference Snippet ---
# def log_error(message: str) -> None:
#     print(f"[ERROR]: {message}")
# --- END Copilot Reference Snippet ---
