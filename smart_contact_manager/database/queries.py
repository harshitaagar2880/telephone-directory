"""
database/queries.py
-------------------
All SQL CRUD operations for the contacts, phone_numbers, groups,
and contact_groups tables.
GUI and service layers call functions from here — no raw SQL anywhere else.
"""

import sqlite3
from typing import Optional, List, Tuple, Dict, Any
from database.connection import get_connection


# ---------------------------------------------------------------------------
# CONTACTS — CREATE
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
# CONTACTS — READ
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
    Case-insensitive search across full_name, primary phone, email,
    AND secondary phone numbers stored in the phone_numbers table.
    Returns matching contact rows ordered by name.
    """
    like = f"%{query}%"
    sql = """
        SELECT DISTINCT c.*
        FROM contacts c
        LEFT JOIN phone_numbers pn ON c.id = pn.contact_id
        WHERE  c.full_name LIKE ? COLLATE NOCASE
           OR  c.phone     LIKE ?
           OR  c.email     LIKE ? COLLATE NOCASE
           OR  pn.number   LIKE ?
        ORDER BY c.full_name COLLATE NOCASE ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (like, like, like, like)).fetchall()
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


def get_favourite_contacts() -> list[sqlite3.Row]:
    """Return all favourite contacts ordered alphabetically."""
    sql = "SELECT * FROM contacts WHERE is_favourite = 1 ORDER BY full_name COLLATE NOCASE ASC"
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_emergency_contacts() -> list[sqlite3.Row]:
    """Return all emergency contacts ordered alphabetically."""
    sql = "SELECT * FROM contacts WHERE is_emergency = 1 ORDER BY full_name COLLATE NOCASE ASC"
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_recent_contacts(limit: int = 5) -> list[sqlite3.Row]:
    """Return the most recently updated/added contacts."""
    sql = "SELECT * FROM contacts ORDER BY updated_at DESC LIMIT ?"
    conn = get_connection()
    try:
        return conn.execute(sql, (limit,)).fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CONTACTS — UPDATE
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


def set_favourite_status(contact_id: int, is_favourite: bool) -> bool:
    """Toggle or set favourite status directly."""
    sql = """
        UPDATE contacts
        SET is_favourite = ?,
            updated_at   = datetime('now','localtime')
        WHERE id = ?
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (1 if is_favourite else 0, contact_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def set_emergency_status(contact_id: int, is_emergency: bool) -> bool:
    """Toggle or set emergency status directly."""
    sql = """
        UPDATE contacts
        SET is_emergency = ?,
            updated_at   = datetime('now','localtime')
        WHERE id = ?
    """
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (1 if is_emergency else 0, contact_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# CONTACTS — DELETE
# ---------------------------------------------------------------------------

def delete_contact(contact_id: int) -> bool:
    """
    Delete a contact by id.
    Foreign key cascades will automatically clean up phone_numbers and contact_groups.
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


# ---------------------------------------------------------------------------
# SECONDARY PHONE NUMBERS (phone_numbers table)
# ---------------------------------------------------------------------------

def get_phone_numbers(contact_id: int) -> list[sqlite3.Row]:
    """Get all extra phone numbers for a contact."""
    sql = "SELECT * FROM phone_numbers WHERE contact_id = ? ORDER BY id ASC"
    conn = get_connection()
    try:
        return conn.execute(sql, (contact_id,)).fetchall()
    finally:
        conn.close()


