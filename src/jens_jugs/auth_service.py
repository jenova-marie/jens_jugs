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
redis_host = os.getenv("REDIS_HOST", "localhost")  # Default to "localhost"
redis_port = int(os.getenv("REDIS_PORT", 6379))    # Default to 6379
redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
logger.info(f"Connected to Redis at {redis_host}:{redis_port}")

# JWT algorithm
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "RS256")  # Retrieve from environment or default to "RS256"

# Retrieve durations from environment variables
JWK_DURATION = int(os.getenv("JWK_DURATION", 86400))  # Default to 1 day (86400 seconds)
JWT_DURATION = int(os.getenv("JWT_DURATION", 3600))   # Default to 1 hour (3600 seconds)

# Retrieve public exponent and key size from environment variables
JWK_PUBLIC_EXPONENT = int(os.getenv("JWK_PUBLIC_EXPONENT", 65537))  # Default to 65537
JWK_KEY_SIZE = int(os.getenv("JWK_KEY_SIZE", 2048))  # Default to 2048

# Validate the active key
logger.info("Validating the active key in Redis.")
active_kid = redis_client.get("active_kid")
if active_kid:
    logger.debug(f"Found active_kid: {active_kid} in Redis.")
    # Fetch the key pair and expiration time
    key_data = redis_client.hgetall(f"jwks:{active_kid}")
    private_key_pem = key_data.get("private_key")
    public_key_pem = key_data.get("public_key")
    exp_at = key_data.get("exp_at")

    if private_key_pem and public_key_pem and exp_at:
        logger.debug(f"Key pair for active_kid: {active_kid} retrieved from Redis.")
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
    logger.info("Generating a new RSA key pair.")
    # Generate RSA private key
    private_key = rsa.generate_private_key(
        public_exponent=JWK_PUBLIC_EXPONENT,
        key_size=JWK_KEY_SIZE,
    )
    logger.debug(f"Generated RSA private key with public_exponent={JWK_PUBLIC_EXPONENT} and key_size={JWK_KEY_SIZE}.")

    # Export private key
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    ).decode("utf-8")
    logger.debug("Exported private key in PEM format.")

    # Export public key
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode("utf-8")
    logger.debug("Exported public key in PEM format.")

    # Increment the Key ID
    active_kid = redis_client.get("active_kid")
    new_kid = str(int(active_kid) + 1) if active_kid else "1"
    logger.info(f"New key ID generated: {new_kid}.")

    # Define the expiration duration for the key pair
    expiration_time = datetime.now(tz=timezone.utc) + timedelta(seconds=JWK_DURATION)
    expiration_timestamp = int(expiration_time.timestamp())  # Convert to UTC timestamp
    logger.debug(f"Key expiration set to {expiration_timestamp} (UTC).")

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
    logger.debug("Converting public key to JWK format.")
    numbers = public_key.public_numbers()
    e = base64.urlsafe_b64encode(numbers.e.to_bytes(3, "big")).decode("utf-8").rstrip("=")
    n = base64.urlsafe_b64encode(numbers.n.to_bytes((numbers.n.bit_length() + 7) // 8, "big")).decode("utf-8").rstrip("=")
    logger.debug(f"Converted public key to JWK with e={e} and n={n}.")
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
    expiration = datetime.utcnow() + timedelta(seconds=JWT_DURATION)
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
        # Connect to Redis using environment variables
        redis_host = os.getenv("REDIS_HOST", "localhost")  # Default to "localhost"
        redis_port = int(os.getenv("REDIS_PORT", 6379))    # Default to 6379
        redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
        logger.debug(f"Connected to Redis at {redis_host}:{redis_port}")

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