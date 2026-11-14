"""
gui/widgets.py
--------------
Reusable custom widget helpers used across pages.
Keeps page files clean and consistent.
"""

import tkinter as tk
from tkinter import ttk
from gui.theme import COLORS, FONTS


# ---------------------------------------------------------------------------
# Labelled Entry (label + text entry combined)
# ---------------------------------------------------------------------------

class LabelledEntry(tk.Frame):
    """
    A compact label + Entry pair displayed vertically.
    Usage:
        entry = LabelledEntry(parent, label="Full Name", required=True)
        value = entry.get()
        entry.set("John")
        entry.clear()
    """

    def __init__(self, parent, label: str, required: bool = False,
                 placeholder: str = "", width: int = 30, **kwargs):
        super().__init__(parent, bg=COLORS["card_bg"], **kwargs)

        # Label row
        label_text = f"{label}  *" if required else label
        label_color = COLORS["danger"] if required else COLORS["text_secondary"]
        tk.Label(
            self, text=label_text,
            font=FONTS["small_bold"], fg=label_color,
            bg=COLORS["card_bg"], anchor="w"
        ).pack(anchor="w")

        # Entry widget
        self._var = tk.StringVar()
        self._entry = tk.Entry(
            self, textvariable=self._var,
            font=FONTS["input"], width=width,
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
        )
        self._entry.pack(fill="x", pady=(2, 0))

        self._placeholder = placeholder
        if placeholder:
            self._show_placeholder()
            self._entry.bind("<FocusIn>",  self._on_focus_in)
            self._entry.bind("<FocusOut>", self._on_focus_out)

    def _show_placeholder(self):
        self._entry.insert(0, self._placeholder)
        self._entry.config(fg=COLORS["text_muted"])
        self._is_placeholder = True

    def _on_focus_in(self, _event):
        if getattr(self, "_is_placeholder", False):
            self._entry.delete(0, "end")
            self._entry.config(fg=COLORS["text_primary"])
            self._is_placeholder = False

    def _on_focus_out(self, _event):
        if not self._entry.get():
            self._show_placeholder()

    def get(self) -> str:
        if getattr(self, "_is_placeholder", False):
            return ""
        return self._var.get()

    def set(self, value: str):
        self._is_placeholder = False
        self._entry.config(fg=COLORS["text_primary"])
        self._var.set(value)

    def clear(self):
        self._var.set("")
        if self._placeholder:
            self._show_placeholder()


# ---------------------------------------------------------------------------
# Labelled Text area
# ---------------------------------------------------------------------------

class LabelledText(tk.Frame):
    """A label + scrollable Text widget pair."""

    def __init__(self, parent, label: str, height: int = 4,
                 width: int = 30, **kwargs):
        super().__init__(parent, bg=COLORS["card_bg"], **kwargs)

        tk.Label(
            self, text=label,
            font=FONTS["small_bold"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"], anchor="w"
        ).pack(anchor="w")

        self._text = tk.Text(
            self, height=height, width=width,
            font=FONTS["input"],
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
            wrap="word",
        )
        self._text.pack(fill="x", pady=(2, 0))

    def get(self) -> str:
        return self._text.get("1.0", "end-1c").strip()

    def set(self, value: str):
        self._text.delete("1.0", "end")
        self._text.insert("1.0", value)

    def clear(self):
        self._text.delete("1.0", "end")


# ---------------------------------------------------------------------------
# Styled Buttons
# ---------------------------------------------------------------------------

def make_button(parent, text: str, command, style: str = "primary",
                width: int = 12, **kwargs) -> tk.Button:
    """
    Create a flat-styled button.
    style options: "primary" | "danger" | "success" | "secondary"
    """
    palettes = {
        "primary":   (COLORS["primary"],   COLORS["primary_hover"],   COLORS["text_on_accent"]),
        "danger":    (COLORS["danger"],     COLORS["danger_hover"],    COLORS["text_on_accent"]),
        "success":   (COLORS["success"],    "#1E8449",                 COLORS["text_on_accent"]),
        "secondary": (COLORS["card_border"],COLORS["input_border"],    COLORS["text_primary"]),
    }
    bg, hover_bg, fg = palettes.get(style, palettes["primary"])

    btn = tk.Button(
        parent, text=text, command=command,
        font=FONTS["button"], width=width,
        bg=bg, fg=fg, activebackground=hover_bg,
        activeforeground=fg, relief="flat", bd=0,
        cursor="hand2", padx=10, pady=6,
        **kwargs
    )
    btn.bind("<Enter>", lambda _: btn.config(bg=hover_bg))
    btn.bind("<Leave>", lambda _: btn.config(bg=bg))
    return btn


# ---------------------------------------------------------------------------
# Stat Card (used on Dashboard)
# ---------------------------------------------------------------------------

class StatCard(tk.Frame):
    """Displays a single statistic: a large number and a label below it."""

    def __init__(self, parent, title: str, value: int,
                 color: str = None, **kwargs):
        color = color or COLORS["primary"]
        super().__init__(
            parent, bg=COLORS["card_bg"],
            relief="flat", bd=1,
            highlightthickness=1,
            highlightbackground=COLORS["card_border"],
            **kwargs
        )
        self.config(padx=20, pady=15)

        self._value_var = tk.StringVar(value=str(value))
        tk.Label(
            self, textvariable=self._value_var,
            font=FONTS["stat_number"], fg=color,
            bg=COLORS["card_bg"]
        ).pack()
        tk.Label(
            self, text=title,
            font=FONTS["stat_label"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"]
        ).pack()

    def update_value(self, new_value: int):
        self._value_var.set(str(new_value))


# ---------------------------------------------------------------------------
# Separator line
# ---------------------------------------------------------------------------

def horizontal_separator(parent) -> tk.Frame:
    """Return a thin horizontal line widget."""
    return tk.Frame(parent, bg=COLORS["card_border"], height=1)
