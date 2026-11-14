"""
services/contact_service.py
----------------------------
Business logic layer: validation, duplicate checking, orchestration of
contacts, secondary phone numbers, favourite/emergency flags, and groups.
GUI widgets call functions here; this layer talks to database/queries.py.
"""

import re
from typing import Optional, Tuple, List, Dict, Any

from models.contact import Contact
import database.queries as db


# ---------------------------------------------------------------------------
# Validation helpers
# ---------------------------------------------------------------------------

PHONE_PATTERN = re.compile(
    r"^\+?[\d\s\-\(\)]{7,15}$"
)
EMAIL_PATTERN = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


def validate_contact(full_name: str, phone: str,
                     email: str = "",
                     extra_phones: Optional[List[Tuple[str, str]]] = None) -> Tuple[bool, str]:
    """
    Validate fields before inserting or updating.
    Returns (True, "") on success or (False, error_message) on failure.
    """
    if not full_name.strip():
        return False, "Full name is required."

    if len(full_name.strip()) < 2:
        return False, "Name must be at least 2 characters."

    if not phone.strip():
        return False, "Primary phone number is required."

    if not PHONE_PATTERN.match(phone.strip()):
        return False, (
            "Invalid primary phone number.\n"
            "Accepted formats: 9876543210, +91 98765 43210, (022) 2345-6789"
        )

    if email.strip() and not EMAIL_PATTERN.match(email.strip()):
        return False, "Invalid email address format."

    if extra_phones:
        for idx, (label, num) in enumerate(extra_phones, 1):
            num_clean = num.strip()
            if num_clean and not PHONE_PATTERN.match(num_clean):
                lbl = label.strip() or f"Secondary #{idx}"
                return False, f"Invalid phone number format for {lbl}: '{num_clean}'"

    return True, ""


# ---------------------------------------------------------------------------
# Helper: Assemble full Contact object with phones and groups
# ---------------------------------------------------------------------------

def _row_to_contact(row) -> Contact:
    """Build a Contact object with extra phone numbers and groups attached."""
    if not row:
        return None
    cid = row["id"]
    
    # Secondary phone numbers
    pn_rows = db.get_phone_numbers(cid)
    extra_phones = [
        {"id": p["id"], "label": p["label"], "number": p["number"]}
        for p in pn_rows
    ]
    
    # Associated groups
    grp_rows = db.get_contact_groups(cid)
    groups = [
        {"id": g["id"], "name": g["name"], "color": g["color"]}
        for g in grp_rows
    ]
    
    return Contact.from_row(row, extra_phones=extra_phones, groups=groups)


# ---------------------------------------------------------------------------
# CRUD service functions
# ---------------------------------------------------------------------------

def add_contact(full_name: str, phone: str, email: str = "",
                address: str = "", notes: str = "",
                is_favourite: bool = False,
                is_emergency: bool = False,
                extra_phones: Optional[List[Tuple[str, str]]] = None,
                group_ids: Optional[List[int]] = None) -> Tuple[bool, str]:
    """
    Validate and insert a new contact, including extra phone numbers and group associations.
    Returns (True, success_message) or (False, error_message).
    """
    # 1. Validate inputs
    ok, msg = validate_contact(full_name, phone, email, extra_phones)
    if not ok:
        return False, msg

    # 2. Duplicate check
    if db.check_duplicate(full_name.strip(), phone.strip()):
        return False, "A contact with the same name and primary phone number already exists."

    # 3. Insert into database
    try:
        new_id = db.insert_contact(
            full_name    = full_name.strip(),
            phone        = phone.strip(),
            email        = email.strip(),
            address      = address.strip(),
            notes        = notes.strip(),
            is_favourite = int(is_favourite),
            is_emergency = int(is_emergency),
        )

        # 4. Save extra phone numbers if any
        if extra_phones:
            db.set_contact_phone_numbers(new_id, extra_phones)

        # 5. Save group associations if any
        if group_ids:
            db.set_contact_groups(new_id, group_ids)

        return True, f"Contact '{full_name.strip()}' added successfully (ID: {new_id})."
    except Exception as e:
        return False, f"Database error: {e}"


