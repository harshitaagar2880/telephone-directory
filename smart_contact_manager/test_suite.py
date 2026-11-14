"""
test_suite.py
--------------
Automated test suite verifying Part 1, Part 2, and Part 3 functionality.
Tests CRUD, secondary phones, groups, search, CSV export, CSV import,
database backup, database restore, and GUI instantiation.
"""

import sys
import os
import csv
import tkinter as tk

# Ensure current directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.connection import initialize_database, get_connection
initialize_database()

# Clean DB for fresh test run
conn = get_connection()
conn.execute('DELETE FROM contacts')
conn.execute('DELETE FROM groups')
conn.commit()
conn.close()
initialize_database()

from services import contact_service as cs
from services import data_service as ds

print("=== STARTING SMART CONTACT MANAGER COMPREHENSIVE TEST SUITE ===")

# --- Test 1: Groups Seeding ---
groups = cs.fetch_all_groups()
grp_names = [g["name"] for g in groups]
print(f"[1] Default groups seeded: {grp_names}")
assert len(groups) >= 4, "Should have at least 4 default groups"

# --- Test 2: Custom Group Creation & Editing ---
ok, msg = cs.create_group("Project Alpha", "#34495E")
assert ok, f"Failed to create group: {msg}"
alpha_grp = [g for g in cs.fetch_all_groups() if g["name"] == "Project Alpha"][0]

ok, msg = cs.edit_group(alpha_grp["id"], "Alpha Team", "#1ABC9C")
assert ok, f"Failed to edit group: {msg}"
alpha_grp = [g for g in cs.fetch_all_groups() if g["name"] == "Alpha Team"][0]
print("[2] Group created and edited to 'Alpha Team': PASS")

# --- Test 3: Add Contact with Multiple Numbers and Multiple Groups ---
extra_nums = [("Work", "+91 22 26543210"), ("Home", "022-28765432")]
college_grp = [g for g in cs.fetch_all_groups() if g["name"] == "College"][0]
assigned_group_ids = [alpha_grp["id"], college_grp["id"]]

ok, msg = cs.add_contact(
    full_name="Aarav Sharma",
    phone="+91 98199 88776",
    email="aarav@college.edu",
    address="Bandra West, Mumbai",
    notes="Campus lead",
    is_favourite=True,
    is_emergency=False,
    extra_phones=extra_nums,
    group_ids=assigned_group_ids
)
assert ok, f"Add contact failed: {msg}"

contacts = cs.fetch_all_contacts()
assert len(contacts) == 1
aarav = contacts[0]
assert len(aarav.extra_phones) == 2, "Should have 2 secondary phone numbers"
assert len(aarav.groups) == 2, "Should belong to 2 groups"
print("[3] Add Contact with multiple numbers and multiple groups: PASS")

# --- Test 4: Search by secondary phone numbers ---
res_work = cs.search_contacts("26543210")
assert len(res_work) == 1 and res_work[0].id == aarav.id, "Search by secondary work number failed"

res_home = cs.search_contacts("28765432")
assert len(res_home) == 1 and res_home[0].id == aarav.id, "Search by secondary home number failed"

res_name = cs.search_contacts("aarav")
assert len(res_name) == 1
print("[4] Search across primary phone, secondary phone numbers, and name: PASS")

# --- Test 5: Favourites Management ---
favs = cs.fetch_favourite_contacts()
assert len(favs) == 1 and favs[0].id == aarav.id

# Unmark favourite
ok, msg = cs.toggle_favourite(aarav.id, False)
assert ok
assert len(cs.fetch_favourite_contacts()) == 0

# Mark favourite again
ok, msg = cs.toggle_favourite(aarav.id, True)
assert ok
assert len(cs.fetch_favourite_contacts()) == 1
print("[5] Favourites toggle & list: PASS")

# --- Test 6: Emergency Contacts Management ---
emers = cs.fetch_emergency_contacts()
assert len(emers) == 0

