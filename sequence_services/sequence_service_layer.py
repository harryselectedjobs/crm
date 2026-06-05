from datetime import datetime
from mysql.connector import Error
from boto3.dynamodb.conditions import Key

from aws_connection.dynamodb_connection import _get_dynamodb_client
from repository.db_connection import get_db_connection


# ================================================================
# HELPERS
# ================================================================

def _fetch_all(cursor) -> list:
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def _fetch_one(cursor) -> dict | None:
    columns = [col[0] for col in cursor.description]
    row = cursor.fetchone()
    return dict(zip(columns, row)) if row else None


# ================================================================
# SEQUENCE SERVICES
# ================================================================

def create_sequence(name: str, status: str, goal: str | None) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO sequence (name, status, goal) VALUES (%s, %s, %s)",
            (name, status, goal)
        )
        conn.commit()
        cursor.execute("SELECT * FROM sequence WHERE sequence_id = %s", (cursor.lastrowid,))
        return _fetch_one(cursor)
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


def list_sequences() -> list:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sequence ORDER BY created_at DESC")
        return _fetch_all(cursor)
    finally:
        conn.close()


def get_sequence(sequence_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM sequence WHERE sequence_id = %s", (sequence_id,))
        seq = _fetch_one(cursor)
        if not seq:
            raise LookupError("Sequence not found")

        cursor.execute(
            "SELECT * FROM sequence_step WHERE sequence_id = %s ORDER BY step_order",
            (sequence_id,)
        )
        seq["steps"] = _fetch_all(cursor)
        return seq
    finally:
        conn.close()


def update_sequence(sequence_id: int, updates: dict) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        if not updates:
            raise ValueError("No fields to update")

        fields = ", ".join(f"{k} = %s" for k in updates)
        values = list(updates.values()) + [sequence_id]

        cursor = conn.cursor()
        cursor.execute(f"UPDATE sequence SET {fields} WHERE sequence_id = %s", values)
        conn.commit()

        cursor.execute("SELECT * FROM sequence WHERE sequence_id = %s", (sequence_id,))
        seq = _fetch_one(cursor)
        if not seq:
            raise LookupError("Sequence not found")
        return seq
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


def delete_sequence(sequence_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT sequence_id FROM sequence WHERE sequence_id = %s", (sequence_id,))
        if not cursor.fetchone():
            raise LookupError("Sequence not found")

        cursor.execute("DELETE FROM sequence WHERE sequence_id = %s", (sequence_id,))
        conn.commit()
        return {"message": "Sequence deleted"}
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


# ================================================================
# STEP SERVICES
# ================================================================

def add_step(sequence_id: int, step_order: int, delay_days: int,
             subject: str, body_template: str,
             send_window_start: str, send_window_end: str) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()

        # Verify sequence exists
        cursor.execute("SELECT sequence_id FROM sequence WHERE sequence_id = %s", (sequence_id,))
        if not cursor.fetchone():
            raise LookupError("Sequence not found")

        cursor.execute(
            """INSERT INTO sequence_step
               (sequence_id, step_order, delay_days, subject, body_template, send_window_start, send_window_end)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (sequence_id, step_order, delay_days, subject, body_template, send_window_start, send_window_end)
        )
        conn.commit()
        cursor.execute("SELECT * FROM sequence_step WHERE step_id = %s", (cursor.lastrowid,))
        return _fetch_one(cursor)
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


def list_steps(sequence_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sequence_step WHERE sequence_id = %s ORDER BY step_order",
            (sequence_id,)
        )
        return _fetch_all(cursor)
    finally:
        conn.close()


def update_step(sequence_id: int, step_id: int, updates: dict) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        if not updates:
            raise ValueError("No fields to update")

        fields = ", ".join(f"{k} = %s" for k in updates)
        values = list(updates.values()) + [step_id, sequence_id]

        cursor = conn.cursor()
        cursor.execute(
            f"UPDATE sequence_step SET {fields} WHERE step_id = %s AND sequence_id = %s",
            values
        )
        conn.commit()

        cursor.execute("SELECT * FROM sequence_step WHERE step_id = %s", (step_id,))
        step = _fetch_one(cursor)
        if not step:
            raise LookupError("Step not found")
        return step
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


def delete_step(sequence_id: int, step_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT step_id FROM sequence_step WHERE step_id = %s AND sequence_id = %s",
            (step_id, sequence_id)
        )
        if not cursor.fetchone():
            raise LookupError("Step not found")

        cursor.execute(
            "DELETE FROM sequence_step WHERE step_id = %s AND sequence_id = %s",
            (step_id, sequence_id)
        )
        conn.commit()
        return {"message": "Step deleted"}
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


# ================================================================
# ENROLLMENT SERVICES
# ================================================================

def enroll_contact(sequence_id: int, contact_id: int, enrolled_by: str) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()

        # Sequence must exist and be active
        cursor.execute("SELECT status FROM sequence WHERE sequence_id = %s", (sequence_id,))
        seq = _fetch_one(cursor)
        if not seq:
            raise LookupError("Sequence not found")
        if seq["status"] != "active":
            raise ValueError("Sequence is not active. Activate it before enrolling contacts.")

        # Sequence must have at least 1 step
        cursor.execute(
            "SELECT COUNT(*) as cnt FROM sequence_step WHERE sequence_id = %s", (sequence_id,)
        )
        row = cursor.fetchone()
        if row[0] == 0:
            raise ValueError("Sequence has no steps. Add at least one step before enrolling.")

        # No duplicate enrollments
        cursor.execute(
            "SELECT enrollment_id FROM contact_enrollment WHERE contact_id = %s AND sequence_id = %s",
            (contact_id, sequence_id)
        )
        if cursor.fetchone():
            raise ValueError("Contact is already enrolled in this sequence")

        # Enroll — first mail goes out immediately
        cursor.execute(
            """INSERT INTO contact_enrollment
               (contact_id, sequence_id, enrolled_by, current_step, next_send_at)
               VALUES (%s, %s, %s, 1, %s)""",
            (contact_id, sequence_id, enrolled_by, datetime.utcnow())
        )
        conn.commit()
        cursor.execute(
            "SELECT * FROM contact_enrollment WHERE enrollment_id = %s", (cursor.lastrowid,)
        )
        return _fetch_one(cursor)
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


def list_enrollments(sequence_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM contact_enrollment WHERE sequence_id = %s ORDER BY enrolled_at DESC",
            (sequence_id,)
        )
        return _fetch_all(cursor)
    finally:
        conn.close()


def get_contact_enrollments(contact_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT ce.*, s.name AS sequence_name, s.goal
               FROM contact_enrollment ce
               JOIN sequence s ON ce.sequence_id = s.sequence_id
               WHERE ce.contact_id = %s
               ORDER BY ce.enrolled_at DESC""",
            (contact_id,)
        )
        return _fetch_all(cursor)
    finally:
        conn.close()


def update_enrollment_status(enrollment_id: int, status: str) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT enrollment_id FROM contact_enrollment WHERE enrollment_id = %s", (enrollment_id,)
        )
        if not cursor.fetchone():
            raise LookupError("Enrollment not found")

        # Clear next_send_at when stopping the sequence
        clear_next = status in ("paused", "completed", "unsubscribed", "bounced")
        if clear_next:
            cursor.execute(
                "UPDATE contact_enrollment SET status = %s, next_send_at = NULL WHERE enrollment_id = %s",
                (status, enrollment_id)
            )
        else:
            cursor.execute(
                "UPDATE contact_enrollment SET status = %s WHERE enrollment_id = %s",
                (status, enrollment_id)
            )

        conn.commit()
        cursor.execute("SELECT * FROM contact_enrollment WHERE enrollment_id = %s", (enrollment_id,))
        return _fetch_one(cursor)
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


# ================================================================
# EMAIL LOG SERVICES
# ================================================================

def get_contact_logs(contact_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT el.*, ss.subject, ss.step_order, s.name AS sequence_name
               FROM sequence_email_log el
               JOIN sequence_step ss ON el.step_id = ss.step_id
               JOIN sequence s ON ss.sequence_id = s.sequence_id
               WHERE el.contact_id = %s
               ORDER BY el.sent_at DESC""",
            (contact_id,)
        )
        return _fetch_all(cursor)
    finally:
        conn.close()


def get_enrollment_logs(enrollment_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM sequence_email_log WHERE enrollment_id = %s ORDER BY sent_at",
            (enrollment_id,)
        )
        return _fetch_all(cursor)
    finally:
        conn.close()


# ================================================================
# WEBHOOK SERVICE
# ================================================================

def handle_email_event(enrollment_id: int, step_id: int, event: str) -> dict:
    conn = get_db_connection()
    if not conn:
        raise ConnectionError("DB connection failed")
    try:
        cursor = conn.cursor()
        now = datetime.utcnow()
        event = event.lower()

        field_map = {
            "opened":  "opened_at",
            "clicked": "clicked_at",
            "replied": "replied_at",
        }

        if event in field_map:
            cursor.execute(
                f"UPDATE sequence_email_log SET {field_map[event]} = %s "
                f"WHERE enrollment_id = %s AND step_id = %s",
                (now, enrollment_id, step_id)
            )
        elif event == "bounced":
            cursor.execute(
                "UPDATE sequence_email_log SET bounced = TRUE WHERE enrollment_id = %s AND step_id = %s",
                (enrollment_id, step_id)
            )
            cursor.execute(
                "UPDATE contact_enrollment SET status = 'bounced', next_send_at = NULL WHERE enrollment_id = %s",
                (enrollment_id,)
            )
        elif event == "unsubscribed":
            cursor.execute(
                "UPDATE sequence_email_log SET unsubscribed = TRUE WHERE enrollment_id = %s AND step_id = %s",
                (enrollment_id, step_id)
            )
            cursor.execute(
                "UPDATE contact_enrollment SET status = 'unsubscribed', next_send_at = NULL WHERE enrollment_id = %s",
                (enrollment_id,)
            )
        else:
            raise ValueError(f"Unknown event type: {event}")

        conn.commit()
        return {"message": f"Event '{event}' recorded"}
    except Error as e:
        raise ValueError(str(e))
    finally:
        conn.close()


def get_unenrolled_contacts(sequence_id: str, page: int = 1, limit: int = 10) -> dict:
    try:
        # Step 1 — get already enrolled contact_ids from DynamoDB
        dynamodb = _get_dynamodb_client()
        table = dynamodb.Table("SequenceEnrollments")

        response = table.query(
            KeyConditionExpression=Key("sequence_id").eq(str(sequence_id)),
            ProjectionExpression="contact_id"
        )
        enrolled_ids = [int(item["contact_id"]) for item in response.get("Items", [])]

        # Step 2 — fetch contacts from MySQL excluding enrolled ones
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        offset = (page - 1) * limit

        if enrolled_ids:
            placeholders = ", ".join(["%s"] * len(enrolled_ids))
            exclude_clause = f"AND contactId NOT IN ({placeholders})"
        else:
            exclude_clause = ""
            enrolled_ids = []

        # count
        cursor.execute(
            f"SELECT COUNT(*) as total FROM contacts WHERE 1=1 {exclude_clause}",
            enrolled_ids
        )
        total = cursor.fetchone()["total"]

        # fetch
        cursor.execute(
            f"SELECT * FROM contacts WHERE 1=1 {exclude_clause} ORDER BY contactId DESC LIMIT %s OFFSET %s",
            enrolled_ids + [limit, offset]
        )
        contacts = cursor.fetchall()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": contacts,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit,
            "already_enrolled": len(enrolled_ids)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}