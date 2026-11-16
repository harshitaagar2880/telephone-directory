"""
gui/pages/trash_page.py
------------------------
Dedicated Trash / Recycle Bin page.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from models.contact import Contact
from services.contact_service import (
    fetch_trashed_contacts, restore_contact, purge_contact, fetch_contact,
    check_duplicate
)


class TrashPage(tk.Frame):
    """Dedicated Trash / Recycle Bin page for soft-deleted contacts."""

    COLUMNS = [
        ("name",    "Full Name",     220, "w"),
        ("phone",   "Primary Phone", 150, "w"),
        ("email",   "Email",         180, "w"),
        ("groups",  "Groups",        130, "w"),
        ("deleted", "Deleted At",    150, "center"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._selected_id: Optional[int] = None
        self._contacts: List[Contact] = []
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ---- Top Header ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(20, 5))

        title_box = tk.Frame(topbar, bg=COLORS["main_bg"])
        title_box.pack(side="left")

        tk.Label(
            title_box, text="🗑️ Trash (Recycle Bin)",
            font=FONTS["page_title"], fg=COLORS["danger"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        self._count_badge = tk.Label(
            title_box, text="0",
            font=FONTS["small_bold"], bg=COLORS["danger_light"],
            fg=COLORS["danger"], padx=8, pady=2
        )
        self._count_badge.pack(side="left", padx=10)

        # Info banner
        banner = tk.Frame(self, bg=COLORS["warning_light"], padx=15, pady=8,
                          highlightthickness=1, highlightbackground=COLORS["warning"])
        banner.pack(fill="x", padx=30, pady=(10, 10))

        tk.Label(
            banner,
            text="⚠️ Contacts in the Trash can be restored or permanently deleted. "
                 "Restored contacts keep all their original details, phone numbers, "
                 "favourite/emergency status, and group memberships.",
            font=FONTS["small"], fg=COLORS["text_secondary"],
            bg=COLORS["warning_light"], anchor="w", justify="left"
        ).pack(fill="x")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 15))

        # ---- Main content: Treeview + Action panel ----
        content = tk.Frame(self, bg=COLORS["main_bg"])
        content.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        # Left: Treeview
        tree_frame = tk.Frame(content, bg=COLORS["card_bg"],
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
            self._tree.heading(col_id, text=header)
            self._tree.column(col_id, width=width, anchor=anchor,
                              minwidth=30, stretch=(col_id == "name" or col_id == "email"))

        self._tree.tag_configure("odd",  background=COLORS["tree_odd"])
        self._tree.tag_configure("even", background=COLORS["tree_even"])

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview,
                            style="Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True, padx=5, pady=5)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>", self._restore_selected)

        # Right: Detail panel
        detail_frame = tk.Frame(content, bg=COLORS["card_bg"], width=300,
                                highlightthickness=1,
                                highlightbackground=COLORS["card_border"])
        detail_frame.pack(side="right", fill="y", padx=(10, 0))
        detail_frame.pack_propagate(False)

        detail_inner = tk.Frame(detail_frame, bg=COLORS["card_bg"], padx=20, pady=20)
        detail_inner.pack(fill="both", expand=True)

        tk.Label(
            detail_inner, text="Contact Details",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", pady=(0, 15))

        self._detail_labels = {}
        for field in ("name", "phone", "email", "address", "notes", "groups", "extra_phones"):
            row = tk.Frame(detail_inner, bg=COLORS["card_bg"])
            row.pack(fill="x", pady=3)
            tk.Label(row, text=field.replace("_", " ").title() + ":",
                     font=FONTS["small_bold"], fg=COLORS["text_secondary"],
                     bg=COLORS["card_bg"], width=14, anchor="w").pack(side="left")
            lbl = tk.Label(row, text="—", font=FONTS["body"], fg=COLORS["text_primary"],
                           bg=COLORS["card_bg"], anchor="w", justify="left")
            lbl.pack(side="left", fill="x", expand=True)
            self._detail_labels[field] = lbl

        # Action buttons
        btn_frame = tk.Frame(detail_inner, bg=COLORS["card_bg"])
        btn_frame.pack(fill="x", pady=(25, 0))

        self._restore_btn = make_button(
            btn_frame, text="♻️ Restore", command=self._restore_selected,
            style="success", width=12
        )
        self._restore_btn.pack(side="left", padx=(0, 8))

        self._purge_btn = make_button(
            btn_frame, text="🗑️ Delete Forever", command=self._purge_selected,
            style="danger", width=12
        )
        self._purge_btn.pack(side="left")

        self._restore_btn.config(state="disabled")
        self._purge_btn.config(state="disabled")

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def refresh(self):
        """Reload trashed contacts from the database."""
        self._contacts = fetch_trashed_contacts()
        self._populate_tree(self._contacts)
        self._clear_detail()
        self._selected_id = None
        self._toggle_buttons(enabled=False)
        self._count_badge.config(text=str(len(self._contacts)))

    def _populate_tree(self, contacts: List[Contact]):
        for row in self._tree.get_children():
            self._tree.delete(row)

        for i, c in enumerate(contacts):
            tag = "even" if i % 2 == 0 else "odd"
            groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else "None"
            fav = "⭐" if c.is_favourite else ""
            emer = "🚨" if c.is_emergency else ""
            name_label = c.full_name
            if fav or emer:
                name_label = f"{name_label} {fav}{emer}"
            self._tree.insert(
                "", "end",
                iid=str(c.id),
                values=(name_label, c.phone, c.email, groups_str,
                        c.updated_at or "—"),
                tags=(tag,)
            )

    def _on_select(self, _event=None):
        selected = self._tree.selection()
        if not selected:
            return
        contact_id = int(selected[0])
        self._selected_id = contact_id
        contact = fetch_contact(contact_id, include_deleted=True)
        if contact:
            self._show_detail(contact)
            self._toggle_buttons(enabled=True)

    def _show_detail(self, c: Contact):
        self._detail_labels["name"].config(text=c.full_name or "—")
        self._detail_labels["phone"].config(text=c.phone or "—")
        self._detail_labels["email"].config(text=c.email or "—")
        self._detail_labels["address"].config(text=c.address or "—")
        self._detail_labels["notes"].config(text=c.notes or "—")
        groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else "None"
        self._detail_labels["groups"].config(text=groups_str)
        if c.extra_phones:
            extras = "\n".join(f"• {p['label']}: {p['number']}" for p in c.extra_phones)
            self._detail_labels["extra_phones"].config(text=extras)
        else:
            self._detail_labels["extra_phones"].config(text="None")

    def _clear_detail(self):
        for lbl in self._detail_labels.values():
            lbl.config(text="—")
        self._toggle_buttons(enabled=False)

    def _toggle_buttons(self, enabled: bool):
        st = "normal" if enabled else "disabled"
        self._restore_btn.config(state=st)
        self._purge_btn.config(state=st)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _restore_selected(self, _event=None):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id, include_deleted=True)
        if not contact:
            messagebox.showerror("Error", "Contact not found in Trash.")
            return

        # Check for duplicate conflicts (same name + phone already exists among active contacts)
        if check_duplicate(contact.full_name, contact.phone, exclude_id=self._selected_id):
            result = messagebox.askyesnocancel(
                "Restore Conflict",
                f"A contact with the same name and phone number already exists.\n\n"
                f"Contact: {contact.full_name}\nPhone: {contact.phone}\n\n"
                f"Yes = Restore anyway\nNo = Cancel",
                icon="warning"
            )
            if result is None or result is False:
                return

        ok, msg = restore_contact(self._selected_id)
        if ok:
            messagebox.showinfo("Restored", msg)
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def _purge_selected(self):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id, include_deleted=True)
        if not contact:
            messagebox.showerror("Error", "Contact not found in Trash.")
            return

        confirmed = messagebox.askyesno(
            "Confirm Permanent Deletion",
            f"Are you sure you want to permanently delete '{contact.full_name}'?\n\n"
            "This action CANNOT be undone.\n"
            "All associated phone numbers and group memberships will also be removed.",
            icon="warning"
        )
        if not confirmed:
            return

        ok, msg = purge_contact(self._selected_id)
        if ok:
            messagebox.showinfo("Deleted", msg)
            self.refresh()
        else:
            messagebox.showerror("Error", msg)