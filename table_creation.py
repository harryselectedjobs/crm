from repository.db_connection import get_db_connection

def create_email_sequence_queue_table():
    connection = get_db_connection()

    if not connection:
        print("Database connection failed")
        return

    try:
        cursor = connection.cursor()

        create_table_query = """
        CREATE TABLE IF NOT EXISTS email_sequence_queue (

            id BIGINT AUTO_INCREMENT PRIMARY KEY,

            email VARCHAR(255) NOT NULL,

            sequence JSON NOT NULL,

            current_step INT DEFAULT 0,

            next_send_at DATETIME NOT NULL,

            status VARCHAR(50) DEFAULT 'active',

            completed BOOLEAN DEFAULT FALSE,

            last_sent_at DATETIME NULL,

            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ON UPDATE CURRENT_TIMESTAMP

        );
        """

        cursor.execute(create_table_query)

        connection.commit()

        print("Table 'email_sequence_queue' created successfully")

    except Exception as e:
        print(f"Error creating table: {e}")

    finally:
        cursor.close()
        connection.close()


if __name__ == "__main__":
    create_email_sequence_queue_table()