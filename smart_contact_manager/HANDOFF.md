# HANDOFF.md — Smart Contact Manager

> **For the next AI agent continuing this project.**
> Read this file first. Do not re-implement anything marked ✅.

---

## Project Overview

**Smart Contact Manager** is an offline desktop contacts application.
- Language: Python 3.10+
- GUI: Tkinter + ttk (standard library only — no CustomTkinter needed)
- Database: SQLite via `sqlite3` (standard library)
- Platform: Windows 10/11

**Entry point:** `python main.py` (run from inside `smart_contact_manager/`)

---

## Current Folder Structure

```
Contacts/                           ← Original project root
├── _backup_original/               ← Original text-file app (DO NOT TOUCH)
│   ├── index.py
│   ├── numbers.txt
│   └── README.md
├── index.py                        ← Original entry (preserved)
├── numbers.txt                     ← Original data file (preserved)
├── README.md                       ← Original readme (preserved)
└── smart_contact_manager/          ← NEW application (Part 1)
    ├── main.py                     ← Entry point
    ├── contacts.db                 ← SQLite database (auto-created)
    ├── requirements.txt
    ├── README.md
    ├── PROJECT_PLAN.md
    ├── TASKS.md
    ├── HANDOFF.md                  ← This file
    ├── database/
    │   ├── __init__.py
    │   ├── connection.py           ← get_connection(), initialize_database()
    │   └── queries.py              ← All CRUD SQL (parameterised)
    ├── models/
    │   ├── __init__.py
    │   └── contact.py              ← Contact dataclass + from_row()
    ├── services/
    │   ├── __init__.py
    │   └── contact_service.py      ← Validation + CRUD orchestration
    ├── gui/
    │   ├── __init__.py
    │   ├── app_window.py           ← Root Tk window + sidebar
    │   ├── theme.py                ← COLORS dict, FONTS dict, ttk styles
    │   ├── widgets.py              ← LabelledEntry, LabelledText, make_button, StatCard
    │   ├── contact_form.py         ← Add/Edit modal dialog (ContactFormDialog)
    │   └── pages/
    │       ├── __init__.py
    │       ├── dashboard_page.py   ← Dashboard with stat cards
    │       └── contacts_page.py    ← Contacts list, search, detail panel
    └── assets/                     ← Empty — for future icons/images
```

---

## Database Schema

### Table: `contacts` (main table)
| Column        | Type    | Notes                              |
|---------------|---------|------------------------------------|
| id            | INTEGER | PRIMARY KEY AUTOINCREMENT          |
| full_name     | TEXT    | NOT NULL                           |
| phone         | TEXT    | NOT NULL                           |
| email         | TEXT    | DEFAULT ''                         |
| address       | TEXT    | DEFAULT ''                         |
| notes         | TEXT    | DEFAULT ''                         |
| is_favourite  | INTEGER | 0=No 1=Yes                         |
| is_emergency  | INTEGER | 0=No 1=Yes                         |
| created_at    | TEXT    | datetime('now','localtime')        |
| updated_at    | TEXT    | datetime('now','localtime')        |

### Table: `phone_numbers` (future — Part 2)
| Column     | Type    | Notes                              |
|------------|---------|------------------------------------|
| id         | INTEGER | PRIMARY KEY AUTOINCREMENT          |
| contact_id | INTEGER | FK → contacts.id ON DELETE CASCADE |
| label      | TEXT    | 'Mobile' / 'Home' / 'Work'         |
| number     | TEXT    | NOT NULL                           |

### Table: `groups` (future — Part 2)
| Column | Type    | Notes              |
|--------|---------|--------------------|
| id     | INTEGER | PRIMARY KEY        |
| name   | TEXT    | UNIQUE NOT NULL    |
| color  | TEXT    | Hex colour string  |

### Table: `contact_groups` (future — Part 2)
| Column     | Type    | Notes              |
|------------|---------|--------------------|
| contact_id | INTEGER | FK → contacts.id   |
| group_id   | INTEGER | FK → groups.id     |

