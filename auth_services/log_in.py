import boto3
import hashlib
import hmac
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from botocore.exceptions import ClientError
from aws_connection.dynamodb_connection import _get_dynamodb_client


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class AuthStatus(Enum):
    SUCCESS = "success"
    INVALID_CREDENTIALS = "invalid_credentials"
    USER_NOT_FOUND = "user_not_found"
    DB_ERROR = "db_error"
    INVALID_INPUT = "invalid_input"


# ──────────────────────────────────────────────
# Response Dataclass
# ──────────────────────────────────────────────

@dataclass
class AuthResponse:
    is_authenticated: bool
    status: AuthStatus
    message: str
    email: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "is_authenticated": self.is_authenticated,
            "status": self.status.value,
            "message": self.message,
            "email": self.email,
        }


# ──────────────────────────────────────────────
# Password Hashing Utility
# ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    """SHA-256 hash. Replace with bcrypt/argon2 for production."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def verify_password(plain: str, stored_hash: str) -> bool:
    """Constant-time comparison to prevent timing attacks."""
    return hmac.compare_digest(
        hash_password(plain),
        stored_hash
    )


# ──────────────────────────────────────────────
# Core Auth Function
# ──────────────────────────────────────────────

def authenticate_user(email: str, password: str) -> AuthResponse:
    """
    Authenticates a user against DynamoDB table 'users'.

    Args:
        email:    User's email (partition key).
        password: Plain-text password to verify.

    Returns:
        AuthResponse with is_authenticated bool + status enum.
    """

    # 1. Input validation
    if not email or not isinstance(email, str):
        return AuthResponse(
            is_authenticated=False,
            status=AuthStatus.INVALID_INPUT,
            message="Email must be a non-empty string."
        )
    if not password or not isinstance(password, str):
        return AuthResponse(
            is_authenticated=False,
            status=AuthStatus.INVALID_INPUT,
            message="Password must be a non-empty string."
        )

    email = email.strip().lower()

    # 2. Fetch user from DynamoDB
    try:
        dynamodb = _get_dynamodb_client()
        table = dynamodb.Table("users")

        response = table.get_item(
            Key={"email": email}
        )

    except ClientError as e:
        return AuthResponse(
            is_authenticated=False,
            status=AuthStatus.DB_ERROR,
            message=f"DynamoDB error: {e.response['Error']['Message']}"
        )

    # 3. Check user exists
    item = response.get("Item")
    if not item:
        return AuthResponse(
            is_authenticated=False,
            status=AuthStatus.USER_NOT_FOUND,
            message="No user found with the provided email."
        )

    # 4. Verify password
    stored_password = item.get("password", "")

    # ── If passwords are stored as plain text (not recommended) ──
    # password_match = hmac.compare_digest(password, stored_password)

    # ── If passwords are stored as SHA-256 hash (recommended) ──
    password_match = verify_password(password, stored_password)

    if not password_match:
        return AuthResponse(
            is_authenticated=False,
            status=AuthStatus.INVALID_CREDENTIALS,
            message="Incorrect password.",
            email=email
        )

    # 5. Success
    return AuthResponse(
        is_authenticated=True,
        status=AuthStatus.SUCCESS,
        message="Authentication successful.",
        email=email
    )
