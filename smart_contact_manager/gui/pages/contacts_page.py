"""
gui/pages/contacts_page.py
---------------------------
All Contacts page.
Provides:
  - Search bar across name, email, and primary/secondary phone numbers
  - Quick filter buttons: All, Favourites, Emergency
  - Add Contact button
  - Treeview listing all contacts
  - Detailed side panel showing all phone numbers, groups, notes
  - Edit, Delete, Toggle Favourite, Toggle Emergency actions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from gui.contact_form import ContactFormDialog
from models.contact import Contact
from services.contact_service import (
    fetch_all_contacts, search_contacts, remove_contact, fetch_contact,
    toggle_favourite, toggle_emergency
)
from services.data_service import export_contacts_to_csv, import_contacts_from_csv


class ContactsPage(tk.Frame):
    """
    Main contacts management page.
    """

    # Treeview column definitions: (id, display_header, width, anchor)
    COLUMNS = [
        ("name",      "Full Name",    200, "w"),
        ("phone",     "Primary Phone",130, "w"),
        ("email",     "Email",        170, "w"),
        ("groups",    "Groups",       120, "w"),
        ("fav",       "⭐",            35,  "center"),
        ("emer",      "🚨",            35,  "center"),
        ("updated",   "Last Updated", 110, "center"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._selected_id: Optional[int] = None
        self._contacts: List[Contact] = []
        self._current_filter: str = "all"  # "all" | "fav" | "emer"
        self._build_ui()
        self.refresh()

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self):
        # ---- Top bar (title + Add button) ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(20, 5))

        tk.Label(
            topbar, text="All Contacts",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        # Top right action buttons
        actions_box = tk.Frame(topbar, bg=COLORS["main_bg"])
        actions_box.pack(side="right")

        make_button(
            actions_box, text="📥  Import CSV",
            command=self._quick_import_csv,
            style="secondary", width=13
        ).pack(side="left", padx=(0, 6))

        make_button(
            actions_box, text="📤  Export CSV",
            command=self._quick_export_csv,
            style="secondary", width=13
        ).pack(side="left", padx=(0, 6))

        make_button(
            actions_box, text="＋  Add Contact",
            command=self._open_add_form,
            style="primary", width=15
        ).pack(side="left")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 10))

        # ---- Controls bar: Search + Quick Filters ----
        controls_frame = tk.Frame(self, bg=COLORS["main_bg"])
        controls_frame.pack(fill="x", padx=30, pady=(0, 10))

        # Search bar
        tk.Label(
            controls_frame, text="🔍",
            font=FONTS["body"], bg=COLORS["main_bg"]
        ).pack(side="left", padx=(0, 5))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        search_entry = tk.Entry(
            controls_frame,
            textvariable=self._search_var,
            font=FONTS["input"], width=28,
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
        )
        search_entry.pack(side="left", ipady=4)

        make_button(
            controls_frame, text="Clear",
            command=self._clear_search,
            style="secondary", width=6
        ).pack(side="left", padx=(6, 20))

        # Filter buttons
        filter_box = tk.Frame(controls_frame, bg=COLORS["main_bg"])
        filter_box.pack(side="left")

        self._btn_filter_all = tk.Button(
            filter_box, text="All", font=FONTS["small_bold"],
            bg=COLORS["primary"], fg=COLORS["text_on_accent"],
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=lambda: self._set_filter("all")
        )
        self._btn_filter_all.pack(side="left", padx=2)

        self._btn_filter_fav = tk.Button(
            filter_box, text="⭐ Favourites", font=FONTS["small"],
            bg=COLORS["card_border"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=lambda: self._set_filter("fav")
        )
        self._btn_filter_fav.pack(side="left", padx=2)

        self._btn_filter_emer = tk.Button(
            filter_box, text="🚨 Emergency", font=FONTS["small"],
            bg=COLORS["card_border"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=lambda: self._set_filter("emer")
        )
        self._btn_filter_emer.pack(side="left", padx=2)

        # ---- Main content: Treeview + Detail panel ----
        content = tk.Frame(self, bg=COLORS["main_bg"])
        content.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self._build_treeview(content)
        self._build_detail_panel(content)

        # ---- Bottom action bar ----
        self._build_action_bar()

    def _build_treeview(self, parent):
        """Build the contacts list treeview."""
        tree_frame = tk.Frame(parent, bg=COLORS["card_bg"],
                              highlightthickness=1,
                              highlightbackground=COLORS["card_border"])
        tree_frame.pack(side="left", fill="both", expand=True)

        self._tree = ttk.Treeview(
            tree_frame,
            style="Contacts.Treeview",
            selectmode="browse",
            show="headings",
            columns=[col[0] for col in self.COLUMNS],
        )

        for col_id, header, width, anchor in self.COLUMNS:
            self._tree.heading(col_id, text=header,
                               command=lambda c=col_id: self._sort_by(c))
            self._tree.column(col_id, width=width, anchor=anchor,
                              minwidth=30, stretch=(col_id == "name" or col_id == "email"))

        self._tree.tag_configure("odd",  background=COLORS["tree_odd"])
        self._tree.tag_configure("even", background=COLORS["tree_even"])

        vsb = ttk.Scrollbar(tree_frame, orient="vertical",
                            command=self._tree.yview,
                            style="Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>",          self._open_edit_form)

    def _build_detail_panel(self, parent):
        """Right-side panel showing full details of the selected contact."""
        self._detail_frame = tk.Frame(
            parent, bg=COLORS["card_bg"], width=280,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"]
        )
        self._detail_frame.pack(side="right", fill="y", padx=(10, 0))
        self._detail_frame.pack_propagate(False)

        tk.Label(
            self._detail_frame, text="Contact Details",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", padx=15, pady=(12, 4))

        horizontal_separator(self._detail_frame).pack(fill="x", padx=10)

        # Scrollable container inside detail frame
        canvas = tk.Canvas(self._detail_frame, bg=COLORS["card_bg"], highlightthickness=0)
        canvas.pack(fill="both", expand=True, padx=5, pady=5)
        d_body = tk.Frame(canvas, bg=COLORS["card_bg"])
        canvas.create_window((0, 0), window=d_body, anchor="nw")

        def _conf(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
        d_body.bind("<Configure>", _conf)

        self._detail_labels: dict[str, tk.Label] = {}
        fields = [
            ("name",         "Full Name"),
            ("phone",        "Primary Phone"),
            ("extra_phones", "Other Numbers"),
            ("email",        "Email"),
            ("groups",       "Groups"),
            ("address",      "Address"),
            ("notes",        "Notes"),
            ("created",      "Added"),
            ("updated",      "Updated"),
        ]
        for key, label in fields:
            tk.Label(
                d_body, text=label + ":",
                font=FONTS["small_bold"], fg=COLORS["text_secondary"],
                bg=COLORS["card_bg"], anchor="w"
            ).pack(anchor="w", padx=10, pady=(6, 1))

            lbl = tk.Label(
                d_body, text="—",
                font=FONTS["small"], fg=COLORS["text_primary"],
                bg=COLORS["card_bg"], anchor="w",
                wraplength=250, justify="left"
            )
            lbl.pack(anchor="w", padx=10)
            self._detail_labels[key] = lbl

        # Badges row
        self._badge_frame = tk.Frame(d_body, bg=COLORS["card_bg"])
        self._badge_frame.pack(anchor="w", padx=10, pady=(10, 5))
        self._fav_badge  = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._emer_badge = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._fav_badge.pack(side="left", padx=(0, 6))
        self._emer_badge.pack(side="left")

        # Quick toggle buttons on detail panel
        self._quick_action_frame = tk.Frame(d_body, bg=COLORS["card_bg"])
        self._quick_action_frame.pack(fill="x", padx=10, pady=(10, 10))

        self._toggle_fav_btn = tk.Button(
            self._quick_action_frame, text="⭐ Favourite",
            font=FONTS["small"], bg=COLORS["warning_light"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=6, pady=4, cursor="hand2",
            command=self._toggle_favourite_selected, state="disabled"
        )
        self._toggle_fav_btn.pack(side="left", padx=(0, 6))

        self._toggle_emer_btn = tk.Button(
            self._quick_action_frame, text="🚨 Emergency",
            font=FONTS["small"], bg=COLORS["danger_light"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=6, pady=4, cursor="hand2",
            command=self._toggle_emergency_selected, state="disabled"
        )
        self._toggle_emer_btn.pack(side="left")

        self._clear_detail()

    def _build_action_bar(self):
        """Bottom row with Edit and Delete buttons."""
        bar = tk.Frame(self, bg=COLORS["main_bg"])
        bar.pack(fill="x", padx=30, pady=(0, 12))

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

        self._count_var = tk.StringVar(value="0 contacts")
        tk.Label(
            bar, textvariable=self._count_var,
            font=FONTS["small"], fg=COLORS["text_secondary"],
            bg=COLORS["main_bg"]
        ).pack(side="right")

    # ------------------------------------------------------------------
    # Filtering & Data loading
    # ------------------------------------------------------------------

    def _set_filter(self, filter_name: str):
        self._current_filter = filter_name

        # Update button highlights
        def style_btn(btn, active):
            if active:
                btn.config(bg=COLORS["primary"], fg=COLORS["text_on_accent"], font=FONTS["small_bold"])
            else:
                btn.config(bg=COLORS["card_border"], fg=COLORS["text_primary"], font=FONTS["small"])

        style_btn(self._btn_filter_all,  filter_name == "all")
        style_btn(self._btn_filter_fav,  filter_name == "fav")
        style_btn(self._btn_filter_emer, filter_name == "emer")

        self.refresh()

    def refresh(self):
        """Reload contacts and apply current search and filter."""
        query = self._search_var.get().strip() if hasattr(self, "_search_var") else ""
        contacts = search_contacts(query) if query else fetch_all_contacts()

        # Apply quick filter
        if self._current_filter == "fav":
            contacts = [c for c in contacts if c.is_favourite]
        elif self._current_filter == "emer":
            contacts = [c for c in contacts if c.is_emergency]

        self._contacts = contacts
        self._populate_tree(self._contacts)
        self._clear_detail()
        self._selected_id = None
        self._toggle_buttons(enabled=False)

    def _populate_tree(self, contacts: List[Contact]):
        """Clear and repopulate treeview rows."""
        for row in self._tree.get_children():
            self._tree.delete(row)

        for i, c in enumerate(contacts):
            tag = "even" if i % 2 == 0 else "odd"
            fav  = "⭐" if c.is_favourite else ""
            emer = "🚨" if c.is_emergency else ""
            updated = c.updated_at[:10] if len(c.updated_at) >= 10 else c.updated_at
            groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else ""

            self._tree.insert(
                "", "end",
                iid=str(c.id),
                values=(c.full_name, c.phone, c.email, groups_str, fav, emer, updated),
                tags=(tag,),
            )

        total = len(contacts)
        noun = "contact" if total == 1 else "contacts"
        self._count_var.set(f"{total} {noun}")

    def _on_search_change(self, *_args):
        self.refresh()

    def _clear_search(self):
        self._search_var.set("")

    # ------------------------------------------------------------------
    # Selection & detail panel
    # ------------------------------------------------------------------

    def _on_select(self, _event=None):
        selected = self._tree.selection()
        if not selected:
            return
        contact_id = int(selected[0])
        self._selected_id = contact_id
        contact = fetch_contact(contact_id)
        if contact:
            self._show_detail(contact)
            self._toggle_buttons(enabled=True)

    def _show_detail(self, c: Contact):
        self._detail_labels["name"].config(text=c.full_name or "—")
        self._detail_labels["phone"].config(text=c.phone or "—")

        # Secondary phone numbers
        if c.extra_phones:
            extras = "\n".join(f"• {p['label']}: {p['number']}" for p in c.extra_phones)
            self._detail_labels["extra_phones"].config(text=extras)
        else:
            self._detail_labels["extra_phones"].config(text="None")

        self._detail_labels["email"].config(text=c.email or "—")

        # Groups
        if c.groups:
            g_names = ", ".join(g["name"] for g in c.groups)
            self._detail_labels["groups"].config(text=g_names)
        else:
            self._detail_labels["groups"].config(text="None")

        self._detail_labels["address"].config(text=c.address or "—")
        self._detail_labels["notes"].config(text=c.notes or "—")
        self._detail_labels["created"].config(text=c.created_at or "—")
        self._detail_labels["updated"].config(text=c.updated_at or "—")

        # Badges
        self._fav_badge.config(
            text="⭐ Favourite" if c.is_favourite else "",
            fg=COLORS["favourite"], font=FONTS["small_bold"]
        )
        self._emer_badge.config(
            text="🚨 Emergency" if c.is_emergency else "",
            fg=COLORS["danger"], font=FONTS["small_bold"]
        )

        # Quick action button labels
        self._toggle_fav_btn.config(
            text="★ Unfavourite" if c.is_favourite else "⭐ Favourite",
            state="normal"
        )
        self._toggle_emer_btn.config(
            text="Remove Emergency" if c.is_emergency else "🚨 Set Emergency",
            state="normal"
        )

    def _clear_detail(self):
        for lbl in self._detail_labels.values():
            lbl.config(text="—")
        self._fav_badge.config(text="")
        self._emer_badge.config(text="")
        self._toggle_fav_btn.config(state="disabled")
        self._toggle_emer_btn.config(state="disabled")

    def _toggle_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._edit_btn.config(state=state)
        self._delete_btn.config(state=state)

    # ------------------------------------------------------------------
    # Quick Toggle Actions
    # ------------------------------------------------------------------

    def _toggle_favourite_selected(self):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id)
        if not contact:
            return
        new_status = not contact.is_favourite
        ok, msg = toggle_favourite(self._selected_id, new_status)
        if ok:
            # Refresh and reselect
            cur_id = self._selected_id
            self.refresh()
            if self._tree.exists(str(cur_id)):
                self._tree.selection_set(str(cur_id))
                self._on_select()

    def _toggle_emergency_selected(self):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id)
        if not contact:
            return
        new_status = not contact.is_emergency
        ok, msg = toggle_emergency(self._selected_id, new_status)
        if ok:
            cur_id = self._selected_id
            self.refresh()
            if self._tree.exists(str(cur_id)):
                self._tree.selection_set(str(cur_id))
                self._on_select()

    # ------------------------------------------------------------------
    # Actions: Add, Edit, Delete, Import, Export
    # ------------------------------------------------------------------

    def _quick_export_csv(self):
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Export Contacts to CSV",
            defaultextension=".csv",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")],
            initialfile="contacts_export.csv"
        )
        if not filename:
            return
        ok, msg, count = export_contacts_to_csv(filename)
        if ok:
            messagebox.showinfo("Export Successful", msg, parent=self)
        else:
            messagebox.showerror("Export Failed", msg, parent=self)

    def _quick_import_csv(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="Select CSV File to Import",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if not filename:
            return
        summary = import_contacts_from_csv(filename)
        msg = (
            f"Import Processed:\n"
            f"• Total Rows: {summary['total']}\n"
            f"• Successfully Imported: {summary['imported']}\n"
            f"• Skipped (Duplicates): {summary['skipped']}\n"
            f"• Failed (Invalid): {summary['failed']}"
        )
        if summary["errors"]:
            msg += "\n\nFirst Errors:\n" + "\n".join(summary["errors"][:5])

        if summary["imported"] > 0:
            messagebox.showinfo("Import Summary", msg, parent=self)
            self.refresh()
        elif summary["total"] == 0 and summary["errors"]:
            messagebox.showerror("Import Failed", "\n".join(summary["errors"]), parent=self)
        else:
            messagebox.showwarning("Import Summary", msg, parent=self)

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
            f"Are you sure you want to delete '{contact.full_name}'?\n\n"
            "This will delete all associated phone numbers as well.\n"
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

    # ------------------------------------------------------------------
    # Sorting
    # ------------------------------------------------------------------

    def _sort_by(self, col_id: str):
        col_map = {
            "name":    lambda c: c.full_name.lower(),
            "phone":   lambda c: c.phone,
            "email":   lambda c: c.email.lower(),
            "groups":  lambda c: len(c.groups),
            "fav":     lambda c: not c.is_favourite,
            "emer":    lambda c: not c.is_emergency,
            "updated": lambda c: c.updated_at,
        }
        key_fn = col_map.get(col_id, lambda c: c.full_name.lower())

        current_dir = getattr(self, "_sort_dir", {})
        asc = not current_dir.get(col_id, False)
        current_dir[col_id] = asc
        self._sort_dir = current_dir

        self._contacts.sort(key=key_fn, reverse=not asc)
        self._populate_tree(self._contacts)
