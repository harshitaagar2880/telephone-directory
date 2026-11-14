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

        conn.commit()
        print(f"[DB] Database initialized at: {DB_PATH}")
    except sqlite3.Error as e:
        print(f"[DB ERROR] Failed to initialize database: {e}")
        raise
    finally:
        conn.close()