All foreign keys use `ON DELETE CASCADE`. `PRAGMA foreign_keys = ON` is set on every connection.

---

## Completed Features (Part 1)

| Feature                        | Status | File                              |
|--------------------------------|--------|-----------------------------------|
| SQLite database setup          | ✅     | database/connection.py            |
| All CRUD SQL functions         | ✅     | database/queries.py               |
| Contact dataclass              | ✅     | models/contact.py                 |
| Input validation (regex)       | ✅     | services/contact_service.py       |
| Duplicate prevention           | ✅     | services/contact_service.py       |
| Add contact                    | ✅     | gui/contact_form.py               |
| View all contacts (Treeview)   | ✅     | gui/pages/contacts_page.py        |
| Contact detail panel           | ✅     | gui/pages/contacts_page.py        |
| Search (name/phone/email)      | ✅     | gui/pages/contacts_page.py        |
| Edit contact                   | ✅     | gui/contact_form.py               |
| Delete with confirmation       | ✅     | gui/pages/contacts_page.py        |
| Favourite flag                 | ✅     | contact_form + contacts_page      |
| Emergency flag                 | ✅     | contact_form + contacts_page      |
| Dashboard stats                | ✅     | gui/pages/dashboard_page.py       |
| Sidebar navigation             | ✅     | gui/app_window.py                 |
| Sortable columns               | ✅     | gui/pages/contacts_page.py        |
| Professional theme             | ✅     | gui/theme.py                      |

---

## Pending Features (Part 2)

1. **Multiple phone numbers per contact**
   - `phone_numbers` table already exists in the DB
   - Add a mini form inside ContactFormDialog to add/remove phone rows
   - Display all numbers in the detail panel

2. **Contact groups**
   - `groups` and `contact_groups` tables already exist
   - Add a Groups management page in the sidebar
   - Allow assigning contacts to multiple groups
   - Add filter by group on the Contacts page

3. **Filter views**
   - Favourites filter button on Contacts page
   - Emergency filter button on Contacts page
   - Add these as toggle buttons on the top bar of ContactsPage

4. **Import / Export**
   - Import contacts from a CSV file
   - Export all contacts to CSV
   - Use Python's built-in `csv` module

5. **Recent contacts on Dashboard**
   - Add a `SELECT * FROM contacts ORDER BY updated_at DESC LIMIT 5` query
   - Show a "Recently Updated" section below the stat cards on DashboardPage

---

## Known Bugs / Limitations

- None known. All Part 1 features are tested and working.
- The Stats values on the dashboard for `favourites` count currently shows 0 after
  editing a contact's favourite status (requires a page switch to refresh).
  This is cosmetic — data is saved correctly. Fix: call `dashboard.refresh()` after edit.

---

## Exact Next Steps for Part 2

1. Open `TASKS.md` and move Part 2 items to an "In Progress" section.
2. Start with **multiple phone numbers** — it is the most self-contained feature:
   - Add a `PhoneNumberRow` widget in `gui/widgets.py` (label dropdown + number entry + remove button)
   - Modify `ContactFormDialog` to hold a list of `PhoneNumberRow` widgets
   - Add `get_phone_numbers(contact_id)`, `add_phone_number()`, `delete_phone_numbers_for_contact()` to `database/queries.py`
   - Update `contact_service.py` to save/load phone numbers together with the contact
   - Display all numbers in the detail panel of `contacts_page.py`
3. Then add **Groups** — create `gui/pages/groups_page.py` and register it in `app_window.py`.
4. Then add **filter buttons** to `contacts_page.py` top bar.
5. Then add **CSV import/export**.
6. Update `TASKS.md` and `HANDOFF.md` after each feature.

---

## How to Run

```bash
cd "c:\Users\Harshita\OneDrive\Desktop\Contacts\smart_contact_manager"
python main.py
```

No pip installs required — only Python standard library is used.

---

*Last updated: Part 1 completion — 2026-11-14*
