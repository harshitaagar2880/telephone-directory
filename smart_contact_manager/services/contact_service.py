"""
services/contact_service.py
----------------------------
Business logic layer: validation, duplicate checking, and orchestration.
GUI widgets call functions here; this layer talks to database/queries.py.
"""

import re
from typing import Optional, Tuple

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
                     email: str = "") -> Tuple[bool, str]:
    """
    Validate fields before inserting or updating.
    Returns (True, "") on success or (False, error_message) on failure.
    """
    if not full_name.strip():
        return False, "Full name is required."

    if len(full_name.strip()) < 2:
        return False, "Name must be at least 2 characters."

    if not phone.strip():
        return False, "Phone number is required."

    if not PHONE_PATTERN.match(phone.strip()):
        return False, (
            "Invalid phone number.\n"
            "Accepted formats: 9876543210, +91 98765 43210, (022) 2345-6789"
        )

    if email.strip() and not EMAIL_PATTERN.match(email.strip()):
        return False, "Invalid email address format."

    return True, ""


# ---------------------------------------------------------------------------
# CRUD service functions
# ---------------------------------------------------------------------------

def add_contact(full_name: str, phone: str, email: str = "",
                address: str = "", notes: str = "",
                is_favourite: bool = False,
                is_emergency: bool = False) -> Tuple[bool, str]:
    """
    Validate and insert a new contact.
    Returns (True, success_message) or (False, error_message).
    """
    # 1. Validate inputs
    ok, msg = validate_contact(full_name, phone, email)
    if not ok:
        return False, msg

    # 2. Duplicate check
    if db.check_duplicate(full_name.strip(), phone.strip()):
        return False, "A contact with the same name and phone number already exists."

    # 3. Insert
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
        return True, f"Contact '{full_name.strip()}' added successfully (ID: {new_id})."
    except Exception as e:
        return False, f"Database error: {e}"


def edit_contact(contact_id: int, full_name: str, phone: str,
                 email: str = "", address: str = "", notes: str = "",
                 is_favourite: bool = False,
                 is_emergency: bool = False) -> Tuple[bool, str]:
    """
    Validate and update an existing contact.
    Returns (True, success_message) or (False, error_message).
    """
    ok, msg = validate_contact(full_name, phone, email)
    if not ok:
        return False, msg

    if db.check_duplicate(full_name.strip(), phone.strip(),
                          exclude_id=contact_id):
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
        if updated:
            return True, f"Contact '{full_name.strip()}' updated successfully."
        return False, "Contact not found in the database."
    except Exception as e:
        return False, f"Database error: {e}"


def remove_contact(contact_id: int) -> Tuple[bool, str]:
    """
    Delete a contact by id.
    Returns (True, success_message) or (False, error_message).
    """
    try:
        deleted = db.delete_contact(contact_id)
        if deleted:
            return True, "Contact deleted successfully."
        return False, "Contact not found."
    except Exception as e:
        return False, f"Database error: {e}"


def fetch_all_contacts() -> list[Contact]:
    """Return all contacts as Contact objects."""
    rows = db.get_all_contacts()
    return [Contact.from_row(r) for r in rows]


def fetch_contact(contact_id: int) -> Optional[Contact]:
    """Return a single Contact by id, or None."""
    row = db.get_contact_by_id(contact_id)
    return Contact.from_row(row) if row else None


def search_contacts(query: str) -> list[Contact]:
    """Search contacts and return matching Contact objects."""
    if not query.strip():
        return fetch_all_contacts()
    rows = db.search_contacts(query.strip())
    return [Contact.from_row(r) for r in rows]


def get_dashboard_stats() -> dict:
    """Return summary statistics for the dashboard."""
    return {
        "total":     db.get_contact_count(),
        "favourites": db.get_favourite_count(),
        "emergency": db.get_emergency_count(),
    }
