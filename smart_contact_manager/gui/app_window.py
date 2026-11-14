"""
gui/app_window.py
------------------
Root application window.
Builds the sidebar navigation and manages page switching.
Imports and hosts DashboardPage and ContactsPage.
"""

import tkinter as tk
from tkinter import ttk

from gui.theme import COLORS, FONTS, apply_treeview_style
from gui.pages.dashboard_page import DashboardPage
from gui.pages.contacts_page  import ContactsPage


class AppWindow(tk.Tk):
    """
    The main application window.
    Inherits from tk.Tk so it IS the root window.
    """

    APP_TITLE   = "Smart Contact Manager"
    APP_VERSION = "1.0"
    MIN_WIDTH   = 980
    MIN_HEIGHT  = 600

    def __init__(self):
        super().__init__()

        # --- Basic window setup ---
        self.title(f"{self.APP_TITLE}  v{self.APP_VERSION}")
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.geometry("1100x680")
        self.configure(bg=COLORS["sidebar_bg"])

        # Center on screen
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        x  = (sw - 1100) // 2
        y  = (sh - 680)  // 2
        self.geometry(f"1100x680+{x}+{y}")

        # Apply ttk styles
        style = ttk.Style(self)
        apply_treeview_style(style)

        # Build the layout
        self._build_layout()
        self._active_page: str = ""
        self._pages: dict[str, tk.Frame] = {}
        self._nav_buttons: dict[str, tk.Button] = {}

        self._init_pages()
        self._show_page("dashboard")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def _build_layout(self):
        """Create sidebar + main area side by side."""

        # ---- Sidebar ----
        self._sidebar = tk.Frame(self, bg=COLORS["sidebar_bg"], width=200)
        self._sidebar.pack(side="left", fill="y")
        self._sidebar.pack_propagate(False)   # keep fixed width

        # App brand at the top of sidebar
        brand = tk.Frame(self._sidebar, bg=COLORS["sidebar_bg"])
        brand.pack(fill="x", pady=(20, 10))

        tk.Label(
            brand, text="📋",
            font=("Segoe UI Emoji", 22), fg=COLORS["sidebar_text"],
            bg=COLORS["sidebar_bg"]
        ).pack()
        tk.Label(
            brand, text="Smart Contact\nManager",
            font=FONTS["body_bold"], fg=COLORS["sidebar_text"],
            bg=COLORS["sidebar_bg"], justify="center"
        ).pack()

        # Thin separator below brand
        tk.Frame(self._sidebar, bg=COLORS["sidebar_hover"], height=1).pack(
            fill="x", padx=15, pady=(10, 0)
        )

        # Navigation label
        tk.Label(
            self._sidebar, text="NAVIGATION",
            font=FONTS["small_bold"], fg=COLORS["sidebar_icon"],
            bg=COLORS["sidebar_bg"]
        ).pack(anchor="w", padx=18, pady=(15, 5))

        # Nav buttons will be added in _init_pages()
        self._nav_frame = tk.Frame(self._sidebar, bg=COLORS["sidebar_bg"])
        self._nav_frame.pack(fill="x")

        # Version label at the very bottom
        tk.Label(
            self._sidebar, text=f"v{self.APP_VERSION}",
            font=FONTS["small"], fg=COLORS["sidebar_icon"],
            bg=COLORS["sidebar_bg"]
        ).pack(side="bottom", pady=10)

        # ---- Main content area ----
        self._main_area = tk.Frame(self, bg=COLORS["main_bg"])
        self._main_area.pack(side="right", fill="both", expand=True)

    # ------------------------------------------------------------------
    # Page management
    # ------------------------------------------------------------------

    def _init_pages(self):
        """Instantiate all pages and their sidebar nav buttons."""
        nav_items = [
            ("dashboard", "🏠  Dashboard",   DashboardPage),
            ("contacts",  "👤  Contacts",    ContactsPage),
        ]

        for page_key, label, PageClass in nav_items:
            # Create the page frame inside main_area
            page = PageClass(self._main_area)
            page.place(relx=0, rely=0, relwidth=1, relheight=1)
            self._pages[page_key] = page

            # Sidebar button
            btn = tk.Button(
                self._nav_frame,
                text=label,
                font=FONTS["body"],
                fg=COLORS["sidebar_text"],
                bg=COLORS["sidebar_bg"],
                activebackground=COLORS["sidebar_hover"],
                activeforeground=COLORS["sidebar_text"],
                relief="flat", bd=0,
                anchor="w", padx=18, pady=10,
                cursor="hand2",
                command=lambda k=page_key: self._show_page(k)
            )
            btn.pack(fill="x")
            btn.bind("<Enter>",
                     lambda e, b=btn: b.config(bg=COLORS["sidebar_hover"]))
            btn.bind("<Leave>",
                     lambda e, b=btn, k=page_key: b.config(
                         bg=COLORS["sidebar_active"] if k == self._active_page
                         else COLORS["sidebar_bg"]
                     ))
            self._nav_buttons[page_key] = btn

    def _show_page(self, page_key: str):
        """Raise the selected page and update sidebar highlight."""
        if page_key == self._active_page:
            return

        # Deactivate previous button
        if self._active_page and self._active_page in self._nav_buttons:
            self._nav_buttons[self._active_page].config(
                bg=COLORS["sidebar_bg"]
            )

        # Activate new button
        self._nav_buttons[page_key].config(bg=COLORS["sidebar_active"])
        self._active_page = page_key

        # Raise the page to the top
        page = self._pages[page_key]
        page.lift()

        # Call refresh() if the page has it, to update data
        if hasattr(page, "refresh"):
            page.refresh()
