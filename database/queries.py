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
    """Return all non-trashed contacts ordered alphabetically by name."""
    sql = "SELECT * FROM contacts WHERE is_deleted = 0 ORDER BY full_name COLLATE NOCASE ASC"
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_contact_by_id(contact_id: int, include_deleted: bool = False) -> Optional[sqlite3.Row]:
    """Return a single contact row by its primary key, or None if not found.
    Set include_deleted=True to also find soft-deleted (trashed) contacts."""
    if include_deleted:
        sql = "SELECT * FROM contacts WHERE id = ?"
    else:
        sql = "SELECT * FROM contacts WHERE id = ? AND is_deleted = 0"
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
        WHERE c.is_deleted = 0
          AND (
            c.full_name LIKE ? COLLATE NOCASE
           OR c.phone     LIKE ?
           OR c.email     LIKE ? COLLATE NOCASE
           OR pn.number   LIKE ?
        )
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
    """Return all non-trashed favourite contacts ordered alphabetically."""
    sql = "SELECT * FROM contacts WHERE is_favourite = 1 AND is_deleted = 0 ORDER BY full_name COLLATE NOCASE ASC"
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_emergency_contacts() -> list[sqlite3.Row]:
    """Return all non-trashed emergency contacts ordered alphabetically."""
    sql = "SELECT * FROM contacts WHERE is_emergency = 1 AND is_deleted = 0 ORDER BY full_name COLLATE NOCASE ASC"
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def get_recent_contacts(limit: int = 5) -> list[sqlite3.Row]:
    """Return the most recently updated/added non-trashed contacts."""
    sql = "SELECT * FROM contacts WHERE is_deleted = 0 ORDER BY updated_at DESC LIMIT ?"
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
    Soft-delete a contact by id (moves to Trash / Recycle Bin).
    Sets is_deleted=1 and deleted_at timestamp. Related phone_numbers and
    contact_groups are preserved so the contact can be restored intact.
    Use purge_contact() for permanent hard deletion.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE contacts SET is_deleted = 1, deleted_at = datetime('now','localtime') WHERE id = ?",
            (contact_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def purge_contact(contact_id: int) -> bool:
    """
    Permanently hard-delete a contact from the database.
    Foreign key cascades will automatically clean up phone_numbers and contact_groups.
    Cannot be undone.
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


def restore_contact(contact_id: int) -> bool:
    """
    Restore a soft-deleted contact from the Trash.
    Clears is_deleted and deleted_at so the contact reappears in all lists.
    """
    conn = get_connection()
    try:
        cursor = conn.execute(
            "UPDATE contacts SET is_deleted = 0, deleted_at = NULL WHERE id = ? AND is_deleted = 1",
            (contact_id,)
        )
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_trashed_contacts() -> list[sqlite3.Row]:
    """
    Return all soft-deleted contacts (in the Trash), ordered by deletion date descending.
    Includes extra phone numbers and groups are NOT included here — callers fetch those separately.
    """
    sql = """
        SELECT * FROM contacts
        WHERE is_deleted = 1
        ORDER BY deleted_at DESC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
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


# ---------------------------------------------------------------------------
# RECENTLY VIEWED (Part 4)
# ---------------------------------------------------------------------------

def record_recently_viewed(contact_id: int) -> None:
    """Record that a contact was viewed/opened with microsecond precision."""
    import datetime
    now_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")
    sql = """
        INSERT INTO recently_viewed (contact_id, viewed_at)
        VALUES (?, ?)
        ON CONFLICT(contact_id) DO UPDATE SET viewed_at = ?
    """
    conn = get_connection()
    try:
        conn.execute(sql, (contact_id, now_ts, now_ts))
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
    finally:
        conn.close()


def get_recently_viewed_contacts(limit: int = 10) -> list[sqlite3.Row]:
    """Return non-trashed contacts ordered by the most recently viewed first."""
    sql = """
        SELECT c.*, rv.viewed_at
        FROM contacts c
        JOIN recently_viewed rv ON c.id = rv.contact_id
        WHERE c.is_deleted = 0
        ORDER BY rv.viewed_at DESC
        LIMIT ?
    """
    conn = get_connection()
    try:
        return conn.execute(sql, (limit,)).fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# SPEED DIAL (Part 4)
# ---------------------------------------------------------------------------

def get_speed_dial_slots() -> list[sqlite3.Row]:
    """Return all 9 speed dial slots joined with contact data if assigned."""
    sql = """
        SELECT sd.slot, sd.assigned_at, c.id AS contact_id, c.full_name, c.phone, c.email
        FROM speed_dial sd
        JOIN contacts c ON sd.contact_id = c.id
        ORDER BY sd.slot ASC
    """
    conn = get_connection()
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()


def set_speed_dial_slot(slot: int, contact_id: int) -> bool:
    """
    Assign a contact to a speed dial slot (1-9).
    If the contact or slot was previously assigned, clears previous assignments first.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        # Remove any existing assignment for this contact or slot
        cursor.execute("DELETE FROM speed_dial WHERE slot = ? OR contact_id = ?", (slot, contact_id))
        cursor.execute(
            "INSERT INTO speed_dial (slot, contact_id, assigned_at) VALUES (?, ?, datetime('now','localtime'))",
            (slot, contact_id)
        )
        conn.commit()
        return True
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def clear_speed_dial_slot(slot: int) -> bool:
    """Remove a speed dial assignment for a given slot (1-9)."""
    sql = "DELETE FROM speed_dial WHERE slot = ?"
    conn = get_connection()
    try:
        cursor = conn.execute(sql, (slot,))
        conn.commit()
        return cursor.rowcount > 0
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()


def get_contact_speed_dial(contact_id: int) -> Optional[int]:
    """Return the speed dial slot assigned to a contact, or None."""
    sql = "SELECT slot FROM speed_dial WHERE contact_id = ?"
    conn = get_connection()
    try:
        row = conn.execute(sql, (contact_id,)).fetchone()
        return row["slot"] if row else None
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ADVANCED DUPLICATE DETECTION (Part 4)
# ---------------------------------------------------------------------------

def find_duplicate_contacts_clusters() -> list[dict]:
    """
    Identify potential duplicate contact clusters.
    Detects matching phone numbers (primary and secondary), matching emails,
    and matching full names.
    Returns a list of cluster dicts:
        [
            {
                "reason": "Matching Phone Number (+91 98...)",
                "contacts": [Row, Row]
            },
            ...
        ]
    """
    clusters = []
    conn = get_connection()
    try:
        # 1. Matching Primary Phone
        phone_matches = conn.execute("""
            SELECT phone FROM contacts
            GROUP BY phone
            HAVING COUNT(*) > 1
        """).fetchall()

        for p in phone_matches:
            val = p["phone"]
            rows = conn.execute("SELECT * FROM contacts WHERE phone = ? ORDER BY id ASC", (val,)).fetchall()
            clusters.append({
                "type": "Phone",
                "value": val,
                "reason": f"Same Primary Phone: {val}",
                "contacts": rows
            })

        # 2. Matching Secondary Phone Numbers or Primary-to-Secondary matches
        cross_phone_matches = conn.execute("""
            SELECT pn.number FROM phone_numbers pn
            JOIN contacts c ON c.phone = pn.number AND c.id != pn.contact_id
            GROUP BY pn.number
        """).fetchall()

        for cp in cross_phone_matches:
            val = cp["number"]
            rows = conn.execute("""
                SELECT DISTINCT c.* FROM contacts c
                LEFT JOIN phone_numbers pn ON c.id = pn.contact_id
                WHERE c.phone = ? OR pn.number = ?
                ORDER BY c.id ASC
            """, (val, val)).fetchall()
            if len(rows) > 1 and not any(c["value"] == val for c in clusters):
                clusters.append({
                    "type": "Secondary Phone",
                    "value": val,
                    "reason": f"Shared Secondary/Primary Phone: {val}",
                    "contacts": rows
                })

        # 3. Matching Email (non-empty)
        email_matches = conn.execute("""
            SELECT email FROM contacts
            WHERE email != ''
            GROUP BY email COLLATE NOCASE
            HAVING COUNT(*) > 1
        """).fetchall()

        for em in email_matches:
            val = em["email"]
            rows = conn.execute("SELECT * FROM contacts WHERE email = ? COLLATE NOCASE ORDER BY id ASC", (val,)).fetchall()
            if not any(c["value"] == val for c in clusters):
                clusters.append({
                    "type": "Email",
                    "value": val,
                    "reason": f"Same Email Address: {val}",
                    "contacts": rows
                })

        # 4. Matching Full Name (exact case-insensitive)
        name_matches = conn.execute("""
            SELECT full_name FROM contacts
            GROUP BY full_name COLLATE NOCASE
            HAVING COUNT(*) > 1
        """).fetchall()

        for nm in name_matches:
            val = nm["full_name"]
            rows = conn.execute("SELECT * FROM contacts WHERE full_name = ? COLLATE NOCASE ORDER BY id ASC", (val,)).fetchall()
            # If not already completely in an existing cluster
            id_set = {r["id"] for r in rows}
            if not any({r["id"] for r in c["contacts"]} == id_set for c in clusters):
                clusters.append({
                    "type": "Name",
                    "value": val,
                    "reason": f"Identical Full Name: '{val}'",
                    "contacts": rows
                })

        return clusters
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# ADVANCED SEARCH, FILTER & SORT (Part 4)
# ---------------------------------------------------------------------------

def query_contacts_filtered_and_sorted(
    search_query: str = "",
    filter_type: str = "all",
    group_id: Optional[int] = None,
    sort_by: str = "name_asc"
) -> list[sqlite3.Row]:
    """
    Unified advanced query supporting:
      - search_query across name, primary phone, email, and secondary phone numbers
      - filter_type: 'all' | 'fav' | 'emer'
      - group_id: specific group filtering
      - sort_by: 'name_asc' | 'name_desc' | 'date_desc' | 'date_asc'
    """
    conditions = []
    params = []

    sql = """
        SELECT DISTINCT c.*
        FROM contacts c
        LEFT JOIN phone_numbers pn ON c.id = pn.contact_id
    """

    # Always exclude soft-deleted contacts
    conditions.append("c.is_deleted = 0")

    if group_id is not None:
        sql += " JOIN contact_groups cg ON c.id = cg.contact_id "
        conditions.append("cg.group_id = ?")
        params.append(group_id)

    # Search query
    if search_query.strip():
        like = f"%{search_query.strip()}%"
        conditions.append("""(
            c.full_name LIKE ? COLLATE NOCASE
            OR c.phone     LIKE ?
            OR c.email     LIKE ? COLLATE NOCASE
            OR pn.number   LIKE ?
        )""")
        params.extend([like, like, like, like])

    # Quick filters
    if filter_type == "fav":
        conditions.append("c.is_favourite = 1")
    elif filter_type == "emer":
        conditions.append("c.is_emergency = 1")

    if conditions:
        sql += " WHERE " + " AND ".join(conditions)

    # Sorting
    sort_clauses = {
        "name_asc":   "c.full_name COLLATE NOCASE ASC",
        "name_desc":  "c.full_name COLLATE NOCASE DESC",
        "date_desc":  "c.updated_at DESC",
        "date_asc":   "c.updated_at ASC",
    }
    order_by = sort_clauses.get(sort_by, "c.full_name COLLATE NOCASE ASC")
    sql += f" ORDER BY {order_by}"

    conn = get_connection()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------------
# APP SETTINGS (Part 4A: Themes & Personalization)
# ---------------------------------------------------------------------------

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return a setting value by key, or default if not found."""
    conn = get_connection()
    try:
        row = conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        return row["value"] if row else default
    finally:
        conn.close()


def set_setting(key: str, value: str) -> None:
    """Insert or update a setting key-value pair."""
    conn = get_connection()
    try:
        conn.execute(
            "INSERT INTO settings (key, value) VALUES (?, ?) "
            "ON CONFLICT(key) DO UPDATE SET value = excluded.value",
            (key, value)
        )
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        conn.close()
