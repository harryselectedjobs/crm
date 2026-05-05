from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from sequence_services.sequence_service_layer import (
    create_sequence, list_sequences, get_sequence, update_sequence, delete_sequence,
    add_step, list_steps, update_step, delete_step,
    enroll_contact, list_enrollments, get_contact_enrollments, update_enrollment_status,
    get_contact_logs, get_enrollment_logs,
    handle_email_event
)

router = APIRouter(prefix="/api/v1", tags=["Sequences"])


# ================================================================
# PYDANTIC SCHEMAS
# ================================================================

class SequenceCreate(BaseModel):
    name:   str
    status: Optional[str] = "draft"
    goal:   Optional[str] = None

class SequenceUpdate(BaseModel):
    name:   Optional[str] = None
    status: Optional[str] = None
    goal:   Optional[str] = None

class StepCreate(BaseModel):
    step_order:         int
    delay_days:         int = 0
    subject:            str
    body_template:      str
    send_window_start:  Optional[str] = "09:00:00"
    send_window_end:    Optional[str] = "17:00:00"

class StepUpdate(BaseModel):
    delay_days:         Optional[int] = None
    subject:            Optional[str] = None
    body_template:      Optional[str] = None
    send_window_start:  Optional[str] = None
    send_window_end:    Optional[str] = None

class EnrollRequest(BaseModel):
    contact_id:  int
    enrolled_by: Optional[str] = "manual"

class StatusUpdate(BaseModel):
    status: str

class WebhookEvent(BaseModel):
    enrollment_id: int
    step_id:       int
    contact_id:    int
    event:         str


# ================================================================
# HELPER — maps service exceptions to HTTP responses
# ================================================================

def _handle(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except LookupError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except ConnectionError as e:
        raise HTTPException(status_code=500, detail=str(e))


# ================================================================
# SEQUENCE ROUTES
# ================================================================

@router.post("/sequences")
def route_create_sequence(payload: SequenceCreate):
    return _handle(create_sequence, payload.name, payload.status, payload.goal)

@router.get("/sequences")
def route_list_sequences():
    return _handle(list_sequences)

@router.get("/sequences/{sequence_id}")
def route_get_sequence(sequence_id: int):
    return _handle(get_sequence, sequence_id)

@router.patch("/sequences/{sequence_id}")
def route_update_sequence(sequence_id: int, payload: SequenceUpdate):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    return _handle(update_sequence, sequence_id, updates)

@router.delete("/sequences/{sequence_id}")
def route_delete_sequence(sequence_id: int):
    return _handle(delete_sequence, sequence_id)


# ================================================================
# STEP ROUTES
# ================================================================

@router.post("/sequences/{sequence_id}/steps")
def route_add_step(sequence_id: int, payload: StepCreate):
    return _handle(
        add_step,
        sequence_id, payload.step_order, payload.delay_days,
        payload.subject, payload.body_template,
        payload.send_window_start, payload.send_window_end
    )

@router.get("/sequences/{sequence_id}/steps")
def route_list_steps(sequence_id: int):
    return _handle(list_steps, sequence_id)

@router.patch("/sequences/{sequence_id}/steps/{step_id}")
def route_update_step(sequence_id: int, step_id: int, payload: StepUpdate):
    updates = {k: v for k, v in payload.model_dump().items() if v is not None}
    return _handle(update_step, sequence_id, step_id, updates)

@router.delete("/sequences/{sequence_id}/steps/{step_id}")
def route_delete_step(sequence_id: int, step_id: int):
    return _handle(delete_step, sequence_id, step_id)


# ================================================================
# ENROLLMENT ROUTES
# ================================================================

@router.post("/sequences/{sequence_id}/enroll")
def route_enroll_contact(sequence_id: int, payload: EnrollRequest):
    return _handle(enroll_contact, sequence_id, payload.contact_id, payload.enrolled_by)

@router.get("/sequences/{sequence_id}/enrollments")
def route_list_enrollments(sequence_id: int):
    return _handle(list_enrollments, sequence_id)

@router.get("/contacts/{contact_id}/enrollments")
def route_get_contact_enrollments(contact_id: int):
    return _handle(get_contact_enrollments, contact_id)

@router.patch("/enrollments/{enrollment_id}/status")
def route_update_enrollment_status(enrollment_id: int, payload: StatusUpdate):
    return _handle(update_enrollment_status, enrollment_id, payload.status)


# ================================================================
# EMAIL LOG ROUTES
# ================================================================

@router.get("/contacts/{contact_id}/logs")
def route_get_contact_logs(contact_id: int):
    return _handle(get_contact_logs, contact_id)

@router.get("/enrollments/{enrollment_id}/logs")
def route_get_enrollment_logs(enrollment_id: int):
    return _handle(get_enrollment_logs, enrollment_id)


# ================================================================
# WEBHOOK ROUTE
# ================================================================

@router.post("/webhooks/email-event")
def route_handle_email_event(payload: WebhookEvent):
    return _handle(handle_email_event, payload.enrollment_id, payload.step_id, payload.event)