from datetime import datetime
from repository.db_connection import get_db_connection


def get_all_companies(search: str = None, page: int = 1, limit: int = 10):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        offset = (page - 1) * limit

        if search:
            count_query = "SELECT COUNT(*) as total FROM company WHERE name LIKE %s OR domain LIKE %s OR industry LIKE %s"
            search_term = f"%{search}%"
            cursor.execute(count_query, (search_term, search_term, search_term))
            total = cursor.fetchone()["total"]

            query = """
                SELECT * FROM company
                WHERE name LIKE %s OR domain LIKE %s OR industry LIKE %s
                ORDER BY created_at DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (search_term, search_term, search_term, limit, offset))
        else:
            cursor.execute("SELECT COUNT(*) as total FROM company")
            total = cursor.fetchone()["total"]

            query = "SELECT * FROM company ORDER BY created_at DESC LIMIT %s OFFSET %s"
            cursor.execute(query, (limit, offset))

        companies = cursor.fetchall()

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "data": companies,
            "total": total,
            "page": page,
            "limit": limit,
            "total_pages": (total + limit - 1) // limit
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def get_company_by_id(company_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM company WHERE id = %s", (company_id,))
        company = cursor.fetchone()

        cursor.close()
        conn.close()

        if not company:
            return {"status": "error", "message": f"Company with id {company_id} not found"}

        return {"status": "success", "data": company}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def create_company(data: dict):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Check if company name already exists
        cursor.execute("SELECT id FROM company WHERE LOWER(name) = LOWER(%s)", (data.get("name"),))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return {"status": "error", "message": f"Company '{data.get('name')}' already exists"}

        now = datetime.now()

        insert_query = """
            INSERT INTO company (
                name, domain, website, description,
                city, state, country, address, zip,
                industry, numberofemployees, annualrevenue,
                linkedin_company_page, technology_category,
                software_category, area_of_work,
                created_at, updated_at
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        cursor.execute(insert_query, (
            data.get("name"),
            data.get("domain"),
            data.get("website"),
            data.get("description"),
            data.get("city"),
            data.get("state"),
            data.get("country"),
            data.get("address"),
            data.get("zip"),
            data.get("industry"),
            data.get("numberofemployees"),
            data.get("annualrevenue"),
            data.get("linkedin_company_page"),
            data.get("technology_category"),
            data.get("software_category"),
            data.get("area_of_work"),
            now,
            now
        ))

        conn.commit()
        new_id = cursor.lastrowid

        cursor.close()
        conn.close()

        return {"status": "success", "message": "Company created successfully", "id": new_id}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def update_company(company_id: int, data: dict):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Check if company exists
        cursor.execute("SELECT id FROM company WHERE id = %s", (company_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"status": "error", "message": f"Company with id {company_id} not found"}

        # ✅ Build dynamic SET clause from provided fields only
        allowed_fields = [
            "name", "domain", "website", "description",
            "city", "state", "country", "address", "zip",
            "industry", "numberofemployees", "annualrevenue",
            "linkedin_company_page", "technology_category",
            "software_category", "area_of_work"
        ]

        fields_to_update = {k: v for k, v in data.items() if k in allowed_fields}

        if not fields_to_update:
            cursor.close()
            conn.close()
            return {"status": "error", "message": "No valid fields provided to update"}

        fields_to_update["updated_at"] = datetime.now()

        set_clause = ", ".join(f"{key} = %s" for key in fields_to_update.keys())
        values = list(fields_to_update.values())
        values.append(company_id)

        update_query = f"UPDATE company SET {set_clause} WHERE id = %s"
        cursor.execute(update_query, values)
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "Company updated successfully"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_company(company_id: int):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Check if company exists
        cursor.execute("SELECT id FROM company WHERE id = %s", (company_id,))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return {"status": "error", "message": f"Company with id {company_id} not found"}

        cursor.execute("DELETE FROM company WHERE id = %s", (company_id,))
        conn.commit()

        cursor.close()
        conn.close()

        return {"status": "success", "message": "Company deleted successfully"}

    except Exception as e:
        return {"status": "error", "message": str(e)}


def delete_multiple_companies(company_ids: list):
    try:
        if not company_ids:
            return {"status": "error", "message": "No company IDs provided"}

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        placeholders = ", ".join(["%s"] * len(company_ids))
        cursor.execute(f"DELETE FROM company WHERE id IN ({placeholders})", company_ids)
        conn.commit()

        deleted_count = cursor.rowcount

        cursor.close()
        conn.close()

        return {"status": "success", "message": f"{deleted_count} companies deleted successfully"}

    except Exception as e:
        return {"status": "error", "message": str(e)}