def edit_contact(contact_id: int, full_name: str, phone: str,
                 email: str = "", address: str = "", notes: str = "",
                 is_favourite: bool = False,
                 is_emergency: bool = False,
                 extra_phones: Optional[List[Tuple[str, str]]] = None,
                 group_ids: Optional[List[int]] = None) -> Tuple[bool, str]:
    """
    Validate and update an existing contact along with extra phones and groups.
    Returns (True, success_message) or (False, error_message).
    """
    ok, msg = validate_contact(full_name, phone, email, extra_phones)
    if not ok:
        return False, msg

    if db.check_duplicate(full_name.strip(), phone.strip(), exclude_id=contact_id):
        return False, "Another contact with the same name and phone already exists."

    try:
        updated = db.update_contact(
            contact_id   = contact_id,
            full_name    = full_name.strip(),
            phone        = phone.strip(),
            email        = email.strip(),
            address      = address.strip(),
            notes        = notes.strip(),
            is_favourite = int(is_favourite),
            is_emergency = int(is_emergency),
        )
        if not updated:
            return False, "Contact not found in the database."

        # Update secondary phone numbers if supplied
        if extra_phones is not None:
            db.set_contact_phone_numbers(contact_id, extra_phones)

        # Update group associations if supplied
        if group_ids is not None:
            db.set_contact_groups(contact_id, group_ids)

        return True, f"Contact '{full_name.strip()}' updated successfully."
    except Exception as e:
        return False, f"Database error: {e}"


def remove_contact(contact_id: int) -> Tuple[bool, str]:
    """
    Soft-delete a contact by id (moves to Trash / Recycle Bin).
    Related phone numbers and group memberships are preserved for restoration.
    """
    try:
        deleted = db.delete_contact(contact_id)
        if deleted:
            return True, "Contact moved to Trash."
        return False, "Contact not found."
    except Exception as e:
        return False, f"Database error: {e}"


def purge_contact(contact_id: int) -> Tuple[bool, str]:
    """
    Permanently hard-delete a contact from the database.
    Cannot be undone. Related phone numbers and group memberships are also removed.
    """
    try:
        deleted = db.purge_contact(contact_id)
        if deleted:
            return True, "Contact permanently deleted."
        return False, "Contact not found."
    except Exception as e:
        return False, f"Database error: {e}"


def restore_contact(contact_id: int) -> Tuple[bool, str]:
    """
    Restore a soft-deleted contact from the Trash.
    The contact retains its original details, phone numbers, favourite/emergency
    status, and group memberships.
    """
    try:
        restored = db.restore_contact(contact_id)
        if restored:
            return True, "Contact restored from Trash."
        return False, "Contact not found in Trash."
    except Exception as e:
        return False, f"Database error: {e}"


def fetch_trashed_contacts() -> List[Contact]:
    """Return all soft-deleted contacts (in the Trash) with phones and groups."""
    rows = db.get_trashed_contacts()
    return [_row_to_contact(r) for r in rows]


def fetch_all_contacts() -> List[Contact]:
    """Return all contacts as Contact objects."""
    rows = db.get_all_contacts()
    return [_row_to_contact(r) for r in rows]


def fetch_contact(contact_id: int) -> Optional[Contact]:
    """Return a single Contact by id, or None."""
    row = db.get_contact_by_id(contact_id)
    return _row_to_contact(row) if row else None


def search_contacts(query: str) -> List[Contact]:
    """Search contacts by name, primary phone, email, or secondary phones."""
    if not query.strip():
        return fetch_all_contacts()
    rows = db.search_contacts(query.strip())
    return [_row_to_contact(r) for r in rows]


# ---------------------------------------------------------------------------
# Favourites and Emergency services
# ---------------------------------------------------------------------------

def fetch_favourite_contacts() -> List[Contact]:
    """Return all favourite contacts."""
    rows = db.get_favourite_contacts()
    return [_row_to_contact(r) for r in rows]


def toggle_favourite(contact_id: int, is_favourite: bool) -> Tuple[bool, str]:
    """Mark or unmark a contact as favourite."""
    try:
        ok = db.set_favourite_status(contact_id, is_favourite)
        if ok:
            action = "marked as favourite" if is_favourite else "removed from favourites"
            return True, f"Contact {action}."
        return False, "Contact not found."
    except Exception as e:
        return False, f"Database error: {e}"


def fetch_emergency_contacts() -> List[Contact]:
    """Return all emergency contacts."""
    rows = db.get_emergency_contacts()
    return [_row_to_contact(r) for r in rows]


