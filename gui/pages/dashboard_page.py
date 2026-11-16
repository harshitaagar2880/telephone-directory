"""
gui/pages/dashboard_page.py
----------------------------
Dashboard page shown at startup.
Displays:
  - 5 Live Summary Stat Cards (Total, Favourites, Emergency, Groups, Speed Dial)
  - Quick Contact creation button
  - Interactive Table toggling between "Recently Added / Updated" and "Recently Viewed"
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import COLORS, FONTS
from gui.widgets import StatCard, horizontal_separator, make_button
from gui.contact_form import ContactFormDialog
from services.contact_service import (
    get_dashboard_stats, get_recent_contacts, fetch_recently_viewed_contacts
)


class DashboardPage(tk.Frame):
    """
    The landing page of the application with live stats and recent activity tabs.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._stat_cards = {}
        self._active_tab = "updated"  # "updated" | "viewed"
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

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 12))

        # --- Stat cards row (5 cards) ---
        cards_frame = tk.Frame(self, bg=COLORS["main_bg"])
        cards_frame.pack(fill="x", padx=30)

        stats_config = [
            ("Total Contacts",    "total",       COLORS["primary"]),
            ("Favourites ⭐",     "favourites",   COLORS["favourite"]),
            ("Emergency 🚨",      "emergency",    COLORS["emergency"]),
            ("Groups 📁",         "groups",       "#8E44AD"),
            ("Speed Dial ⚡",     "speed_dial",   "#D35400"),
        ]

        stats = get_dashboard_stats()

        for col, (title, key, color) in enumerate(stats_config):
            card = StatCard(
                cards_frame,
                title=title,
                value=stats.get(key, 0),
                color=color,
            )
            card.grid(row=0, column=col, padx=6, pady=5, sticky="nsew")
            self._stat_cards[key] = card
            cards_frame.columnconfigure(col, weight=1)

        # --- Recent Contacts Section with Toggle Switch ---
        recent_hdr = tk.Frame(self, bg=COLORS["main_bg"])
        recent_hdr.pack(fill="x", padx=30, pady=(18, 6))

        # Toggle buttons: Recently Added vs Recently Viewed
        tab_box = tk.Frame(recent_hdr, bg=COLORS["main_bg"])
        tab_box.pack(side="left")

        self._btn_tab_updated = tk.Button(
            tab_box, text="🕒 Recently Added / Updated",
            font=FONTS["small_bold"], bg=COLORS["primary"], fg=COLORS["text_on_accent"],
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=lambda: self._set_recent_tab("updated")
        )
        self._btn_tab_updated.pack(side="left", padx=(0, 4))

        self._btn_tab_viewed = tk.Button(
            tab_box, text="👁️ Recently Viewed",
            font=FONTS["small"], bg=COLORS["card_border"], fg=COLORS["text_primary"],
            relief="flat", bd=0, padx=10, pady=4, cursor="hand2",
            command=lambda: self._set_recent_tab("viewed")
        )
        self._btn_tab_viewed.pack(side="left")

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
            ("updated", "Timestamp",     130, "center"),
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

    def _set_recent_tab(self, tab: str):
        self._active_tab = tab
        if tab == "updated":
            self._btn_tab_updated.config(bg=COLORS["primary"], fg=COLORS["text_on_accent"], font=FONTS["small_bold"])
            self._btn_tab_viewed.config(bg=COLORS["card_border"], fg=COLORS["text_primary"], font=FONTS["small"])
        else:
            self._btn_tab_viewed.config(bg=COLORS["primary"], fg=COLORS["text_on_accent"], font=FONTS["small_bold"])
            self._btn_tab_updated.config(bg=COLORS["card_border"], fg=COLORS["text_primary"], font=FONTS["small"])
        self._load_table_data()

    def refresh(self):
        """Update stat cards and repopulate table."""
        stats = get_dashboard_stats()
        for key, card in self._stat_cards.items():
            card.update_value(stats.get(key, 0))
        self._load_table_data()

    def _load_table_data(self):
        for r in self._recent_tree.get_children():
            self._recent_tree.delete(r)

        if self._active_tab == "updated":
            contacts = get_recent_contacts(limit=8)
        else:
            contacts = fetch_recently_viewed_contacts(limit=8)

        for i, c in enumerate(contacts):
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
