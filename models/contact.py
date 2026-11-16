"""
models/contact.py
-----------------
Data class representing a contact, along with helper types for
phone numbers and contact groups.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
import sqlite3


@dataclass
class PhoneNumber:
    id: Optional[int] = None
    contact_id: Optional[int] = None
    label: str = "Personal"
    number: str = ""


@dataclass
class Group:
    id: Optional[int] = None
    name: str = ""
    color: str = "#4A90D9"
    contact_count: int = 0


@dataclass
class Contact:
    """Represents a contact record with its associated phones and groups."""
    id:           Optional[int] = None
    full_name:    str           = ""
    phone:        str           = ""
    email:        str           = ""
    address:      str           = ""
    notes:        str           = ""
    is_favourite: bool          = False
    is_emergency: bool          = False
    created_at:   str           = ""
    updated_at:   str           = ""
    extra_phones: List[Dict[str, Any]] = field(default_factory=list)
    groups:       List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_row(cls, row: sqlite3.Row,
                 extra_phones: Optional[List[Dict[str, Any]]] = None,
                 groups: Optional[List[Dict[str, Any]]] = None) -> "Contact":
        """
        Build a Contact from a sqlite3.Row returned by a query.
        """
        return cls(
            id           = row["id"],
            full_name    = row["full_name"],
            phone        = row["phone"],
            email        = row["email"]        or "",
            address      = row["address"]      or "",
            notes        = row["notes"]        or "",
            is_favourite = bool(row["is_favourite"]),
            is_emergency = bool(row["is_emergency"]),
            created_at   = row["created_at"]   or "",
            updated_at   = row["updated_at"]   or "",
            extra_phones = extra_phones or [],
            groups       = groups or [],
        )
