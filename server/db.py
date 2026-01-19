import mysql.connector

def get_db_connection():
    """
    Creates and returns a MySQL database connection
    """
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="1351",
        database="minttracker"
    )
