"""
gui/pages/data_page.py
-----------------------
Dedicated page for:
  - CSV Contact Export
  - CSV Contact Import with duplicate detection and summary
  - SQLite Database Backup
  - SQLite Database Restore with safety snapshot and integrity checks
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Callable

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from database.connection import DB_PATH
from services.data_service import (
    export_contacts_to_csv, import_contacts_from_csv,
    create_database_backup, restore_database_from_backup,
    generate_default_backup_filename
)
from services.contact_service import get_dashboard_stats


class DataPage(tk.Frame):
    """
    Data management, CSV import/export, and Database backup/restore page.
    """

    def __init__(self, parent, on_data_change: Optional[Callable] = None, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._on_data_change = on_data_change
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ---- Header ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(20, 5))

        tk.Label(
            topbar, text="💾 Data Management & Backup",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        self._stats_lbl = tk.Label(
            topbar, text="",
            font=FONTS["small"], fg=COLORS["text_secondary"],
            bg=COLORS["main_bg"]
        )
        self._stats_lbl.pack(side="right")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 15))

        # ---- Scrollable Container ----
        canvas = tk.Canvas(self, bg=COLORS["main_bg"], highlightthickness=0)
        scrollbar = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        body = tk.Frame(canvas, bg=COLORS["main_bg"], padx=30, pady=5)
        body_id = canvas.create_window((0, 0), window=body, anchor="nw")

        def _conf(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            canvas.itemconfig(body_id, width=canvas.winfo_width())

        body.bind("<Configure>", _conf)
        canvas.bind("<Configure>", _conf)

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(-1 * (e.delta // 120), "units"))

        # Grid of cards: 2x2 layout
        cards_grid = tk.Frame(body, bg=COLORS["main_bg"])
        cards_grid.pack(fill="both", expand=True)
        cards_grid.columnconfigure(0, weight=1)
        cards_grid.columnconfigure(1, weight=1)

        # 1. CSV Export Card
        self._build_export_card(cards_grid, row=0, col=0)

        # 2. CSV Import Card
        self._build_import_card(cards_grid, row=0, col=1)

        # 3. Database Backup Card
        self._build_backup_card(cards_grid, row=1, col=0)

        # 4. Database Restore Card
        self._build_restore_card(cards_grid, row=1, col=1)

    # ------------------------------------------------------------------
    # Card 1: CSV Export
    # ------------------------------------------------------------------
    def _build_export_card(self, parent, row, col):
        card = tk.Frame(parent, bg=COLORS["card_bg"], padx=20, pady=18,
                        highlightthickness=1, highlightbackground=COLORS["card_border"])
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        tk.Label(card, text="📤 Export Contacts (CSV)", font=FONTS["section"],
                 fg=COLORS["primary"], bg=COLORS["card_bg"]).pack(anchor="w")

        desc = (
            "Save all your contacts to a CSV file. Includes full names, "
            "primary and secondary phone numbers, email addresses, "
            "assigned groups, and favourite/emergency statuses."
        )
        tk.Label(card, text=desc, font=FONTS["small"], fg=COLORS["text_secondary"],
                 bg=COLORS["card_bg"], wraplength=380, justify="left").pack(anchor="w", pady=(6, 15))

        make_button(
            card, text="Export to CSV...", command=self._handle_export_csv,
            style="primary", width=18
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Card 2: CSV Import
    # ------------------------------------------------------------------
    def _build_import_card(self, parent, row, col):
        card = tk.Frame(parent, bg=COLORS["card_bg"], padx=20, pady=18,
                        highlightthickness=1, highlightbackground=COLORS["card_border"])
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        tk.Label(card, text="📥 Import Contacts (CSV)", font=FONTS["section"],
                 fg="#16A085", bg=COLORS["card_bg"]).pack(anchor="w")

        desc = (
            "Import contacts from any CSV file. Automatic column matching, "
            "regex format validation, and duplicate prevention. "
            "A summary of imported and skipped records is shown."
        )
        tk.Label(card, text=desc, font=FONTS["small"], fg=COLORS["text_secondary"],
                 bg=COLORS["card_bg"], wraplength=380, justify="left").pack(anchor="w", pady=(6, 15))

        make_button(
            card, text="Import from CSV...", command=self._handle_import_csv,
            style="success", width=18
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Card 3: Database Backup
    # ------------------------------------------------------------------
    def _build_backup_card(self, parent, row, col):
        card = tk.Frame(parent, bg=COLORS["card_bg"], padx=20, pady=18,
                        highlightthickness=1, highlightbackground=COLORS["card_border"])
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        tk.Label(card, text="🛡️ Database Backup", font=FONTS["section"],
                 fg="#2980B9", bg=COLORS["card_bg"]).pack(anchor="w")

        desc = (
            "Create a point-in-time snapshot of the entire SQLite database. "
            "Uses SQLite's online backup API for a 100% consistent, "
            "un-corrupted backup copy with timestamped naming."
        )
        tk.Label(card, text=desc, font=FONTS["small"], fg=COLORS["text_secondary"],
                 bg=COLORS["card_bg"], wraplength=380, justify="left").pack(anchor="w", pady=(6, 15))

        make_button(
            card, text="Create Backup...", command=self._handle_backup_db,
            style="primary", width=18
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Card 4: Database Restore
    # ------------------------------------------------------------------
    def _build_restore_card(self, parent, row, col):
        card = tk.Frame(parent, bg=COLORS["card_bg"], padx=20, pady=18,
                        highlightthickness=1, highlightbackground=COLORS["card_border"])
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        tk.Label(card, text="🔄 Database Restore", font=FONTS["section"],
                 fg=COLORS["danger"], bg=COLORS["card_bg"]).pack(anchor="w")

        desc = (
            "Restore the application from an existing database backup. "
            "Candidate files are checked for database integrity, and a "
            "safety snapshot of current data is created before restoring."
        )
        tk.Label(card, text=desc, font=FONTS["small"], fg=COLORS["text_secondary"],
                 bg=COLORS["card_bg"], wraplength=380, justify="left").pack(anchor="w", pady=(6, 15))

        make_button(
            card, text="Restore Database...", command=self._handle_restore_db,
            style="danger", width=18
        ).pack(anchor="w")

    # ------------------------------------------------------------------
    # Actions
    # ------------------------------------------------------------------
    def refresh(self):
        """Update top status with active database size and contact count."""
        stats = get_dashboard_stats()
        db_size_kb = os.path.getsize(DB_PATH) / 1024 if os.path.exists(DB_PATH) else 0
        self._stats_lbl.config(
            text=f"Active Database: contacts.db ({db_size_kb:.1f} KB) • {stats['total']} Contacts"
        )

    def _handle_export_csv(self):
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

    def _handle_import_csv(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="Select CSV File to Import",
            filetypes=[("CSV Files (*.csv)", "*.csv"), ("All Files (*.*)", "*.*")]
        )
        if not filename:
            return

        summary = import_contacts_from_csv(filename)
        self._show_import_summary(summary)

        if summary["imported"] > 0 and self._on_data_change:
            self._on_data_change()
        self.refresh()

    def _show_import_summary(self, summary: dict):
        """Display detailed modal dialog showing the result of the import."""
        win = tk.Toplevel(self)
        win.title("Import Summary")
        win.resizable(False, False)
        win.configure(bg=COLORS["card_bg"])
        win.grab_set()

        w, h = 460, 360
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        win.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(win, bg=COLORS["primary"], height=45)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text="CSV Import Summary", font=FONTS["section"],
                 fg=COLORS["text_on_accent"], bg=COLORS["primary"]).pack(side="left", padx=15, pady=10)

        body = tk.Frame(win, bg=COLORS["card_bg"], padx=20, pady=15)
        body.pack(fill="both", expand=True)

        rows = [
            ("Total Rows Processed:", str(summary["total"])),
            ("✅ Successfully Imported:", str(summary["imported"])),
            ("⚠️ Skipped (Duplicates):", str(summary["skipped"])),
            ("❌ Failed (Invalid):", str(summary["failed"])),
        ]
        for label, val in rows:
            r = tk.Frame(body, bg=COLORS["card_bg"])
            r.pack(fill="x", pady=3)
            tk.Label(r, text=label, font=FONTS["body_bold"], fg=COLORS["text_primary"], bg=COLORS["card_bg"]).pack(side="left")
            tk.Label(r, text=val, font=FONTS["body_bold"], fg=COLORS["primary"], bg=COLORS["card_bg"]).pack(side="right")

        if summary["errors"]:
            tk.Label(body, text="Error Log / Details:", font=FONTS["small_bold"],
                     fg=COLORS["danger"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(10, 2))

            err_box = tk.Text(body, height=5, font=FONTS["small"], bg=COLORS["main_bg"],
                              highlightthickness=1, highlightbackground=COLORS["card_border"])
            err_box.pack(fill="x", pady=(0, 10))
            err_box.insert("end", "\n".join(summary["errors"][:10]))
            if len(summary["errors"]) > 10:
                err_box.insert("end", f"\n... and {len(summary['errors']) - 10} more errors.")
            err_box.config(state="disabled")

        make_button(body, text="OK", command=win.destroy, style="primary", width=10).pack(side="right", pady=(10, 0))

    def _handle_backup_db(self):
        default_name = generate_default_backup_filename()
        filename = filedialog.asksaveasfilename(
            parent=self,
            title="Save Database Backup",
            defaultextension=".db",
            filetypes=[("SQLite Database (*.db)", "*.db"), ("All Files (*.*)", "*.*")],
            initialfile=default_name
        )
        if not filename:
            return

        ok, msg = create_database_backup(filename)
        if ok:
            messagebox.showinfo("Backup Successful", msg, parent=self)
        else:
            messagebox.showerror("Backup Failed", msg, parent=self)

    def _handle_restore_db(self):
        filename = filedialog.askopenfilename(
            parent=self,
            title="Select Backup File to Restore",
            filetypes=[("SQLite Database (*.db;*.sqlite)", "*.db;*.sqlite"), ("All Files (*.*)", "*.*")]
        )
        if not filename:
            return

        # Confirm before restoring
        confirmed = messagebox.askyesno(
            "Confirm Database Restore",
            "WARNING: Restoring will overwrite the current active database.\n\n"
            "• An automatic safety snapshot will be created before proceeding.\n"
            "• The backup file will be verified for integrity.\n\n"
            "Do you want to proceed with restoring from this backup?",
            icon="warning", parent=self
        )
        if not confirmed:
            return

        ok, msg = restore_database_from_backup(filename)
        if ok:
            messagebox.showinfo("Restore Successful", msg, parent=self)
            if self._on_data_change:
                self._on_data_change()
            self.refresh()
        else:
            messagebox.showerror("Restore Failed", msg, parent=self)