def toggle_emergency(contact_id: int, is_emergency: bool) -> Tuple[bool, str]:
    """Mark or unmark a contact as emergency."""
    try:
        ok = db.set_emergency_status(contact_id, is_emergency)
        if ok:
            action = "marked as emergency contact" if is_emergency else "removed from emergency contacts"
            return True, f"Contact {action}."
        return False, "Contact not found."
    except Exception as e:
        return False, f"Database error: {e}"


# ---------------------------------------------------------------------------
# Group management services
# ---------------------------------------------------------------------------

def fetch_all_groups() -> List[Dict[str, Any]]:
    """Return all groups with id, name, color, and contact count."""
    rows = db.get_all_groups()
    return [
        {"id": r["id"], "name": r["name"], "color": r["color"], "contact_count": r["contact_count"]}
        for r in rows
    ]


def create_group(name: str, color: str = "#4A90D9") -> Tuple[bool, str]:
    """Validate and create a new group."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Group name cannot be empty."
    if len(clean_name) < 2:
        return False, "Group name must be at least 2 characters."
    
    if db.get_group_by_name(clean_name):
        return False, f"A group named '{clean_name}' already exists."

    try:
        gid = db.create_group(clean_name, color)
        return True, f"Group '{clean_name}' created successfully (ID: {gid})."
    except Exception as e:
        return False, f"Database error: {e}"


def edit_group(group_id: int, name: str, color: str = "#4A90D9") -> Tuple[bool, str]:
    """Update a group's name and color."""
    clean_name = name.strip()
    if not clean_name:
        return False, "Group name cannot be empty."
    
    existing = db.get_group_by_name(clean_name)
    if existing and existing["id"] != group_id:
        return False, f"Another group named '{clean_name}' already exists."

    try:
        ok = db.update_group(group_id, clean_name, color)
        if ok:
            return True, f"Group updated to '{clean_name}'."
        return False, "Group not found."
    except Exception as e:
        return False, f"Database error: {e}"


def delete_group(group_id: int) -> Tuple[bool, str]:
    """
    Delete a group without deleting its contacts.
    """
    try:
        ok = db.delete_group(group_id)
        if ok:
            return True, "Group deleted successfully (contacts were preserved)."
        return False, "Group not found."
    except Exception as e:
        return False, f"Database error: {e}"


# Aliases for explicit naming
create_custom_group = create_group
edit_custom_group = edit_group
delete_custom_group = delete_group


def fetch_contacts_by_group(group_id: int) -> List[Contact]:
    """Return all contacts in a specific group."""
    rows = db.get_contacts_by_group(group_id)
    return [_row_to_contact(r) for r in rows]


def add_contact_to_group(contact_id: int, group_id: int) -> Tuple[bool, str]:
    """Add a contact to a group."""
    try:
        ok = db.add_contact_to_group(contact_id, group_id)
        if ok:
            return True, "Contact added to group."
        return False, "Contact is already in this group."
    except Exception as e:
        return False, f"Database error: {e}"


def remove_contact_from_group(contact_id: int, group_id: int) -> Tuple[bool, str]:
    """Remove a contact from a group."""
    try:
        ok = db.remove_contact_from_group(contact_id, group_id)
        if ok:
            return True, "Contact removed from group."
        return False, "Contact was not in this group."
    except Exception as e:
        return False, f"Database error: {e}"


# ---------------------------------------------------------------------------
# Dashboard and Recent contacts
# ---------------------------------------------------------------------------

def get_recent_contacts(limit: int = 5) -> List[Contact]:
    """Fetch the most recently added or updated contacts."""
    rows = db.get_recent_contacts(limit)
    return [_row_to_contact(r) for r in rows]


def get_dashboard_stats() -> dict:
    """Return summary statistics for the dashboard."""
    groups = db.get_all_groups()
    speed_dials = db.get_speed_dial_slots()
    return {
        "total":       db.get_contact_count(),
        "favourites":  db.get_favourite_count(),
        "emergency":   db.get_emergency_count(),
        "groups":      len(groups),
        "speed_dial":  len(speed_dials),
    }


# ---------------------------------------------------------------------------
# RECENTLY VIEWED (Part 4)
# ---------------------------------------------------------------------------

def record_contact_viewed(contact_id: int) -> None:
    """Track that a contact was opened/viewed."""
    try:
        db.record_recently_viewed(contact_id)
    except Exception as e:
        print(f"[Warning] Failed to record recently viewed: {e}")


def fetch_recently_viewed_contacts(limit: int = 10) -> List[Contact]:
    """Return contacts ordered by the most recently viewed first, avoiding duplicates."""
    rows = db.get_recently_viewed_contacts(limit)
    return [_row_to_contact(r) for r in rows]


