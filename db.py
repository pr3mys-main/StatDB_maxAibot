import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

load_dotenv()

def connection():
    try:
        db = mysql.connector.connect(
            host =os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        return db
    except Error as e:
        print(f"Ошибка подключения к БД: {e}")
        return False

def execute_query(query, params=None):
    db = connection()
    if not db:
        return None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, params)
    except Error as e:
        print(f"Ошибка выполнения SQL: {e}")
        return None
    finally:
        db.close()



