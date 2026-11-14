"""
database/connection.py
----------------------
Handles SQLite database connection and schema initialization.
All other modules import get_connection() from here.
"""

import sqlite3
import os

# The database file is stored inside the smart_contact_manager folder.
# Using an absolute path keeps it predictable regardless of the working directory.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "contacts.db")


def get_connection() -> sqlite3.Connection:
    """
    Open (or create) the SQLite database and return a connection object.
    Row factory is set so that rows behave like dictionaries.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # access columns by name, e.g. row["name"]
    conn.execute("PRAGMA foreign_keys = ON")  # enforce FK constraints
    return conn


def initialize_database() -> None:
    """
    Create all required tables if they do not already exist.
    Safe to call every time the app starts.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()

        # --- Main contacts table ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contacts (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name     TEXT    NOT NULL,
                phone         TEXT    NOT NULL,
                email         TEXT    DEFAULT '',
                address       TEXT    DEFAULT '',
                notes         TEXT    DEFAULT '',
                is_favourite  INTEGER DEFAULT 0,   -- 0 = No, 1 = Yes
                is_emergency  INTEGER DEFAULT 0,   -- 0 = No, 1 = Yes
                created_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                updated_at    TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)

        # --- Future-ready: extra phone numbers per contact ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS phone_numbers (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                contact_id INTEGER NOT NULL,
                label      TEXT    DEFAULT 'Mobile',  -- Mobile / Home / Work etc.
                number     TEXT    NOT NULL,
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)

        # --- Future-ready: contact groups ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS groups (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL UNIQUE,
                color      TEXT    DEFAULT '#4A90D9'
            )
        """)

        # --- Future-ready: many-to-many contacts <-> groups ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS contact_groups (
                contact_id INTEGER NOT NULL,
                group_id   INTEGER NOT NULL,
                PRIMARY KEY (contact_id, group_id),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE,
                FOREIGN KEY (group_id)   REFERENCES groups(id)   ON DELETE CASCADE
            )
        """)

        # --- Activity Logs table (Part 3) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS activity_logs (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                action      TEXT    NOT NULL,
                description TEXT    NOT NULL,
                timestamp   TEXT    NOT NULL DEFAULT (datetime('now','localtime'))
            )
        """)

        # --- Recently Viewed table (Part 4) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS recently_viewed (
                contact_id INTEGER PRIMARY KEY,
                viewed_at  TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)

        # --- Speed Dial table (Part 4) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS speed_dial (
                slot        INTEGER PRIMARY KEY,  -- 1 to 9
                contact_id  INTEGER NOT NULL UNIQUE,
                assigned_at TEXT    NOT NULL DEFAULT (datetime('now','localtime')),
                FOREIGN KEY (contact_id) REFERENCES contacts(id) ON DELETE CASCADE
            )
        """)

        # --- Recycle Bin columns on contacts (Part 4B) ---
        # Soft-delete support: is_deleted=1 means contact is in Trash.
        # Existing databases get these columns via ALTER TABLE (safe, idempotent).
        try:
            cursor.execute("ALTER TABLE contacts ADD COLUMN is_deleted INTEGER DEFAULT 0")
        except sqlite3.Error:
            pass  # column already exists
        try:
            cursor.execute("ALTER TABLE contacts ADD COLUMN deleted_at TEXT DEFAULT NULL")
        except sqlite3.Error:
            pass  # column already exists

        # --- App settings table (Part 4A: themes & personalization) ---
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key    TEXT    PRIMARY KEY,
                value  TEXT    NOT NULL
            )
        """)

        # --- Seed default groups if not exist ---
        cursor.execute("SELECT COUNT(*) AS cnt FROM groups")
        if cursor.fetchone()["cnt"] == 0:
            default_groups = [
                ("Family", "#E67E22"),
                ("Friends", "#2ECC71"),
                ("Work", "#3498DB"),
                ("College", "#9B59B6"),
            ]
            cursor.executemany("INSERT INTO groups (name, color) VALUES (?, ?)", default_groups)

        conn.commit()
        print(f"[DB] Database initialized at: {DB_PATH}")
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to initialize database: {e}")
        raise
    finally:
        conn.close()
