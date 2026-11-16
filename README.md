# Smart Contact Manager — Advanced Telephone Directory

An offline-first desktop contact management application built using **Python, Tkinter, ttk, and SQLite**. It provides a structured way to store, organize, search, and manage contacts through a modern graphical interface.

The application follows a modular, MVC-inspired architecture and uses local SQLite storage to keep contact information accessible without an internet connection.

---

## ✨ Features

### Contact Management
- Add, view, edit, and delete contacts with confirmation dialogs.
- Soft-delete contacts by moving them to the Trash.
- Restore deleted contacts or permanently remove them.
- Prevent duplicate contact entries.
- View comprehensive contact information through a dedicated detail panel.
- Display contacts in a sortable Treeview with alternating row colours.

### Search & Validation
- Real-time search across contact names, email addresses, and phone numbers.
- Regex-based validation for phone numbers and email addresses.
- Search using primary and secondary phone numbers.
- Case-insensitive CSV header matching during imports.

### Multiple Phone Numbers
- Store multiple phone numbers for each contact.
- Assign customizable labels: `Personal`, `Work`, `Home`, and `Other`.
- Dynamically add or remove phone number fields in the contact form.
- Store phone numbers in a separate relational `phone_numbers` table.

### Favourites & Emergency Contacts
- Mark or unmark contacts as favourites.
- Dedicated Favourites page in the sidebar.
- Remove favourites directly from the Favourites page.
- Mark or unmark contacts as emergency contacts.
- Dedicated Emergency Contacts page with a high-visibility contact layout.
- Quick filters for favourites and emergency contacts on the All Contacts page.

### Contact Groups
- Create, edit, and delete custom groups such as `Family`, `Friends`, `Work`, and `College`.
- Automatically seed default groups on first launch.
- Support many-to-many relationships, allowing contacts to belong to multiple groups.
- Dedicated Groups page displaying group members.
- Add or remove contacts through dialog-based pickers.
- Deleting a group does not delete its associated contacts.

### Dashboard & Speed Dial
- Five live statistic cards:
  - Total Contacts
  - Favourites
  - Emergency Contacts
  - Contact Groups
  - Speed Dial
- Recently Added and Recently Updated contact lists.
- Recently Viewed contacts tab.
- Double-click contacts to view or edit their details.
- Dedicated Speed Dial page with slots 1–9.

### CSV Import & Export
- Export contacts into standard CSV format.
- UTF-8 with BOM encoding for Microsoft Excel compatibility.
- Export names, primary and secondary phone numbers, labels, email addresses, addresses, notes, favourite status, emergency status, and assigned groups.
- Import contacts from external CSV files.
- Support smart, case-insensitive header matching.
- Validate phone numbers and email addresses row by row.
- Automatically detect and skip duplicate contacts.
- Resolve existing groups and create missing groups when necessary.
- Display an interactive import summary containing processed, imported, skipped, and failed records with error details.
- Access import/export functionality through the All Contacts and Backup & Data pages.

### Database Backup & Restore
- Create consistent database snapshots using SQLite's native online backup API (`sqlite3.backup`).
- Choose backup destination folders.
- Generate timestamped backup filenames: `contacts_backup_YYYYMMDD_HHMMSS.db`.
- Prevent accidental overwriting of existing backups.
- Restore application data from previously created SQLite backups.
- Verify database integrity using `PRAGMA integrity_check`.
- Verify required schema tables before restoration.
- Automatically create a pre-restore safety snapshot inside `_pre_restore_backup/`.
- Reload application pages after successful restoration.

### Themes & Personalization

**Implemented**

- Light and Dark themes.
- Six accent colour options: Blue, Green, Purple, Orange, Red, and Teal.
- Consistent styling across pages, buttons, forms, navigation, and dialogs.
- Persist theme and accent colour preferences in the local SQLite `settings` table.
- Switch themes instantly through the sidebar.

### Trash / Recycle Bin

**Implemented**

