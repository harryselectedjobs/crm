from fastapi import APIRouter
from pydantic import BaseModel, EmailStr
from datetime import datetime

from email_transcript.transcript_services import (
    save_email_message,
    get_email_transcripts
)

router = APIRouter(
    prefix="/transcript",
    tags=["Email Transcript"]
)


class EmailMessageRequest(BaseModel):
    sender_email: EmailStr
    receiver_email: EmailStr
    subject: str
    body: str
    direction: str
    sent_at: datetime


@router.post("/save")
def save_email(payload: EmailMessageRequest):
    return save_email_message(**payload.model_dump())


@router.get("/email/{email}")
def fetch_transcripts(email: str):
    return get_email_transcripts(email)