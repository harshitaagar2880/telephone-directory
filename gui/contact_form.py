"""
gui/contact_form.py
--------------------
Modal dialog used for both adding and editing contacts.
Supports:
  - Full contact info (name, primary phone, email, address, notes)
  - Dynamic secondary phone numbers with custom labels (Personal, Work, Home, Other)
  - Group assignment via multi-selection checkboxes
  - Favourite (⭐) and Emergency (🚨) toggles
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, Callable, List, Tuple

from gui.theme import COLORS, FONTS
from gui.widgets import LabelledEntry, LabelledText, make_button, horizontal_separator
from models.contact import Contact
from services.contact_service import (
    add_contact, edit_contact, fetch_all_groups, fetch_contact
)


class ContactFormDialog(tk.Toplevel):
    """
    A modal Toplevel window with the full contact form,
    supporting secondary phone numbers and group associations.
    """

    PHONE_LABELS = ["Personal", "Work", "Home", "Other"]

    def __init__(self, parent, contact: Optional[Contact] = None,
                 on_save: Optional[Callable] = None):
        super().__init__(parent)

        self._contact = contact
        self._on_save = on_save
        self._is_edit = contact is not None
        self._phone_rows: List[dict] = []
        self._group_check_vars: dict[int, tk.BooleanVar] = {}

        # --- Window setup ---
        title = "Edit Contact" if self._is_edit else "Add New Contact"
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()          # modal
        self.focus_set()

        # Center on screen
        self.update_idletasks()
        w, h = 540, 680
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui(title)

        # Pre-fill if editing
        if self._is_edit:
            # Re-fetch full details to ensure extra_phones and groups are fresh
            full_c = fetch_contact(contact.id) or contact
            self._populate(full_c)

    # ------------------------------------------------------------------
    # UI construction
    # ------------------------------------------------------------------

    def _build_ui(self, title: str):
        # ---- Header ----
        header = tk.Frame(self, bg=COLORS["primary"], height=55)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Label(
            header, text=title,
            font=FONTS["page_title"], fg=COLORS["text_on_accent"],
            bg=COLORS["primary"]
        ).pack(side="left", padx=20, pady=12)

        # ---- Scrollable body ----
        canvas = tk.Canvas(self, bg=COLORS["card_bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=COLORS["card_bg"], padx=25, pady=15)
        body_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def _on_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(body_id, width=canvas.winfo_width())

        body.bind("<Configure>", _on_configure)
        canvas.bind("<Configure>", _on_configure)

        # Mouse wheel scrolling
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        pad = {"fill": "x", "pady": 5}

        # 1. Full Name
        self._name_entry = LabelledEntry(
            body, label="Full Name", required=True,
            placeholder="e.g. Priya Sharma", width=42
        )
        self._name_entry.pack(**pad)

        # 2. Primary Phone Number
        self._phone_entry = LabelledEntry(
            body, label="Primary Phone Number", required=True,
            placeholder="e.g. +91 98765 43210", width=42
        )
        self._phone_entry.pack(**pad)

        # 3. Secondary Phone Numbers Section
        sec_header = tk.Frame(body, bg=COLORS["card_bg"])
        sec_header.pack(fill="x", pady=(8, 2))
        
        tk.Label(
            sec_header, text="Additional Phone Numbers",
            font=FONTS["small_bold"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"]
        ).pack(side="left")

        add_num_btn = tk.Button(
            sec_header, text="＋ Add Number",
            font=FONTS["small_bold"], fg=COLORS["primary"],
            bg=COLORS["card_bg"], activeforeground=COLORS["primary_hover"],
            activebackground=COLORS["card_bg"], bd=0, cursor="hand2",
            command=self._add_phone_row
        )
        add_num_btn.pack(side="right")

        self._phone_rows_container = tk.Frame(body, bg=COLORS["card_bg"])
        self._phone_rows_container.pack(fill="x", pady=(2, 6))

        # 4. Email
        self._email_entry = LabelledEntry(
            body, label="Email Address",
            placeholder="e.g. priya@example.com", width=42
        )
        self._email_entry.pack(**pad)

        # 5. Address
        self._address_entry = LabelledText(
            body, label="Address", height=2, width=42
        )
        self._address_entry.pack(**pad)

        # 6. Notes
        self._notes_entry = LabelledText(
            body, label="Notes", height=2, width=42
        )
        self._notes_entry.pack(**pad)

        # 7. Groups Assignment Section
        grp_header = tk.Frame(body, bg=COLORS["card_bg"])
        grp_header.pack(fill="x", pady=(10, 2))
        tk.Label(
            grp_header, text="Assign to Groups",
            font=FONTS["small_bold"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"]
        ).pack(side="left")

        self._groups_container = tk.Frame(body, bg=COLORS["main_bg"], padx=10, pady=8,
                                          highlightthickness=1, highlightbackground=COLORS["card_border"])
        self._groups_container.pack(fill="x", pady=(2, 8))
        self._build_group_checkboxes()

        # 8. Toggles (Favourite & Emergency)
        toggle_frame = tk.Frame(body, bg=COLORS["card_bg"])
        toggle_frame.pack(fill="x", pady=8)

        self._favourite_var = tk.BooleanVar()
        self._emergency_var  = tk.BooleanVar()

        tk.Checkbutton(
            toggle_frame, text="⭐  Mark as Favourite",
            variable=self._favourite_var,
            font=FONTS["body"], bg=COLORS["card_bg"],
            fg=COLORS["favourite"], selectcolor=COLORS["card_bg"],
            activebackground=COLORS["card_bg"],
            cursor="hand2",
        ).pack(side="left", padx=(0, 20))

        tk.Checkbutton(
            toggle_frame, text="🚨  Emergency Contact",
            variable=self._emergency_var,
            font=FONTS["body"], bg=COLORS["card_bg"],
            fg=COLORS["emergency"], selectcolor=COLORS["card_bg"],
            activebackground=COLORS["card_bg"],
            cursor="hand2",
        ).pack(side="left")

        # Required note
        tk.Label(
            body, text="* Required fields",
            font=FONTS["small"], fg=COLORS["danger"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", pady=(2, 0))

        # ---- Action buttons ----
        btn_frame = tk.Frame(body, bg=COLORS["card_bg"])
        btn_frame.pack(fill="x", pady=(15, 10))

        label = "Save Changes" if self._is_edit else "Add Contact"
        make_button(
            btn_frame, text=label,
            command=self._on_submit, style="primary", width=16
        ).pack(side="left", padx=(0, 10))

        make_button(
            btn_frame, text="Cancel",
            command=self.destroy, style="secondary", width=10
        ).pack(side="left")

    # ------------------------------------------------------------------
    # Dynamic Phone Rows
    # ------------------------------------------------------------------

    def _add_phone_row(self, label: str = "Work", number: str = ""):
        """Add a secondary phone input row."""
        row_frame = tk.Frame(self._phone_rows_container, bg=COLORS["card_bg"], pady=2)
        row_frame.pack(fill="x")

        # Dropdown for label
        label_var = tk.StringVar(value=label if label in self.PHONE_LABELS else "Other")
        dropdown = ttk.Combobox(
            row_frame, textvariable=label_var,
            values=self.PHONE_LABELS, state="readonly", width=9,
            font=FONTS["small"]
        )
        dropdown.pack(side="left", padx=(0, 6), ipady=2)

        # Phone Entry
        num_entry = tk.Entry(
            row_frame, font=FONTS["input"],
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"]
        )
        if number:
            num_entry.insert(0, number)
        num_entry.pack(side="left", fill="x", expand=True, ipady=3, padx=(0, 6))

        # Delete button for this row
        row_info = {"frame": row_frame, "label_var": label_var, "entry": num_entry}

        del_btn = tk.Button(
            row_frame, text="✕", font=FONTS["small_bold"],
            fg=COLORS["danger"], bg=COLORS["card_bg"], bd=0,
            activeforeground=COLORS["danger_hover"], activebackground=COLORS["card_bg"],
            cursor="hand2", command=lambda r=row_info: self._remove_phone_row(r)
        )
        del_btn.pack(side="right")

        self._phone_rows.append(row_info)

    def _remove_phone_row(self, row_info: dict):
        if row_info in self._phone_rows:
            self._phone_rows.remove(row_info)
            row_info["frame"].destroy()

    # ------------------------------------------------------------------
    # Group Checkboxes
    # ------------------------------------------------------------------

    def _build_group_checkboxes(self):
        """Display all existing groups as checkboxes."""
        for widget in self._groups_container.winfo_children():
            widget.destroy()

        groups = fetch_all_groups()
        if not groups:
            tk.Label(
                self._groups_container, text="No groups created yet.",
                font=FONTS["small"], fg=COLORS["text_secondary"],
                bg=COLORS["main_bg"]
            ).pack(anchor="w")
            return

        cols = 3
        for i, grp in enumerate(groups):
            gid = grp["id"]
            var = tk.BooleanVar(value=False)
            self._group_check_vars[gid] = var

            cb = tk.Checkbutton(
                self._groups_container,
                text=grp["name"],
                variable=var,
                font=FONTS["small"],
                bg=COLORS["main_bg"],
                selectcolor=COLORS["card_bg"],
                activebackground=COLORS["main_bg"],
                cursor="hand2"
            )
            r, c = divmod(i, cols)
            cb.grid(row=r, column=c, sticky="w", padx=8, pady=3)

    # ------------------------------------------------------------------
    # Pre-fill form for edit mode
    # ------------------------------------------------------------------

    def _populate(self, contact: Contact):
        self._name_entry.set(contact.full_name)
        self._phone_entry.set(contact.phone)
        self._email_entry.set(contact.email)
        self._address_entry.set(contact.address)
        self._notes_entry.set(contact.notes)
        self._favourite_var.set(contact.is_favourite)
        self._emergency_var.set(contact.is_emergency)

        # Pre-fill extra phone numbers
        for p in contact.extra_phones:
            self._add_phone_row(label=p.get("label", "Work"), number=p.get("number", ""))

        # Check assigned groups
        assigned_gids = {g["id"] for g in contact.groups if "id" in g}
        for gid, var in self._group_check_vars.items():
            if gid in assigned_gids:
                var.set(True)

    # ------------------------------------------------------------------
    # Form submission
    # ------------------------------------------------------------------

    def _on_submit(self):
        """Collect field values, validate, call service, show result."""
        full_name    = self._name_entry.get().strip()
        phone        = self._phone_entry.get().strip()
        email        = self._email_entry.get().strip()
        address      = self._address_entry.get().strip()
        notes        = self._notes_entry.get().strip()
        is_favourite = self._favourite_var.get()
        is_emergency = self._emergency_var.get()

        # Collect secondary phone numbers
        extra_phones: List[Tuple[str, str]] = []
        for row in self._phone_rows:
            lbl = row["label_var"].get().strip()
            num = row["entry"].get().strip()
            if num:
                extra_phones.append((lbl, num))

        # Collect assigned group ids
        selected_group_ids = [
            gid for gid, var in self._group_check_vars.items()
            if var.get()
        ]

        if self._is_edit:
            ok, msg = edit_contact(
                contact_id   = self._contact.id,
                full_name    = full_name,
                phone        = phone,
                email        = email,
                address      = address,
                notes        = notes,
                is_favourite = is_favourite,
                is_emergency = is_emergency,
                extra_phones = extra_phones,
                group_ids    = selected_group_ids
            )
        else:
            ok, msg = add_contact(
                full_name    = full_name,
                phone        = phone,
                email        = email,
                address      = address,
                notes        = notes,
                is_favourite = is_favourite,
                is_emergency = is_emergency,
                extra_phones = extra_phones,
                group_ids    = selected_group_ids
            )

        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            if self._on_save:
                self._on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)
