import pandas as pd
from datetime import datetime
from fastapi import UploadFile
from repository.db_connection import get_db_connection


def import_companies_from_csv(uploadFile: UploadFile):
    try:
        uploadFile.file.seek(0)
        df = pd.read_csv(uploadFile.file)

        df.columns = df.columns.str.strip()

        df = df.rename(columns={
            "Name": "name",
            "Domain": "domain",
            "Website": "website",
            "Description": "description",
            "City": "city",
            "State": "state",
            "Country": "country",
            "Address": "address",
            "Zip": "zip",
            "Industry": "industry",
            "Number of Employees": "numberofemployees",
            "Annual Revenue": "annualrevenue",
            "LinkedIn Company Page": "linkedin_company_page",
            "Technology Category": "technology_category",
            "Software Category": "software_category",
            "Area of Work": "area_of_work"
        })

        df["created_at"] = datetime.now()
        df["updated_at"] = datetime.now()

        columns = [
            "name", "domain", "website", "description",
            "city", "state", "country", "address", "zip",
            "industry", "numberofemployees", "annualrevenue",
            "linkedin_company_page", "technology_category",
            "software_category", "area_of_work",
            "created_at", "updated_at"
        ]

        df = df.reindex(columns=columns)

        # ✅ Convert numerics BEFORE replacing NaN with None
        df["numberofemployees"] = pd.to_numeric(df["numberofemployees"], errors='coerce')
        df["annualrevenue"] = pd.to_numeric(df["annualrevenue"], errors='coerce')

        # ✅ Now safely replace all NaN with None (SQL NULL)
        df = df.astype(object).where(pd.notnull(df), None)

        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Fetch existing company names from DB
        cursor.execute("SELECT LOWER(name) FROM company WHERE name IS NOT NULL")
        existing_names = set(row[0] for row in cursor.fetchall())

        # ✅ Filter out duplicates (case-insensitive)
        df_filtered = df[
            df["name"].apply(lambda x: x.lower() if x else None).isin(existing_names) == False
        ]

        skipped = len(df) - len(df_filtered)

        if df_filtered.empty:
            cursor.close()
            conn.close()
            return {
                "status": "success",
                "rows_inserted": 0,
                "rows_skipped": skipped,
                "message": "All companies already exist in the database."
            }

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

        data = [tuple(row) for row in df_filtered.to_numpy()]

        cursor.executemany(insert_query, data)
        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "rows_inserted": len(df_filtered),
            "rows_skipped": skipped
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def import_contacts_from_csv(uploadFile: UploadFile):
    try:
        uploadFile.file.seek(0)
        df = pd.read_csv(uploadFile.file)

        df.columns = df.columns.str.strip()

        df = df.rename(columns={
            "First Name": "firstname",
            "Last Name": "lastname",
            "Job Title": "jobtitle",
            "Job Function": "job_function",
            "Seniority": "seniority",
            "Email": "email",
            "Mobile Phone": "mobilephone",
            "Phone": "phone",
            "LinkedIn URL": "hs_linkedin_url",
            "Follower Count": "followercount",
            "LinkedIn Connections": "linkedinconnections",
            "Country": "country",
            "City": "city",
            "State": "state",
            "Start Date": "start_date",
            "Company": "company",
            "Industry": "industry",
            "Company Size": "company_size"
        })

        df["lifecycle_stage"] = "NEW"

        columns = [
            "firstname", "lastname", "jobtitle", "job_function", "seniority",
            "email", "mobilephone", "phone",
            "hs_linkedin_url", "followercount", "linkedinconnections",
            "country", "city", "state",
            "start_date",
            "company", "industry", "company_size",
            "lifecycle_stage"
        ]

        df = df.reindex(columns=columns)

        # ✅ Convert numerics BEFORE replacing NaN with None
        df["followercount"] = pd.to_numeric(df["followercount"], errors='coerce')
        df["linkedinconnections"] = pd.to_numeric(df["linkedinconnections"], errors='coerce')

        # ✅ Now safely replace all NaN with None (SQL NULL)
        df = df.astype(object).where(pd.notnull(df), None)

        # ✅ Skip rows with no email
        df = df[df["email"].notna() & (df["email"] != "")]

        conn = get_db_connection()
        cursor = conn.cursor()

        # ✅ Fetch existing emails from DB
        cursor.execute("SELECT LOWER(email) FROM contacts WHERE email IS NOT NULL")
        existing_emails = set(row[0] for row in cursor.fetchall())

        # ✅ Skip rows where email already exists in DB
        df_filtered = df[
            df["email"].apply(lambda x: x.lower() if x else None).isin(existing_emails) == False
        ]

        skipped = len(df) - len(df_filtered)

        if df_filtered.empty:
            cursor.close()
            conn.close()
            return {
                "status": "success",
                "rows_inserted": 0,
                "rows_skipped": skipped,
                "message": "All contacts already exist in the database."
            }

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

        data = [tuple(row) for row in df_filtered.to_numpy()]

        cursor.executemany(insert_query, data)
        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "rows_inserted": len(df_filtered),
            "rows_skipped": skipped
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

def process_csv_file(file: UploadFile, type: str):
    try:
        if type == "contacts":
            return import_contacts_from_csv(file)

        elif type == "companies":
            return import_companies_from_csv(file)

        else:
            return {
                "status": "error",
                "message": f"Invalid type '{type}'. Must be 'contacts' or 'companies'"
            }

    except Exception as e:
        return {"status": "error", "message": str(e)}