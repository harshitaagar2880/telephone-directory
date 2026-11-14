# HANDOFF.md — Smart Contact Manager

> **For the next AI agent continuing this project.**
> Read this file first. Parts 1, 2, 3, and 4 are fully completed, tested, and operational.
> Do NOT rewrite or modify working features. Follow the guidelines below for any future work.

---

## Project Overview

**Smart Contact Manager** is an offline-first desktop contact management system built for a college project.
- Language: Python 3.10+ (Tested on Python 3.14.7)
- GUI: Tkinter + ttk (using standard library)
- Database: SQLite via Python's built-in `sqlite3` module
- Architecture: Modular MVC-like separation (database, models, services, gui)
- Platform: Windows 10/11 offline desktop application

**Entry point:** `python main.py` (run from `smart_contact_manager/`)
**Automated test runner:** `python test_suite.py` (runs all 19 integration test modules)

---

## Current Folder Structure

```
Contacts/                           ← Root project folder
├── _backup_original/               ← Original text-file app backup (PRESERVED)
│   ├── index.py
│   ├── numbers.txt
│   └── README.md
├── index.py                        ← Original entry point (preserved)
├── numbers.txt                     ← Original data file (preserved)
├── README.md                       ← Original readme (preserved)
└── smart_contact_manager/          ← Application Directory
    ├── main.py                     ← Application entry point
    ├── test_suite.py               ← Comprehensive 15-module automated test suite
    ├── contacts.db                 ← SQLite database (auto-initialized & seeded)
    ├── _pre_restore_backup/        ← Automatic pre-restore safety snapshots
    ├── requirements.txt            ← Dependency specification
    ├── README.md                   ← User & college documentation
    ├── PROJECT_PLAN.md             ← Multi-phase roadmap
    ├── TASKS.md                    ← Task checklist
    ├── HANDOFF.md                  ← This handoff guide
    ├── database/
    │   ├── __init__.py
    │   ├── connection.py           ← get_connection(), initialize_database() + group seeding
    │   └── queries.py              ← Parameterised CRUD for contacts, phones, groups, contact_groups
    ├── models/
    │   ├── __init__.py
    │   └── contact.py              ← Contact, PhoneNumber, Group dataclasses
    ├── services/
    │   ├── __init__.py
    │   ├── contact_service.py      ← Validation, duplicate check, CRUD, filters, group logic
    │   └── data_service.py         ← CSV export, CSV import, SQLite backup, SQLite restore
    ├── gui/
    │   ├── __init__.py
    │   ├── app_window.py           ← Root Tk window + 8-item sidebar navigation
    │   ├── theme.py                ← Visual styling, Light/Dark themes, accent colours
    │   ├── widgets.py              ← LabelledEntry, LabelledText, make_button, StatCard
    │   ├── contact_form.py         ← Modal form with dynamic phone rows & group checkboxes
    │   └── pages/
    │       ├── __init__.py
    │       ├── dashboard_page.py   ← 5 Stat cards + Recently added/updated & Recently Viewed tabs
    │       ├── contacts_page.py    ← All contacts list, search, filters, detail panel, quick export/import
    │       ├── favourites_page.py  ← Dedicated favourites page with instant unfavourite
    │       ├── emergency_page.py   ← Dedicated emergency page with dial-ready phone display
    │       ├── groups_page.py      ← Dedicated custom groups management + group members
    │       ├── speed_dial_page.py  ← Dedicated Speed Dial page (slots 1-9)
    │       ├── trash_page.py       ← Trash / Recycle Bin: restore or permanently delete
    │       └── data_page.py        ← Dedicated Backup & Data page (CSV & SQLite tools)
    └── assets/                     ← Assets folder for future icons/images
```

---

## Database Schema (Complete)

All foreign keys use `ON DELETE CASCADE`. Foreign key constraints are enforced with `PRAGMA foreign_keys = ON`.

### 1. Table: `contacts`
| Column        | Type    | Constraints                        | Description                           |
|---------------|---------|------------------------------------|---------------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT          | Unique contact ID                     |
| full_name     | TEXT    | NOT NULL                           | Contact's full name                   |
| phone         | TEXT    | NOT NULL                           | Primary phone number                  |
| email         | TEXT    | DEFAULT ''                         | Email address                         |
| address       | TEXT    | DEFAULT ''                         | Physical address                      |
| notes         | TEXT    | DEFAULT ''                         | Additional notes                      |
| is_favourite  | INTEGER | DEFAULT 0                          | 0 = No, 1 = Yes                       |
| is_emergency  | INTEGER | DEFAULT 0                          | 0 = No, 1 = Yes                       |
| created_at    | TEXT    | DEFAULT (datetime('now','localtime')) | Creation timestamp                 |
| updated_at    | TEXT    | DEFAULT (datetime('now','localtime')) | Last updated timestamp             |

