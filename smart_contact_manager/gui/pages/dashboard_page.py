"""
gui/pages/dashboard_page.py
----------------------------
Dashboard page shown at startup.
Displays summary statistics and a quick welcome section.
"""

import tkinter as tk
from gui.theme import COLORS, FONTS
from gui.widgets import StatCard, horizontal_separator
from services.contact_service import get_dashboard_stats


class DashboardPage(tk.Frame):
    """
    The landing page of the application.
    Shows total contacts, favourites and emergency contacts.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._stat_cards = {}
        self._build_ui()

    # ------------------------------------------------------------------
    # Build UI
    # ------------------------------------------------------------------

    def _build_ui(self):
        # --- Page title ---
        header = tk.Frame(self, bg=COLORS["main_bg"])
        header.pack(fill="x", padx=30, pady=(25, 5))

        tk.Label(
            header, text="Dashboard",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(0, 20))

        # --- Stat cards row ---
        cards_frame = tk.Frame(self, bg=COLORS["main_bg"])
        cards_frame.pack(fill="x", padx=30)

        stats_config = [
            ("Total Contacts",    "total",     COLORS["primary"]),
            ("Favourites ⭐",     "favourites", COLORS["favourite"]),
            ("Emergency 🚨",      "emergency",  COLORS["emergency"]),
        ]

        stats = get_dashboard_stats()

        for col, (title, key, color) in enumerate(stats_config):
            card = StatCard(
                cards_frame,
                title=title,
                value=stats.get(key, 0),
                color=color,
            )
            card.grid(row=0, column=col, padx=10, pady=5, sticky="nsew")
            self._stat_cards[key] = card
            cards_frame.columnconfigure(col, weight=1)

        # --- Welcome section ---
        horizontal_separator(self).pack(fill="x", padx=30, pady=20)

        welcome = tk.Frame(self, bg=COLORS["card_bg"],
                           highlightthickness=1,
                           highlightbackground=COLORS["card_border"])
        welcome.pack(fill="x", padx=30)

        tk.Label(
            welcome,
            text="👋  Welcome to Smart Contact Manager",
            font=FONTS["section"], fg=COLORS["text_primary"],
            bg=COLORS["card_bg"]
        ).pack(anchor="w", padx=20, pady=(15, 5))

        tips = [
            "• Use the  Contacts  page in the sidebar to view and manage all contacts.",
            "• Click  Add Contact  to create a new entry with phone, email and address.",
            "• Use the search bar to instantly find contacts by name or phone number.",
            "• Select a contact and use  Edit  or  Delete  to make changes.",
            "• Contacts are stored in a local SQLite database — no internet needed.",
        ]
        for tip in tips:
            tk.Label(
                welcome, text=tip,
                font=FONTS["body"], fg=COLORS["text_secondary"],
                bg=COLORS["card_bg"], justify="left", anchor="w"
            ).pack(anchor="w", padx=20, pady=2)

        tk.Label(welcome, text="", bg=COLORS["card_bg"]).pack(pady=5)

    # ------------------------------------------------------------------
    # Public method — called by sidebar whenever this page is shown
    # ------------------------------------------------------------------

    def refresh(self):
        """Update the stat cards with fresh database values."""
        stats = get_dashboard_stats()
        for key, card in self._stat_cards.items():
            card.update_value(stats.get(key, 0))
