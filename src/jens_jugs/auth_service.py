from flask import Blueprint, request, jsonify
import jwt  # PyJWT library for generating JWTs
from datetime import datetime, timedelta, timezone
import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import json
import base64
import redis
from cloudwatch_logger import get_logger

# Initialize logger
logger = get_logger(log_name="auth_service")

# Connect to Redis
redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)

# JWT algorithm
JWT_ALGORITHM = "RS256"

# Validate the active key
active_kid = redis_client.get("active_kid")
if active_kid:
    # Fetch the key pair and expiration time
    key_data = redis_client.hgetall(f"jwks:{active_kid}")
    private_key_pem = key_data.get("private_key")
    public_key_pem = key_data.get("public_key")
    exp_at = key_data.get("exp_at")

    if private_key_pem and public_key_pem and exp_at:
        # Check if the key has expired
        current_timestamp = int(datetime.now(tz=timezone.utc).timestamp())
        if current_timestamp >= int(exp_at):
            logger.warning(f"Key pair for active_kid: {active_kid} has expired. Generating a new key pair.")
            active_kid = None  # Mark as invalid to generate a new key pair
        else:
            logger.info(f"Using existing key pair with active_kid: {active_kid}, exp_at: {exp_at} (UTC).")
    else:
        logger.warning(f"Key pair for active_kid: {active_kid} is missing or invalid. Generating a new key pair.")
        active_kid = None  # Mark as invalid to generate a new key pair
else:
    logger.info("No active_kid found in Redis. Generating a new key pair.")

# If no valid key pair exists, generate a new one
if not active_kid:
    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )

    # Export private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")

    # Export public key
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")

    # Increment the Key ID
    active_kid = redis_client.get("active_kid")
    new_kid = str(int(active_kid) + 1) if active_kid else "1"

    # Define the expiration duration for the key pair
    key_expiration_duration = timedelta(days=1)  # Set expiration to 1 day (adjust as needed)
    expiration_time = datetime.now(tz=timezone.utc) + key_expiration_duration
    expiration_timestamp = int(expiration_time.timestamp())  # Convert to UTC timestamp

    # Store the new keys in Redis with an expiration timestamp
    redis_client.hset(f"jwks:{new_kid}", mapping={
        "private_key": private_key_pem,
        "public_key": public_key_pem,
        "exp_at": expiration_timestamp  # Store the expiration timestamp
    })
    redis_client.set("active_kid", new_kid)  # Mark the new key as active
    logger.info(f"Generated new key pair with kid: {new_kid}, exp_at: {expiration_timestamp} (UTC).")
else:
    logger.info(f"Using existing key pair with kid: {active_kid}")

# Convert public key to JWK format
def public_key_to_jwk(public_key):
    numbers = public_key.public_numbers()
    e = base64.urlsafe_b64encode(numbers.e.to_bytes(3, "big")).decode("utf-8").rstrip("=")
    n = base64.urlsafe_b64encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")).decode("utf-8").rstrip("=")
    return {
        "kty": "RSA",
        "use": "sig",
        "kid": active_kid,  # Use the updated Key ID
        "alg": JWT_ALGORITHM,  # Use the JWT_ALGORITHM variable
        "n": n,
        "e": e,
    }

# Create a Flask Blueprint for the auth service
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/api/auth", methods=["POST"])
def generate_jwt():
    logger.debug("Received request for /api/auth endpoint.")
    user_id = request.json.get("userId")
    if not user_id:
        logger.warning("Missing userId in request body.")
        return jsonify({"error": "Missing userId"}), 400

    # Fetch the active private key from Redis
    redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
    active_kid = redis_client.get("active_kid")
    if not active_kid:
        logger.error("No active_kid found in Redis.")
        raise RuntimeError("No active_kid found in Redis.")

    private_key_pem = redis_client.hget(f"jwks:{active_kid}", "private_key")
    if not private_key_pem:
        logger.error(f"No private key found for active_kid: {active_kid}")
        raise RuntimeError(f"No private key found for active_kid: {active_kid}")

    logger.info(f"Loaded active_kid: {active_kid} from Redis.")
    private_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=None)

    # Generate JWT token
    expiration = datetime.utcnow() + timedelta(hours=1)
    payload = {
        "userId": user_id,
        "exp": expiration,
        "iat": datetime.utcnow(),
        "iss": "urn:jens-jugs:issuer"  # Add the issuer claim
    }
    token = jwt.encode(payload, private_key, algorithm=JWT_ALGORITHM, headers={"kid": active_kid})

    logger.info(f"Generated JWT for userId: {user_id}, kid: {active_kid}")
    logger.debug(f"JWT payload: {payload}")

    return jsonify({"token": token})

# JWKS endpoint
@auth_bp.route("/.well-known/jwks.json", methods=["GET"])
def jwks():
    logger.info("Received request for /.well-known/jwks.json endpoint.")
    try:
        # Connect to Redis
        redis_client = redis.StrictRedis(host="localhost", port=6379, decode_responses=True)
        keys = []

        # Fetch all JWKs from Redis
        for key_id in redis_client.keys("jwks:*"):
            logger.debug(f"Processing Redis key: {key_id}")
            public_key_pem = redis_client.hget(key_id, "public_key")
            if not public_key_pem:
                logger.warning(f"No public key found for key_id: {key_id}")
                continue

            # Convert public key to JWK format
            public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
            jwk = public_key_to_jwk(public_key)
            keys.append(jwk)
            logger.debug(f"Added JWK for key_id: {key_id}: {jwk}")

        if not keys:
            logger.warning("No JWKs found in Redis.")
            return jsonify({"error": "No JWKs found"}), 404

        logger.info(f"Returning {len(keys)} JWK(s).")
        return jsonify({"keys": keys}), 200

    except redis.ConnectionError as e:
        logger.error(f"Redis connection error: {e}")
        return jsonify({"error": "Failed to connect to Redis"}), 500
    except Exception as e:
        logger.error(f"Error processing JWKs request: {e}")
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500