### 2. Table: `phone_numbers`
| Column     | Type    | Constraints                        | Description                           |
|------------|---------|------------------------------------|---------------------------------------|
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT          | Unique phone record ID                |
| contact_id | INTEGER | FK -> contacts(id) ON DELETE CASCADE | Associated contact                  |
| label      | TEXT    | DEFAULT 'Mobile'                   | Personal, Work, Home, Other           |
| number     | TEXT    | NOT NULL                           | Secondary phone number string         |

### 3. Table: `groups`
| Column | Type    | Constraints             | Description                           |
|--------|---------|-------------------------|---------------------------------------|
| id     | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique group ID                     |
| name   | TEXT    | NOT NULL UNIQUE         | Group name (e.g. Family, Friends)    |
| color  | TEXT    | DEFAULT '#4A90D9'       | Hex color code for badges             |

*Default seeded groups:* `Family` (`#E67E22`), `Friends` (`#2ECC71`), `Work` (`#3498DB`), `College` (`#9B59B6`).

### 4. Table: `contact_groups` (Many-to-Many)
| Column     | Type    | Constraints                                                   |
|------------|---------|---------------------------------------------------------------|
| contact_id | INTEGER | NOT NULL, FK -> contacts(id) ON DELETE CASCADE                |
| group_id   | INTEGER | NOT NULL, FK -> groups(id) ON DELETE CASCADE                  |
| PRIMARY KEY|         | (contact_id, group_id)                                        |

*Deletion safety:* When a group is deleted, only records in `contact_groups` are cascade-deleted. Contacts in the `contacts` table remain intact.

### 5. Table: `contacts` — Soft-Delete Columns (Part 4B)
| Column | Type    | Constraints             | Description                           |
|--------|---------|-------------------------|---------------------------------------|
| is_deleted | INTEGER | DEFAULT 0              | 0 = active, 1 = moved to Trash       |
| deleted_at | TEXT    | DEFAULT NULL            | Timestamp when contact was trashed   |

*Soft-delete behaviour:* Deleting a contact sets `is_deleted = 1` instead of removing the row. Related `phone_numbers` and `contact_groups` are preserved. Use `restore_contact()` to un-delete or `purge_contact()` for permanent removal.

### 6. Table: `settings` (Part 4A — Themes & Personalization)
| Column | Type    | Constraints         | Description                           |
|--------|---------|---------------------|---------------------------------------|
| key    | TEXT    | PRIMARY KEY         | Setting key (e.g. 'theme', 'accent')  |
| value  | TEXT    | NOT NULL            | Setting value (e.g. 'dark', 'green')  |

*Usage:* `get_setting(key, default)` / `set_setting(key, value)` in `database/queries.py`.

---

## Completed Features (Parts 1, 2, 3, and 4)

