"""
gui/pages/dashboard_page.py
----------------------------
Dashboard page shown at startup.
Displays summary statistics (Total, Favourites, Emergency, Groups)
and a Recently Added / Updated Contacts section with quick access.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import COLORS, FONTS
from gui.widgets import StatCard, horizontal_separator, make_button
from gui.contact_form import ContactFormDialog
from services.contact_service import get_dashboard_stats, get_recent_contacts


class DashboardPage(tk.Frame):
    """
    The landing page of the application.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._stat_cards = {}
        self._build_ui()

    def _build_ui(self):
        # --- Page title & Quick Add ---
        header = tk.Frame(self, bg=COLORS["main_bg"])
        header.pack(fill="x", padx=30, pady=(20, 5))

        tk.Label(
            header, text="Dashboard",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        make_button(
            header, text="＋  Add Contact",
            command=self._open_add_contact,
            style="primary", width=14
        ).pack(side="right")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 15))

        # --- Stat cards row ---
        cards_frame = tk.Frame(self, bg=COLORS["main_bg"])
        cards_frame.pack(fill="x", padx=30)

        stats_config = [
            ("Total Contacts",    "total",       COLORS["primary"]),
            ("Favourites ⭐",     "favourites",   COLORS["favourite"]),
            ("Emergency 🚨",      "emergency",    COLORS["emergency"]),
            ("Contact Groups 📁", "groups",       "#8E44AD"),
        ]

        stats = get_dashboard_stats()

        for col, (title, key, color) in enumerate(stats_config):
            card = StatCard(
                cards_frame,
                title=title,
                value=stats.get(key, 0),
                color=color,
            )
            card.grid(row=0, column=col, padx=8, pady=5, sticky="nsew")
            self._stat_cards[key] = card
            cards_frame.columnconfigure(col, weight=1)

        # --- Recent Contacts Section ---
        recent_hdr = tk.Frame(self, bg=COLORS["main_bg"])
        recent_hdr.pack(fill="x", padx=30, pady=(20, 8))

        tk.Label(
            recent_hdr, text="🕒 Recently Added / Updated Contacts",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        recent_container = tk.Frame(self, bg=COLORS["card_bg"],
                                    highlightthickness=1,
                                    highlightbackground=COLORS["card_border"])
        recent_container.pack(fill="both", expand=True, padx=30, pady=(0, 20))

        cols = [
            ("name",    "Full Name",     200, "w"),
            ("phone",   "Primary Phone", 140, "w"),
            ("email",   "Email",         180, "w"),
            ("groups",  "Groups",        130, "w"),
            ("fav",     "⭐",             35,  "center"),
            ("emer",    "🚨",             35,  "center"),
            ("updated", "Updated",       130, "center"),
        ]

        self._recent_tree = ttk.Treeview(
            recent_container, style="Contacts.Treeview", selectmode="browse",
            show="headings", columns=[c[0] for c in cols], height=6
        )

        for cid, h, w, a in cols:
            self._recent_tree.heading(cid, text=h)
            self._recent_tree.column(cid, width=w, anchor=a, stretch=(cid == "name" or cid == "email"))

        self._recent_tree.tag_configure("odd",  background=COLORS["tree_odd"])
        self._recent_tree.tag_configure("even", background=COLORS["tree_even"])

        vsb = ttk.Scrollbar(recent_container, orient="vertical", command=self._recent_tree.yview, style="Vertical.TScrollbar")
        self._recent_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._recent_tree.pack(fill="both", expand=True, padx=5, pady=5)

        self._recent_tree.bind("<Double-1>", self._open_edit_contact)

        self.refresh()

    def refresh(self):
        """Update stat cards and repopulate recent contacts."""
        stats = get_dashboard_stats()
        for key, card in self._stat_cards.items():
            card.update_value(stats.get(key, 0))

        # Repopulate recent contacts
        for r in self._recent_tree.get_children():
            self._recent_tree.delete(r)

        recents = get_recent_contacts(limit=8)
        for i, c in enumerate(recents):
            tag = "even" if i % 2 == 0 else "odd"
            fav = "⭐" if c.is_favourite else ""
            emer = "🚨" if c.is_emergency else ""
            groups_str = ", ".join(g["name"] for g in c.groups) if c.groups else ""
            self._recent_tree.insert(
                "", "end", iid=str(c.id),
                values=(c.full_name, c.phone, c.email, groups_str, fav, emer, c.updated_at),
                tags=(tag,)
            )

    def _open_add_contact(self):
        ContactFormDialog(self, contact=None, on_save=self.refresh)

    def _open_edit_contact(self, _event=None):
        sel = self._recent_tree.selection()
        if not sel:
            return
        from services.contact_service import fetch_contact
        cid = int(sel[0])
        c = fetch_contact(cid)
        if c:
            ContactFormDialog(self, contact=c, on_save=self.refresh)
