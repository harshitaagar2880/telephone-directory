"""
gui/theme.py
------------
Centralised colour palette, fonts and widget style definitions.
Import COLORS and FONTS in every GUI module for consistent styling.
"""

# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------
COLORS = {
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
