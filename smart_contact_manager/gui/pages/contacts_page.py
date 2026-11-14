"""
gui/pages/contacts_page.py
---------------------------
All Contacts page.
Provides:
  - Search bar
  - Add Contact button
  - Treeview listing all contacts
  - Detail panel on the right
  - Edit and Delete buttons
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from gui.contact_form import ContactFormDialog
from models.contact import Contact
from services.contact_service import (
    fetch_all_contacts, search_contacts, remove_contact, fetch_contact
)


class ContactsPage(tk.Frame):
    """
    Main contacts management page.
    """

    # Treeview column definitions: (id, display_header, width, anchor)
    COLUMNS = [
        ("name",      "Full Name",    220, "w"),
        ("phone",     "Phone",        140, "w"),
        ("email",     "Email",        180, "w"),
        ("fav",       "⭐",            35,  "center"),
        ("emer",      "🚨",            35,  "center"),
        ("updated",   "Last Updated", 130, "center"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._selected_id: Optional[int] = None
        self._contacts: list[Contact] = []
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ---- Top bar (title + Add button) ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(25, 5))

        tk.Label(
            topbar, text="All Contacts",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        make_button(
            topbar, text="＋  Add Contact",
            command=self._open_add_form,
            style="primary", width=16
        ).pack(side="right")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(0, 10))

        # ---- Search bar ----
        search_frame = tk.Frame(self, bg=COLORS["main_bg"])
        search_frame.pack(fill="x", padx=30, pady=(0, 10))

        tk.Label(
            search_frame, text="🔍",
            font=FONTS["body"], bg=COLORS["main_bg"]
        ).pack(side="left", padx=(0, 5))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        search_entry = tk.Entry(
            search_frame,
            textvariable=self._search_var,
            font=FONTS["input"], width=36,
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
        )
        search_entry.pack(side="left", ipady=4)

        make_button(
            search_frame, text="Clear",
            command=self._clear_search,
            style="secondary", width=6
        ).pack(side="left", padx=(8, 0))

        # ---- Main area: Treeview + Detail panel ----
        content = tk.Frame(self, bg=COLORS["main_bg"])
        content.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        # Left side: Treeview
        self._build_treeview(content)

        # Right side: Detail panel
        self._build_detail_panel(content)

        # ---- Bottom action bar ----
        self._build_action_bar()

    def _build_treeview(self, parent):
        """Build the contacts list treeview."""
        tree_frame = tk.Frame(parent, bg=COLORS["card_bg"],
                              highlightthickness=1,
                              highlightbackground=COLORS["card_border"])
        tree_frame.pack(side="left", fill="both", expand=True)

        # Style applied from app_window.py
        self._tree = ttk.Treeview(
            tree_frame,
            style="Contacts.Treeview",
            selectmode="browse",
            show="headings",
            columns=[col[0] for col in self.COLUMNS],
        )

        # Configure columns
        for col_id, header, width, anchor in self.COLUMNS:
            self._tree.heading(col_id, text=header,
                               command=lambda c=col_id: self._sort_by(c))
            self._tree.column(col_id, width=width, anchor=anchor,
                              minwidth=30, stretch=(col_id == "name"))

        # Alternating row colours
        self._tree.tag_configure("odd",  background=COLORS["tree_odd"])
        self._tree.tag_configure("even", background=COLORS["tree_even"])
        self._tree.tag_configure("fav",  foreground=COLORS["favourite"])
        self._tree.tag_configure("emer", foreground=COLORS["emergency"])

        # Vertical scrollbar
        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview,
                            style="Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        # Selection event
        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>",          self._open_edit_form)

    def _build_detail_panel(self, parent):
        """Right-side panel showing full details of the selected contact."""
        self._detail_frame = tk.Frame(
            parent, bg=COLORS["card_bg"], width=240,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"]
        )
        self._detail_frame.pack(side="right", fill="y", padx=(10, 0))
        self._detail_frame.pack_propagate(False)

        tk.Label(
            self._detail_frame, text="Contact Details",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", padx=15, pady=(15, 5))

        horizontal_separator(self._detail_frame).pack(fill="x", padx=10)

        self._detail_labels: dict[str, tk.Label] = {}
        fields = [
            ("name",    "Name"),
            ("phone",   "Phone"),
            ("email",   "Email"),
            ("address", "Address"),
            ("notes",   "Notes"),
            ("created", "Added"),
            ("updated", "Updated"),
        ]
        for key, label in fields:
            tk.Label(
                self._detail_frame, text=label + ":",
                font=FONTS["small_bold"], fg=COLORS["text_secondary"],
                bg=COLORS["card_bg"], anchor="w"
            ).pack(anchor="w", padx=15, pady=(8, 0))

            lbl = tk.Label(
                self._detail_frame, text="—",
                font=FONTS["small"], fg=COLORS["text_primary"],
                bg=COLORS["card_bg"], anchor="w",
                wraplength=200, justify="left"
            )
            lbl.pack(anchor="w", padx=15)
            self._detail_labels[key] = lbl

        # Badges row
        self._badge_frame = tk.Frame(self._detail_frame, bg=COLORS["card_bg"])
        self._badge_frame.pack(anchor="w", padx=15, pady=(10, 5))
        self._fav_badge  = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._emer_badge = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._fav_badge.pack(side="left", padx=(0, 8))
        self._emer_badge.pack(side="left")

        self._clear_detail()

    def _build_action_bar(self):
        """Bottom row with Edit and Delete buttons."""
        bar = tk.Frame(self, bg=COLORS["main_bg"])
        bar.pack(fill="x", padx=30, pady=(0, 15))

        self._edit_btn = make_button(
            bar, text="✏  Edit",
            command=self._open_edit_form,
            style="primary", width=12
        )
        self._edit_btn.pack(side="left", padx=(0, 10))
        self._edit_btn.config(state="disabled")

        self._delete_btn = make_button(
            bar, text="🗑  Delete",
            command=self._delete_selected,
            style="danger", width=12
        )
        self._delete_btn.pack(side="left")
        self._delete_btn.config(state="disabled")

        # Row count label (right side)
        self._count_var = tk.StringVar(value="0 contacts")
        tk.Label(
            bar, textvariable=self._count_var,
            font=FONTS["small"], fg=COLORS["text_secondary"],
            bg=COLORS["main_bg"]
        ).pack(side="right")

    # ------------------------------------------------------------------
    # Data loading & search
    # ------------------------------------------------------------------

    def refresh(self):
        """Reload contacts from the database and repopulate the treeview."""
        query = self._search_var.get() if hasattr(self, "_search_var") else ""
        self._contacts = search_contacts(query) if query else fetch_all_contacts()
        self._populate_tree(self._contacts)
        self._clear_detail()
        self._selected_id = None
        self._toggle_buttons(enabled=False)

    def _populate_tree(self, contacts: list[Contact]):
        """Clear and reload all treeview rows."""
        for row in self._tree.get_children():
            self._tree.delete(row)

        for i, c in enumerate(contacts):
            tag = "even" if i % 2 == 0 else "odd"
            fav  = "⭐" if c.is_favourite else ""
            emer = "🚨" if c.is_emergency else ""
            # Show only date part of updated_at
            updated = c.updated_at[:10] if len(c.updated_at) >= 10 else c.updated_at

            self._tree.insert(
                "", "end",
                iid=str(c.id),
                values=(c.full_name, c.phone, c.email, fav, emer, updated),
                tags=(tag,),
            )

        total = len(contacts)
        noun = "contact" if total == 1 else "contacts"
        self._count_var.set(f"{total} {noun}")

    def _on_search_change(self, *_args):
        """Called whenever the search field changes (trace callback)."""
        query = self._search_var.get()
        self._contacts = search_contacts(query) if query else fetch_all_contacts()
        self._populate_tree(self._contacts)
        self._clear_detail()
        self._selected_id = None
        self._toggle_buttons(enabled=False)

    def _clear_search(self):
        self._search_var.set("")

    # ------------------------------------------------------------------
    # Selection & detail panel
    # ------------------------------------------------------------------

    def _on_select(self, _event=None):
        """Called when a row is clicked in the treeview."""
        selected = self._tree.selection()
        if not selected:
            return
        contact_id = int(selected[0])
        if contact_id == self._selected_id:
            return
        self._selected_id = contact_id
        contact = fetch_contact(contact_id)
        if contact:
            self._show_detail(contact)
            self._toggle_buttons(enabled=True)

    def _show_detail(self, c: Contact):
        """Populate the detail panel with a contact's data."""
        self._detail_labels["name"].config(   text=c.full_name  or "—")
        self._detail_labels["phone"].config(  text=c.phone      or "—")
        self._detail_labels["email"].config(  text=c.email      or "—")
        self._detail_labels["address"].config(text=c.address    or "—")
        self._detail_labels["notes"].config(  text=c.notes      or "—")
        self._detail_labels["created"].config(text=c.created_at or "—")
        self._detail_labels["updated"].config(text=c.updated_at or "—")

        # Badges
        self._fav_badge.config(
            text="⭐ Favourite" if c.is_favourite else "",
            fg=COLORS["favourite"], font=FONTS["small_bold"]
        )
        self._emer_badge.config(
            text="🚨 Emergency" if c.is_emergency else "",
            fg=COLORS["emergency"], font=FONTS["small_bold"]
        )

    def _clear_detail(self):
        """Reset the detail panel to its empty state."""
        for lbl in self._detail_labels.values():
            lbl.config(text="—")
        self._fav_badge.config(text="")
        self._emer_badge.config(text="")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _open_add_form(self):
        ContactFormDialog(self, contact=None, on_save=self.refresh)

    def _open_edit_form(self, _event=None):
        if self._selected_id is None:
            messagebox.showwarning("No Selection", "Please select a contact first.")
            return
        contact = fetch_contact(self._selected_id)
        if not contact:
            messagebox.showerror("Error", "Contact not found.")
            self.refresh()
            return
        ContactFormDialog(self, contact=contact, on_save=self.refresh)

    def _delete_selected(self):
        if self._selected_id is None:
            messagebox.showwarning("No Selection", "Please select a contact first.")
            return

        contact = fetch_contact(self._selected_id)
        if not contact:
            self.refresh()
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete  '{contact.full_name}'?\n\n"
            "This action cannot be undone.",
            icon="warning"
        )
        if not confirmed:
            return

        ok, msg = remove_contact(self._selected_id)
        if ok:
            messagebox.showinfo("Deleted", msg)
            self._selected_id = None
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def _toggle_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._edit_btn.config(state=state)
        self._delete_btn.config(state=state)

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def _sort_by(self, col_id: str):
        """Sort treeview rows by the clicked column header."""
        col_map = {
            "name":    lambda c: c.full_name.lower(),
            "phone":   lambda c: c.phone,
            "email":   lambda c: c.email.lower(),
            "fav":     lambda c: not c.is_favourite,
            "emer":    lambda c: not c.is_emergency,
            "updated": lambda c: c.updated_at,
        }
        key_fn = col_map.get(col_id, lambda c: c.full_name.lower())

        # Toggle sort direction
        current_dir = getattr(self, "_sort_dir", {})
        asc = not current_dir.get(col_id, False)
        current_dir[col_id] = asc
        self._sort_dir = current_dir

        self._contacts.sort(key=key_fn, reverse=not asc)
        self._populate_tree(self._contacts)
