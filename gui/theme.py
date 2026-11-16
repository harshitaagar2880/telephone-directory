"""
gui/theme.py
------------
Centralised colour palette, fonts and widget style definitions.
Supports Light / Dark themes and accent colour options.
Import COLORS and FONTS in every GUI module for consistent styling.
Call apply_theme("light"|"dark") and set_accent_color(hex) to change appearance.
"""

# ---------------------------------------------------------------------------
# Colour palettes — Light (default) and Dark
# ---------------------------------------------------------------------------

LIGHT_COLORS = {
    # Sidebar
    "sidebar_bg":      "#1E2A3A",
    "sidebar_hover":   "#2C3E55",
    "sidebar_active":  "#2980B9",
    "sidebar_text":    "#ECF0F1",
    "sidebar_icon":    "#7F8C8D",

    # Main area
    "main_bg":         "#F0F4F8",
    "card_bg":         "#FFFFFF",
    "card_border":     "#DDE3EA",

    # Header / title bar
    "header_bg":       "#FFFFFF",
    "header_border":   "#DDE3EA",

    # Accent
    "primary":         "#2980B9",
    "primary_hover":   "#2471A3",
    "primary_light":   "#D6EAF8",

    "success":         "#27AE60",
    "success_light":   "#D5F5E3",
    "danger":          "#E74C3C",
    "danger_hover":    "#C0392B",
    "danger_light":    "#FADBD8",
    "warning":         "#F39C12",
    "warning_light":   "#FDEBD0",

    # Text
    "text_primary":    "#2C3E50",
    "text_secondary":  "#7F8C8D",
    "text_muted":      "#BDC3C7",
    "text_on_accent":  "#FFFFFF",

    # Inputs
    "input_bg":        "#FFFFFF",
    "input_border":    "#BDC3C7",
    "input_focus":     "#2980B9",

    # Treeview
    "tree_header":     "#2C3E50",
    "tree_header_fg":  "#FFFFFF",
    "tree_odd":        "#FFFFFF",
    "tree_even":       "#F7F9FC",
    "tree_selected":   "#D6EAF8",
    "tree_selected_fg":"#1A252F",

    # Favourite / Emergency badges
    "favourite":       "#F39C12",
    "emergency":       "#E74C3C",
}

DARK_COLORS = {
    # Sidebar
    "sidebar_bg":      "#2C3E50",
    "sidebar_hover":   "#34495E",
    "sidebar_active":  "#3498DB",
    "sidebar_text":    "#ECF0F1",
    "sidebar_icon":    "#95A5A6",

    # Main area
    "main_bg":         "#1A1A2E",
    "card_bg":         "#16213E",
    "card_border":     "#0F3460",

    # Header / title bar
    "header_bg":       "#16213E",
    "header_border":   "#0F3460",

    # Accent
    "primary":         "#3498DB",
    "primary_hover":   "#2980B9",
    "primary_light":   "#2C3E50",

    "success":         "#2ECC71",
    "success_light":   "#1B4332",
    "danger":          "#E74C3C",
    "danger_hover":    "#C0392B",
    "danger_light":    "#4A1A1A",
    "warning":         "#F39C12",
    "warning_light":   "#6B4226",

    # Text
    "text_primary":    "#ECF0F1",
    "text_secondary":  "#95A5A6",
    "text_muted":      "#7F8C8D",
    "text_on_accent":  "#FFFFFF",

    # Inputs
    "input_bg":        "#0F3460",
    "input_border":    "#1A1A2E",
    "input_focus":     "#3498DB",

    # Treeview
    "tree_header":     "#34495E",
    "tree_header_fg":  "#ECF0F1",
    "tree_odd":        "#16213E",
    "tree_even":       "#1F2A44",
    "tree_selected":   "#3498DB",
    "tree_selected_fg":"#FFFFFF",

    # Favourite / Emergency badges
    "favourite":       "#F39C12",
    "emergency":       "#E74C3C",
}

# Accent colour options (overrides the "primary" accent)
ACCENT_COLORS = {
    "blue":   "#2980B9",
    "green":  "#27AE60",
    "purple": "#8E44AD",
    "orange": "#E67E22",
    "red":    "#E74C3C",
    "teal":   "#1ABC9C",
}

# ---------------------------------------------------------------------------
# Current theme state
# ---------------------------------------------------------------------------

