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


TABLES = {
    "sequence": """
        CREATE TABLE IF NOT EXISTS sequence (
            sequence_id  INT AUTO_INCREMENT PRIMARY KEY,
            name         VARCHAR(255) NOT NULL,
            status       ENUM('draft', 'active', 'paused') DEFAULT 'draft',
            goal         VARCHAR(255),
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    """,

    "sequence_step": """
        CREATE TABLE IF NOT EXISTS sequence_step (
            step_id            INT AUTO_INCREMENT PRIMARY KEY,
            sequence_id        INT NOT NULL,
            step_order         INT NOT NULL,
            delay_days         INT NOT NULL DEFAULT 0,
            subject            VARCHAR(500) NOT NULL,
            body_template      TEXT NOT NULL,
            send_window_start  TIME DEFAULT '09:00:00',
            send_window_end    TIME DEFAULT '17:00:00',
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sequence_id) REFERENCES sequence(sequence_id) ON DELETE CASCADE
        )
    """,

    "contact_enrollment": """
        CREATE TABLE IF NOT EXISTS contact_enrollment (
            enrollment_id  INT AUTO_INCREMENT PRIMARY KEY,
            contact_id     INT NOT NULL,
            sequence_id    INT NOT NULL,
            current_step   INT DEFAULT 1,
            status         ENUM('active', 'paused', 'completed', 'unsubscribed', 'bounced') DEFAULT 'active',
            enrolled_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            enrolled_by    VARCHAR(255) DEFAULT 'manual',
            next_send_at   TIMESTAMP NULL,
            FOREIGN KEY (sequence_id) REFERENCES sequence(sequence_id) ON DELETE CASCADE,
            UNIQUE KEY unique_contact_sequence (contact_id, sequence_id)
        )
    """,

    "sequence_email_log": """
        CREATE TABLE IF NOT EXISTS sequence_email_log (
            log_id         INT AUTO_INCREMENT PRIMARY KEY,
            enrollment_id  INT NOT NULL,
            step_id        INT NOT NULL,
            contact_id     INT NOT NULL,
            sent_at        TIMESTAMP NULL,
            opened_at      TIMESTAMP NULL,
            clicked_at     TIMESTAMP NULL,
            replied_at     TIMESTAMP NULL,
            bounced        BOOLEAN DEFAULT FALSE,
            unsubscribed   BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (enrollment_id) REFERENCES contact_enrollment(enrollment_id) ON DELETE CASCADE,
            FOREIGN KEY (step_id) REFERENCES sequence_step(step_id) ON DELETE CASCADE,
            UNIQUE KEY unique_enrollment_step (enrollment_id, step_id)
        )
    """
}


def create_tables():
    connection = get_db_connection()
    if not connection:
        print("Failed to connect. Aborting.")
        return

    cursor = connection.cursor()
    for table_name, ddl in TABLES.items():
        try:
            cursor.execute(ddl)
            print(f"✅ Table '{table_name}' created (or already exists)")
        except Error as e:
            print(f"❌ Error creating table '{table_name}': {e}")

    connection.commit()
    cursor.close()
    connection.close()
    print("\nDone. All tables are ready.")


if __name__ == "__main__":
    create_tables()