# ---------------------------------------------------------------------------
# SPEED DIAL (Part 4)
# ---------------------------------------------------------------------------

def fetch_speed_dial_slots() -> List[Dict[str, Any]]:
    """Return slots 1 through 9 with contact details if assigned."""
    assigned_rows = db.get_speed_dial_slots()
    assigned_dict = {r["slot"]: r for r in assigned_rows}

    slots = []
    for slot_num in range(1, 10):
        if slot_num in assigned_dict:
            r = assigned_dict[slot_num]
            c = fetch_contact(r["contact_id"])
            slots.append({
                "slot": slot_num,
                "assigned": True,
                "contact": c,
                "assigned_at": r["assigned_at"]
            })
        else:
            slots.append({
                "slot": slot_num,
                "assigned": False,
                "contact": None,
                "assigned_at": None
            })
    return slots


def assign_speed_dial(slot: int, contact_id: int) -> Tuple[bool, str]:
    """Assign a contact to speed dial slot (1 to 9)."""
    if not (1 <= slot <= 9):
        return False, "Speed dial slot must be between 1 and 9."

    contact = fetch_contact(contact_id)
    if not contact:
        return False, "Contact not found."

    try:
        ok = db.set_speed_dial_slot(slot, contact_id)
        if ok:
            return True, f"Speed Dial #{slot} assigned to '{contact.full_name}'."
        return False, "Failed to assign speed dial slot."
    except Exception as e:
        return False, f"Database error: {e}"


def clear_speed_dial(slot: int) -> Tuple[bool, str]:
    """Clear assignment for a speed dial slot (1 to 9)."""
    if not (1 <= slot <= 9):
        return False, "Invalid slot number."
    try:
        ok = db.clear_speed_dial_slot(slot)
        if ok:
            return True, f"Speed Dial #{slot} cleared."
        return False, f"Speed Dial #{slot} was not assigned."
    except Exception as e:
        return False, f"Database error: {e}"


def fetch_contact_speed_dial(contact_id: int) -> Optional[int]:
    """Return which speed dial slot is assigned to a contact, or None."""
    return db.get_contact_speed_dial(contact_id)


# ---------------------------------------------------------------------------
# ADVANCED DUPLICATE DETECTION (Part 4)
# ---------------------------------------------------------------------------

def detect_duplicate_contacts() -> List[Dict[str, Any]]:
    """
    Find clusters of contacts that share phone numbers, emails, or exact names.
    Returns list of dicts:
        [
            {
                "type": "Phone" | "Email" | "Name",
                "value": "...",
                "reason": "...",
                "contacts": [Contact, Contact, ...]
            },
            ...
        ]
    """
    raw_clusters = db.find_duplicate_contacts_clusters()
    processed_clusters = []

    for cluster in raw_clusters:
        contacts = [_row_to_contact(r) for r in cluster["contacts"]]
        processed_clusters.append({
            "type": cluster["type"],
            "value": cluster["value"],
            "reason": cluster["reason"],
            "contacts": contacts
        })
    return processed_clusters


# ---------------------------------------------------------------------------
# ADVANCED FILTER & SORT (Part 4)
# ---------------------------------------------------------------------------

def fetch_contacts_filtered_and_sorted(
    search_query: str = "",
    filter_type: str = "all",
    group_id: Optional[int] = None,
    sort_by: str = "name_asc"
) -> List[Contact]:
    """
    Unified search, filter, and sort across all contacts.
    """
    rows = db.query_contacts_filtered_and_sorted(
        search_query=search_query,
        filter_type=filter_type,
        group_id=group_id,
        sort_by=sort_by
    )
    return [_row_to_contact(r) for r in rows]


# ---------------------------------------------------------------------------
# APP SETTINGS (Part 4A: Themes & Personalization)
# ---------------------------------------------------------------------------

def get_setting(key: str, default: Optional[str] = None) -> Optional[str]:
    """Return an app setting value by key, or default if not found."""
    return db.get_setting(key, default=default)


def set_setting(key: str, value: str) -> None:
    """Save an app setting key-value pair."""
    db.set_setting(key, value)


def check_duplicate(full_name: str, phone: str,
                    exclude_id: Optional[int] = None) -> bool:
    """Wrapper around db.check_duplicate for convenience."""
    return db.check_duplicate(full_name.strip(), phone.strip(), exclude_id=exclude_id)
