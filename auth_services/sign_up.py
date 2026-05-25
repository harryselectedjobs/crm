import boto3
import hashlib
import hmac
import os
from enum import Enum
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
from botocore.exceptions import ClientError
from aws_connection.dynamodb_connection import _get_dynamodb_client
load_dotenv()


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class SignUpStatus(Enum):
    SUCCESS = "success"
    USER_ALREADY_EXISTS = "user_already_exists"
    PASSWORD_MISMATCH = "password_mismatch"
    WEAK_PASSWORD = "weak_password"
    DB_ERROR = "db_error"
    INVALID_INPUT = "invalid_input"


# ──────────────────────────────────────────────
# Response Dataclass
# ──────────────────────────────────────────────

@dataclass
class SignUpResponse:
    success: bool
    status: SignUpStatus
    message: str
    email: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "status": self.status.value,
            "message": self.message,
            "email": self.email,
        }


# ──────────────────────────────────────────────
# Password Utilities
# ──────────────────────────────────────────────

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def validate_password_strength(password: str) -> Optional[str]:
    if len(password) < 8:
        return "Password must be at least 8 characters."
    if not any(c.isupper() for c in password):
        return "Password must contain at least one uppercase letter."
    if not any(c.islower() for c in password):
        return "Password must contain at least one lowercase letter."
    if not any(c.isdigit() for c in password):
        return "Password must contain at least one digit."
    if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        return "Password must contain at least one special character."
    return None


# ──────────────────────────────────────────────
# SIGN UP
# ──────────────────────────────────────────────

def sign_up_user(email: str, password: str, confirm_password: str) -> SignUpResponse:

    # 1. Input validation
    if not email or not isinstance(email, str):
        return SignUpResponse(False, SignUpStatus.INVALID_INPUT, "Email must be a non-empty string.")
    if not password or not isinstance(password, str):
        return SignUpResponse(False, SignUpStatus.INVALID_INPUT, "Password must be a non-empty string.")
    if not confirm_password or not isinstance(confirm_password, str):
        return SignUpResponse(False, SignUpStatus.INVALID_INPUT, "Confirm password must be a non-empty string.")

    email = email.strip().lower()

    # 2. Confirm password match
    if not hmac.compare_digest(password, confirm_password):
        return SignUpResponse(False, SignUpStatus.PASSWORD_MISMATCH, "Passwords do not match.")

    # 3. Password strength
    strength_error = validate_password_strength(password)
    if strength_error:
        return SignUpResponse(False, SignUpStatus.WEAK_PASSWORD, strength_error)

    # 4. Check duplicate email
    try:
        dynamodb = _get_dynamodb_client()
        table = dynamodb.Table("users")
        existing = table.get_item(Key={"email": email})

    except ClientError as e:
        return SignUpResponse(False, SignUpStatus.DB_ERROR, f"DynamoDB error: {e.response['Error']['Message']}")

    if existing.get("Item"):
        return SignUpResponse(False, SignUpStatus.USER_ALREADY_EXISTS, "An account with this email already exists.")

    # 5. Hash and store
    try:
        table.put_item(Item={
            "email": email,
            "password": hash_password(password)
        })

    except ClientError as e:
        return SignUpResponse(False, SignUpStatus.DB_ERROR, f"Failed to create user: {e.response['Error']['Message']}")

    return SignUpResponse(True, SignUpStatus.SUCCESS, "Account created successfully.", email=email)