# Mark emergency
ok, msg = cs.toggle_emergency(aarav.id, True)
assert ok
emers = cs.fetch_emergency_contacts()
assert len(emers) == 1 and emers[0].id == aarav.id

# Unmark emergency
ok, msg = cs.toggle_emergency(aarav.id, False)
assert ok
assert len(cs.fetch_emergency_contacts()) == 0
print("[6] Emergency contacts toggle & list: PASS")

# --- Test 7: Edit Contact and update secondary numbers / groups ---
updated_extras = [("Work", "+91 22 99998888")]
ok, msg = cs.edit_contact(
    contact_id=aarav.id,
    full_name="Aarav Sharma Updated",
    phone="+91 98199 88776",
    email="aarav.new@college.edu",
    is_favourite=True,
    is_emergency=False,
    extra_phones=updated_extras,
    group_ids=[alpha_grp["id"]]
)
assert ok, f"Edit failed: {msg}"

aarav_updated = cs.fetch_contact(aarav.id)
assert aarav_updated.full_name == "Aarav Sharma Updated"
assert len(aarav_updated.extra_phones) == 1
assert aarav_updated.extra_phones[0]["number"] == "+91 22 99998888"
assert len(aarav_updated.groups) == 1
assert aarav_updated.groups[0]["name"] == "Alpha Team"
print("[7] Edit Contact (numbers and groups updated): PASS")

# --- Test 8: Safe Group Deletion (Contacts must NOT be deleted) ---
ok, msg = cs.delete_group(alpha_grp["id"])
assert ok
remaining_contacts = cs.fetch_all_contacts()
assert len(remaining_contacts) == 1, "Contact must not be deleted when its group is deleted"
aarav_after_grp_del = cs.fetch_contact(aarav.id)
assert len(aarav_after_grp_del.groups) == 0, "Group association removed cleanly"
print("[8] Safe group deletion preserving contacts: PASS")

# --- Test 9: Add second contact, test duplicate checks, and test group membership ---
ok, msg = cs.add_contact(
    full_name="Priya Patel",
    phone="+91 98200 55443",
    email="priya@example.com",
    is_favourite=True,
    is_emergency=True,
    group_ids=[college_grp["id"]]
)
assert ok

# Duplicate check
dup_check = cs.add_contact("Priya Patel", "+91 98200 55443")
assert not dup_check[0], "Should prevent duplicate contact"

# Test contacts by group
college_contacts = cs.fetch_contacts_by_group(college_grp["id"])
assert len(college_contacts) == 1 and college_contacts[0].full_name == "Priya Patel"
print("[9] Duplicate validation and contacts-by-group: PASS")

# --- Test 10: Dashboard statistics ---
stats = cs.get_dashboard_stats()
print(f"[10] Dashboard stats: {stats}")
assert stats["total"] == 2
assert stats["favourites"] == 2
assert stats["emergency"] == 1
assert stats["groups"] >= 4

# ===================================================================
# PART 3 TESTS: CSV EXPORT, CSV IMPORT, BACKUP, RESTORE
# ===================================================================

# --- Test 11: CSV Export ---
test_export_path = os.path.join(os.path.dirname(__file__), "test_contacts_export.csv")
ok, msg, count = ds.export_contacts_to_csv(test_export_path)
assert ok, f"Export failed: {msg}"
assert count == 2, f"Expected 2 exported contacts, got {count}"
assert os.path.exists(test_export_path), "Export file should exist"

# Verify CSV content
with open(test_export_path, mode="r", encoding="utf-8-sig") as f:
    reader = csv.reader(f)
    header = next(reader)
    assert header == ds.CSV_HEADERS, "CSV headers do not match expected schema"
    rows = list(reader)
    assert len(rows) == 2, f"Expected 2 CSV rows, got {len(rows)}"
print(f"[11] CSV Export ({count} contacts): PASS")

