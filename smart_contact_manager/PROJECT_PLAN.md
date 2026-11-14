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
| Charts      | Matplotlib (Phase 3+)             |
| OS          | Windows 10/11                     |

---

## Phase Roadmap

### ✅ Part 1 — Foundation (COMPLETE)
- Folder structure and module layout
- SQLite database with future-proof schema
- Full CRUD operations (Add, View, Edit, Delete)
- Search by name, phone, email
- Input validation (phone regex, email regex, required fields)
- Duplicate contact prevention
- Dashboard with live statistics
- Professional sidebar UI
- Detail panel per contact
- Favourite and emergency flags

### 🔲 Part 2 — Enhanced Features
- Multiple phone numbers per contact
- Contact groups (create, assign, filter by group)
- Import contacts from CSV / VCF
- Export contacts to CSV / PDF
- Favourite and Emergency filter views
- Recent contacts list on Dashboard

### 🔲 Part 3 — Statistics & Analytics
- Matplotlib charts on Dashboard (contacts added over time, group distribution)
- Contact activity log / history

### 🔲 Part 4 — Polish & Advanced
- Profile photo per contact
- Birthday reminders
- Dark mode toggle
- Keyboard shortcuts
- Global search with fuzzy matching

---

## Database Design Principles
- `contacts` table holds core fields; designed to never need a rebuild
- `phone_numbers` table enables multiple numbers per contact (Part 2)
- `groups` and `contact_groups` enable many-to-many group membership (Part 2)
- All foreign keys use ON DELETE CASCADE
- Timestamps stored as text in SQLite-friendly format
