import os
import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from jens_jugs.auth_service import auth_bp
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

@pytest.fixture
def app():
    """Fixture to create the Flask app for testing."""
    app = Flask(__name__)
    app.register_blueprint(auth_bp)
    return app


@pytest.fixture
def client(app):
    """Fixture to create a test client for the Flask app."""
    return app.test_client()


@pytest.fixture
def mock_bearer():
    """Fixture to provide a mock bearer token."""
    return os.environ.get("API_AUTH_KEY", os.getenv("API_AUTH_KEY"))


def generate_mock_private_key():
    """Generate a mock RSA private key for testing purposes."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return private_key_pem.decode("utf-8")


def generate_mock_public_key():
    """Generate a mock RSA public key for testing purposes."""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_pem.decode("utf-8")


@patch("jens_jugs.auth_service.get_logger")
@patch("jens_jugs.auth_service.redis_client")
@patch("jens_jugs.auth_service.serialization.load_pem_private_key")
@patch("jens_jugs.auth_service.jwt.encode")
def test_valid_auth_request(
    mock_jwt_encode,
    mock_load_private_key,
    mock_redis_client,
    mock_get_logger,
    client,
    mock_bearer,
):
    """Test a valid authentication request."""
    mock_get_logger.return_value = MagicMock()

    # Generate a mock private key
    mock_private_key = generate_mock_private_key()

    # Mock Redis responses
    mock_redis_client.get.side_effect = lambda key: "1" if key == "active_kid" else None
    mock_redis_client.hget.side_effect = lambda key, field: (
        mock_private_key if field == "private_key" else None
    )

    # Mock private key loading
    mock_private_key_obj = MagicMock()
    mock_load_private_key.return_value = mock_private_key_obj

    # Mock JWT encoding
    mock_jwt_encode.return_value = "mock-jwt-token"

    # Simulate a valid request
    response = client.post(
        "/api/auth",
        json={"userId": "user123"},
        headers={"Authorization": f"Bearer {mock_bearer}"},
    )

    # Assertions
    assert response.status_code == 200
    assert "token" in response.json
    assert response.json["token"] == "mock-jwt-token"


@patch("jens_jugs.auth_service.get_logger")
def test_missing_authorization_header(mock_get_logger, client):
    """Test a request without the Authorization header."""
    mock_get_logger.return_value = MagicMock()

    # Simulate a request without the Authorization header
    response = client.post(
        "/api/auth",
        json={"userId": "user123"},
    )

    # Assertions
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


@patch("jens_jugs.auth_service.get_logger")
def test_invalid_authorization_header(mock_get_logger, client):
    """Test a request with an invalid Authorization header."""
    mock_get_logger.return_value = MagicMock()

    # Simulate a request with an invalid Authorization header
    response = client.post(
        "/api/auth",
        json={"userId": "user123"},
        headers={"Authorization": "InvalidToken"},
    )

    # Assertions
    assert response.status_code == 401
    assert response.json == {"error": "Unauthorized"}


@patch("jens_jugs.auth_service.get_logger")
def test_missing_user_id(mock_get_logger, client, mock_bearer):
    """Test a request without the userId in the JSON payload."""
    mock_get_logger.return_value = MagicMock()

    # Simulate a request without the userId
    response = client.post(
        "/api/auth",
        json={},
        headers={"Authorization": f"Bearer {mock_bearer}"},
    )

    # Assertions
    assert response.status_code == 400
    assert response.json == {"error": "Missing userId"}


@patch("jens_jugs.auth_service.get_logger")
@patch("jens_jugs.auth_service.redis_client")
def test_missing_active_kid_in_redis(mock_redis_client, mock_get_logger, client, mock_bearer):
    """Test a request when active_kid is missing in Redis."""
    mock_get_logger.return_value = MagicMock()

    # Mock Redis to return None for active_kid
    mock_redis_client.get.return_value = None

    # Simulate a valid request
    response = client.post(
        "/api/auth",
        json={"userId": "user123"},
        headers={"Authorization": f"Bearer {mock_bearer}"},
    )

    # Assertions
    assert response.status_code == 500
    assert response.json == {"error": "Failed to retrieve active_kid from Redis"}