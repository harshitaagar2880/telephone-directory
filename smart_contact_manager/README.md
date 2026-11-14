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

> **Note:** The application uses only Python standard libraries (`tkinter`, `sqlite3`, `re`, `dataclasses`). No `pip install` is required for Parts 1 & 2!

---

## 🧪 Running Automated Tests

To run the automated verification test suite covering all 11 modules:
```bash
cd smart_contact_manager
python test_suite.py
```

---

## 📁 Project Architecture

```
smart_contact_manager/
├── main.py                     # Entry point
├── test_suite.py               # Comprehensive 11-module automated test suite
├── contacts.db                 # SQLite database (auto-initialized & seeded)
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
│   └── contact_service.py      # Business logic, validation, group & phone orchestration
├── gui/
│   ├── app_window.py           # Root window with 5-item sidebar navigation
│   ├── theme.py                # Visual styling, colors, typography, clam ttk theme
│   ├── widgets.py              # Reusable LabelledEntry, StatCard, styled buttons
│   ├── contact_form.py         # Modal form with dynamic phone rows & group checkboxes
│   └── pages/
│       ├── dashboard_page.py   # Dashboard with 4 stat cards & recent contacts
│       ├── contacts_page.py    # All contacts list, search, filters & detail panel
│       ├── favourites_page.py  # Dedicated favourites page
│       ├── emergency_page.py   # Dedicated emergency page
│       └── groups_page.py      # Dedicated group management page
└── assets/                     # Icons & resources
```

---

## 🎓 College Viva Preparation Guide

1. **Architecture:** The project follows a strict **Layered (MVC-like) Architecture**:
   - `gui/`: Handles all visual elements and user events.
   - `services/`: Encapsulates business rules, regex validations, and data orchestration.
   - `models/`: Plain Python dataclasses ensuring loose coupling.
   - `database/`: Manages SQLite connections and parameterized SQL queries.
2. **Database Integrity:**
   - Enforces Foreign Key constraints with `PRAGMA foreign_keys = ON`.
   - Uses `ON DELETE CASCADE` so deleting a contact automatically removes secondary numbers and group associations.
   - Deleting a group removes records from `contact_groups` while leaving the `contacts` table untouched.
3. **Security:** All database queries utilize **parameterized SQL** (`?` placeholders) to prevent SQL injection vulnerabilities.