| Feature | Scope | Status | File Location |
|---------|-------|--------|---------------|
| Database Connection & Schema | Part 1 | ✅ | `database/connection.py` |
| Contact CRUD Operations | Part 1 | ✅ | `database/queries.py` |
| Parameterised SQL Queries | Part 1 | ✅ | `database/queries.py` |
| Contact Data Models | Part 1 & 2 | ✅ | `models/contact.py` |
| Regex Input Validation | Part 1 & 2 | ✅ | `services/contact_service.py` |
| Duplicate Contact Prevention | Part 1 | ✅ | `services/contact_service.py` |
| Add / View / Edit / Delete Contact | Part 1 | ✅ | `gui/contact_form.py`, `contacts_page.py` |
| Search (Name, Email, Primary & Secondary Phones) | Part 1 & 2 | ✅ | `database/queries.py`, `contacts_page.py` |
| Multiple Phone Numbers per Contact | Part 2 | ✅ | `contact_form.py`, `services/contact_service.py` |
| Dynamic Phone Row Addition & Removal | Part 2 | ✅ | `gui/contact_form.py` |
| Display Secondary Phones in Details | Part 2 | ✅ | `contacts_page.py`, `favourites_page.py`, `emergency_page.py` |
| Favourite Contacts Page | Part 2 | ✅ | `gui/pages/favourites_page.py` |
| Emergency Contacts Page | Part 2 | ✅ | `gui/pages/emergency_page.py` |
| Custom Contact Groups (CRUD & Safe Deletion) | Part 2 | ✅ | `gui/pages/groups_page.py` |
| Quick Filters (All, Favourites, Emergency) | Part 2 | ✅ | `gui/pages/contacts_page.py` |
| Dashboard Stat Cards & Recent Contacts | Part 2 | ✅ | `gui/pages/dashboard_page.py` |
| CSV Export with full details | Part 3 | ✅ | `services/data_service.py` |
| CSV Import with Validation & Duplicate Skip | Part 3 | ✅ | `services/data_service.py` |
| CSV Import Detailed Modal Summary | Part 3 | ✅ | `gui/pages/data_page.py` |
| Database Backup using `sqlite3.backup` API | Part 3 | ✅ | `services/data_service.py` |
| Database Restore with Pre-restore Safety Snapshot | Part 3 | ✅ | `services/data_service.py` |
| Backup File Integrity Verification (`PRAGMA integrity_check`) | Part 3 | ✅ | `services/data_service.py` |
| Dedicated Data Management & Backup Page | Part 3 | ✅ | `gui/pages/data_page.py` |
| Quick Export & Import Buttons on Contacts Page | Part 3 | ✅ | `gui/pages/contacts_page.py` |
| Global Data Synchronization (`_refresh_all_pages`) | Part 3 | ✅ | `gui/app_window.py` |
| Light / Dark Theme Toggle | Part 4A | ✅ | `gui/theme.py`, `gui/app_window.py` |
| Accent Colour Options (blue, green, purple, orange, red, teal) | Part 4A | ✅ | `gui/theme.py` |
| Theme & Accent Persistence (settings table) | Part 4A | ✅ | `database/queries.py`, `services/contact_service.py` |
| Theme Switch Button in Sidebar | Part 4A | ✅ | `gui/app_window.py` |
| Soft-Delete / Move to Trash | Part 4B | ✅ | `database/queries.py`, `services/contact_service.py` |
| Dedicated Trash Page | Part 4B | ✅ | `gui/pages/trash_page.py` |
| Restore from Trash (preserves phones, groups, fav/emergency) | Part 4B | ✅ | `services/contact_service.py`, `gui/pages/trash_page.py` |
| Permanent Delete from Trash (with confirmation) | Part 4B | ✅ | `services/contact_service.py`, `gui/pages/trash_page.py` |
| Duplicate Conflict Handling on Restore | Part 4B | ✅ | `gui/pages/trash_page.py` |

---

## Files Created or Modified in Part 4 (Themes + Recycle Bin)

### New files:
- `gui/pages/trash_page.py` *(NEW)*: Trash / Recycle Bin page — view trashed contacts, restore, or permanently delete with confirmation.
- `test_trash_theme.py` *(TEMP, deleted)*: Manual verification script (removed after testing).

### Modified files:
- `database/connection.py`: Added `is_deleted` and `deleted_at` columns to `contacts` table (via safe ALTER TABLE); added `settings` table for theme/accent persistence.
- `database/queries.py`: Changed `delete_contact` to soft-delete; added `purge_contact`, `restore_contact`, `get_trashed_contacts`; added `get_setting`/`set_setting`; updated all read queries to filter `is_deleted = 0`.
- `services/contact_service.py`: `remove_contact` now soft-deletes; added `purge_contact`, `restore_contact`, `fetch_trashed_contacts`, `check_duplicate` wrapper, `get_setting`/`set_setting`.
- `gui/theme.py`: Split `COLORS` into `LIGHT_COLORS` / `DARK_COLORS`; added `ACCENT_COLORS` (6 options); added `apply_theme()`, `set_accent_color()`, `get_current_theme()`, `get_current_accent()`.
- `gui/app_window.py`: Loads saved theme/accent on startup; added 🌓 "Switch Theme" button in sidebar; added Trash page to navigation (8 items total); `_toggle_theme()` persists choice.
- `gui/pages/contacts_page.py`: Delete confirmation now says "Move to Trash" instead of permanent delete.
- `gui/pages/favourites_page.py`: Delete confirmation updated for Trash behaviour.
- `gui/pages/emergency_page.py`: Delete confirmation updated for Trash behaviour.
- `TASKS.md`, `README.md`, `HANDOFF.md`: Full documentation update.

---

## Known Bugs / Limitations

None. All 19 automated test modules pass cleanly.

### Design notes for future development:
1. **Theme changes require page refresh:** Switching themes calls `_refresh_all_pages()` which rebuilds all page widgets. This is by design — Tkinter widgets don't dynamically restyle when `COLORS` dict changes.
2. **Soft-delete preserves data:** Deleted contacts keep phone numbers and group memberships. If a contact is restored and a duplicate (same name+phone) now exists, the user is prompted to confirm restore-anyway.
3. **Permanent delete is irreversible:** `purge_contact()` hard-deletes the row and cascades to `phone_numbers` and `contact_groups`.

---

## How to Run

```bash
cd "c:\Users\Harshita\OneDrive\Desktop\Contacts\smart_contact_manager"
python main.py
```

To run the automated test suite:
```bash
python test_suite.py
```
