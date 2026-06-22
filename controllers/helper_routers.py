from fastapi import APIRouter, HTTPException

from email_listener_services.helper_functions import check_email_id_exits_in_contact, \
    delete_sequence_enrollment_by_email

router = APIRouter(prefix="/helper", tags=["helper"])


@router.get("/email-exists/{email}")
async def email_exists(email: str):
    try:
        exists = check_email_id_exits_in_contact(email)

        return {
            "email": email,
            "exists": exists
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check email: {str(exc)}"
        )


@router.delete("/sequence-enrollment/{email}")
async def delete_sequence_enrollment(email: str):
    try:
        deleted_count = delete_sequence_enrollment_by_email(email)

        return {
            "success": True,
            "email": email,
            "deleted_records": deleted_count
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete sequence enrollment(s): {str(exc)}"
        )