# --- Test 12: CSV Import ---
test_import_path = os.path.join(os.path.dirname(__file__), "test_contacts_import.csv")
with open(test_import_path, mode="w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(ds.CSV_HEADERS)
    # Row 1: Brand new contact with secondary phone & groups
    writer.writerow([
        "Rohan Gupta", "+91 98333 44556", "Work: 022-24354657; Home: +91 98111 22334",
        "rohan@test.com", "Andheri, Mumbai", "Project manager", "Yes", "No", "Work, TechLead"
    ])
    # Row 2: Duplicate of Priya Patel (should be skipped)
    writer.writerow([
        "Priya Patel", "+91 98200 55443", "", "priya@example.com", "", "", "No", "No", ""
    ])
    # Row 3: Invalid row (invalid phone format)
    writer.writerow([
        "Invalid Contact", "not-a-number", "", "", "", "", "No", "No", ""
    ])

summary = ds.import_contacts_from_csv(test_import_path)
print(f"[12] Import summary: {summary}")
assert summary["total"] == 3, f"Expected 3 processed rows, got {summary['total']}"
assert summary["imported"] == 1, f"Expected 1 imported contact, got {summary['imported']}"
assert summary["skipped"] == 1, f"Expected 1 duplicate skipped, got {summary['skipped']}"
assert summary["failed"] == 1, f"Expected 1 invalid row failed, got {summary['failed']}"

# Verify Rohan was added properly
rohan_list = cs.search_contacts("Rohan Gupta")
assert len(rohan_list) == 1
rohan = rohan_list[0]
assert len(rohan.extra_phones) == 2, "Rohan should have 2 imported extra phones"
assert any(g["name"] == "TechLead" for g in rohan.groups), "TechLead group should be created and assigned"
print("[12] CSV Import (validation, duplicates, secondary phones, auto-groups): PASS")

# Clean temp CSV files
if os.path.exists(test_export_path):
    os.remove(test_export_path)
if os.path.exists(test_import_path):
    os.remove(test_import_path)

# --- Test 13: Database Backup ---
test_backup_path = os.path.join(os.path.dirname(__file__), "test_backup.db")
if os.path.exists(test_backup_path):
    os.remove(test_backup_path)

ok, msg = ds.create_database_backup(test_backup_path)
assert ok, f"Backup creation failed: {msg}"
assert os.path.exists(test_backup_path), "Backup database file should exist"
assert os.path.getsize(test_backup_path) > 0, "Backup file should not be empty"

# Verify backup integrity
valid, verify_msg = ds.verify_backup_file(test_backup_path)
assert valid, f"Backup verification failed: {verify_msg}"
print(f"[13] Database Backup & Integrity Check: PASS")

# --- Test 14: Database Restore ---
# First, delete all contacts to simulate data loss
conn = get_connection()
conn.execute("DELETE FROM contacts")
conn.commit()
conn.close()
assert len(cs.fetch_all_contacts()) == 0, "Contacts should be empty before restore"

# Now restore from backup
ok, restore_msg = ds.restore_database_from_backup(test_backup_path)
assert ok, f"Database restore failed: {restore_msg}"

# Verify contacts are restored completely
restored_contacts = cs.fetch_all_contacts()
assert len(restored_contacts) == 3, f"Expected 3 restored contacts, got {len(restored_contacts)}"
names = {c.full_name for c in restored_contacts}
assert "Aarav Sharma Updated" in names
assert "Priya Patel" in names
assert "Rohan Gupta" in names

# Clean temp backup
if os.path.exists(test_backup_path):
    os.remove(test_backup_path)
print("[14] Database Restore & Data Preservation: PASS")

# --- Test 15: All 6 GUI Pages Instantiation ---
root = tk.Tk()
root.withdraw()
from gui.app_window import AppWindow
app = AppWindow()
pages = ["dashboard", "contacts", "favourites", "emergency", "groups", "data"]
for p in pages:
    app._show_page(p)
app.destroy()
root.destroy()
print(f"[15] All 6 GUI pages loaded and navigated cleanly: PASS")

# Clean test data from DB so it's fresh for the user
conn = get_connection()
conn.execute("DELETE FROM contacts")
conn.commit()
conn.close()

print("=== ALL 15 TEST MODULES PASSED SUCCESSFULLY! ===")
