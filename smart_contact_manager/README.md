# Smart Contact Manager

A professional desktop contact management system built with Python, Tkinter and SQLite.

## Features (Part 1)
- Add, view, edit and delete contacts
- Search contacts by name, phone or email
- Favourite and emergency contact flags
- Duplicate contact prevention
- Input validation (phone format, email format)
- Professional sidebar navigation
- Dashboard with live statistics
- Contact detail panel
- Sortable contact list

## How to Run

```bash
cd smart_contact_manager
python main.py
```

> Requires Python 3.10 or later. No third-party packages needed.

## Project Structure

```
smart_contact_manager/
├── main.py                     # Entry point
├── contacts.db                 # SQLite database (auto-created)
├── requirements.txt
├── database/
│   ├── connection.py           # DB connection + schema init
│   └── queries.py              # All SQL CRUD functions
├── models/
│   └── contact.py              # Contact data class
├── services/
│   └── contact_service.py      # Business logic + validation
├── gui/
│   ├── app_window.py           # Root window + sidebar
│   ├── theme.py                # Colours + fonts
│   ├── widgets.py              # Reusable widget helpers
│   ├── contact_form.py         # Add/Edit modal dialog
│   └── pages/
│       ├── dashboard_page.py   # Dashboard with stats
│       └── contacts_page.py    # Contacts list + actions
└── assets/                     # Icons and images (future use)
```

## Original Project
The original text-file based telephone directory is preserved in `_backup_original/`.

## College Project Notes
This project demonstrates:
- **MVC-like separation**: database / services / GUI layers
- **SQLite** via Python's built-in `sqlite3` module
- **Tkinter + ttk** for a professional desktop UI
- **Parameterised SQL** to prevent injection
- **Input validation** with regex
- **Object-oriented design** with dataclasses
