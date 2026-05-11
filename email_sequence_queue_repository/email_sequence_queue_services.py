

import json
from repository.db_connection import get_db_connection


def add_sequence_records(email_list, sequence_response):

    connection = get_db_connection()

    if not connection:
        return {
            "success": False,
            "message": "Database connection failed"
        }

    try:
        cursor = connection.cursor()

        insert_query = """
        INSERT INTO email_sequence_queue (
            email,
            sequence,
            current_step,
            next_send_at,
            status,
            completed
        )
        VALUES (
            %s,
            %s,
            %s,
            NOW(),
            %s,
            %s
        )
        """

        sequence_json = json.dumps(sequence_response)

        records = []

        for email in email_list:

            records.append((
                email,
                sequence_json,
                0,
                'active',
                False
            ))

        cursor.executemany(insert_query, records)

        connection.commit()

        return {
            "success": True,
            "message": f"{cursor.rowcount} records inserted successfully",
            "total_records": cursor.rowcount,
            "sequence_name": sequence_response.get("name")
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        cursor.close()
        connection.close()


def get_scheduled_sequences():

    connection = get_db_connection()

    if not connection:
        return {
            "success": False,
            "message": "Database connection failed"
        }

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT
            id,
            email,
            sequence,
            current_step,
            next_send_at,
            status,
            completed,
            created_at
        FROM email_sequence_queue
        ORDER BY created_at DESC
        """

        cursor.execute(query)

        rows = cursor.fetchall()

        formatted_response = []

        for row in rows:

            sequence_data = row["sequence"]

            if isinstance(sequence_data, str):
                sequence_data = json.loads(sequence_data)

            steps = sequence_data.get("steps", [])

            current_step = row["current_step"]

            next_step_data = None

            if current_step < len(steps):
                next_step_data = steps[current_step]

            formatted_response.append({
                "queue_id": row["id"],
                "email": row["email"],
                "sequence_name": sequence_data.get("name"),
                "status": row["status"],
                "completed": row["completed"],
                "current_step": current_step,
                "next_send_at": str(row["next_send_at"]),
                "next_email_subject": next_step_data.get("subject") if next_step_data else None,
                "created_at": str(row["created_at"])
            })

        return {
            "success": True,
            "total_records": len(formatted_response),
            "data": formatted_response
        }

    except Exception as e:
        return {
            "success": False,
            "message": str(e)
        }

    finally:
        cursor.close()
        connection.close()