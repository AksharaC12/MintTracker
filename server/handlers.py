from db import get_db_connection
import mysql.connector
import bcrypt
from decimal import Decimal
from datetime import date, datetime


# ---------- UTIL ----------
def serialize(val):
    if isinstance(val, Decimal):
        return float(val)
    if isinstance(val, (date, datetime)):
        return val.isoformat()
    return val


# ---------- ROUTER ----------
def handle_request(data):
    action = data.get("action")

    print("📨 ACTION:", action)
    print("📨 DATA:", data)

    routes = {
        "signup": signup,
        "login": login,
        "add_expense": add_expense,
        "get_expenses": get_expenses,
        "get_total": get_total,
        "category_summary": category_summary,
    }

    handler = routes.get(action)
    if not handler:
        return {"status": "error", "message": "Invalid action"}

    return handler(data)


# ---------- AUTH ----------
def signup(data):
    full_name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    if not full_name or not email or not password:
        return {"status": "error", "message": "Missing fields"}

    password_hash = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Check duplicate email
        cursor.execute(
            "SELECT id FROM users WHERE email=%s",
            (email,)
        )
        if cursor.fetchone():
            return {"status": "error", "message": "Email already exists"}

        cursor.execute(
            """
            INSERT INTO users (full_name, email, password_hash)
            VALUES (%s, %s, %s)
            """,
            (full_name, email, password_hash)
        )

        conn.commit()

        print("✅ USER CREATED:", email)
        return {
            "status": "success",
            "user_id": cursor.lastrowid
        }

    except Exception as e:
        print("❌ SIGNUP ERROR:", e)
        return {"status": "error", "message": "Signup failed"}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def login(data):
    email = data.get("email", "").strip().lower()
    password = data.get("password", "").strip()

    print(f"🔍 LOGIN EMAIL RECEIVED: '{email}'")

    if not email or not password:
        return {"status": "error", "message": "Missing fields"}

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, password_hash
            FROM users
            WHERE email=%s
            """,
            (email,)
        )

        user = cursor.fetchone()
        print("🔍 DB USER:", user)

        if not user:
            return {"status": "error", "message": "User not found"}

        if not bcrypt.checkpw(
            password.encode("utf-8"),
            user["password_hash"].encode("utf-8")
        ):
            return {"status": "error", "message": "Wrong password"}

        return {
            "status": "success",
            "user_id": user["id"]
        }

    except Exception as e:
        print("❌ LOGIN ERROR:", e)
        return {"status": "error", "message": "Login failed"}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ---------- EXPENSES ----------
def add_expense(data):
    required = ["user_id", "amount", "category", "date"]
    for field in required:
        if field not in data:
            return {"status": "error", "message": f"Missing field {field}"}

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO expenses (user_id, amount, category_name, expense_date)
            VALUES (%s, %s, %s, %s)
            """,
            (
                int(data["user_id"]),
                float(data["amount"]),
                data["category"],
                data["date"]
            )
        )

        conn.commit()
        return {"status": "success"}

    except Exception as e:
        print("❌ ADD EXPENSE ERROR:", e)
        return {"status": "error", "message": "Failed to add expense"}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_expenses(data):
    user_id = data.get("user_id")
    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT id, amount, category_name, expense_date
            FROM expenses
            WHERE user_id=%s
            ORDER BY expense_date DESC
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        return {
            "status": "success",
            "data": [{k: serialize(v) for k, v in row.items()} for row in rows]
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def get_total(data):
    user_id = data.get("user_id")
    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT IFNULL(SUM(amount), 0)
            FROM expenses
            WHERE user_id=%s
            """,
            (user_id,)
        )

        total = cursor.fetchone()[0]
        return {"status": "success", "total": float(total)}

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def category_summary(data):
    user_id = data.get("user_id")
    if not user_id:
        return {"status": "error", "message": "Missing user_id"}

    conn = cursor = None
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute(
            """
            SELECT category_name, SUM(amount) AS total
            FROM expenses
            WHERE user_id=%s
            GROUP BY category_name
            """,
            (user_id,)
        )

        rows = cursor.fetchall()

        return {
            "status": "success",
            "data": [{k: serialize(v) for k, v in row.items()} for row in rows]
        }

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
