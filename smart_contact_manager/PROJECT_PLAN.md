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
| Charts      | Matplotlib (Part 3)               |
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

### 🔲 Part 3 — Statistics, Analytics, Import & Export (UPCOMING)
- Matplotlib visualizations on Dashboard (pie chart of group distribution, contact growth)
- Export contacts to CSV format
- Export contacts to vCard (VCF) format
- Import contacts from CSV with field mapping & duplicate detection
- Activity log / audit history of contact modifications

### 🔲 Part 4 — Polish & Advanced Features (FUTURE)
- Contact profile photos / avatars
- Birthday & anniversary reminders
- Light / Dark theme toggle
- Keyboard shortcuts
- Global search with fuzzy matching
