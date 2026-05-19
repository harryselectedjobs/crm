from mysql.connector import Error
from repository.db_connection import get_db_connection


# =========================
# 1. ADD NEW RECORD
# =========================
def add_contact_us(data):
    connection = get_db_connection()

    if not connection:
        return {"success": False, "message": "DB connection failed"}

    try:
        cursor = connection.cursor()

        query = """
        INSERT INTO client_inquiries (
            full_name,
            company_name,
            work_email,
            phone_number,
            practice_area,
            hiring_brief,
            is_contacted
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        values = (
            data.get("full_name"),
            data.get("company_name"),
            data.get("work_email"),
            data.get("phone_number"),
            data.get("practice_area"),
            data.get("hiring_brief"),
            False  # default not contacted
        )

        cursor.execute(query, values)
        connection.commit()

        return {
            "success": True,
            "message": "Contact request added successfully",
            "id": cursor.lastrowid
        }

    except Error as e:
        return {"success": False, "message": str(e)}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# =========================
# 2. GET ALL RECORDS
# =========================
def get_all_contact_us():
    connection = get_db_connection()

    if not connection:
        return {"success": False, "message": "DB connection failed"}

    try:
        cursor = connection.cursor(dictionary=True)

        query = """
        SELECT 
            id,
            full_name,
            company_name,
            work_email,
            phone_number,
            practice_area,
            hiring_brief,
            is_contacted,
            created_at
        FROM client_inquiries
        ORDER BY created_at DESC
        """

        cursor.execute(query)
        records = cursor.fetchall()

        # Convert 0/1 to True/False
        for record in records:
            record["is_contacted"] = bool(record["is_contacted"])

        return {
            "success": True,
            "data": records
        }

    except Error as e:
        return {"success": False, "message": str(e)}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


# =========================
# 3. UPDATE is_contacted STATUS
# =========================
def update_contact_status(inquiry_id, status: bool):
    connection = get_db_connection()

    if not connection:
        return {"success": False, "message": "DB connection failed"}

    try:
        cursor = connection.cursor()

        query = """
        UPDATE client_inquiries
        SET is_contacted = %s
        WHERE id = %s
        """

        cursor.execute(query, (status, inquiry_id))
        connection.commit()

        return {
            "success": True,
            "message": "Contact status updated successfully"
        }

    except Error as e:
        return {"success": False, "message": str(e)}

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()