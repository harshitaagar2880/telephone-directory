"""
models/contact.py
-----------------
A simple data class that represents a single contact.
Provides a convenient way to pass contact data between layers
without coupling anything to sqlite3.Row objects.
"""

from dataclasses import dataclass, field
from typing import Optional
import sqlite3


@dataclass
class Contact:
    """Represents a contact record."""
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

    @classmethod
    def from_row(cls, row: sqlite3.Row) -> "Contact":
        """
        Build a Contact from a sqlite3.Row returned by a query.
        This keeps the rest of the application independent from sqlite3 types.
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
        )
