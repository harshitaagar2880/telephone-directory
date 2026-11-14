"""
gui/contact_form.py
--------------------
Modal dialog used for both adding and editing contacts.
Receives an optional Contact object (edit mode) or None (add mode).
Calls back to the parent page via on_save() after a successful save.
"""

import tkinter as tk
from tkinter import messagebox
from typing import Optional, Callable

from gui.theme import COLORS, FONTS
from gui.widgets import LabelledEntry, LabelledText, make_button
from models.contact import Contact
from services.contact_service import add_contact, edit_contact


class ContactFormDialog(tk.Toplevel):
    """
    A modal Toplevel window with the full contact form.

    Parameters
    ----------
    parent      : tk widget — the parent window (keeps dialog on top)
    contact     : Contact | None — if given, pre-fills fields for editing
    on_save     : callable — called with no args after a successful save
    """

    def __init__(self, parent, contact: Optional[Contact] = None,
                 on_save: Optional[Callable] = None):
        super().__init__(parent)

        self._contact = contact
        self._on_save = on_save
        self._is_edit = contact is not None

        # --- Window setup ---
        title = "Edit Contact" if self._is_edit else "Add New Contact"
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()          # make it modal
        self.focus_set()

        # Center on screen
        self.update_idletasks()
        w, h = 500, 620
        x = (self.winfo_screenwidth()  - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        self._build_ui(title)

        # Pre-fill if editing
        if self._is_edit:
            self._populate(contact)

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
        canvas = tk.Canvas(self, bg=COLORS["card_bg"],
                           highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical",
                                 command=canvas.yview)
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

        # ---- Form fields ----
        pad = {"fill": "x", "pady": 6}

        self._name_entry = LabelledEntry(
            body, label="Full Name", required=True,
            placeholder="e.g. Priya Sharma", width=40
        )
        self._name_entry.pack(**pad)

        self._phone_entry = LabelledEntry(
            body, label="Phone Number", required=True,
            placeholder="e.g. +91 98765 43210", width=40
        )
        self._phone_entry.pack(**pad)

        self._email_entry = LabelledEntry(
            body, label="Email Address",
            placeholder="e.g. priya@example.com", width=40
        )
        self._email_entry.pack(**pad)

        self._address_entry = LabelledText(
            body, label="Address", height=3, width=40
        )
        self._address_entry.pack(**pad)

        self._notes_entry = LabelledText(
            body, label="Notes", height=3, width=40
        )
        self._notes_entry.pack(**pad)

        # ---- Toggles ----
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

        # ---- Required note ----
        tk.Label(
            body, text="* Required fields",
            font=FONTS["small"], fg=COLORS["danger"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", pady=(4, 0))

        # ---- Action buttons ----
        btn_frame = tk.Frame(body, bg=COLORS["card_bg"])
        btn_frame.pack(fill="x", pady=(15, 5))

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

    # ------------------------------------------------------------------
    # Form submission
    # ------------------------------------------------------------------

    def _on_submit(self):
        """Collect field values, call service, show result."""
        full_name    = self._name_entry.get()
        phone        = self._phone_entry.get()
        email        = self._email_entry.get()
        address      = self._address_entry.get()
        notes        = self._notes_entry.get()
        is_favourite = self._favourite_var.get()
        is_emergency = self._emergency_var.get()

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
            )

        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            if self._on_save:
                self._on_save()
            self.destroy()
        else:
            messagebox.showerror("Error", msg, parent=self)
