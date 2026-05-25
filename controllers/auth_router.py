from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from auth_services.log_in import authenticate_user
from auth_services.sign_up import sign_up_user

router = APIRouter(prefix="/api", tags=["Authentication"])


# ──────────────────────────────────────────────
# Request Models
# ──────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class SignUpRequest(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

@router.post("/login")
def login(payload: LoginRequest):
    result = authenticate_user(payload.email, payload.password)
    return result.to_dict()


@router.post("/signup")
def signup(payload: SignUpRequest):
    result = sign_up_user(payload.email, payload.password, payload.confirm_password)
    return result.to_dict()