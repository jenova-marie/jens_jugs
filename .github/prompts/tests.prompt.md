### **File: `tests.prompt.md`**
```markdown
<!-- filepath: /Users/mikki/projects/jens_jugs/.github/prompts/tests.prompt.md -->
# Copilot Instructions for [tests](http://_vscodecontentref_/2) Directory

## General Guidelines
- Write tests to cover all edge cases, including invalid inputs, missing fields, and unauthorized access.
- Use [unittest.mock](http://_vscodecontentref_/3) to mock external dependencies like Redis, OpenAI, and AWS Secrets Manager.
- Ensure all tests are idempotent and do not rely on external state.

## Module-Specific Instructions
### [test_auth_service.py](http://_vscodecontentref_/4)
- Test JWT generation and validation workflows, including edge cases like expired tokens and invalid signatures.
- Mock Redis interactions to simulate key retrieval and expiration scenarios.
- Validate that the `/api/auth` endpoint returns appropriate error codes for unauthorized requests.

### [test_relay_server.py](http://_vscodecontentref_/5)
- Test all `/api/chat` endpoint scenarios, including valid requests, invalid JSON payloads, and missing user IDs.
- Mock Redis and OpenAI interactions to simulate game state retrieval and API responses.
- Verify that rate limiting and throttling are enforced under high traffic conditions.

### [test_rule_executor.py](http://_vscodecontentref_/6) and [test_rule_evaluator.py](http://_vscodecontentref_/7)
- Test rule validation against the JSON schema, including invalid rules and missing fields.
- Ensure all condition types ([all](http://_vscodecontentref_/8), [any](http://_vscodecontentref_/9), `includes`, etc.) are evaluated correctly.
- Validate that actions ([set](http://_vscodecontentref_/10), `increase`, `addNarrative`, etc.) are applied as expected.

### [test_sys_init.py](http://_vscodecontentref_/11)
- Test that [populate_redis_with_defaults](http://_vscodecontentref_/12) correctly initializes Redis with default values.
- Mock file system interactions to simulate missing or corrupted configuration files.

### `test_env_setup.py`
- Validate that all required environment variables are loaded and fallback defaults are applied.
- Test error handling for missing or invalid `.env` files.

## Additional Notes
- Use [pytest](http://_vscodecontentref_/13) fixtures to set up reusable test clients and mock objects.
- Log test execution details to help debug failures in CI/CD pipelines.