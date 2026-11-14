"""
gui/pages/favourites_page.py
-----------------------------
Dedicated page showing all Favourite Contacts.
Allows:
  - Viewing favourite contacts
  - Removing a contact from favourites directly
  - Viewing full contact details and secondary phone numbers
  - Editing and deleting favourite contacts
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from gui.contact_form import ContactFormDialog
from models.contact import Contact
from services.contact_service import (
    fetch_favourite_contacts, remove_contact, fetch_contact, toggle_favourite
)


class FavouritesPage(tk.Frame):
    """
    Dedicated Favourites contacts page.
    """

    COLUMNS = [
        ("name",    "Full Name",     220, "w"),
        ("phone",   "Primary Phone", 140, "w"),
        ("email",   "Email",         180, "w"),
        ("groups",  "Groups",        130, "w"),
        ("emer",    "🚨",             40, "center"),
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
            title_box, text="⭐ Favourite Contacts",
            font=FONTS["page_title"], fg=COLORS["favourite"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        self._count_badge = tk.Label(
            title_box, text="0",
            font=FONTS["small_bold"], bg=COLORS["warning_light"],
            fg=COLORS["favourite"], padx=8, pady=2
        )
        self._count_badge.pack(side="left", padx=10)

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 15))

        # ---- Main content: Treeview + Detail panel ----
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

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self._tree.yview, style="Vertical.TScrollbar")
        self._tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._tree.pack(fill="both", expand=True)

        self._tree.bind("<<TreeviewSelect>>", self._on_select)
        self._tree.bind("<Double-1>",          self._open_edit_form)

        # Right: Detail panel
        self._build_detail_panel(content)

        # Bottom action bar
        self._build_action_bar()

    def _build_detail_panel(self, parent):
        self._detail_frame = tk.Frame(
            parent, bg=COLORS["card_bg"], width=280,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"]
        )
        self._detail_frame.pack(side="right", fill="y", padx=(10, 0))
        self._detail_frame.pack_propagate(False)

        tk.Label(
            self._detail_frame, text="Favourite Details",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", padx=15, pady=(12, 4))

        horizontal_separator(self._detail_frame).pack(fill="x", padx=10)

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

        # Quick action on detail panel: Remove from favourites
        self._unfav_btn = tk.Button(
            d_body, text="★ Remove from Favourites",
            font=FONTS["small_bold"], bg=COLORS["warning_light"],
            fg=COLORS["favourite"], relief="flat", bd=0, padx=8, pady=5,
            cursor="hand2", command=self._remove_from_favourites, state="disabled"
        )
        self._unfav_btn.pack(anchor="w", padx=10, pady=(15, 10))

    def _build_action_bar(self):
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

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def refresh(self):
        self._contacts = fetch_favourite_contacts()
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
            emer = "🚨" if c.is_emergency else ""
            groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else ""

            self._tree.insert(
                "", "end",
                iid=str(c.id),
                values=(c.full_name, c.phone, c.email, groups_str, emer),
                tags=(tag,),
            )

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

        if c.extra_phones:
            extras = "\n".join(f"• {p['label']}: {p['number']}" for p in c.extra_phones)
            self._detail_labels["extra_phones"].config(text=extras)
        else:
            self._detail_labels["extra_phones"].config(text="None")

        self._detail_labels["email"].config(text=c.email or "—")
        groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else "None"
        self._detail_labels["groups"].config(text=groups_str)
        self._detail_labels["address"].config(text=c.address or "—")
        self._detail_labels["notes"].config(text=c.notes or "—")

        self._unfav_btn.config(state="normal")

    def _clear_detail(self):
        for lbl in self._detail_labels.values():
            lbl.config(text="—")
        self._unfav_btn.config(state="disabled")

    def _toggle_buttons(self, enabled: bool):
        st = "normal" if enabled else "disabled"
        self._edit_btn.config(state=st)
        self._delete_btn.config(state=st)

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------

    def _remove_from_favourites(self):
        if self._selected_id is None:
            return
        ok, msg = toggle_favourite(self._selected_id, False)
        if ok:
            self.refresh()

    def _open_edit_form(self, _event=None):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id)
        if contact:
            ContactFormDialog(self, contact=contact, on_save=self.refresh)

    def _delete_selected(self):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id)
        if not contact:
            return
        if not messagebox.askyesno("Confirm Delete", f"Delete '{contact.full_name}' permanently?"):
            return
        ok, msg = remove_contact(self._selected_id)
        if ok:
            self.refresh()
