from db import get_db_connection
import mysql.connector
import bcrypt
from decimal import Decimal
from datetime import datetime


# ---------- UTIL ----------

def serialize(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.isoformat()
    return value


# ---------- REQUEST ROUTER ----------

def handle_request(data):
    action = data.get("action")

    if action == "signup":
        return signup(data)
    elif action == "login":
        return login(data)
    elif action == "add_expense":
        return add_expense(data)
    elif action == "get_expenses":
        return get_expenses(data)
    elif action == "get_total":
        return get_total(data)
    else:
        return {
            "status": "error",
            "message": "Invalid action"
        }


# ---------- AUTH ----------

def signup(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "status": "error",
            "message": "Missing credentials"
        }

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            INSERT INTO users (username, password_hash)
            VALUES (%s, %s)
            """,
            (username, password_hash)
        )

        conn.commit()

        return {
            "status": "success",
            "user_id": cursor.lastrowid
        }

    except mysql.connector.IntegrityError:
        return {
            "status": "error",
            "message": "Username already exists"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def login(data):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return {
            "status": "error",
            "message": "Missing credentials"
        }

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            "SELECT id, password_hash FROM users WHERE username = %s",
            (username,)
        )

        user = cursor.fetchone()

        if not user:
            return {
                "status": "error",
                "message": "User not found"
            }

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return {
                "status": "error",
                "message": "Invalid password"
            }

        cursor.execute(
            "UPDATE users SET last_login = NOW() WHERE id = %s",
            (user["id"],)
        )
        conn.commit()

        return {
            "status": "success",
            "user_id": user["id"]
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ---------- EXPENSES ----------

def add_expense(data):
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO expenses (user_id, amount, category, note)
            VALUES (%s, %s, %s, %s)
            """,
            (
                data["user_id"],
                float(data["amount"]),
                data["category"],
                data.get("note", "")
            )
        )

        conn.commit()
        return {"status": "success"}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_expenses(data):
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT amount, category, note, created_at
            FROM expenses
            WHERE user_id = %s
            ORDER BY created_at DESC
            """,
            (data["user_id"],)
        )

        rows = cursor.fetchall()

        return {
            "status": "success",
            "expenses": [
                {k: serialize(v) for k, v in row.items()}
                for row in rows
            ]
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_total(data):
    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT IFNULL(SUM(amount), 0) FROM expenses WHERE user_id = %s",
            (data["user_id"],)
        )

        return {
            "status": "success",
            "total": float(cursor.fetchone()[0])
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
