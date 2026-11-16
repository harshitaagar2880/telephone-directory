"""
gui/pages/contacts_page.py
---------------------------
All Contacts page.
Features:
  - Advanced Search across name, email, and primary/secondary phone numbers
  - Sorting: Name (A-Z), Name (Z-A), Recently Updated, Oldest First
  - Filtering: Quick filters (All, Favourites, Emergency) + Custom Group dropdown filter
  - Duplicate Detection: Interactive duplicate review dialog
  - Speed Dial Assignment: Direct button to assign or clear speed dial slots
  - Automatic Recently Viewed tracking
  - Detail panel with full secondary phones, groups, and actions
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from typing import Optional, List, Dict, Any

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from gui.contact_form import ContactFormDialog
from models.contact import Contact
from services.contact_service import (
    fetch_all_contacts, search_contacts, remove_contact, fetch_contact,
    toggle_favourite, toggle_emergency, fetch_all_groups,
    record_contact_viewed, fetch_contact_speed_dial, assign_speed_dial,
    clear_speed_dial, detect_duplicate_contacts, fetch_contacts_filtered_and_sorted
)
from services.data_service import export_contacts_to_csv, import_contacts_from_csv


class DuplicateReviewDialog(tk.Toplevel):
    """
    Modal dialog allowing users to review potential duplicate contacts.
    Never merges or deletes automatically — gives full control to the user.
    """

    def __init__(self, parent, on_change=None):
        super().__init__(parent)
        self.title("Duplicate Contacts Review")
        self.resizable(True, True)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()
        self._on_change = on_change

        w, h = 820, 540
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")
        self.minsize(700, 400)

        self._clusters = detect_duplicate_contacts()
        self._build_ui()

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg=COLORS["primary"], height=50)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)

        tk.Label(
            hdr, text="🔍 Review Duplicate Contacts",
            font=FONTS["page_title"], fg=COLORS["text_on_accent"],
            bg=COLORS["primary"]
        ).pack(side="left", padx=20, pady=10)

        # Informational note
        note = tk.Label(
            self,
            text="Safety Guarantee: Contacts are never merged or deleted automatically. Review the matching clusters below.",
            font=FONTS["small"], fg=COLORS["text_secondary"], bg=COLORS["card_bg"],
            padx=20, pady=8, anchor="w"
        )
        note.pack(fill="x")

        horizontal_separator(self).pack(fill="x", padx=20)

        if not self._clusters:
            empty_box = tk.Frame(self, bg=COLORS["card_bg"], padx=30, pady=40)
            empty_box.pack(fill="both", expand=True)

            tk.Label(
                empty_box, text="🎉 No Duplicates Detected!",
                font=FONTS["page_title"], fg=COLORS["success"],
                bg=COLORS["card_bg"]
            ).pack(pady=(20, 8))

            tk.Label(
                empty_box,
                text="All contact names, phone numbers, and email addresses appear completely unique.",
                font=FONTS["body"], fg=COLORS["text_secondary"],
                bg=COLORS["card_bg"]
            ).pack()

            make_button(
                empty_box, text="Close", command=self.destroy,
                style="primary", width=12
            ).pack(pady=20)
            return

        # Main split: Left cluster list, Right contacts comparison
        split_pane = tk.Frame(self, bg=COLORS["card_bg"])
        split_pane.pack(fill="both", expand=True, padx=20, pady=10)

        # Left pane: cluster list
        left_frame = tk.Frame(split_pane, bg=COLORS["main_bg"], width=280,
                              highlightthickness=1, highlightbackground=COLORS["card_border"])
        left_frame.pack(side="left", fill="y", padx=(0, 10))
        left_frame.pack_propagate(False)

        tk.Label(
            left_frame, text=f"Potential Clusters ({len(self._clusters)})",
            font=FONTS["small_bold"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"], padx=10, pady=8
        ).pack(anchor="w")

        self._cluster_tree = ttk.Treeview(
            left_frame, style="Contacts.Treeview", selectmode="browse",
            show="headings", columns=["reason"]
        )
        self._cluster_tree.heading("reason", text="Matching Criteria")
        self._cluster_tree.column("reason", width=260, anchor="w")
        self._cluster_tree.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        self._cluster_tree.bind("<<TreeviewSelect>>", self._on_cluster_select)

        for i, cl in enumerate(self._clusters):
            self._cluster_tree.insert(
                "", "end", iid=str(i),
                values=(f"{cl['type']}: {cl['value']} ({len(cl['contacts'])})",)
            )

        # Right pane: details of contacts in selected cluster
        right_frame = tk.Frame(split_pane, bg=COLORS["card_bg"],
                               highlightthickness=1, highlightbackground=COLORS["card_border"])
        right_frame.pack(side="right", fill="both", expand=True)

        self._cluster_title = tk.Label(
            right_frame, text="Select a cluster on the left to inspect",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["card_bg"], padx=15, pady=10
        )
        self._cluster_title.pack(anchor="w")

        horizontal_separator(right_frame).pack(fill="x", padx=10)

        # Scrollable container for contact cards
        canvas = tk.Canvas(right_frame, bg=COLORS["card_bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(right_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        self._cards_container = tk.Frame(canvas, bg=COLORS["card_bg"], padx=10, pady=10)
        c_id = canvas.create_window((0, 0), window=self._cards_container, anchor="nw")

        def _conf(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(c_id, width=canvas.winfo_width())
        self._cards_container.bind("<Configure>", _conf)
        canvas.bind("<Configure>", _conf)

        if self._clusters:
            self._cluster_tree.selection_set("0")
            self._on_cluster_select()

    def _on_cluster_select(self, _event=None):
        sel = self._cluster_tree.selection()
        if not sel:
            return
        idx = int(sel[0])
        cluster = self._clusters[idx]
        self._cluster_title.config(text=f"Reason: {cluster['reason']}")

        for w in self._cards_container.winfo_children():
            w.destroy()

        for c in cluster["contacts"]:
            self._build_duplicate_contact_card(self._cards_container, c)

    def _build_duplicate_contact_card(self, parent, contact: Contact):
        card = tk.Frame(
            parent, bg=COLORS["main_bg"], padx=15, pady=10,
            highlightthickness=1, highlightbackground=COLORS["card_border"]
        )
        card.pack(fill="x", pady=5)

        # Header with ID and Name
        top_row = tk.Frame(card, bg=COLORS["main_bg"])
        top_row.pack(fill="x", pady=(0, 4))

        tk.Label(
            top_row, text=f"ID #{contact.id}: {contact.full_name}",
            font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["main_bg"]
        ).pack(side="left")

        # Edit and Delete buttons on card
        del_btn = tk.Button(
            top_row, text="🗑 Delete", font=FONTS["small"],
            bg=COLORS["danger_light"], fg=COLORS["danger"],
            relief="flat", bd=0, padx=6, pady=2, cursor="hand2",
            command=lambda cid=contact.id, name=contact.full_name: self._delete_contact(cid, name)
        )
        del_btn.pack(side="right")

        edit_btn = tk.Button(
            top_row, text="✏ Edit", font=FONTS["small"],
            bg=COLORS["primary_light"], fg=COLORS["primary"],
            relief="flat", bd=0, padx=6, pady=2, cursor="hand2",
            command=lambda c=contact: self._edit_contact(c)
        )
        edit_btn.pack(side="right", padx=(0, 6))

        # Details
        info_lines = [
            f"Phone: {contact.phone}" + (f" (Other: {', '.join(p['number'] for p in contact.extra_phones)})" if contact.extra_phones else ""),
            f"Email: {contact.email or 'None'} | Address: {contact.address or 'None'}",
            f"Groups: {', '.join(g['name'] for g in contact.groups) if contact.groups else 'None'} | Last Updated: {contact.updated_at[:10]}"
        ]
        for line in info_lines:
            tk.Label(
                card, text=line, font=FONTS["small"],
                fg=COLORS["text_secondary"], bg=COLORS["main_bg"], anchor="w"
            ).pack(fill="x")

    def _edit_contact(self, contact: Contact):
        ContactFormDialog(self, contact=contact, on_save=self._refresh_data)

    def _delete_contact(self, contact_id: int, name: str):
        if messagebox.askyesno("Confirm Delete", f"Delete duplicate contact '{name}' (ID #{contact_id})?", parent=self):
            ok, msg = remove_contact(contact_id)
            if ok:
                self._refresh_data()

    def _refresh_data(self):
        if self._on_change:
            self._on_change()
        # Re-detect clusters
        self._clusters = detect_duplicate_contacts()
        for w in self.winfo_children():
            w.destroy()
        self._build_ui()


class SpeedDialSlotDialog(tk.Toplevel):
    """Dialog allowing user to choose a speed dial slot (1-9) for a contact."""

    def __init__(self, parent, contact: Contact, current_slot: Optional[int] = None, on_save=None):
        super().__init__(parent)
        self.title("Speed Dial Assignment")
        self.resizable(False, False)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()

        self._contact = contact
        self._current_slot = current_slot
        self._on_save = on_save

        w, h = 380, 280
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(self, bg=COLORS["primary"], height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text=f"⚡ Speed Dial: {contact.full_name}",
            font=FONTS["section"], fg=COLORS["text_on_accent"], bg=COLORS["primary"]
        ).pack(side="left", padx=15, pady=12)

        body = tk.Frame(self, bg=COLORS["card_bg"], padx=20, pady=15)
        body.pack(fill="both", expand=True)

        tk.Label(
            body, text="Select Speed Dial Slot (1 through 9):",
            font=FONTS["small_bold"], fg=COLORS["text_secondary"], bg=COLORS["card_bg"]
        ).pack(anchor="w", pady=(0, 8))

        self._slot_var = tk.IntVar(value=current_slot if current_slot else 1)
        slot_box = tk.Frame(body, bg=COLORS["card_bg"])
        slot_box.pack(fill="x", pady=(0, 15))

        for s in range(1, 10):
            r = (s - 1) // 5
            c = (s - 1) % 5
            rb = tk.Radiobutton(
                slot_box, text=f"#{s}", value=s, variable=self._slot_var,
                font=FONTS["small_bold"], bg=COLORS["card_bg"],
                selectcolor=COLORS["card_bg"], activebackground=COLORS["card_bg"],
                cursor="hand2"
            )
            rb.grid(row=r, column=c, padx=4, pady=4, sticky="w")

        btn_box = tk.Frame(body, bg=COLORS["card_bg"])
        btn_box.pack(fill="x", pady=(10, 0))

        make_button(
            btn_box, text="Save Slot",
            command=self._on_save_slot, style="primary", width=12
        ).pack(side="left", padx=(0, 6))

        if current_slot:
            make_button(
                btn_box, text="Clear Slot",
                command=self._on_clear_slot, style="danger", width=10
            ).pack(side="left", padx=(0, 6))

        make_button(
            btn_box, text="Cancel",
            command=self.destroy, style="secondary", width=8
        ).pack(side="left")

    def _on_save_slot(self):
        slot = self._slot_var.get()
        ok, msg = assign_speed_dial(slot, self._contact.id)
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            if self._on_save:
                self._on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _on_clear_slot(self):
        if self._current_slot:
            ok, msg = clear_speed_dial(self._current_slot)
            if ok:
                messagebox.showinfo("Cleared", msg, parent=self)
                if self._on_save:
                    self._on_save()
                self.destroy()


class ContactsPage(tk.Frame):
    """
    Main contacts management page.
    """

    COLUMNS = [
        ("name",      "Full Name",    190, "w"),
        ("phone",     "Primary Phone",130, "w"),
        ("email",     "Email",        160, "w"),
        ("groups",    "Groups",       120, "w"),
        ("speed_dial","⚡",            35,  "center"),
        ("fav",       "⭐",            35,  "center"),
        ("emer",      "🚨",            35,  "center"),
        ("updated",   "Last Updated", 100, "center"),
    ]

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._selected_id: Optional[int] = None
        self._contacts: List[Contact] = []
        self._current_filter: str = "all"  # "all" | "fav" | "emer"
        self._current_group_id: Optional[int] = None
        self._current_sort: str = "name_asc"
        self._groups_map = {}

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ---- Top bar ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(18, 5))

        tk.Label(
            topbar, text="All Contacts",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        actions_box = tk.Frame(topbar, bg=COLORS["main_bg"])
        actions_box.pack(side="right")

        make_button(
            actions_box, text="🔍  Find Duplicates",
            command=self._open_duplicate_review,
            style="secondary", width=16
        ).pack(side="left", padx=(0, 6))

        make_button(
            actions_box, text="📥  Import CSV",
            command=self._quick_import_csv,
            style="secondary", width=12
        ).pack(side="left", padx=(0, 6))

        make_button(
            actions_box, text="📤  Export CSV",
            command=self._quick_export_csv,
            style="secondary", width=12
        ).pack(side="left", padx=(0, 6))

        make_button(
            actions_box, text="＋  Add Contact",
            command=self._open_add_form,
            style="primary", width=14
        ).pack(side="left")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 8))

        # ---- Controls bar: Search + Quick Filters + Group Dropdown + Sort Dropdown ----
        controls_frame = tk.Frame(self, bg=COLORS["main_bg"])
        controls_frame.pack(fill="x", padx=30, pady=(0, 8))

        # Search bar
        tk.Label(
            controls_frame, text="🔍",
            font=FONTS["body"], bg=COLORS["main_bg"]
        ).pack(side="left", padx=(0, 4))

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)

        search_entry = tk.Entry(
            controls_frame,
            textvariable=self._search_var,
            font=FONTS["input"], width=22,
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
        )
        search_entry.pack(side="left", ipady=3)

        make_button(
            controls_frame, text="Clear",
            command=self._clear_search,
            style="secondary", width=5
        ).pack(side="left", padx=(4, 12))

        # Filter buttons
        filter_box = tk.Frame(controls_frame, bg=COLORS["main_bg"])
        filter_box.pack(side="left", padx=(0, 10))

        self._btn_filter_all = tk.Button(
            filter_box, text="All", font=FONTS["small_bold"],
            bg=COLORS["primary"], fg=COLORS["text_on_accent"],
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
            command=lambda: self._set_filter("all")
        )
        self._btn_filter_all.pack(side="left", padx=2)

        self._btn_filter_fav = tk.Button(
            filter_box, text="⭐ Favourites", font=FONTS["small"],
            bg=COLORS["card_border"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
            command=lambda: self._set_filter("fav")
        )
        self._btn_filter_fav.pack(side="left", padx=2)

        self._btn_filter_emer = tk.Button(
            filter_box, text="🚨 Emergency", font=FONTS["small"],
            bg=COLORS["card_border"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=8, pady=3, cursor="hand2",
            command=lambda: self._set_filter("emer")
        )
        self._btn_filter_emer.pack(side="left", padx=2)

        # Group Dropdown Filter
        tk.Label(controls_frame, text="Group:", font=FONTS["small_bold"],
                 fg=COLORS["text_secondary"], bg=COLORS["main_bg"]).pack(side="left", padx=(8, 3))

        self._group_filter_var = tk.StringVar(value="All Groups")
        self._group_dropdown = ttk.Combobox(
            controls_frame, textvariable=self._group_filter_var,
            state="readonly", width=13, font=FONTS["small"]
        )
        self._group_dropdown.pack(side="left", padx=(0, 10), ipady=1)
        self._group_dropdown.bind("<<ComboboxSelected>>", self._on_group_filter_change)

        # Sort Dropdown
        tk.Label(controls_frame, text="Sort:", font=FONTS["small_bold"],
                 fg=COLORS["text_secondary"], bg=COLORS["main_bg"]).pack(side="left", padx=(4, 3))

        self._sort_var = tk.StringVar(value="Name (A–Z)")
        self._sort_dropdown = ttk.Combobox(
            controls_frame, textvariable=self._sort_var,
            state="readonly", width=15, font=FONTS["small"],
            values=["Name (A–Z)", "Name (Z–A)", "Recently Updated", "Oldest First"]
        )
        self._sort_dropdown.pack(side="left", ipady=1)
        self._sort_dropdown.bind("<<ComboboxSelected>>", self._on_sort_change)

        # ---- Main content: Treeview + Detail panel ----
        content = tk.Frame(self, bg=COLORS["main_bg"])
        content.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self._build_treeview(content)
        self._build_detail_panel(content)

        # ---- Bottom action bar ----
        self._build_action_bar()

    def _build_treeview(self, parent):
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
        self._detail_frame = tk.Frame(
            parent, bg=COLORS["card_bg"], width=290,
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
            ).pack(anchor="w", padx=10, pady=(5, 1))

            lbl = tk.Label(
                d_body, text="—",
                font=FONTS["small"], fg=COLORS["text_primary"],
                bg=COLORS["card_bg"], anchor="w",
                wraplength=250, justify="left"
            )
            lbl.pack(anchor="w", padx=10)
            self._detail_labels[key] = lbl

        # Badges row (Speed Dial, Fav, Emer)
        self._badge_frame = tk.Frame(d_body, bg=COLORS["card_bg"])
        self._badge_frame.pack(anchor="w", padx=10, pady=(8, 4))
        self._sd_badge   = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._fav_badge  = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._emer_badge = tk.Label(self._badge_frame, text="", bg=COLORS["card_bg"])
        self._sd_badge.pack(side="left", padx=(0, 6))
        self._fav_badge.pack(side="left", padx=(0, 6))
        self._emer_badge.pack(side="left")

        # Quick action buttons on detail panel
        self._quick_action_frame = tk.Frame(d_body, bg=COLORS["card_bg"])
        self._quick_action_frame.pack(fill="x", padx=10, pady=(8, 10))

        self._toggle_fav_btn = tk.Button(
            self._quick_action_frame, text="⭐ Favourite",
            font=FONTS["small"], bg=COLORS["warning_light"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=5, pady=3, cursor="hand2",
            command=self._toggle_favourite_selected, state="disabled"
        )
        self._toggle_fav_btn.pack(side="left", padx=(0, 4))

        self._toggle_emer_btn = tk.Button(
            self._quick_action_frame, text="🚨 Emergency",
            font=FONTS["small"], bg=COLORS["danger_light"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=5, pady=3, cursor="hand2",
            command=self._toggle_emergency_selected, state="disabled"
        )
        self._toggle_emer_btn.pack(side="left", padx=(0, 4))

        self._speed_dial_btn = tk.Button(
            self._quick_action_frame, text="⚡ Speed Dial",
            font=FONTS["small"], bg=COLORS["primary_light"], fg=COLORS["primary"],
            relief="flat", bd=0, padx=5, pady=3, cursor="hand2",
            command=self._open_speed_dial_dialog, state="disabled"
        )
        self._speed_dial_btn.pack(side="left")

        self._clear_detail()

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

        self._count_var = tk.StringVar(value="0 contacts")
        tk.Label(
            bar, textvariable=self._count_var,
            font=FONTS["small"], fg=COLORS["text_secondary"],
            bg=COLORS["main_bg"]
        ).pack(side="right")

    # ------------------------------------------------------------------
    # Filtering, Sorting & Data loading
    # ------------------------------------------------------------------

    def _set_filter(self, filter_name: str):
        self._current_filter = filter_name

        def style_btn(btn, active):
            if active:
                btn.config(bg=COLORS["primary"], fg=COLORS["text_on_accent"], font=FONTS["small_bold"])
            else:
                btn.config(bg=COLORS["card_border"], fg=COLORS["text_primary"], font=FONTS["small"])

        style_btn(self._btn_filter_all,  filter_name == "all")
        style_btn(self._btn_filter_fav,  filter_name == "fav")
        style_btn(self._btn_filter_emer, filter_name == "emer")

        self.refresh()

    def _on_group_filter_change(self, _event=None):
        selected_name = self._group_filter_var.get()
        if selected_name == "All Groups":
            self._current_group_id = None
        else:
            self._current_group_id = self._groups_map.get(selected_name)
        self.refresh()

    def _on_sort_change(self, _event=None):
        sort_choice = self._sort_var.get()
        mapping = {
            "Name (A–Z)": "name_asc",
            "Name (Z–A)": "name_desc",
            "Recently Updated": "date_desc",
            "Oldest First": "date_asc"
        }
        self._current_sort = mapping.get(sort_choice, "name_asc")
        self.refresh()

    def refresh(self):
        """Update group dropdown options, reload contacts, apply search, sort & filters."""
        # Refresh group dropdown list
        all_groups = fetch_all_groups()
        self._groups_map = {g["name"]: g["id"] for g in all_groups}
        dropdown_vals = ["All Groups"] + [g["name"] for g in all_groups]
        self._group_dropdown.config(values=dropdown_vals)

        query = self._search_var.get().strip() if hasattr(self, "_search_var") else ""

        # Fetch filtered and sorted
        self._contacts = fetch_contacts_filtered_and_sorted(
            search_query=query,
            filter_type=self._current_filter,
            group_id=self._current_group_id,
            sort_by=self._current_sort
        )

        self._populate_tree(self._contacts)
        self._clear_detail()
        self._selected_id = None
        self._toggle_buttons(enabled=False)

    def _populate_tree(self, contacts: List[Contact]):
        for row in self._tree.get_children():
            self._tree.delete(row)

        for i, c in enumerate(contacts):
            tag = "even" if i % 2 == 0 else "odd"
            fav  = "⭐" if c.is_favourite else ""
            emer = "🚨" if c.is_emergency else ""
            sd_slot = fetch_contact_speed_dial(c.id)
            sd_str = f"#{sd_slot}" if sd_slot else ""
            updated = c.updated_at[:10] if len(c.updated_at) >= 10 else c.updated_at
            groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else ""

            self._tree.insert(
                "", "end",
                iid=str(c.id),
                values=(c.full_name, c.phone, c.email, groups_str, sd_str, fav, emer, updated),
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
    # Selection & detail panel (with recently viewed recording)
    # ------------------------------------------------------------------

    def _on_select(self, _event=None):
        selected = self._tree.selection()
        if not selected:
            return
        contact_id = int(selected[0])
        self._selected_id = contact_id
        contact = fetch_contact(contact_id)
        if contact:
            # Record recently viewed
            record_contact_viewed(contact_id)
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
        sd_slot = fetch_contact_speed_dial(c.id)
        self._sd_badge.config(
            text=f"⚡ Speed Dial #{sd_slot}" if sd_slot else "",
            fg=COLORS["primary"], font=FONTS["small_bold"]
        )
        self._fav_badge.config(
            text="⭐ Favourite" if c.is_favourite else "",
            fg=COLORS["favourite"], font=FONTS["small_bold"]
        )
        self._emer_badge.config(
            text="🚨 Emergency" if c.is_emergency else "",
            fg=COLORS["danger"], font=FONTS["small_bold"]
        )

        self._toggle_fav_btn.config(
            text="★ Unfavourite" if c.is_favourite else "⭐ Favourite",
            state="normal"
        )
        self._toggle_emer_btn.config(
            text="Remove Emergency" if c.is_emergency else "🚨 Set Emergency",
            state="normal"
        )
        self._speed_dial_btn.config(state="normal")

    def _clear_detail(self):
        for lbl in self._detail_labels.values():
            lbl.config(text="—")
        self._sd_badge.config(text="")
        self._fav_badge.config(text="")
        self._emer_badge.config(text="")
        self._toggle_fav_btn.config(state="disabled")
        self._toggle_emer_btn.config(state="disabled")
        self._speed_dial_btn.config(state="disabled")

    def _toggle_buttons(self, enabled: bool):
        state = "normal" if enabled else "disabled"
        self._edit_btn.config(state=state)
        self._delete_btn.config(state=state)

    # ------------------------------------------------------------------
    # Quick Actions
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

    def _open_speed_dial_dialog(self):
        if self._selected_id is None:
            return
        contact = fetch_contact(self._selected_id)
        if not contact:
            return
        current_slot = fetch_contact_speed_dial(self._selected_id)
        SpeedDialSlotDialog(self, contact=contact, current_slot=current_slot, on_save=self.refresh)

    def _open_duplicate_review(self):
        DuplicateReviewDialog(self, on_change=self.refresh)

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
            "Move to Trash",
            f"Are you sure you want to move '{contact.full_name}' to the Trash?\n\n"
            "The contact will be moved to the Recycle Bin where you can restore it later.\n"
            "All associated phone numbers and group memberships will be preserved.",
            icon="warning"
        )
        if not confirmed:
            return

        ok, msg = remove_contact(self._selected_id)
        if ok:
            messagebox.showinfo("Moved to Trash", msg)
            self._selected_id = None
            self.refresh()
        else:
            messagebox.showerror("Error", msg)

    def _sort_by(self, col_id: str):
        # Column header click sorting toggles
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