_CURRENT_THEME = "light"   # "light" or "dark"
_CURRENT_ACCENT = "blue"   # key into ACCENT_COLORS

COLORS = dict(LIGHT_COLORS)  # active palette (mutable, updated by apply_theme)


def get_current_theme() -> str:
    """Return the current theme name: 'light' or 'dark'."""
    return _CURRENT_THEME


def get_current_accent() -> str:
    """Return the current accent color key."""
    return _CURRENT_ACCENT


def apply_theme(theme_name: str) -> None:
    """
    Switch the active colour palette in place.
    theme_name: "light" or "dark".
    All modules that imported COLORS will see the update because they reference
    the same dict object.
    """
    global _CURRENT_THEME, COLORS
    theme_name = theme_name.lower()
    if theme_name not in ("light", "dark"):
        theme_name = "light"
    _CURRENT_THEME = theme_name
    base = LIGHT_COLORS if theme_name == "light" else DARK_COLORS
    COLORS.clear()
    COLORS.update(base)
    # Re-apply the saved accent colour on top of the base palette
    accent_hex = ACCENT_COLORS.get(_CURRENT_ACCENT, ACCENT_COLORS["blue"])
    COLORS["primary"] = accent_hex
    COLORS["primary_hover"] = accent_hex
    COLORS["input_focus"] = accent_hex
    COLORS["tree_selected"] = accent_hex


def set_accent_color(accent_key: str) -> None:
    """
    Change the accent colour used for primary buttons, selection, focus, etc.
    accent_key: one of ACCENT_COLORS keys (blue, green, purple, orange, red, teal).
    """
    global _CURRENT_ACCENT, COLORS
    if accent_key not in ACCENT_COLORS:
        accent_key = "blue"
    _CURRENT_ACCENT = accent_key
    COLORS["primary"] = ACCENT_COLORS[accent_key]
    COLORS["primary_hover"] = ACCENT_COLORS[accent_key]
    COLORS["input_focus"] = ACCENT_COLORS[accent_key]
    COLORS["tree_selected"] = ACCENT_COLORS[accent_key]

# ---------------------------------------------------------------------------
# Font definitions   (family, size, weight)
# ---------------------------------------------------------------------------
FONTS = {
    "app_title":   ("Segoe UI", 18, "bold"),
    "page_title":  ("Segoe UI", 15, "bold"),
    "section":     ("Segoe UI", 11, "bold"),
    "body":        ("Segoe UI", 10),
    "body_bold":   ("Segoe UI", 10, "bold"),
    "small":       ("Segoe UI", 9),
    "small_bold":  ("Segoe UI", 9, "bold"),
    "button":      ("Segoe UI", 10),
    "input":       ("Segoe UI", 10),
    "mono":        ("Consolas",  9),
    "stat_number": ("Segoe UI", 22, "bold"),
    "stat_label":  ("Segoe UI",  9),
}

# ---------------------------------------------------------------------------
# TTK style configuration helper
# ---------------------------------------------------------------------------

def apply_treeview_style(style) -> None:
    """
    Configure a ttk.Style object for the contacts Treeview.
    Call once after creating the root window.
    """
    style.theme_use("clam")

    # Treeview body
    style.configure(
        "Contacts.Treeview",
        background    = COLORS["tree_odd"],
        fieldbackground = COLORS["tree_odd"],
        foreground    = COLORS["text_primary"],
        rowheight     = 32,
        font          = FONTS["body"],
        borderwidth   = 0,
    )
    style.map(
        "Contacts.Treeview",
        background  = [("selected", COLORS["tree_selected"])],
        foreground  = [("selected", COLORS["tree_selected_fg"])],
    )

    # Column headers
    style.configure(
        "Contacts.Treeview.Heading",
        background  = COLORS["tree_header"],
        foreground  = COLORS["tree_header_fg"],
        font        = FONTS["body_bold"],
        relief      = "flat",
        padding     = (8, 6),
    )
    style.map(
        "Contacts.Treeview.Heading",
        background = [("active", COLORS["sidebar_active"])],
    )

    # Scrollbars
    style.configure(
        "Vertical.TScrollbar",
        background  = COLORS["card_border"],
        troughcolor = COLORS["main_bg"],
        arrowcolor  = COLORS["text_secondary"],
        borderwidth = 0,
        width       = 10,
    )
