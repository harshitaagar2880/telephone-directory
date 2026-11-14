"""
database/queries.py
-------------------
All SQL CRUD operations for the contacts table.
GUI and service layers call functions from here — no raw SQL anywhere else.
"""

import sqlite3
from typing import Optional
from database.connection import get_connection


# ---------------------------------------------------------------------------
# CREATE
# ---------------------------------------------------------------------------

def insert_contact(full_name: str, phone: str, email: str = "",
                   address: str = "", notes: str = "",
                   is_favourite: int = 0, is_emergency: int = 0) -> int:
    """
    Insert a new contact and return the new row's id.
    Raises sqlite3.Error on failure.
    """
    sql = """
        INSERT INTO contacts
            (full_name, phone, email, address, notes, is_favourite, is_emergency,
             created_at, updated_at)
        VALUES
            (?, ?, ?, ?, ?, ?, ?, datetime('now','localtime'), datetime('now','localtime'))
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (full_name, phone, email, address, notes,
                                    is_favourite, is_emergency))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# READ
# ---------------------------------------------------------------------------

def get_all_contacts() -> list[sqlite3.Row]:
    """Return all contacts ordered alphabetically by name."""
    sql = "SELECT * FROM contacts ORDER BY full_name COLLATE NOCASE ASC"
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_contact_by_id(contact_id: int) -> Optional[sqlite3.Row]:
    """Return a single contact row by its primary key, or None if not found."""
    sql = "SELECT * FROM contacts WHERE id = ?"
    conn = get_connection()
    try:
        return conn.execute(sql, (contact_id,)).fetchone()
    finally:
        conn.close()


def search_contacts(query: str) -> list[sqlite3.Row]:
    """
    Case-insensitive search across full_name, phone, and email.
    Returns matching rows ordered by name.
    """
    like = f"%{query}%"
    sql = """
        SELECT * FROM contacts
        WHERE  full_name LIKE ? COLLATE NOCASE
           OR  phone     LIKE ?
           OR  email     LIKE ? COLLATE NOCASE
        ORDER BY full_name COLLATE NOCASE ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (like, like, like)).fetchall()
    finally:
        conn.close()


def check_duplicate(full_name: str, phone: str,
                    exclude_id: Optional[int] = None) -> bool:
    """
    Return True if a contact with the same name AND phone already exists.
    Pass exclude_id when editing so the contact being edited is not flagged.
    """
    if exclude_id is not None:
        sql = """
            SELECT 1 FROM contacts
            WHERE full_name = ? COLLATE NOCASE AND phone = ? AND id != ?
            LIMIT 1
        """
        params = (full_name, phone, exclude_id)
    else:
        sql = """
            SELECT 1 FROM contacts
            WHERE full_name = ? COLLATE NOCASE AND phone = ?
            LIMIT 1
        """
        params = (full_name, phone)

    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchone() is not None
    finally:
        conn.close()


def get_contact_count() -> int:
    """Return the total number of contacts in the database."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT COUNT(*) AS cnt FROM contacts").fetchone()
        return row["cnt"]
    finally:
        conn.close()


def get_favourite_count() -> int:
    """Return the number of contacts marked as favourite."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM contacts WHERE is_favourite = 1"
        ).fetchone()
        return row["cnt"]
    finally:
        conn.close()


def get_emergency_count() -> int:
    """Return the number of contacts marked as emergency."""
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT COUNT(*) AS cnt FROM contacts WHERE is_emergency = 1"
        ).fetchone()
        return row["cnt"]
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# UPDATE
# ---------------------------------------------------------------------------

def update_contact(contact_id: int, full_name: str, phone: str,
                   email: str = "", address: str = "", notes: str = "",
                   is_favourite: int = 0, is_emergency: int = 0) -> bool:
    """
    Update an existing contact. Returns True on success, False if not found.
    """
    sql = """
        UPDATE contacts
        SET full_name    = ?,
            phone        = ?,
            email        = ?,
            address      = ?,
            notes        = ?,
            is_favourite = ?,
            is_emergency = ?,
            updated_at   = datetime('now','localtime')
        WHERE id = ?
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (full_name, phone, email, address, notes,
                                    is_favourite, is_emergency, contact_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# DELETE
# ---------------------------------------------------------------------------

def delete_contact(contact_id: int) -> bool:
    """
    Delete a contact by id. Returns True if a row was deleted.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
