from fastapi import APIRouter, HTTPException, Body

from email_listener_services.helper_functions import check_email_id_exits_in_contact, \
    delete_sequence_enrollment_by_email, update_lead_status, get_leads_by_status, save_lead_from_sequence

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

@router.post("/crm-sequence-lead")
async def create_crm_sequence_lead(
    email: str = Body(...),
    status: str = Body(default="open")
):
    try:
        return save_lead_from_sequence(
            email=email,
            status=status,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save lead: {str(exc)}"
        )


@router.get("/crm-sequence-leads/{status}")
async def fetch_crm_sequence_leads(status: str):
    try:
        leads = get_leads_by_status(status)

        return {
            "status": status,
            "count": len(leads),
            "data": leads,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch leads: {str(exc)}"
        )


@router.put("/crm-sequence-lead/{email}/status")
async def change_crm_sequence_lead_status(
    email: str,
    status: str = Body(..., embed=True)
):
    try:
        updated_record = update_lead_status(
            email=email,
            status=status,
        )

        return {
            "success": True,
            "data": updated_record,
        }

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update lead status: {str(exc)}"
        )