def set_contact_phone_numbers(contact_id: int, numbers: list[Tuple[str, str]]) -> None:
    """
    Replace all extra phone numbers for a contact.
    numbers: list of (label, number) tuples.
    Avoids duplicate phone numbers for the same contact.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM phone_numbers WHERE contact_id = ?", (contact_id,))
        
        seen = set()
        to_insert = []
        for label, num in numbers:
            cleaned_num = num.strip()
            if not cleaned_num or cleaned_num in seen:
                continue
            seen.add(cleaned_num)
            to_insert.append((contact_id, label.strip() or "Other", cleaned_num))
            
        if to_insert:
            cursor.executemany(
                "INSERT INTO phone_numbers (contact_id, label, number) VALUES (?, ?, ?)",
                to_insert
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_single_phone_number(phone_id: int) -> bool:
    """Delete an extra phone number by its primary key."""
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM phone_numbers WHERE id = ?", (phone_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# GROUPS (groups and contact_groups tables)
# ---------------------------------------------------------------------------

def get_all_groups() -> list[sqlite3.Row]:
    """
    Return all groups along with the count of contacts in each group.
    """
    sql = """
        SELECT g.id, g.name, g.color, COUNT(cg.contact_id) AS contact_count
        FROM groups g
        LEFT JOIN contact_groups cg ON g.id = cg.group_id
        GROUP BY g.id, g.name, g.color
        ORDER BY g.name COLLATE NOCASE ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_group_by_id(group_id: int) -> Optional[sqlite3.Row]:
    """Fetch a single group by id."""
    sql = "SELECT * FROM groups WHERE id = ?"
    conn = get_connection()
    try:
        return conn.execute(sql, (group_id,)).fetchone()
    finally:
        conn.close()


def get_group_by_name(name: str) -> Optional[sqlite3.Row]:
    """Fetch a single group by name."""
    sql = "SELECT * FROM groups WHERE name = ? COLLATE NOCASE"
    conn = get_connection()
    try:
        return conn.execute(sql, (name.strip(),)).fetchone()
    finally:
        conn.close()


def create_group(name: str, color: str = "#4A90D9") -> int:
    """Create a new group. Returns the new group id."""
    sql = "INSERT INTO groups (name, color) VALUES (?, ?)"
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (name.strip(), color.strip()))
        conn.commit()
        return cursor.lastrowid
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def update_group(group_id: int, name: str, color: str = "#4A90D9") -> bool:
    """Update a group's name and color."""
    sql = "UPDATE groups SET name = ?, color = ? WHERE id = ?"
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (name.strip(), color.strip(), group_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def delete_group(group_id: int) -> bool:
    """
    Delete a group.
    Note: Foreign key cascade deletes entries in contact_groups,
    leaving the actual contacts in the contacts table completely intact.
    """
    conn = get_connection()
    try:
        cursor = conn.execute("DELETE FROM groups WHERE id = ?", (group_id,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_contact_groups(contact_id: int) -> list[sqlite3.Row]:
    """Return all groups a contact belongs to."""
    sql = """
        SELECT g.id, g.name, g.color
        FROM groups g
        JOIN contact_groups cg ON g.id = cg.group_id
        WHERE cg.contact_id = ?
        ORDER BY g.name COLLATE NOCASE ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (contact_id,)).fetchall()
    finally:
        conn.close()


def set_contact_groups(contact_id: int, group_ids: list[int]) -> None:
    """
    Replace the groups assigned to a contact.
    Uses transaction and eliminates duplicate group ids.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM contact_groups WHERE contact_id = ?", (contact_id,))
        
        unique_ids = set(group_ids)
        if unique_ids:
            cursor.executemany(
                "INSERT OR IGNORE INTO contact_groups (contact_id, group_id) VALUES (?, ?)",
                [(contact_id, gid) for gid in unique_ids]
            )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_contacts_by_group(group_id: int) -> list[sqlite3.Row]:
    """Return all contacts belonging to a specific group."""
    sql = """
        SELECT c.*
        FROM contacts c
        JOIN contact_groups cg ON c.id = cg.contact_id
        WHERE cg.group_id = ?
        ORDER BY c.full_name COLLATE NOCASE ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (group_id,)).fetchall()
    finally:
        conn.close()


def add_contact_to_group(contact_id: int, group_id: int) -> bool:
    """Add a contact to a group (ignores if already added)."""
    sql = "INSERT OR IGNORE INTO contact_groups (contact_id, group_id) VALUES (?, ?)"
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (contact_id, group_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def remove_contact_from_group(contact_id: int, group_id: int) -> bool:
    """Remove a contact from a group."""
    sql = "DELETE FROM contact_groups WHERE contact_id = ? AND group_id = ?"
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (contact_id, group_id))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
