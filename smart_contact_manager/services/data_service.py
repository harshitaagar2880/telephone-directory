"""
services/data_service.py
-------------------------
Handles CSV Import, CSV Export, SQLite Database Backup, and Database Restore.
Ensures data consistency, duplicate handling, input validation, and safety snapshots.
"""

import os
import csv
import sqlite3
import datetime
from typing import Tuple, List, Dict, Any, Optional

from database.connection import DB_PATH, get_connection
from services.contact_service import (
    fetch_all_contacts, add_contact, validate_contact, fetch_all_groups, create_group
)
import database.queries as db


# ---------------------------------------------------------------------------
# CSV EXPORT
# ---------------------------------------------------------------------------

CSV_HEADERS = [
    "Full Name",
    "Primary Phone",
    "Additional Numbers",
    "Email",
    "Address",
    "Notes",
    "Is Favourite",
    "Is Emergency",
    "Groups"
]


def export_contacts_to_csv(filepath: str) -> Tuple[bool, str, int]:
    """
    Export all contacts to a standard CSV file with utf-8-sig encoding for Excel compatibility.
    Returns (success, message, count).
    """
    try:
        contacts = fetch_all_contacts()
        
        # Ensure parent directory exists
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)

        with open(filepath, mode="w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)

            for c in contacts:
                # Format secondary phone numbers: "Work: +91 98...; Home: 022..."
                extra_str = "; ".join(
                    f"{p['label']}: {p['number']}" for p in c.extra_phones
                ) if c.extra_phones else ""

                # Format groups: "Family, Work"
                groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else ""

                fav_str = "Yes" if c.is_favourite else "No"
                emer_str = "Yes" if c.is_emergency else "No"

                writer.writerow([
                    c.full_name,
                    c.phone,
                    extra_str,
                    c.email,
                    c.address,
                    c.notes,
                    fav_str,
                    emer_str,
                    groups_str
                ])

        return True, f"Successfully exported {len(contacts)} contacts to:\n{filepath}", len(contacts)
    except Exception as e:
        return False, f"Failed to export contacts: {e}", 0


# ---------------------------------------------------------------------------
# CSV IMPORT
# ---------------------------------------------------------------------------

def _parse_extra_phones(extra_str: str) -> List[Tuple[str, str]]:
    """Parse 'Work: +123; Home: 456' or comma/semicolon separated numbers."""
    if not extra_str or not extra_str.strip():
        return []
    
    results = []
    # split by semicolon or newline
    entries = [e.strip() for e in extra_str.replace("\n", ";").split(";") if e.strip()]
    for item in entries:
        if ":" in item:
            parts = item.split(":", 1)
            label = parts[0].strip() or "Other"
            num = parts[1].strip()
        else:
            label = "Other"
            num = item.strip()
        if num:
            results.append((label, num))
    return results


def _resolve_group_ids(groups_str: str, group_cache: Dict[str, int]) -> List[int]:
    """Parse comma-separated group names and return group IDs, creating missing groups automatically."""
    if not groups_str or not groups_str.strip():
        return []
    
    g_ids = []
    names = [n.strip() for n in groups_str.split(",") if n.strip()]
    for name in names:
        lower_name = name.lower()
        if lower_name in group_cache:
            g_ids.append(group_cache[lower_name])
        else:
            # Create the group if it doesn't exist
            ok, msg = create_group(name)
            if ok:
                # Refresh group in cache
                all_g = fetch_all_groups()
                for g in all_g:
                    group_cache[g["name"].lower()] = g["id"]
                if lower_name in group_cache:
                    g_ids.append(group_cache[lower_name])
    return g_ids


def import_contacts_from_csv(filepath: str) -> Dict[str, Any]:
    """
    Import contacts from a CSV file.
    Validates rows, detects duplicates, parses secondary phones and groups.
    Returns a summary dictionary:
        {
            "total": int,
            "imported": int,
            "skipped": int,
            "failed": int,
            "errors": list[str]
        }
    """
    summary = {
        "total": 0,
        "imported": 0,
        "skipped": 0,
        "failed": 0,
        "errors": []
    }

    if not os.path.exists(filepath):
        summary["errors"].append(f"File not found: {filepath}")
        return summary

    # Cache existing groups for rapid name -> id lookup
    existing_groups = fetch_all_groups()
    group_cache: Dict[str, int] = {g["name"].lower(): g["id"] for g in existing_groups}

    try:
        with open(filepath, mode="r", encoding="utf-8-sig", errors="replace") as f:
            reader = csv.reader(f)
            try:
                raw_headers = next(reader)
            except StopIteration:
                summary["errors"].append("The selected CSV file is empty.")
                return summary

            # Normalize headers
            headers = [h.strip().lower().replace("_", " ").replace("-", " ") for h in raw_headers]

            def get_col_idx(*names):
                for n in names:
                    if n in headers:
                        return headers.index(n)
                return -1

            idx_name      = get_col_idx("full name", "name", "contact name")
            idx_phone     = get_col_idx("primary phone", "phone", "mobile", "phone number")
            idx_extra     = get_col_idx("additional numbers", "extra phones", "other numbers", "secondary phones")
            idx_email     = get_col_idx("email", "email address")
            idx_address   = get_col_idx("address", "location")
            idx_notes     = get_col_idx("notes", "note")
            idx_fav       = get_col_idx("is favourite", "favourite", "favorite", "fav")
            idx_emer      = get_col_idx("is emergency", "emergency", "emer")
            idx_groups    = get_col_idx("groups", "group")

            if idx_name == -1 or idx_phone == -1:
                summary["errors"].append("CSV missing required columns: 'Full Name' and 'Phone'.")
                return summary

            row_num = 1
            for row in reader:
                row_num += 1
                if not row or all(c.strip() == "" for c in row):
                    continue

                summary["total"] += 1

                def val(idx):
                    return row[idx].strip() if 0 <= idx < len(row) else ""

                full_name = val(idx_name)
                phone     = val(idx_phone)
                extra_str = val(idx_extra)
                email     = val(idx_email)
                address   = val(idx_address)
                notes     = val(idx_notes)
                fav_str   = val(idx_fav).lower()
                emer_str  = val(idx_emer).lower()
                grp_str   = val(idx_groups)

                is_fav = fav_str in ("yes", "y", "1", "true")
                is_emer = emer_str in ("yes", "y", "1", "true")

                extra_phones = _parse_extra_phones(extra_str)
                group_ids = _resolve_group_ids(grp_str, group_cache)

                # Validation
                ok, err_msg = validate_contact(full_name, phone, email, extra_phones)
                if not ok:
                    summary["failed"] += 1
                    summary["errors"].append(f"Row {row_num} ('{full_name}'): {err_msg}")
                    continue

                # Duplicate check
                if db.check_duplicate(full_name, phone):
                    summary["skipped"] += 1
                    continue

                # Insert contact
                success, add_msg = add_contact(
                    full_name    = full_name,
                    phone        = phone,
                    email        = email,
                    address      = address,
                    notes        = notes,
                    is_favourite = is_fav,
                    is_emergency = is_emer,
                    extra_phones = extra_phones,
                    group_ids    = group_ids
                )

                if success:
                    summary["imported"] += 1
                else:
                    summary["failed"] += 1
                    summary["errors"].append(f"Row {row_num} ('{full_name}'): {add_msg}")

        return summary
    except Exception as e:
        summary["errors"].append(f"Error reading CSV file: {e}")
        return summary


# ---------------------------------------------------------------------------
# DATABASE BACKUP
# ---------------------------------------------------------------------------

def create_database_backup(destination_filepath: str) -> Tuple[bool, str]:
    """
    Create a consistent online SQLite backup of contacts.db using sqlite3.backup API.
    Returns (success, message).
    """
    if not os.path.exists(DB_PATH):
        return False, "Active database file not found."

    try:
        # Ensure target directory exists
        os.makedirs(os.path.dirname(os.path.abspath(destination_filepath)), exist_ok=True)

        src_conn = get_connection()
        dst_conn = sqlite3.connect(destination_filepath)

        with dst_conn:
            src_conn.backup(dst_conn, pages=0)  # copy all pages

        dst_conn.close()
        src_conn.close()

        file_size_kb = os.path.getsize(destination_filepath) / 1024
        return True, f"Backup successfully created at:\n{destination_filepath}\n(Size: {file_size_kb:.1f} KB)"
    except Exception as e:
        return False, f"Failed to create backup: {e}"


def generate_default_backup_filename() -> str:
    """Return a timestamped default backup filename."""
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"contacts_backup_{ts}.db"


# ---------------------------------------------------------------------------
# DATABASE RESTORE
# ---------------------------------------------------------------------------

def verify_backup_file(backup_filepath: str) -> Tuple[bool, str]:
    """
    Verify the integrity of a backup SQLite database file before attempting restore.
    Checks file existence, sqlite magic header, integrity_check, and required tables.
    """
    if not os.path.exists(backup_filepath):
        return False, "Selected backup file does not exist."

    if os.path.getsize(backup_filepath) == 0:
        return False, "The selected file is empty."

    try:
        conn = sqlite3.connect(backup_filepath)
        cursor = conn.cursor()

        # Run SQLite integrity check
        check_row = cursor.execute("PRAGMA integrity_check").fetchone()
        if not check_row or check_row[0] != "ok":
            conn.close()
            return False, f"Database integrity check failed: {check_row[0] if check_row else 'Unknown'}"

        # Verify required tables exist
        tables = [r[0] for r in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]
        required = ["contacts", "phone_numbers", "groups", "contact_groups"]
        missing = [t for t in required if t not in tables]

        conn.close()

        if missing:
            return False, f"Backup file is missing required tables: {', '.join(missing)}"

        return True, "Backup file verified successfully."
    except Exception as e:
        return False, f"Invalid or corrupted backup database: {e}"


def restore_database_from_backup(backup_filepath: str) -> Tuple[bool, str]:
    """
    Safely restore the active database from a backup file.
    Steps:
      1. Verifies candidate backup file integrity.
      2. Creates an automatic safety snapshot of current database before restoring.
      3. Overwrites active database using atomic sqlite3 backup.
    Returns (success, message).
    """
    # 1. Verify backup file
    valid, msg = verify_backup_file(backup_filepath)
    if not valid:
        return False, f"Restore aborted: {msg}"

    # 2. Safety snapshot of current database before overwriting
    pre_restore_dir = os.path.join(os.path.dirname(DB_PATH), "_pre_restore_backup")
    os.makedirs(pre_restore_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    safety_snapshot_path = os.path.join(pre_restore_dir, f"pre_restore_snapshot_{ts}.db")

    try:
        if os.path.exists(DB_PATH):
            create_database_backup(safety_snapshot_path)
    except Exception as e:
        return False, f"Failed to create pre-restore safety snapshot: {e}"

    # 3. Restore using sqlite3 backup API
    try:
        backup_conn = sqlite3.connect(backup_filepath)
        active_conn = sqlite3.connect(DB_PATH)

        with active_conn:
            backup_conn.backup(active_conn, pages=0)

        active_conn.close()
        backup_conn.close()

        return True, (
            "Database restored successfully!\n\n"
            f"Restored from: {os.path.basename(backup_filepath)}\n"
            f"A pre-restore safety snapshot was saved to:\n{safety_snapshot_path}"
        )
    except Exception as e:
        return False, f"Failed during database restoration: {e}"
