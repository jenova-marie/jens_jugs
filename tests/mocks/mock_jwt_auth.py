import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_jwt_verify():
    """
    Fixture to mock jwt_verify as a pass-through decorator.
    This allows Flask routes decorated with @jwt_verify to be tested
    without requiring actual JWT verification.
    """
    # Create a mock for jwt_verify
    mock = MagicMock()

    # Define the pass-through decorator
    def jwt_verify_decorator(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__name__ = func.__name__
        return wrapper

    # Set the side effect of the mock to use the pass-through decorator
    mock.side_effect = jwt_verify_decorator

    return mock
