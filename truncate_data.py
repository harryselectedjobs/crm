from repository.db_connection import get_db_connection

def clear_all_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")

        cursor.execute("TRUNCATE TABLE contacts")
        cursor.execute("TRUNCATE TABLE company")

        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

        conn.commit()

        cursor.close()
        conn.close()

        print("✅ All data deleted successfully")

    except Exception as e:
        print("❌ Error:", str(e))

clear_all_data()