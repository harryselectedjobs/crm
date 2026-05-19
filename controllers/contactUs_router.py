from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from contactUsPage.contactUsServices import (
    add_contact_us,
    get_all_contact_us,
    update_contact_status
)

router = APIRouter(prefix="/contact-us", tags=["Contact Us"])


# =========================
# REQUEST SCHEMA
# =========================
class ContactUsRequest(BaseModel):
    full_name: str
    company_name: str
    work_email: str
    phone_number: str | None = None
    practice_area: str
    hiring_brief: str


class UpdateStatusRequest(BaseModel):
    inquiry_id: int
    is_contacted: bool


# =========================
# 1. ADD RECORD
# =========================
@router.post("/add")
def add_contact(payload: ContactUsRequest):
    result = add_contact_us(payload.dict())

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result


# =========================
# 2. GET ALL RECORDS
# =========================
@router.get("/all")
def get_all_contacts():
    result = get_all_contact_us()

    if not result["success"]:
        print("DB ERROR:", result["message"])  # <-- add this
        raise HTTPException(status_code=400, detail=result["message"])

    return result


# =========================
# 3. UPDATE is_contacted
# =========================
@router.put("/update-status")
def update_status(payload: UpdateStatusRequest):
    result = update_contact_status(
        payload.inquiry_id,
        payload.is_contacted
    )

    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["message"])

    return result