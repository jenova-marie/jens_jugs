from flask import request, jsonify
from jose import jwt, jwk
from datetime import datetime, timezone
import requests
import os
from jens_jugs.logger import get_logger

logger = get_logger(log_name="jwt_auth", streams=["console", "cloudwatch", "file"], config={
                    "file": {
                        "path": "./logs",
                        "max_bytes": 10 * 1024 * 1024,  # 10 MB
                        "backup_count": 5
                    }
                })

def jwt_verify(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            logger.warning("Authorization token is missing.")
            return jsonify({"message": "Authorization token is missing"}), 401
        else:
            logger.debug(f"Authorization header received: {token}")
            token = token.split(" ")[1]
            logger.debug(f"Extracted JWT: {token}")

        try:
            # Fetch the JWKs from the authentication server
            jwks_url = f"http://localhost:{os.getenv('API_PORT_HTTP', '5000')}/.well-known/jwks.json"
            logger.info(f"Fetching JWKs from {jwks_url}")
            response = requests.get(jwks_url)
            response.raise_for_status()
            jwks = response.json()
            logger.debug(f"Fetched JWKs: {jwks}")

            # Decode the JWT header to get the key ID (kid)
            headers = jwt.get_unverified_header(token)
            logger.debug(f"Decoded JWT header: {headers}")
            kid = headers.get("kid")
            if not kid:
                logger.error("Missing 'kid' in JWT header.")
                raise ValueError("Missing 'kid' in token header")
            logger.info(f"Decoded JWT header, kid: {kid}")

            # Find the matching JWK
            key = next((key for key in jwks["keys"] if key["kid"] == kid), None)
            if not key:
                logger.error(f"No matching JWK found for kid: {kid}")
                raise ValueError("No matching JWK found")
            logger.info(f"Found matching JWK for kid: {kid}")
            logger.debug(f"Matching JWK: {key}")

            # Construct the JWK
            logger.debug("Constructing public key from JWK.")
            public_key = jwk.construct(key)
            logger.debug("Public key constructed successfully.")

            # Verify the JWT
            logger.info("Verifying JWT.")
            payload = jwt.decode(
                token,
                public_key,
                algorithms=[os.getenv("JWT_ALGORITHM", "RS256")],
                audience="urn:user:audience",
                issuer="urn:jens-jugs:issuer",
                options={"verify_exp": True}
            )
            logger.debug(f"Decoded JWT payload: {payload}")

            # Check expiration
            current_timestamp = datetime.now(tz=timezone.utc).timestamp()
            if payload["exp"] < current_timestamp:
                logger.error(f"Token is expired. Current timestamp: {current_timestamp}, exp: {payload['exp']}")
                raise ValueError("Token is expired")
            logger.info(f"JWT verified successfully for userId: {payload.get('userId')}")
            logger.debug(f"JWT payload: {payload}")

            # Attach the payload to the request for downstream use
            request.payload = payload
            logger.debug("JWT payload attached to the request.")
            return func(*args, **kwargs)

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to fetch JWKs: {e}")
            return jsonify({"message": "Failed to fetch JWKs"}), 500
        except jwt.ExpiredSignatureError:
            logger.error("JWT verification failed: Token has expired.")
            return jsonify({"message": "Token has expired"}), 401
        except jwt.JWTError as e:
            logger.error(f"JWT verification failed: {e}")
            return jsonify({"message": f"Invalid Authorization: {str(e)}"}), 401
        except Exception as e:
            logger.error(f"Unexpected error during JWT verification: {e}")
            return jsonify({"message": f"Unexpected error: {str(e)}"}), 500

    wrapper.__name__ = func.__name__
    return wrapper