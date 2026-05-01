import mysql.connector
from mysql.connector import Error

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host="selectedgroupcrm.cbmo6qu6oqc6.eu-north-1.rds.amazonaws.com",
            port=3306,
            user="root",
            password="root2000",
            database="selectedgroupcrm"
        )

        if connection.is_connected():
            print("Connected to MySQL database")
            return connection

    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None