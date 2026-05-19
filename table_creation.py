from aifc import Error

from repository.db_connection import get_db_connection


def reset_client_inquiries():
    connection = get_db_connection()
    if not connection:
        return
    try:
        cursor = connection.cursor()

        # Step 1: Delete all records
        cursor.execute("DELETE FROM client_inquiries")
        connection.commit()
        print("All records deleted successfully")

        # Step 2: Insert few sample records
        records = [
            (
                "John Doe",
                "Tech Corp",
                "john.doe@techcorp.com",
                "+1-555-001-0001",
                "Software Development",
                "Looking for a senior Python developer for a 6-month project.",
                False
            ),
            (
                "Jane Smith",
                "Legal Partners LLP",
                "jane.smith@legalpartners.com",
                "+1-555-002-0002",
                "Legal Services",
                "Need a corporate lawyer for contract negotiations.",
                False
            ),
            (
                "Robert Brown",
                "Finance Hub",
                "robert.brown@financehub.com",
                "+1-555-003-0003",
                "Finance & Accounting",
                "Hiring a CFO for our growing startup.",
                True
            ),
            (
                "Emily Davis",
                "HealthCare Plus",
                "emily.davis@healthcareplus.com",
                "+1-555-004-0004",
                "Healthcare",
                "Seeking experienced medical consultants for clinic expansion.",
                False
            ),
            (
                "Michael Wilson",
                "BuildIt Construction",
                "michael.wilson@buildit.com",
                "+1-555-005-0005",
                "Engineering",
                "Require civil engineers for a large infrastructure project.",
                True
            ),
        ]

        query = """
            INSERT INTO client_inquiries 
            (full_name, company_name, work_email, phone_number, practice_area, hiring_brief, is_contacted)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """

        cursor.executemany(query, records)
        connection.commit()
        print(f"{cursor.rowcount} records inserted successfully")

    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

reset_client_inquiries()