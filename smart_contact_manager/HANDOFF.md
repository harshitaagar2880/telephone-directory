# HANDOFF.md — Smart Contact Manager

> **For the next AI agent continuing this project.**
> Read this file first. Both Part 1 and Part 2 are fully completed and tested.
> Do NOT rewrite or modify working features. Follow the exact next steps for Part 3.

---

## Project Overview

**Smart Contact Manager** is an offline-first desktop contact management system built for a college project.
- Language: Python 3.10+ (Tested on Python 3.14.7)
- GUI: Tkinter + ttk (using standard library)
- Database: SQLite via Python's built-in `sqlite3` module
- Architecture: Modular MVC-like separation (database, models, services, gui)
- Platform: Windows 10/11 offline desktop application

**Entry point:** `python main.py` (run from `smart_contact_manager/`)
**Automated test runner:** `python test_suite.py` (runs all 11 integration test modules)

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
    ├── test_suite.py               ← Comprehensive 11-module automated test suite
    ├── contacts.db                 ← SQLite database (auto-seeded)
    ├── requirements.txt            ← Dependency documentation
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
    │   └── contact_service.py      ← Validation, duplicate check, CRUD, filters, group logic
    ├── gui/
    │   ├── __init__.py
    │   ├── app_window.py           ← Root Tk window + 5-item sidebar navigation
    │   ├── theme.py                ← Palette, typography, ttk clam styling
    │   ├── widgets.py              ← LabelledEntry, LabelledText, make_button, StatCard
    │   ├── contact_form.py         ← Add/Edit modal dialog with dynamic phone rows & group checkboxes
    │   └── pages/
    │       ├── __init__.py
    │       ├── dashboard_page.py   ← 4 Stat cards + Recently added/updated contacts list
    │       ├── contacts_page.py    ← All contacts list, search, quick filters, detail panel
    │       ├── favourites_page.py  ← Dedicated favourites page with instant unfavourite
    │       ├── emergency_page.py   ← Dedicated emergency page with dial-ready phone display
    │       └── groups_page.py      ← Dedicated custom groups management + group members
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

*Note on deletion safety:* When a group is deleted, only entries in `contact_groups` are deleted via cascade. The contacts in `contacts` table remain completely intact.

---

## Completed Features (Parts 1 & 2)

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
| Unmark Favourite from Favourites Page | Part 2 | ✅ | `gui/pages/favourites_page.py` |
| Emergency Contacts Page | Part 2 | ✅ | `gui/pages/emergency_page.py` |
| Emergency Dial Display & Unmark Action | Part 2 | ✅ | `gui/pages/emergency_page.py` |
| Custom Contact Groups (CRUD) | Part 2 | ✅ | `gui/pages/groups_page.py` |
| Multi-group Contact Assignment | Part 2 | ✅ | `gui/contact_form.py`, `groups_page.py` |
| View Contacts by Group | Part 2 | ✅ | `gui/pages/groups_page.py` |
| Safe Group Deletion (Preserves Contacts) | Part 2 | ✅ | `services/contact_service.py` |
| Quick Filters (All, Favourites, Emergency) | Part 2 | ✅ | `gui/pages/contacts_page.py` |
| Dashboard Stat Cards (Total, Fav, Emer, Groups) | Part 2 | ✅ | `gui/pages/dashboard_page.py` |
| Recently Added/Updated Contacts List | Part 2 | ✅ | `gui/pages/dashboard_page.py` |
| Sidebar Navigation with 5 Active Pages | Part 2 | ✅ | `gui/app_window.py` |

---

## Files Created or Modified in Part 2

- `database/connection.py`: Seed default groups on initialize.
- `database/queries.py`: Added queries for secondary phone numbers, groups, contact_groups, and updated `search_contacts` to search across secondary phone numbers.
- `models/contact.py`: Added `PhoneNumber` and `Group` classes; updated `Contact` model with `extra_phones` and `groups`.
- `services/contact_service.py`: Added business logic for secondary phones, groups, favourite/emergency toggles, and recent contacts.
- `gui/contact_form.py`: Added dynamic secondary phone rows (label dropdown + input + remove button) and group assignment checkboxes.
- `gui/pages/contacts_page.py`: Added secondary phone numbers and groups to detail panel, quick filter buttons (All, Favourites, Emergency), and quick toggle buttons.
- `gui/pages/favourites_page.py`: New dedicated page for viewing and managing favourite contacts.
- `gui/pages/emergency_page.py`: New dedicated page for viewing and managing emergency contacts.
- `gui/pages/groups_page.py`: New dedicated page for creating, editing, and deleting groups, plus adding/removing contacts.
- `gui/pages/dashboard_page.py`: Updated with 4 stat cards and recently added/updated contacts list.
- `gui/app_window.py`: Registered all 5 pages in sidebar navigation.
- `test_suite.py`: Automated 11-module test suite verifying all features.
- `TASKS.md`, `PROJECT_PLAN.md`, `README.md`, `HANDOFF.md`: Full documentation update.

---

## Known Bugs / Limitations

None. All 11 automated test modules pass cleanly, and manual verification shows zero syntax or runtime errors.

---

## Exact Next Steps for Part 3

1. **Matplotlib Visualizations on Dashboard:**
   - Add chart(s) on `DashboardPage`:
     - Donut or Pie chart of Group distribution (e.g. Contacts per group)
     - Bar chart of Favourites vs Emergency vs General contacts
   - Embed Matplotlib canvas into Tkinter using `FigureCanvasTkAgg`.
2. **Export Contacts:**
   - Export contacts to CSV format (`filedialog.asksaveasfilename`).
   - Export contacts to VCF (vCard 3.0) format for mobile phone import.
3. **Import Contacts:**
   - Import contacts from CSV format (`filedialog.askopenfilename`).
   - Parse CSV headers and map to `full_name`, `phone`, `email`, `address`, `notes`.
   - Validate imported rows and report number of successfully imported vs skipped contacts.
4. **Audit History / Activity Log:**
   - Add an `activity_log` table to log actions (`Contact Added`, `Contact Updated`, `Contact Deleted`).
   - Show activity log on Dashboard or in a History modal.

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
