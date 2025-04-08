import os
import unittest
from unittest.mock import patch, MagicMock, ANY
from flask import Flask
from jens_jugs.auth_service import auth_bp
from tests.test_base import BaseTestCase
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def generate_mock_private_key():
    """
    Generate a mock RSA private key for testing purposes.

    Returns:
        str: The private key in PEM format as a string.
    """
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
    """
    Generate a mock RSA public key for testing purposes.

    Returns:
        str: The public key in PEM format as a string.
    """
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

class TestAuthService(BaseTestCase):
    def setUp(self):
        super().setUp()  # Call BaseTestCase's setUp to initialize self.local_logger
        self.app = Flask(__name__)
        self.app.register_blueprint(auth_bp)
        self.client = self.app.test_client()
        self.bearer = os.environ.get("API_AUTH_KEY")

    @patch("jens_jugs.auth_service.get_logger")
    @patch("jens_jugs.auth_service.redis_client")
    @patch("jens_jugs.auth_service.serialization.load_pem_private_key")
    @patch("jens_jugs.auth_service.jwt.encode")
    def test_valid_auth_request(
        self,
        mock_jwt_encode,
        mock_load_private_key,
        mock_redis_client,
        mock_get_logger,
    ):
        # Use self.local_logger from BaseTestCase
        mock_get_logger.return_value = self.local_logger

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
        response = self.client.post(
            "/api/auth",
            json={"userId": "user123"},
            headers={"Authorization": "Bearer " + self.bearer},
        )

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.json)
        self.assertEqual(response.json["token"], "mock-jwt-token")

    @patch("jens_jugs.auth_service.get_logger")
    def test_missing_authorization_header(self, mock_get_logger):
        # Use self.local_logger from BaseTestCase
        mock_get_logger.return_value = self.local_logger

        # Simulate a request without the Authorization header
        response = self.client.post(
            "/api/auth",
            json={"userId": "user123"},
        )

        # Assertions
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "Unauthorized"})

    @patch("jens_jugs.auth_service.get_logger")
    def test_invalid_authorization_header(self, mock_get_logger):
        # Use self.local_logger from BaseTestCase
        mock_get_logger.return_value = self.local_logger

        # Simulate a request with an invalid Authorization header
        response = self.client.post(
            "/api/auth",
            json={"userId": "user123"},
            headers={"Authorization": "InvalidToken"},
        )

        # Assertions
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.json, {"error": "Unauthorized"})

    @patch("jens_jugs.auth_service.get_logger")
    def test_missing_user_id(self, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        # Simulate a request without the userId in the JSON payload
        response = self.client.post(
            "/api/auth",
            json={},
            headers={"Authorization": "Bearer " + self.bearer},
        )

        # Assertions
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"error": "Missing userId"})

    @patch("jens_jugs.auth_service.get_logger")
    @patch("jens_jugs.auth_service.redis_client")
    def test_missing_active_kid_in_redis(self, mock_redis_client, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        # Mock Redis to return None for active_kid
        mock_redis_client.get.return_value = None

        # Simulate a valid request
        response = self.client.post(
            "/api/auth",
            json={"userId": "user123"},
            headers={"Authorization": "Bearer " + self.bearer},

        )

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Failed to retrieve active_kid from Redis"})

    @patch("jens_jugs.auth_service.get_logger")
    @patch("jens_jugs.auth_service.redis_client")
    def test_missing_private_key_in_redis(self, mock_redis_client, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        # Mock Redis to return None for the private key
        mock_redis_client.get.return_value = "1"
        mock_redis_client.hget.return_value = None

        # Simulate a valid request
        response = self.client.post(
            "/api/auth",
            json={"userId": "user123"},
            headers={"Authorization": "Bearer " + self.bearer},
        )

        # Assertions
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json, {"error": "Failed to retrieve private key from Redis"})

    @patch("jens_jugs.auth_service.get_logger")
    @patch("jens_jugs.auth_service.redis_client")
    def test_valid_jwks_retrieval(self, mock_redis_client, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        # Generate a mock public key
        mock_public_key = generate_mock_public_key()

        # Mock Redis to return a public key for the active_kid
        mock_redis_client.scan_iter.return_value = ["jwks:1"]
        mock_redis_client.hget.return_value = mock_public_key

        # Simulate a request to the JWKS endpoint
        response = self.client.get("/.well-known/jwks.json")

        # Assertions
        self.assertEqual(response.status_code, 200)
        self.assertIn("keys", response.json)
        self.assertEqual(len(response.json["keys"]), 1)
        self.assertIn("kid", response.json["keys"][0])
        self.assertIn("n", response.json["keys"][0])
        self.assertIn("e", response.json["keys"][0])

    @patch("jens_jugs.auth_service.get_logger")
    @patch("jens_jugs.auth_service.redis_client")
    def test_no_jwks_in_redis(self, mock_redis_client, mock_get_logger):
        mock_get_logger.return_value = self.local_logger
        # Mock Redis to return no keys
        mock_redis_client.scan_iter.return_value = []

        # Simulate a request to the JWKS endpoint
        response = self.client.get("/.well-known/jwks.json")

        # Assertions
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json, {"error": "No JWKs found"})


if __name__ == "__main__":
    unittest.main()