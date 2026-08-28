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

def execute_query(query, params=None, fetch_one=False, fetch_all=False):
    db = connection()
    if not db:
        return None
    cursor = None
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(query, params)

        if fetch_one:
            result = cursor.fetchone()
        elif fetch_all:
            result = cursor.fetchall()
        else:
            result = cursor.rowcount
        return result
    except Error as e:
        print(f"Ошибка выполнения SQL: {e}")
        return None
    finally:
        if cursor:
            cursor.close()
        if db and db.is_connected():
            db.close()