- Move deleted contacts to the Trash instead of immediately removing them.
- Dedicated Trash page in the sidebar.
- Restore contacts with their original details, phone numbers, favourite and emergency status, and group memberships.
- Permanently delete contacts with confirmation.
- Preserve associated phone numbers and group memberships during soft deletion.
- Handle duplicate conflicts when restoring contacts.

### Future Improvements

**Not Implemented**

- Profile photo uploads and avatar display.
- Birthday and anniversary reminders.
- Keyboard shortcuts.
- Fuzzy search matching.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Tkinter support
- SQLite support

The application uses Python's standard library and does not require third-party packages.

### Running the Application

1. Clone or download the project.
2. Open a terminal in the project directory.
3. Run the following command:

```bash
python main.py
```

The SQLite database is initialized automatically when the application starts.

**Note:** No `pip install` is required. The application uses standard Python libraries, including:

- `tkinter`
- `sqlite3`
- `csv`
- `re`
- `dataclasses`

---

## 🧪 Running Automated Tests

The project includes an automated test suite covering 19 modules.

To execute the tests:

```bash
cd smart_contact_manager
python test_suite.py
```

---

## 📁 Project Architecture

The application follows a modular, MVC-inspired architecture that separates database operations, business logic, data models, and graphical interface components.

```text
telephone-directory/
│
├── main.py                     # Application entry point
├── test_suite.py               # Automated test suite (19 modules)
├── contacts.db                 # Local SQLite database
├── requirements.txt            # Dependency specification
├── README.md                   # Project documentation
│
├── _pre_restore_backup/        # Automatic pre-restore snapshots
│
├── agents/
│   ├── HANDOFF.md              # Developer handoff guide
│   ├── PROJECT_PLAN.md         # Project roadmap
│   └── TASKS.md                # Development progress checklist
│
├── database/
│   ├── connection.py           # Database connection and schema initialization
│   └── queries.py              # Parameterized SQL CRUD operations
│
├── models/
│   └── contact.py              # Contact, PhoneNumber, and Group dataclasses
│
├── services/
│   ├── contact_service.py      # Business logic and contact validation
│   └── data_service.py         # CSV import/export and database backup/restore
│
├── gui/
│   ├── app_window.py           # Root window and sidebar navigation
│   ├── theme.py                # Themes and accent colour management
│   ├── widgets.py              # Reusable GUI components
│   ├── contact_form.py         # Contact form with dynamic phone fields
│   │
│   └── pages/
│       ├── dashboard_page.py   # Dashboard and contact statistics
│       ├── contacts_page.py    # All contacts, search, filters, and details
│       ├── speed_dial_page.py  # Speed Dial (slots 1–9)
│       ├── favourites_page.py  # Favourite contacts
│       ├── emergency_page.py   # Emergency contacts
│       ├── groups_page.py      # Contact group management
│       ├── trash_page.py       # Restore and permanently delete contacts
│       └── data_page.py        # Backup, restore, and CSV operations
│
└── assets/                     # Icons and application resources
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application logic |
| Tkinter | Desktop graphical interface |
| ttk | Styled GUI widgets |
| SQLite | Local relational database |
| SQL | Database queries and operations |
| CSV | Contact data import and export |
| Regular Expressions | Input validation |
| Dataclasses | Structured data models |

---

## 🔒 Design Principles

- **Offline First:** Core application functionality does not depend on an internet connection.
- **Local Data Storage:** Contact information is stored locally using SQLite.
- **Modular Architecture:** Separate database, service, model, and GUI layers.
- **Data Integrity:** Parameterized SQL queries and validation help maintain reliable data handling.
- **Data Recovery:** Soft deletion, database backups, and restoration mechanisms provide data recovery options.
- **Standard Library:** Avoid unnecessary third-party dependencies.

---

## 📌 Project Status

The Smart Contact Manager brings together contact management, organization, data portability, and recovery functionality in a single desktop application.

The core application features are implemented, including contact management, multiple phone numbers, favourites, emergency contacts, groups, dashboard statistics, CSV operations, database backup and restoration, themes, and the Trash system.

Profile photos, reminders, keyboard shortcuts, and fuzzy search remain potential future improvements.