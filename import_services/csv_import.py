import pandas as pd
from datetime import datetime
from fastapi import UploadFile
from repository.db_connection import get_db_connection


# ================================
# ✅ IMPORT COMPANIES (NO NULLS)
# ================================
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

        # Ensure all required columns exist
        columns = [
            "name", "domain", "website", "description",
            "city", "state", "country", "address", "zip",
            "industry", "numberofemployees", "annualrevenue",
            "linkedin_company_page", "technology_category",
            "software_category", "area_of_work"
        ]
        df = df.reindex(columns=columns)

        # 🔥 FILL NULL VALUES (NO NULLS IN DB)
        df = df.fillna({
            "name": "Unknown Company",
            "domain": "unknown.com",
            "website": "unknown.com",
            "description": "",
            "city": "Unknown",
            "state": "Unknown",
            "country": "Unknown",
            "address": "",
            "zip": "",
            "industry": "Unknown",
            "numberofemployees": 0,
            "annualrevenue": 0,
            "linkedin_company_page": "",
            "technology_category": "",
            "software_category": "",
            "area_of_work": ""
        })

        # Ensure numeric
        df["numberofemployees"] = pd.to_numeric(df["numberofemployees"], errors="coerce").fillna(0)
        df["annualrevenue"] = pd.to_numeric(df["annualrevenue"], errors="coerce").fillna(0)

        # Add timestamps
        df["created_at"] = datetime.now()
        df["updated_at"] = datetime.now()

        # Final column order
        columns.extend(["created_at", "updated_at"])
        df = df[columns]

        conn = get_db_connection()
        cursor = conn.cursor()

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

        data = [tuple(row) for row in df.to_numpy()]

        cursor.executemany(insert_query, data)
        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "rows_inserted": len(df)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ================================
# ✅ IMPORT CONTACTS (NO NULLS)
# ================================
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

        # 🔥 FILL NULL VALUES
        df = df.fillna({
            "firstname": "",
            "lastname": "",
            "jobtitle": "",
            "job_function": "",
            "seniority": "",
            "email": "",
            "mobilephone": "",
            "phone": "",
            "hs_linkedin_url": "",
            "followercount": 0,
            "linkedinconnections": 0,
            "country": "Unknown",
            "city": "Unknown",
            "state": "Unknown",
            "start_date": "",  # ✅ FIXED
            "company": "",
            "industry": "Unknown",
            "company_size": "",
            "lifecycle_stage": "NEW"
        })

        # Ensure numeric
        df["followercount"] = pd.to_numeric(df["followercount"], errors="coerce").fillna(0)
        df["linkedinconnections"] = pd.to_numeric(df["linkedinconnections"], errors="coerce").fillna(0)

        # Remove rows without email
        df = df[df["email"] != ""]

        conn = get_db_connection()
        cursor = conn.cursor()

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

        data = [tuple(row) for row in df.to_numpy()]

        cursor.executemany(insert_query, data)
        conn.commit()

        cursor.close()
        conn.close()

        return {
            "status": "success",
            "rows_inserted": len(df)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


# ================================
# ✅ ROUTER HANDLER
# ================================
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