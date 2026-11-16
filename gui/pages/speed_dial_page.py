"""
gui/pages/speed_dial_page.py
-----------------------------
Dedicated page for Speed Dial management.
Features:
  - Phone speed dial grid (Slots 1 through 9)
  - Quick dial / copy phone number to clipboard
  - Assign any contact to a speed dial slot
  - Clear / reassign speed dial slots
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List, Dict, Any

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from services.contact_service import (
    fetch_speed_dial_slots, assign_speed_dial, clear_speed_dial,
    fetch_all_contacts, fetch_contact
)


class AssignSpeedDialDialog(tk.Toplevel):
    """Dialog allowing user to choose a contact to assign to a speed dial slot."""

    def __init__(self, parent, slot: int):
        super().__init__(parent)
        self.title(f"Assign Speed Dial #{slot}")
        self.resizable(False, False)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()

        self.selected_contact_id: Optional[int] = None
        self._contacts = fetch_all_contacts()

        w, h = 420, 420
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Header
        hdr = tk.Frame(self, bg=COLORS["primary"], height=48)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(
            hdr, text=f"⚡ Assign to Speed Dial #{slot}",
            font=FONTS["section"], fg=COLORS["text_on_accent"],
            bg=COLORS["primary"]
        ).pack(side="left", padx=15, pady=12)

        body = tk.Frame(self, bg=COLORS["card_bg"], padx=15, pady=10)
        body.pack(fill="both", expand=True)

        tk.Label(
            body, text="Search contact to assign:",
            font=FONTS["small_bold"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", pady=(0, 3))

        self._filter_var = tk.StringVar()
        self._filter_var.trace_add("write", self._on_filter)

        search_entry = tk.Entry(
            body, textvariable=self._filter_var, font=FONTS["input"],
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            relief="flat", bd=1, highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"]
        )
        search_entry.pack(fill="x", ipady=3, pady=(0, 8))

        self._listbox = tk.Listbox(
            body, font=FONTS["body"], selectmode="single",
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            highlightthickness=1, highlightbackground=COLORS["card_border"]
        )
        self._listbox.pack(fill="both", expand=True, pady=(0, 10))

        self._populate_list(self._contacts)

        btn_box = tk.Frame(body, bg=COLORS["card_bg"])
        btn_box.pack(fill="x")

        make_button(
            btn_box, text=f"Set as Speed Dial #{slot}",
            command=self._on_confirm, style="primary", width=20
        ).pack(side="left", padx=(0, 8))

        make_button(
            btn_box, text="Cancel",
            command=self.destroy, style="secondary", width=8
        ).pack(side="left")

    def _populate_list(self, contacts):
        self._listbox.delete(0, "end")
        self._visible_ids = []
        for c in contacts:
            self._listbox.insert("end", f"{c.full_name}  ({c.phone})")
            self._visible_ids.append(c.id)

    def _on_filter(self, *_args):
        q = self._filter_var.get().lower().strip()
        filtered = [c for c in self._contacts if q in c.full_name.lower() or q in c.phone]
        self._populate_list(filtered)

    def _on_confirm(self):
        sel = self._listbox.curselection()
        if not sel:
            messagebox.showwarning("Select Contact", "Please select a contact from the list.", parent=self)
            return
        idx = sel[0]
        if idx < len(self._visible_ids):
            self.selected_contact_id = self._visible_ids[idx]
            self.destroy()


class SpeedDialPage(tk.Frame):
    """
    Dedicated Speed Dial Page.
    Shows 9 numbered speed dial slots (1-9) in a clean dial pad grid.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._slot_cards = {}
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ---- Top Header ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(20, 5))

        tk.Label(
            topbar, text="⚡ Speed Dial Directory",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        tk.Label(
            topbar, text="Quick-access slots 1 through 9 for your most important contacts",
            font=FONTS["small"], fg=COLORS["text_secondary"],
            bg=COLORS["main_bg"]
        ).pack(side="left", padx=15, pady=(4, 0))

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 15))

        # ---- Grid container for 9 slots (3x3 layout) ----
        container = tk.Frame(self, bg=COLORS["main_bg"])
        container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        for i in range(3):
            container.rowconfigure(i, weight=1)
            container.columnconfigure(i, weight=1)

        for slot_num in range(1, 10):
            r = (slot_num - 1) // 3
            c = (slot_num - 1) % 3
            card = self._build_slot_card(container, slot_num)
            card.grid(row=r, column=c, padx=8, pady=8, sticky="nsew")
            self._slot_cards[slot_num] = card

    def _build_slot_card(self, parent, slot_num: int) -> tk.Frame:
        """Create a card representing a single speed dial slot."""
        card = tk.Frame(
            parent, bg=COLORS["card_bg"], padx=15, pady=12,
            highlightthickness=1, highlightbackground=COLORS["card_border"]
        )

        # Slot header with number badge
        hdr = tk.Frame(card, bg=COLORS["card_bg"])
        hdr.pack(fill="x", pady=(0, 5))

        badge = tk.Label(
            hdr, text=str(slot_num), font=("Segoe UI", 13, "bold"),
            bg=COLORS["primary"], fg=COLORS["text_on_accent"],
            width=3, height=1
        )
        badge.pack(side="left")

        slot_title = tk.Label(
            hdr, text=f"Speed Dial #{slot_num}",
            font=FONTS["small_bold"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"]
        )
        slot_title.pack(side="left", padx=8)

        # Contact Name & Phone labels
        name_lbl = tk.Label(
            card, text="[Unassigned]", font=FONTS["body_bold"],
            fg=COLORS["text_muted"], bg=COLORS["card_bg"],
            anchor="w"
        )
        name_lbl.pack(fill="x", pady=(4, 1))

        phone_lbl = tk.Label(
            card, text="Click 'Assign' to set", font=FONTS["small"],
            fg=COLORS["text_secondary"], bg=COLORS["card_bg"],
            anchor="w"
        )
        phone_lbl.pack(fill="x", pady=(0, 8))

        # Button row
        btn_row = tk.Frame(card, bg=COLORS["card_bg"])
        btn_row.pack(fill="x", side="bottom")

        dial_btn = tk.Button(
            btn_row, text="📞 Copy Number", font=FONTS["small"],
            bg=COLORS["success_light"], fg=COLORS["success"],
            relief="flat", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda s=slot_num: self._copy_phone(s), state="disabled"
        )
        dial_btn.pack(side="left", padx=(0, 4))

        assign_btn = tk.Button(
            btn_row, text="Assign", font=FONTS["small"],
            bg=COLORS["primary_light"], fg=COLORS["primary"],
            relief="flat", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda s=slot_num: self._assign_slot(s)
        )
        assign_btn.pack(side="left", padx=(0, 4))

        clear_btn = tk.Button(
            btn_row, text="Clear", font=FONTS["small"],
            bg=COLORS["danger_light"], fg=COLORS["danger"],
            relief="flat", bd=0, padx=6, pady=3, cursor="hand2",
            command=lambda s=slot_num: self._clear_slot(s), state="disabled"
        )
        clear_btn.pack(side="left")

        # Save widget references on card
        card._name_lbl = name_lbl
        card._phone_lbl = phone_lbl
        card._dial_btn = dial_btn
        card._assign_btn = assign_btn
        card._clear_btn = clear_btn
        card._contact = None

        return card

    def refresh(self):
        """Update all 9 slot cards from the database."""
        slots = fetch_speed_dial_slots()
        for s in slots:
            slot_num = s["slot"]
            card = self._slot_cards[slot_num]
            c = s["contact"]

            card._contact = c
            if c:
                card._name_lbl.config(text=c.full_name, fg=COLORS["text_primary"])
                card._phone_lbl.config(text=c.phone, fg=COLORS["primary"])
                card._dial_btn.config(state="normal")
                card._assign_btn.config(text="Change")
                card._clear_btn.config(state="normal")
            else:
                card._name_lbl.config(text="[Unassigned]", fg=COLORS["text_muted"])
                card._phone_lbl.config(text="Click 'Assign' to set", fg=COLORS["text_secondary"])
                card._dial_btn.config(state="disabled")
                card._assign_btn.config(text="Assign")
                card._clear_btn.config(state="disabled")

    def _assign_slot(self, slot_num: int):
        dlg = AssignSpeedDialDialog(self, slot=slot_num)
        self.wait_window(dlg)
        if dlg.selected_contact_id:
            ok, msg = assign_speed_dial(slot_num, dlg.selected_contact_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _clear_slot(self, slot_num: int):
        if messagebox.askyesno("Confirm Clear", f"Clear Speed Dial #{slot_num}?", parent=self):
            ok, msg = clear_speed_dial(slot_num)
            if ok:
                self.refresh()

    def _copy_phone(self, slot_num: int):
        card = self._slot_cards[slot_num]
        if card._contact and card._contact.phone:
            num = card._contact.phone
            self.clipboard_clear()
            self.clipboard_append(num)
            messagebox.showinfo(
                "Speed Dial",
                f"📞 Dialing / Copied to clipboard:\n\n{card._contact.full_name}\n{num}",
                parent=self
            )
