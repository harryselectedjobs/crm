import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os

load_dotenv()

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            print("Connected to MySQL database")
            return connection
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None


def print_schema():
    conn = get_db_connection()
    if not conn:
        return

    cursor = conn.cursor()

    db_name = os.getenv("DB_NAME")

    query = """
    SELECT
        TABLE_NAME,
        COLUMN_NAME,
        COLUMN_TYPE,
        IS_NULLABLE,
        COLUMN_KEY
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = %s
    ORDER BY TABLE_NAME, ORDINAL_POSITION;
    """

    cursor.execute(query, (db_name,))

    current_table = None

    for table_name, column_name, column_type, nullable, key in cursor.fetchall():
        if table_name != current_table:
            current_table = table_name
            print(f"\n=== {table_name} ===")

        print(
            f"  {column_name:<30} "
            f"{column_type:<20} "
            f"NULL={nullable:<3} "
            f"KEY={key}"
        )

    cursor.close()
    conn.close()


if __name__ == "__main__":
    print_schema()