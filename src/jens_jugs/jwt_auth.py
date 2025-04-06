from flask import request, jsonify
from jose import jwt, jwk
from datetime import datetime, timezone
import requests
import os
from cloudwatch_logger import get_logger

logger = get_logger(log_name="jwt_auth")

def jwt_verify(func):
    def wrapper(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            logger.warning("Authorization token is missing.")
            return jsonify({"message": "Authorization token is missing"}), 401
        else:
            token = token.split(" ")[1]

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
            kid = headers.get("kid")
            if not kid:
                raise ValueError("Missing 'kid' in token header")
            logger.info(f"Decoded JWT header, kid: {kid}")

            # Find the matching JWK
            key = next((key for key in jwks["keys"] if key["kid"] == kid), None)
            if not key:
                raise ValueError("No matching JWK found")
            logger.info(f"Found matching JWK for kid: {kid}")

            # Construct the JWK
            public_key = jwk.construct(key)

            # Verify the JWT
            payload = jwt.decode(
                token,
                public_key,
                algorithms=["RS256"],
                audience="urn:user:audience",
                issuer="urn:jens-jugs:issuer",
                options={"verify_exp": True}
            )

            # Check expiration
            if payload["exp"] < datetime.now(tz=timezone.utc).timestamp():
                raise ValueError("Token is expired")

            logger.info(f"JWT verified successfully for userId: {payload.get('userId')}")
            logger.debug(f"JWT payload: {payload}")

            # Attach the payload to the request for downstream use
            request.payload = payload
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