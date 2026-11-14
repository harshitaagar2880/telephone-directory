"""
gui/pages/groups_page.py
-------------------------
Custom Contact Groups page.
Allows:
  - Creating new custom groups with custom colors
  - Renaming and editing groups
  - Deleting groups safely (without deleting any contacts)
  - Selecting a group to view all contacts in that group
  - Adding contacts to the selected group
  - Removing contacts from the group
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
from typing import Optional, List, Dict, Any

from gui.theme import COLORS, FONTS
from gui.widgets import make_button, horizontal_separator
from gui.contact_form import ContactFormDialog
from models.contact import Contact
from services.contact_service import (
    fetch_all_groups, create_group, edit_group, delete_group,
    fetch_contacts_by_group, fetch_all_contacts, add_contact_to_group,
    remove_contact_from_group, fetch_contact
)


class GroupDialog(tk.Toplevel):
    """Dialog for creating or editing a group name and color."""

    DEFAULT_COLORS = [
        ("#4A90D9", "Blue"),
        ("#2ECC71", "Green"),
        ("#E67E22", "Orange"),
        ("#9B59B6", "Purple"),
        ("#E74C3C", "Red"),
        ("#1ABC9C", "Teal"),
        ("#34495E", "Dark Slate"),
    ]

    def __init__(self, parent, title: str, initial_name: str = "", initial_color: str = "#4A90D9"):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()

        self.result: Optional[tuple[str, str]] = None
        self._selected_color = tk.StringVar(value=initial_color)

        w, h = 380, 260
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        # Header
        hdr = tk.Frame(self, bg=COLORS["primary"], height=45)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=title, font=FONTS["section"], fg=COLORS["text_on_accent"], bg=COLORS["primary"]).pack(side="left", padx=15, pady=10)

        body = tk.Frame(self, bg=COLORS["card_bg"], padx=20, pady=15)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Group Name:", font=FONTS["small_bold"], fg=COLORS["text_secondary"], bg=COLORS["card_bg"]).pack(anchor="w")
        self._name_entry = tk.Entry(body, font=FONTS["input"], bg=COLORS["input_bg"], fg=COLORS["text_primary"],
                                    relief="flat", bd=1, highlightthickness=1,
                                    highlightbackground=COLORS["input_border"], highlightcolor=COLORS["input_focus"])
        self._name_entry.pack(fill="x", pady=(3, 12))
        self._name_entry.insert(0, initial_name)
        self._name_entry.focus_set()

        tk.Label(body, text="Color Badge:", font=FONTS["small_bold"], fg=COLORS["text_secondary"], bg=COLORS["card_bg"]).pack(anchor="w")
        color_box = tk.Frame(body, bg=COLORS["card_bg"])
        color_box.pack(fill="x", pady=(4, 15))

        for col, name in self.DEFAULT_COLORS:
            rb = tk.Radiobutton(
                color_box, text="", value=col, variable=self._selected_color,
                bg=col, selectcolor=col, activebackground=col,
                indicatoron=0, width=3, height=1, cursor="hand2"
            )
            rb.pack(side="left", padx=3)

        btn_box = tk.Frame(body, bg=COLORS["card_bg"])
        btn_box.pack(fill="x")
        make_button(btn_box, text="Save", command=self._on_save, style="primary", width=10).pack(side="left", padx=(0, 8))
        make_button(btn_box, text="Cancel", command=self.destroy, style="secondary", width=8).pack(side="left")

    def _on_save(self):
        name = self._name_entry.get().strip()
        if not name:
            messagebox.showwarning("Validation Error", "Please enter a group name.", parent=self)
            return
        self.result = (name, self._selected_color.get())
        self.destroy()


class AddToGroupDialog(tk.Toplevel):
    """Dialog allowing user to choose an existing contact to add to the group."""

    def __init__(self, parent, group_name: str, existing_contact_ids: set[int]):
        super().__init__(parent)
        self.title(f"Add Contacts to {group_name}")
        self.resizable(False, False)
        self.configure(bg=COLORS["card_bg"])
        self.grab_set()

        self.selected_contact_id: Optional[int] = None

        w, h = 420, 400
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{x}+{y}")

        hdr = tk.Frame(self, bg=COLORS["primary"], height=45)
        hdr.pack(fill="x")
        hdr.pack_propagate(False)
        tk.Label(hdr, text=f"Add Contact to '{group_name}'", font=FONTS["section"],
                 fg=COLORS["text_on_accent"], bg=COLORS["primary"]).pack(side="left", padx=15, pady=10)

        body = tk.Frame(self, bg=COLORS["card_bg"], padx=15, pady=10)
        body.pack(fill="both", expand=True)

        tk.Label(body, text="Select a contact to add:", font=FONTS["small_bold"],
                 fg=COLORS["text_secondary"], bg=COLORS["card_bg"]).pack(anchor="w", pady=(0, 5))

        # List of available contacts
        all_contacts = fetch_all_contacts()
        available = [c for c in all_contacts if c.id not in existing_contact_ids]

        self._listbox = tk.Listbox(body, font=FONTS["body"], selectmode="single",
                                   bg=COLORS["input_bg"], fg=COLORS["text_primary"],
                                   highlightthickness=1, highlightbackground=COLORS["card_border"])
        self._listbox.pack(fill="both", expand=True, pady=(0, 10))

        self._available_ids: list[int] = []
        for c in available:
            self._listbox.insert("end", f"{c.full_name}  ({c.phone})")
            self._available_ids.append(c.id)

        if not available:
            self._listbox.insert("end", "(All contacts are already in this group)")

        btn_box = tk.Frame(body, bg=COLORS["card_bg"])
        btn_box.pack(fill="x")

        make_button(btn_box, text="Add Contact", command=self._on_add, style="primary", width=14).pack(side="left", padx=(0, 8))
        make_button(btn_box, text="Cancel", command=self.destroy, style="secondary", width=10).pack(side="left")

    def _on_add(self):
        sel = self._listbox.curselection()
        if not sel or not self._available_ids:
            messagebox.showwarning("Selection", "Please select a contact from the list.", parent=self)
            return
        idx = sel[0]
        if idx < len(self._available_ids):
            self.selected_contact_id = self._available_ids[idx]
            self.destroy()


class GroupsPage(tk.Frame):
    """
    Dedicated Custom Groups management page.
    """

    def __init__(self, parent, **kwargs):
        super().__init__(parent, bg=COLORS["main_bg"], **kwargs)
        self._selected_group_id: Optional[int] = None
        self._selected_contact_id: Optional[int] = None
        self._groups: List[Dict[str, Any]] = []
        self._group_contacts: List[Contact] = []

        self._build_ui()
        self.refresh()

    def _build_ui(self):
        # ---- Top Header ----
        topbar = tk.Frame(self, bg=COLORS["main_bg"])
        topbar.pack(fill="x", padx=30, pady=(20, 5))

        tk.Label(
            topbar, text="📁 Custom Contact Groups",
            font=FONTS["page_title"], fg=COLORS["text_primary"],
            bg=COLORS["main_bg"]
        ).pack(side="left")

        make_button(
            topbar, text="＋  New Group",
            command=self._create_new_group,
            style="primary", width=14
        ).pack(side="right")

        horizontal_separator(self).pack(fill="x", padx=30, pady=(5, 15))

        # ---- Split View: Left (Groups list) & Right (Contacts in group) ----
        container = tk.Frame(self, bg=COLORS["main_bg"])
        container.pack(fill="both", expand=True, padx=30, pady=(0, 15))

        # ---- LEFT: Groups List Pane ----
        left_pane = tk.Frame(container, bg=COLORS["card_bg"], width=280,
                             highlightthickness=1, highlightbackground=COLORS["card_border"])
        left_pane.pack(side="left", fill="y", padx=(0, 15))
        left_pane.pack_propagate(False)

        grp_hdr = tk.Frame(left_pane, bg=COLORS["card_bg"], padx=15, pady=10)
        grp_hdr.pack(fill="x")
        tk.Label(grp_hdr, text="All Groups", font=FONTS["section"],
                 fg=COLORS["text_primary"], bg=COLORS["card_bg"]).pack(side="left")

        self._grp_tree = ttk.Treeview(
            left_pane, style="Contacts.Treeview", selectmode="browse",
            show="headings", columns=["name", "count"]
        )
        self._grp_tree.heading("name", text="Group Name")
        self._grp_tree.heading("count", text="Contacts")
        self._grp_tree.column("name", width=170, anchor="w")
        self._grp_tree.column("count", width=70, anchor="center")
        self._grp_tree.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._grp_tree.bind("<<TreeviewSelect>>", self._on_group_select)

        # Buttons under group list
        grp_actions = tk.Frame(left_pane, bg=COLORS["card_bg"], padx=10, pady=10)
        grp_actions.pack(fill="x")

        self._edit_grp_btn = make_button(
            grp_actions, text="✏ Edit", command=self._edit_selected_group,
            style="secondary", width=8
        )
        self._edit_grp_btn.pack(side="left", padx=(0, 6))
        self._edit_grp_btn.config(state="disabled")

        self._del_grp_btn = make_button(
            grp_actions, text="🗑 Delete", command=self._delete_selected_group,
            style="danger", width=8
        )
        self._del_grp_btn.pack(side="left")
        self._del_grp_btn.config(state="disabled")

        # ---- RIGHT: Contacts in Selected Group Pane ----
        right_pane = tk.Frame(container, bg=COLORS["card_bg"],
                              highlightthickness=1, highlightbackground=COLORS["card_border"])
        right_pane.pack(side="right", fill="both", expand=True)

        r_hdr = tk.Frame(right_pane, bg=COLORS["card_bg"], padx=15, pady=12)
        r_hdr.pack(fill="x")

        self._group_title_lbl = tk.Label(
            r_hdr, text="Select a group to view contacts",
            font=FONTS["section"], fg=COLORS["text_primary"], bg=COLORS["card_bg"]
        )
        self._group_title_lbl.pack(side="left")

        # Right pane action buttons
        self._right_actions = tk.Frame(r_hdr, bg=COLORS["card_bg"])
        self._right_actions.pack(side="right")

        self._add_to_grp_btn = make_button(
            self._right_actions, text="＋ Add Contact",
            command=self._add_contact_to_current_group,
            style="primary", width=14
        )
        self._add_to_grp_btn.pack(side="left", padx=(0, 6))
        self._add_to_grp_btn.config(state="disabled")

        self._rem_from_grp_btn = make_button(
            self._right_actions, text="➖ Remove",
            command=self._remove_contact_from_current_group,
            style="danger", width=10
        )
        self._rem_from_grp_btn.pack(side="left")
        self._rem_from_grp_btn.config(state="disabled")

        horizontal_separator(right_pane).pack(fill="x", padx=10)

        # Contacts treeview in right pane
        cols = [
            ("name",    "Full Name",     180, "w"),
            ("phone",   "Primary Phone", 130, "w"),
            ("email",   "Email",         160, "w"),
            ("fav",     "⭐",             35,  "center"),
            ("emer",    "🚨",             35,  "center"),
        ]
        self._c_tree = ttk.Treeview(
            right_pane, style="Contacts.Treeview", selectmode="browse",
            show="headings", columns=[c[0] for c in cols]
        )
        for cid, h, w, a in cols:
            self._c_tree.heading(cid, text=h)
            self._c_tree.column(cid, width=w, anchor=a, stretch=(cid == "name" or cid == "email"))

        self._c_tree.tag_configure("odd",  background=COLORS["tree_odd"])
        self._c_tree.tag_configure("even", background=COLORS["tree_even"])

        vsb = ttk.Scrollbar(right_pane, orient="vertical", command=self._c_tree.yview, style="Vertical.TScrollbar")
        self._c_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self._c_tree.pack(fill="both", expand=True, padx=10, pady=10)

        self._c_tree.bind("<<TreeviewSelect>>", self._on_contact_select)
        self._c_tree.bind("<Double-1>",          self._open_contact_form)

    # ------------------------------------------------------------------
    # Data loading
    # ------------------------------------------------------------------

    def refresh(self):
        """Reload groups and contacts for currently selected group."""
        self._groups = fetch_all_groups()

        for r in self._grp_tree.get_children():
            self._grp_tree.delete(r)

        for g in self._groups:
            self._grp_tree.insert(
                "", "end", iid=str(g["id"]),
                values=(g["name"], f"{g['contact_count']} contacts")
            )

        if self._selected_group_id and self._grp_tree.exists(str(self._selected_group_id)):
            self._grp_tree.selection_set(str(self._selected_group_id))
            self._load_group_contacts(self._selected_group_id)
        else:
            self._selected_group_id = None
            self._clear_contacts_pane()
            self._edit_grp_btn.config(state="disabled")
            self._del_grp_btn.config(state="disabled")

    def _on_group_select(self, _event=None):
        sel = self._grp_tree.selection()
        if not sel:
            return
        gid = int(sel[0])
        self._selected_group_id = gid
        self._edit_grp_btn.config(state="normal")
        self._del_grp_btn.config(state="normal")
        self._load_group_contacts(gid)

    def _load_group_contacts(self, group_id: int):
        grp = next((g for g in self._groups if g["id"] == group_id), None)
        grp_name = grp["name"] if grp else "Group"
        self._group_title_lbl.config(text=f"Contacts in '{grp_name}'")

        self._group_contacts = fetch_contacts_by_group(group_id)

        for r in self._c_tree.get_children():
            self._c_tree.delete(r)

        for i, c in enumerate(self._group_contacts):
            tag = "even" if i % 2 == 0 else "odd"
            fav = "⭐" if c.is_favourite else ""
            emer = "🚨" if c.is_emergency else ""
            self._c_tree.insert(
                "", "end", iid=str(c.id),
                values=(c.full_name, c.phone, c.email, fav, emer),
                tags=(tag,)
            )

        self._add_to_grp_btn.config(state="normal")
        self._rem_from_grp_btn.config(state="disabled")
        self._selected_contact_id = None

    def _clear_contacts_pane(self):
        self._group_title_lbl.config(text="Select a group to view contacts")
        for r in self._c_tree.get_children():
            self._c_tree.delete(r)
        self._add_to_grp_btn.config(state="disabled")
        self._rem_from_grp_btn.config(state="disabled")

    def _on_contact_select(self, _event=None):
        sel = self._c_tree.selection()
        if not sel:
            self._rem_from_grp_btn.config(state="disabled")
            return
        self._selected_contact_id = int(sel[0])
        self._rem_from_grp_btn.config(state="normal")

    # ------------------------------------------------------------------
    # Group actions
    # ------------------------------------------------------------------

    def _create_new_group(self):
        dlg = GroupDialog(self, title="Create New Group")
        self.wait_window(dlg)
        if dlg.result:
            name, color = dlg.result
            ok, msg = create_group(name, color)
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _edit_selected_group(self):
        if not self._selected_group_id:
            return
        grp = next((g for g in self._groups if g["id"] == self._selected_group_id), None)
        if not grp:
            return
        dlg = GroupDialog(self, title="Edit Group", initial_name=grp["name"], initial_color=grp.get("color", "#4A90D9"))
        self.wait_window(dlg)
        if dlg.result:
            name, color = dlg.result
            ok, msg = edit_group(self._selected_group_id, name, color)
            if ok:
                messagebox.showinfo("Success", msg, parent=self)
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _delete_selected_group(self):
        if not self._selected_group_id:
            return
        grp = next((g for g in self._groups if g["id"] == self._selected_group_id), None)
        if not grp:
            return

        confirmed = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete the group '{grp['name']}'?\n\n"
            "Important: Contacts inside this group will NOT be deleted.",
            icon="warning", parent=self
        )
        if not confirmed:
            return

        ok, msg = delete_group(self._selected_group_id)
        if ok:
            messagebox.showinfo("Success", msg, parent=self)
            self._selected_group_id = None
            self.refresh()
        else:
            messagebox.showerror("Error", msg, parent=self)

    # ------------------------------------------------------------------
    # Contact in group actions
    # ------------------------------------------------------------------

    def _add_contact_to_current_group(self):
        if not self._selected_group_id:
            return
        grp = next((g for g in self._groups if g["id"] == self._selected_group_id), None)
        if not grp:
            return

        existing_ids = {c.id for c in self._group_contacts}
        dlg = AddToGroupDialog(self, group_name=grp["name"], existing_contact_ids=existing_ids)
        self.wait_window(dlg)
        if dlg.selected_contact_id:
            ok, msg = add_contact_to_group(dlg.selected_contact_id, self._selected_group_id)
            if ok:
                self.refresh()
            else:
                messagebox.showerror("Error", msg, parent=self)

    def _remove_contact_from_current_group(self):
        if not self._selected_group_id or not self._selected_contact_id:
            return
        ok, msg = remove_contact_from_group(self._selected_contact_id, self._selected_group_id)
        if ok:
            self.refresh()
        else:
            messagebox.showerror("Error", msg, parent=self)

    def _open_contact_form(self, _event=None):
        if not self._selected_contact_id:
            return
        contact = fetch_contact(self._selected_contact_id)
        if contact:
            ContactFormDialog(self, contact=contact, on_save=self.refresh)
