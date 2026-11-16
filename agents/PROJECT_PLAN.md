# PROJECT_PLAN.md — Smart Contact Manager

## Vision
An offline-first desktop contact manager that evolves from a basic telephone directory
into a feature-rich professional application, built incrementally across multiple phases.

---

## Technology Stack
| Layer       | Technology                        |
|-------------|-----------------------------------|
| Language    | Python 3.10+                      |
| GUI         | Tkinter + ttk (standard library)  |
| Database    | SQLite via sqlite3 (stdlib)        |
| Data Format | CSV (RFC 4180 / UTF-8 with BOM)   |
| Backup      | SQLite Online Backup API          |
| OS          | Windows 10/11                     |

---

## Phase Roadmap

### ✅ Part 1 — Foundation (COMPLETE)
- Folder structure and modular MVC-like layout
- SQLite database with future-proof relational schema
- Full CRUD operations (Add, View, Edit, Delete)
- Search by name, phone, email
- Input validation (phone regex, email regex, required fields)
- Duplicate contact prevention
- Dashboard with live statistics
- Professional sidebar UI
- Detail panel per contact
- Initial favourite and emergency flags

### ✅ Part 2 — Smart Contact Management (COMPLETE)
- **Multiple Phone Numbers per Contact:**
  - Save multiple phone numbers per contact with customizable labels (`Personal`, `Work`, `Home`, `Other`)
  - Dynamic addition and removal of phone rows in contact form
  - Stored in separate relational `phone_numbers` table with foreign key cascade
  - Search contacts using primary phone or any secondary phone number
  - Display all numbers in detail panel
- **Favourite Contacts:**
  - Dedicated Favourites page in sidebar
  - Display and manage favourite contacts
  - Instant unfavourite option directly from Favourites view
  - Quick filter on All Contacts page
- **Emergency Contacts:**
  - Dedicated Emergency Contacts page in sidebar
  - High-visibility dial layout and immediate unmark action
  - Quick filter on All Contacts page
- **Custom Contact Groups:**
  - Dedicated Groups management page in sidebar
  - Create, edit, and delete custom groups (`Family`, `Friends`, `Work`, `College`, etc.)
  - Default groups seeded automatically
  - Many-to-many relationship (`contact_groups` table)
  - Assign contacts to multiple groups via form checkboxes or group picker
  - Safe group deletion: contacts inside deleted group are never deleted
- **Dashboard Enhancements:**
  - 4 Stat cards: Total Contacts, Favourites, Emergency, Groups
  - Recently Added / Updated contacts list with double-click to view/edit
- **Sidebar Navigation:**
  - 5 Fully functional pages: Dashboard, All Contacts, Favourites, Emergency, Groups

### ✅ Part 3 — Data Import, Export & Backup (COMPLETE)
- **CSV Contact Export:**
  - Export all contacts into standard CSV with UTF-8 BOM encoding for Excel compatibility.
  - Includes full names, primary and secondary numbers (with labels), email, address, notes, favourite status, emergency status, and assigned groups.
  - Available via the dedicated Backup & Data page and quick-action button on All Contacts page.
- **CSV Contact Import:**
  - Import contacts from CSV with case-insensitive header matching.
  - Format validation using regex for phone numbers and emails.
  - Automatic duplicate contact detection (skips existing contacts).
  - Automatic group resolution and creation.
  - Detailed Import Summary modal dialog reporting processed, imported, skipped, and failed rows.
- **Database Backup:**
  - Atomic, online backup using Python's native `sqlite3.backup` API.
  - User-selected destination with automatic timestamped filename (`contacts_backup_YYYYMMDD_HHMMSS.db`).
- **Database Restore:**
  - Safely restore active database from any valid SQLite backup.
  - Pre-restore candidate verification (`PRAGMA integrity_check` & schema validation).
  - Automatic pre-restore safety snapshot in `_pre_restore_backup/` to prevent data loss.
  - Automatic reload of all application pages upon successful restoration.
- **Sidebar Navigation:**
  - 6 Fully functional pages: Dashboard, All Contacts, Favourites, Emergency, Groups, Backup & Data.

### 🔲 Part 4 — Polish & Advanced Features (UPCOMING)
- Contact profile photos / avatars
- Birthday & anniversary reminders
- Light / Dark theme toggle
- Keyboard shortcuts
- Global search with fuzzy matching
