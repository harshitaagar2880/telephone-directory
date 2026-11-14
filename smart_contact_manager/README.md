# Smart Contact Manager — Advanced Telephone Directory

A modern, offline-first desktop contact management system built with Python, Tkinter, ttk, and SQLite. Developed with a clean modular MVC-like architecture.

---

## ✨ Features

### Part 1 — Foundation & Core CRUD
- **Add, View, Edit, and Delete Contacts** with confirmation dialogs.
- **SQLite Database** storing all data locally with parameterized queries.
- **Search System** providing real-time filtering across names, emails, and phone numbers.
- **Input Validation** enforcing regex checks for phone formats and email addresses.
- **Duplicate Prevention** preventing accidental duplicate contacts.
- **Treeview Display** with sortable columns and alternating row colors.
- **Detail Panel** showing comprehensive contact information on selection.

### Part 2 — Smart Contact Management
- **Multiple Phone Numbers per Contact:**
  - Save multiple phone numbers per contact with customizable labels: `Personal`, `Work`, `Home`, `Other`.
  - Dynamically add or remove phone fields in the contact form.
  - Search contacts by any of their saved secondary phone numbers.
  - All numbers stored in a separate relational `phone_numbers` table.
- **Favourite Contacts:**
  - Mark/unmark contacts as favourites with a single click.
  - Dedicated **Favourites Page** in the sidebar.
  - Instant unfavourite option directly from the Favourites view.
  - Quick filter button on the All Contacts page.
- **Emergency Contacts:**
  - Mark/unmark contacts as emergency contacts.
  - Dedicated **Emergency Contacts Page** in the sidebar.
  - High-visibility dial layout and immediate unmark action.
  - Quick filter button on the All Contacts page.
- **Custom Contact Groups:**
  - Create, edit, and delete custom groups (`Family`, `Friends`, `Work`, `College`, etc.).
  - Default groups automatically seeded on first launch.
  - Many-to-many relationship: one contact can belong to multiple groups.
  - Dedicated **Groups Page** in the sidebar showing member contacts.
  - Add or remove contacts to/from groups with dialog pickers.
  - **Safe Deletion:** Deleting a group never deletes the contacts inside it.
- **Dashboard Enhancements:**
  - 4 Live stat cards: Total Contacts, Favourites ⭐, Emergency 🚨, Contact Groups 📁.
  - Recently Added / Updated contacts list with double-click to view/edit.

### Part 3 — Data Import, Export & Backup
- **CSV Contact Export:**
  - Export all contacts into standard CSV format with `UTF-8 with BOM` for seamless compatibility with Microsoft Excel.
  - Includes full names, primary and secondary numbers (with labels), email, address, notes, favourite status, emergency status, and assigned groups.
  - Available from the dedicated **Backup & Data** page and via the top-bar button on the **All Contacts** page.
- **CSV Contact Import:**
  - Import contacts from any CSV file with smart, case-insensitive header matching (`Full Name`, `Phone`, `Email`, `Address`, `Notes`, `Groups`, etc.).
  - Robust row-by-row regex format validation for phone numbers and emails.
  - Automatic duplicate detection (prevents duplicate contacts from being imported).
  - Automatically resolves and creates missing contact groups.
  - Interactive **Import Summary Dialog** showing total processed, imported, skipped (duplicates), and failed records with detailed error reasons.
- **Database Backup:**
  - Uses SQLite's native online backup API (`sqlite3.backup`) for a 100% consistent, non-corrupted database snapshot.
  - Allows user to choose destination folder with auto-generated timestamped filenames (`contacts_backup_YYYYMMDD_HHMMSS.db`).
  - Safe operation that will not overwrite existing backups accidentally.
- **Database Restore:**
  - Restore the application from any previously created SQLite database backup.
  - **Integrity Verification:** Runs `PRAGMA integrity_check` and verifies required schema tables before attempting restore.
  - **Safety Snapshot:** Automatically creates a pre-restore safety snapshot of the active database in `_pre_restore_backup/` before overwriting.
  - Seamlessly reloads all open pages upon successful restoration.

---

## 🚀 How to Run

1. Open your terminal or Command Prompt.
2. Navigate to the `smart_contact_manager` folder:
   ```bash
   cd smart_contact_manager
   ```
3. Run the application:
   ```bash
   python main.py
   ```

> **Note:** The application uses only Python standard libraries (`tkinter`, `sqlite3`, `csv`, `re`, `dataclasses`). No `pip install` is required!

---

## 🧪 Running Automated Tests

To run the automated verification test suite covering all 15 modules:
```bash
cd smart_contact_manager
python test_suite.py
```

---

## 📁 Project Architecture

```
smart_contact_manager/
├── main.py                     # Entry point
├── test_suite.py               # Comprehensive 15-module automated test suite
├── contacts.db                 # SQLite database (auto-initialized & seeded)
├── _pre_restore_backup/        # Automatic pre-restore safety snapshots
├── requirements.txt            # Dependency specification
├── README.md                   # Documentation & Viva guide
├── PROJECT_PLAN.md             # Project roadmap
├── TASKS.md                    # Progress checklist
├── HANDOFF.md                  # Developer handoff guide
├── database/
│   ├── connection.py           # DB connection, schema init & group seeding
│   └── queries.py              # Parameterized SQL CRUD for all tables
├── models/
│   └── contact.py              # Dataclasses: Contact, PhoneNumber, Group
├── services/
│   ├── contact_service.py      # Business logic, validation, group & phone orchestration
│   └── data_service.py         # CSV export/import, SQLite backup/restore
├── gui/
│   ├── app_window.py           # Root window with 6-item sidebar navigation
│   ├── theme.py                # Visual styling, colors, typography, clam ttk theme
│   ├── widgets.py              # Reusable LabelledEntry, StatCard, styled buttons
│   ├── contact_form.py         # Modal form with dynamic phone rows & group checkboxes
│   └── pages/
│       ├── dashboard_page.py   # Dashboard with 4 stat cards & recent contacts
│       ├── contacts_page.py    # All contacts list, search, filters, detail panel, quick export/import
│       ├── favourites_page.py  # Dedicated favourites page
│       ├── emergency_page.py   # Dedicated emergency page
│       ├── groups_page.py      # Dedicated group management page
│       └── data_page.py        # Dedicated Backup & Data page
└── assets/                     # Icons & resources
```

---

## 🎓 College Viva Preparation Guide

1. **Architecture:** The project follows a strict **Layered (MVC-like) Architecture**:
   - `gui/`: Handles all visual elements, forms, and user interactions.
   - `services/`: Encapsulates business logic, data import/export, SQLite backups, and regex validation.
   - `models/`: Plain Python dataclasses ensuring loose coupling.
   - `database/`: Manages SQLite connections and parameterized SQL queries.
2. **Database Integrity & Cascades:**
   - Enforces Foreign Key constraints with `PRAGMA foreign_keys = ON`.
   - Uses `ON DELETE CASCADE` so deleting a contact automatically cleans up secondary numbers and group memberships.
   - Deleting a group removes records from `contact_groups` while leaving the `contacts` table untouched.
3. **Backup & Restore Mechanism:**
   - Uses Python's native `sqlite3.backup` API which locks pages during read/write to ensure ACID consistency without file locking conflicts.
   - Restores are preceded by an automatic pre-restore safety snapshot in `_pre_restore_backup/` to guarantee zero data loss.
4. **Security & Data Safety:** All database queries utilize **parameterized SQL** (`?` placeholders) to prevent SQL injection vulnerabilities.
