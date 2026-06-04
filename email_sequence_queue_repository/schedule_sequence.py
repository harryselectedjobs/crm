from botocore.exceptions import ClientError
from datetime import datetime
from aws_connection.dynamodb_connection import _get_dynamodb_client


def push_enrollment(sequence: dict, contact: dict):
    dynamodb = _get_dynamodb_client()
    table    = dynamodb.Table("SequenceEnrollments")

    item = {
        "sequence_id":   str(sequence["sequence_id"]),
        "enrollment_id": f"ENR#{contact['contact_id']}",

        "sequence_name": sequence["name"],
        "sequence_goal": sequence.get("goal", ""),

        "steps": [
            {
                "step_order":    step["step_order"],
                "delay_days":    step["delay_days"],
                "subject":       step["subject"],
                "body_template": step["body_template"],
            }
            for step in sorted(sequence["steps"], key=lambda s: s["step_order"])
        ],

        "contact_id": str(contact["contact_id"]),
        "email":      contact["email"],
        "firstname":  contact.get("firstname", ""),
        "lastname":   contact.get("lastname", ""),
        "company":    contact.get("company", ""),
        "jobtitle":   contact.get("jobtitle", ""),

        "current_step": 1,
        "status":       "active",
        "next_send_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "enrolled_at":  datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
        "email_log":    [],
    }

    try:
        table.put_item(
            Item=item,
            ConditionExpression="attribute_not_exists(enrollment_id)"
        )
        print(f"✅ Enrolled {contact['email']} into sequence {sequence['sequence_id']}")

    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            print(f"⚠️  {contact['email']} already enrolled in this sequence")
        else:
            print(f"❌ Error: {e}")


def get_sequence_tracking(sequence_id: str) -> dict:
    """
    Returns full tracking status of a sequence —
    how many contacts are active, completed, bounced,
    and per-contact progress with email log.

    Parameters
    ----------
    sequence_id : str  e.g. "27"
    """

    dynamodb = _get_dynamodb_client()
    table = dynamodb.Table("SequenceEnrollments")

    # Fetch all enrollments for this sequence
    response = table.query(
        KeyConditionExpression=Key("sequence_id").eq(str(sequence_id))
    )
    records = response.get("Items", [])

    if not records:
        return {"error": f"No enrollments found for sequence {sequence_id}"}

    # ── Summary counters ──────────────────────────────────────────────────────
    summary = {
        "sequence_id": sequence_id,
        "sequence_name": records[0].get("sequence_name", ""),
        "sequence_goal": records[0].get("sequence_goal", ""),
        "total_enrolled": len(records),
        "active": 0,
        "completed": 0,
        "bounced": 0,
        "paused": 0,
        "unsubscribed": 0,
    }

    # ── Per contact breakdown ─────────────────────────────────────────────────
    contacts = []
    total_steps = len(records[0].get("steps", []))

    for record in records:
        status = record.get("status", "unknown")
        current_step = int(record.get("current_step", 1))
        email_log = record.get("email_log", [])

        # increment summary counter
        if status in summary:
            summary[status] += 1

        # build per-step log
        steps_status = []
        for step in sorted(record.get("steps", []), key=lambda s: s["step_order"]):
            order = int(step["step_order"])
            log_entry = next((l for l in email_log if int(l.get("step_order", 0)) == order), None)

            if log_entry:
                step_state = "sent"
                if log_entry.get("bounced"):
                    step_state = "bounced"
                elif log_entry.get("clicked_at"):
                    step_state = "clicked"
                elif log_entry.get("opened_at"):
                    step_state = "opened"
            elif order == current_step and status == "active":
                step_state = "pending"
            elif order < current_step:
                step_state = "sent"
            else:
                step_state = "upcoming"

            steps_status.append({
                "step_order": order,
                "subject": step.get("subject", ""),
                "state": step_state,
                "sent_at": log_entry.get("sent_at") if log_entry else None,
                "opened_at": log_entry.get("opened_at") if log_entry else None,
                "clicked_at": log_entry.get("clicked_at") if log_entry else None,
                "bounced": log_entry.get("bounced", False) if log_entry else False,
            })

        contacts.append({
            "contact_id": record.get("contact_id"),
            "email": record.get("email"),
            "firstname": record.get("firstname"),
            "lastname": record.get("lastname"),
            "company": record.get("company"),
            "status": status,
            "current_step": current_step,
            "total_steps": total_steps,
            "progress": f"{current_step}/{total_steps}",
            "next_send_at": record.get("next_send_at"),
            "enrolled_at": record.get("enrolled_at"),
            "steps": steps_status,
        })

    # sort — active first, then completed, then rest
    order_map = {"active": 0, "paused": 1, "completed": 2, "bounced": 3, "unsubscribed": 4}
    contacts.sort(key=lambda c: order_map.get(c["status"], 5))

    return {
        "summary": summary,
        "contacts": contacts,
    }