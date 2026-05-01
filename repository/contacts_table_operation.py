from datetime import datetime
from repository.db_connection import get_db_connection


def get_all_contacts(search: str = None, page: int = 1, limit: int = 10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        offset = (page - 1) * limit

        if search:
            count_query = """
                SELECT COUNT(*) as total FROM contacts
                WHERE firstname LIKE %s OR lastname LIKE %s
                OR email LIKE %s OR company LIKE %s OR industry LIKE %s
            """
            search_term = f"%{search}%"
            cursor.execute(count_query, (search_term, search_term, search_term, search_term, search_term))
            total = cursor.fetchone()["total"]

            query = """
                SELECT * FROM contacts
                WHERE firstname LIKE %s OR lastname LIKE %s
                OR email LIKE %s OR company LIKE %s OR industry LIKE %s
                ORDER BY contactId DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (search_term, search_term, search_term, search_term, search_term, limit, offset))
        else:
            cursor.execute("SELECT COUNT(*) as total FROM contacts")
            total = cursor.fetchone()["total"]

            query = "SELECT * FROM contacts ORDER BY contactId DESC LIMIT %s OFFSET %s"
            cursor.execute(query, (limit, offset))

        contacts = cursor.fetchall()
        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": contacts,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_contact_by_id(contact_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM contacts WHERE contactId = %s", (contact_id,))
        contact = cursor.fetchone()
        cursor.close()
        conn.close()

        if not contact:
            return {"status": "error", "message": f"Contact with id {contact_id} not found"}
        return {"status": "success", "data": contact}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_contact(data: dict):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT contactId FROM contacts WHERE LOWER(email) = LOWER(%s)", (data.get("email"),))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"status": "error", "message": f"Contact with email '{data.get('email')}' already exists"}

        insert_query = """
            INSERT INTO contacts (
                firstname, lastname, jobtitle, job_function, seniority,
                email, mobilephone, phone,
                hs_linkedin_url, followercount, linkedinconnections,
                country, city, state,
                start_date,
                company, industry, company_size,
                lifecycle_stage
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (
            data.get("firstname"),
            data.get("lastname"),
            data.get("jobtitle"),
            data.get("job_function"),
            data.get("seniority"),
            data.get("email"),
            data.get("mobilephone"),
            data.get("phone"),
            data.get("hs_linkedin_url"),
            data.get("followercount"),
            data.get("linkedinconnections"),
            data.get("country"),
            data.get("city"),
            data.get("state"),
            data.get("start_date"),
            data.get("company"),
            data.get("industry"),
            data.get("company_size"),
            data.get("lifecycle_stage", "NEW")
        ))
        conn.commit()
        new_id = cursor.lastrowid
        cursor.close()
        conn.close()

        return {"status": "success", "message": "Contact created successfully", "id": new_id}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_contact(contact_id: int, data: dict):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT contactId FROM contacts WHERE contactId = %s", (contact_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"status": "error", "message": f"Contact with id {contact_id} not found"}

        allowed_fields = [
            "firstname", "lastname", "jobtitle", "job_function", "seniority",
            "email", "mobilephone", "phone",
            "hs_linkedin_url", "followercount", "linkedinconnections",
            "country", "city", "state",
            "start_date",
            "company", "industry", "company_size",
            "lifecycle_stage"
        ]

        fields_to_update = {k: v for k, v in data.items() if k in allowed_fields}

        if not fields_to_update:
            cursor.close()
            conn.close()
            return {"status": "error", "message": "No valid fields provided to update"}

        set_clause = ", ".join(f"{key} = %s" for key in fields_to_update.keys())
        values = list(fields_to_update.values())
        values.append(contact_id)

        cursor.execute(f"UPDATE contacts SET {set_clause} WHERE contactId = %s", values)
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success", "message": "Contact updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_contact(contact_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT contactId FROM contacts WHERE contactId = %s", (contact_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"status": "error", "message": f"Contact with id {contact_id} not found"}

        cursor.execute("DELETE FROM contacts WHERE contactId = %s", (contact_id,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"status": "success", "message": "Contact deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_multiple_contacts(contact_ids: list):
    try:
        if not contact_ids:
            return {"status": "error", "message": "No contact IDs provided"}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        placeholders = ", ".join(["%s"] * len(contact_ids))
        cursor.execute(f"DELETE FROM contacts WHERE contactId IN ({placeholders})", contact_ids)
        conn.commit()
        deleted_count = cursor.rowcount
        cursor.close()
        conn.close()

        return {"status": "success", "message": f"{deleted_count} contacts deleted successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}