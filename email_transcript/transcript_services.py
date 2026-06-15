from uuid import uuid4
from datetime import datetime

from repository.db_connection import get_db_connection


def save_email_message(
    sender_email: str,
    receiver_email: str,
    subject: str,
    body: str,
    direction: str,
    sent_at: datetime
):
    connection = get_db_connection()

    try:
        cursor = connection.cursor()

        message_id = str(uuid4())

        cursor.execute(
            """
            INSERT INTO email_messages (
                message_id,
                sender_email,
                receiver_email,
                subject,
                body,
                direction,
                sent_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                message_id,
                sender_email,
                receiver_email,
                subject,
                body,
                direction,
                sent_at
            )
        )

        connection.commit()

        return {
            "success": True,
            "message_id": message_id
        }

    except Exception as e:
        print(e)
        return {
            "success": False,
            "error": str(e)
        }

    finally:
        cursor.close()
        connection.close()


def get_email_transcripts(email: str):
    connection = get_db_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT
                message_id,
                sender_email,
                receiver_email,
                subject,
                body,
                direction,
                sent_at
            FROM email_messages
            WHERE sender_email = %s
               OR receiver_email = %s
            ORDER BY sent_at ASC
            """,
            (email, email)
        )

        return cursor.fetchall()

    except Exception as e:
        print(e)
        return []

    finally:
        cursor.close()
        connection.close()
