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
# Themed Button (tk.Button subclass that supports dynamic restyling)
# ---------------------------------------------------------------------------

class ThemedButton(tk.Button):
    """A tk.Button that remembers its style and can restyle on theme change."""

    BUTTON_PALETTES = {
        "primary":   ("primary",   "primary_hover",   "text_on_accent"),
        "danger":    ("danger",     "danger_hover",    "text_on_accent"),
        "success":   ("success",    "primary_hover",   "text_on_accent"),
        "secondary": ("card_border","input_border",    "text_primary"),
    }

    def __init__(self, parent, text: str, command, style: str = "primary",
                 width: int = 12, **kwargs):
        self._button_style = style
        super().__init__(
            parent, text=text, command=command,
            font=FONTS["button"], width=width,
            relief="flat", bd=0,
            cursor="hand2", padx=10, pady=6,
            **kwargs
        )
        self._apply_style()
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _apply_style(self):
        bg_key, hover_key, fg_key = self.BUTTON_PALETTES.get(
            self._button_style, self.BUTTON_PALETTES["primary"]
        )
        bg = COLORS[bg_key]
        hover_bg = COLORS[hover_key]
        fg = COLORS[fg_key]
        self.config(bg=bg, fg=fg, activebackground=hover_bg, activeforeground=fg)

    def _on_enter(self, _event):
        bg_key, hover_key, _ = self.BUTTON_PALETTES.get(
            self._button_style, self.BUTTON_PALETTES["primary"]
        )
        self.config(bg=COLORS[hover_key])

    def _on_leave(self, _event):
        bg_key, _, _ = self.BUTTON_PALETTES.get(
            self._button_style, self.BUTTON_PALETTES["primary"]
        )
        self.config(bg=COLORS[bg_key])

    def restyle(self):
        """Reapply button colors from the current theme."""
        self._apply_style()


def make_button(parent, text: str, command, style: str = "primary",
                width: int = 12, **kwargs) -> ThemedButton:
    """
    Create a flat-styled themed button.
    style options: "primary" | "danger" | "success" | "secondary"
    Returns a ThemedButton that supports restyle().
    """
    return ThemedButton(parent, text=text, command=command,
                        style=style, width=width, **kwargs)

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
        self._label = tk.Label(
            self, text=label_text,
            font=FONTS["small_bold"], fg=label_color,
            bg=COLORS["card_bg"], anchor="w"
        )
        self._label.pack(anchor="w")

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

    def restyle(self):
        """Reapply colors from the current theme."""
        self.config(bg=COLORS["card_bg"])
        label_color = COLORS["danger"] if self._required else COLORS["text_secondary"]
        self._label.config(fg=label_color, bg=COLORS["card_bg"])
        self._entry.config(
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
        )
        if getattr(self, "_is_placeholder", False):
            self._entry.config(fg=COLORS["text_muted"])
        else:
            self._entry.config(fg=COLORS["text_primary"])


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

    def restyle(self):
        """Reapply colors from the current theme."""
        self.config(bg=COLORS["card_bg"])
        self._label.config(fg=COLORS["text_secondary"], bg=COLORS["card_bg"])
        self._text.config(
            bg=COLORS["input_bg"], fg=COLORS["text_primary"],
            insertbackground=COLORS["text_primary"],
            highlightbackground=COLORS["input_border"],
            highlightcolor=COLORS["input_focus"],
        )


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
        self._value_lbl = tk.Label(
            self, textvariable=self._value_var,
            font=FONTS["stat_number"], fg=color,
            bg=COLORS["card_bg"]
        )
        self._value_lbl.pack()
        self._title_lbl = tk.Label(
            self, text=title,
            font=FONTS["stat_label"], fg=COLORS["text_secondary"],
            bg=COLORS["card_bg"]
        )
        self._title_lbl.pack()

    def update_value(self, new_value: int):
        self._value_var.set(str(new_value))

    def restyle(self, color: str = None):
        """Reapply colors from the current theme."""
        color = color or self._stat_color or COLORS["primary"]
        self._stat_color = color
        self.config(bg=COLORS["card_bg"],
                    highlightbackground=COLORS["card_border"])
        self._value_lbl.config(fg=color, bg=COLORS["card_bg"])
        self._title_lbl.config(fg=COLORS["text_secondary"], bg=COLORS["card_bg"])


# ---------------------------------------------------------------------------
# Separator line
# ---------------------------------------------------------------------------

def horizontal_separator(parent) -> tk.Frame:
    """Return a thin horizontal line widget."""
    sep = tk.Frame(parent, bg=COLORS["card_border"], height=1)
    return sep
