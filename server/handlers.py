from db import get_db_connection
import mysql.connector

def handle_request(data):
    action = data.get("action")

    if action == "register":
        return register_user(data)

    elif action == "add_expense":
        return add_expense(data)

    elif action == "get_expenses":
        return get_expenses(data)

    elif action == "get_total":
        return get_total_expense(data)

    else:
        return {
            "status": "error",
            "message": "Invalid action"
        }

def register_user(data):
    username = data.get("username")

    if not username:
        return {"status": "error", "message": "Username is required"}

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute(
            "INSERT INTO users (username) VALUES (%s)",
            (username,)
        )
        conn.commit()

        return {
            "status": "success",
            "user_id": cursor.lastrowid,
            "message": "User registered"
        }

    except mysql.connector.IntegrityError:
        cursor.execute(
            "SELECT id FROM users WHERE username = %s",
            (username,)
        )
        user = cursor.fetchone()

        return {
            "status": "success",
            "user_id": user["id"],
            "message": "User already exists"
        }

    finally:
        cursor.close()
        conn.close()
def add_expense(data):
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
                data["amount"],
                data["category"],
                data.get("note", "")
            )
        )

        conn.commit()

        return {
            "status": "success",
            "message": "Expense added successfully"
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cursor.close()
        conn.close()
def get_expenses(data):
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

    expenses = cursor.fetchall()

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "expenses": expenses
    }
def get_total_expense(data):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        """
        SELECT IFNULL(SUM(amount), 0) AS total
        FROM expenses
        WHERE user_id = %s
        """,
        (data["user_id"],)
    )

    total = cursor.fetchone()["total"]

    cursor.close()
    conn.close()

    return {
        "status": "success",
        "total": float(total)
    }
