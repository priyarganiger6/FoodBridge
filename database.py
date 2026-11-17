import sqlite3
import hashlib
import secrets

DB_NAME = "foodbridge.db"


# =====================================
# DATABASE CONNECTION
# =====================================

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# =====================================
# CREATE DATABASE TABLES
# =====================================

def init_db():

    conn = get_connection()

    cursor = conn.cursor()

    # USERS TABLE

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('Food Donor', 'NGO')),
            location TEXT NOT NULL
        )
    """)

    # DONATIONS TABLE

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS donations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donor_id INTEGER NOT NULL,
            food_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            location TEXT NOT NULL,
            pickup_deadline TEXT NOT NULL,
            status TEXT DEFAULT 'Available',
            FOREIGN KEY (donor_id) REFERENCES users(id)
        )
    """)

    # FOOD REQUESTS TABLE

    # FOOD REQUESTS TABLE

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            donation_id INTEGER NOT NULL,
            ngo_id INTEGER NOT NULL,
            quantity_requested REAL,
            requested_at TEXT,
            status TEXT DEFAULT 'Pending',
            FOREIGN KEY (donation_id) REFERENCES donations(id),
            FOREIGN KEY (ngo_id) REFERENCES users(id)
        )
    """)

    # UPDATE EXISTING DATABASE IF NEEDED

    columns = [
        row["name"]
        for row in cursor.execute(
            "PRAGMA table_info(requests)"
        ).fetchall()
    ]

    if "quantity_requested" not in columns:
        cursor.execute(
            "ALTER TABLE requests ADD COLUMN quantity_requested REAL"
        )

    if "requested_at" not in columns:
        cursor.execute(
            "ALTER TABLE requests ADD COLUMN requested_at TEXT"
        )

    conn.commit()
    conn.close()


# =====================================
# PASSWORD SECURITY
# =====================================

def hash_password(password, salt=None):

    if salt is None:
        salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600000
    )

    return password_hash.hex(), salt


# =====================================
# REGISTER USER
# =====================================

def register_user(name, email, password, role, location):

    if role not in ["Food Donor", "NGO"]:
        return False, "Invalid account type."

    if not all([name.strip(), email.strip(), location.strip(), password]):
        return False, "All fields are required."

    email = email.strip().lower()

    if "@" not in email:
        return False, "Enter a valid email address."

    password_hash, salt = hash_password(password)

    try:

        conn = get_connection()

        conn.execute("""
            INSERT INTO users
            (name, email, password_hash, salt, role, location)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name.strip(),
            email,
            password_hash,
            salt,
            role,
            location.strip()
        ))

        conn.commit()
        conn.close()

        return True, "Account created successfully!"

    except sqlite3.IntegrityError:

        return False, "Email already registered."

    except sqlite3.Error:

        return False, "Database error. Please try again."


# =====================================
# LOGIN AUTHENTICATION
# =====================================

def login_user(email, password):

    conn = get_connection()

    user = conn.execute("""
        SELECT * FROM users
        WHERE email = ?
    """, (email.strip().lower(),)).fetchone()

    conn.close()

    if user is None:
        return None

    stored_hash, _ = hash_password(
        password,
        user["salt"]
    )

    if secrets.compare_digest(
        stored_hash,
        user["password_hash"]
    ):

        return {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"],
            "role": user["role"],
            "location": user["location"]
        }

    return None


# =====================================
# INITIALIZE DATABASE
# =====================================

if __name__ == "__main__":

    init_db()

    print("FoodBridge database created successfully!")
    print("Users, Donations and Requests tables are ready.")