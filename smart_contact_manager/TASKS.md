# TASKS.md — Smart Contact Manager

## Part 1 Tasks

### ✅ Completed
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
- [x] Application tested and running

### 🔲 Pending (Part 2)
- [ ] Multiple phone numbers per contact (uses existing `phone_numbers` table)
- [ ] Contact groups (uses existing `groups` + `contact_groups` tables)
- [ ] Filter view: Favourites only
- [ ] Filter view: Emergency only
- [ ] Import from CSV
- [ ] Export to CSV
- [ ] Recent contacts section on Dashboard
