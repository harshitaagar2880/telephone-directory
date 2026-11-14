# TASKS.md — Smart Contact Manager

## Part 1 Tasks (COMPLETED)
- [x] Back up original files to `_backup_original/`
- [x] Create folder structure: database/, models/, services/, gui/, gui/pages/, assets/
- [x] Create `__init__.py` in every package
- [x] `database/connection.py` — DB path, `get_connection()`, `initialize_database()`
- [x] `database/queries.py` — All CRUD SQL functions with parameterised queries
- [x] `models/contact.py` — Contact dataclass with `from_row()` factory
- [x] `services/contact_service.py` — Validation, duplicate check, CRUD orchestration
- [x] `gui/theme.py` — Colour palette, fonts, ttk style helpers
- [x] `gui/widgets.py` — LabelledEntry, LabelledText, make_button, StatCard
- [x] `gui/contact_form.py` — Add / Edit modal dialog
- [x] `gui/pages/dashboard_page.py` — Dashboard with stat cards
- [x] `gui/pages/contacts_page.py` — Full contacts list, search, detail panel, sort
- [x] `gui/app_window.py` — Root window with sidebar navigation
- [x] `main.py` — Entry point
- [x] `requirements.txt`
- [x] `README.md`
- [x] `PROJECT_PLAN.md`
- [x] `TASKS.md`
- [x] `HANDOFF.md`
- [x] Part 1 Application tested and running

## Part 2 Tasks (COMPLETED)
- [x] Database layer: seed default groups ('Family', 'Friends', 'Work', 'College')
- [x] Database layer: CRUD for extra phone numbers (`phone_numbers` table)
- [x] Database layer: CRUD for groups & contact groups (`groups`, `contact_groups` tables)
- [x] Database layer: search across primary and secondary phone numbers
- [x] Database layer: recent contacts query (`get_recent_contacts`)
- [x] Model layer: update `Contact` model with `extra_phones` and `groups`
- [x] Service layer: multiple phone numbers validation & saving
- [x] Service layer: favourite & emergency toggle helpers
- [x] Service layer: group creation, editing, deletion (with cascade protection for contacts)
- [x] Service layer: multi-group assignment and contact-group queries
- [x] GUI: Contact Form — dynamic adding/removing multiple phone numbers with labels
- [x] GUI: Contact Form — group assignment with multi-selection checkboxes
- [x] GUI: Contacts Page — display secondary numbers, assigned groups, and quick toggle buttons
- [x] GUI: Contacts Page — quick filter buttons (All, ⭐ Favourites, 🚨 Emergency)
- [x] GUI: Favourites Page (`gui/pages/favourites_page.py`) in sidebar with instant unfavourite
- [x] GUI: Emergency Page (`gui/pages/emergency_page.py`) in sidebar with high-visibility phone display
- [x] GUI: Groups Management Page (`gui/pages/groups_page.py`) with group CRUD and member management
- [x] GUI: Dashboard Page — updated 4 stat cards & recently added/updated contacts list
- [x] GUI: Sidebar Navigation updated with 5 active pages
- [x] Testing: Automated test suite passing all Part 2 modules

## Part 3 Tasks — Data Import, Export & Backup (COMPLETED)
- [x] `services/data_service.py`: CSV export with secondary phones, groups, favourites, and emergency status (UTF-8 with BOM for Excel compatibility)
- [x] `services/data_service.py`: CSV import with case-insensitive header matching, regex format validation, duplicate prevention, and auto-group resolution
- [x] `services/data_service.py`: Consistent SQLite database backup using `sqlite3.backup` API with timestamped filenames
- [x] `services/data_service.py`: Database restore with candidate file verification (`PRAGMA integrity_check` & required table checks) and pre-restore safety snapshot
- [x] `gui/pages/data_page.py`: Dedicated Data Management & Backup page in sidebar with card layout
- [x] `gui/pages/contacts_page.py`: Quick Export and Import buttons on the top bar
- [x] Integration into `gui/app_window.py` sidebar navigation (6 items: Dashboard, All Contacts, Favourites, Emergency, Groups, Backup & Data)
- [x] Global data refresh synchronization (`_refresh_all_pages`) on bulk import or database restore
- [x] Testing: Comprehensive automated test suite (`test_suite.py`) expanded to 15 modules covering all Part 1, Part 2, and Part 3 features
- [x] Documentation: Updated README.md, PROJECT_PLAN.md, TASKS.md, and HANDOFF.md

## Part 4 Tasks (PENDING)
- [ ] Profile photo upload & avatar display
- [ ] Birthday / anniversary reminders
- [ ] Light / Dark theme toggle
- [ ] Keyboard shortcuts
- [ ] Fuzzy search matching
