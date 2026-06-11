"""
theme.py
Handles the application stylesheets, theme color palettes, and structural theme assignments.
"""

import os
import json
import tkinter as tk
from tkinter import ttk
import core
import constants

# --- Accent Colors ---
ACCENT_BLUE = "#3b82f6"
ACCENT_BLUE_HOVER = "#2563eb"


# --- Hardcoded Fallback Palette (Safety Net) ---
# Dictionary of UI color keys and their visual mapping:
# bg               : Main application background color.
# fg               : Main text (foreground) color.
# info_bg          : Background color for text areas (e.g., process log, inspector text).
# separator        : Color for borders, separators, and unselected outlines.
# entry_bg         : Background color for input fields, comboboxes, and the file list.
# disabled_fg      : Text color for disabled widgets, hints, and secondary text.
# error_bg         : Background color for error states (e.g., invalid LUFS/TP entry).
# button_bg        : Background color for standard buttons, scrollbars, and inactive tabs.
# button_hover     : Background color for buttons and tabs when hovered or active.
# text_relief      : Border style for text areas (e.g., 'flat', 'sunken', 'solid').
# accent           : Primary highlight color (used for primary buttons, progress bars, active focus).
# tree_selected    : Background color for the selected row(s) in the file list.
# tree_selected_fg : Text color for the selected row(s) in the file list.
# tree_row_alt     : Background color for alternating rows (if implemented by the style).
DEFAULT_PALETTES = {
    "light": {
        "bg": "#E0E0E0",                                              
        "fg": "#000000",                                
        "info_bg": "#ffffff",                                     
        "separator": "#808080",                                   
        "entry_bg": "#ffffff",                       
        "disabled_fg": "#6d6d6d",                                        
        "error_bg": "#f2b8b5",                                          
        "button_bg": "#d3d1ce",                                      
        "button_hover": "#e4e0d8",                                 
        "text_relief": "sunken",                                                
        "accent": "#0a64ad",                                        
        "tree_selected": "#0a64ad",                                        
        "tree_selected_fg": "#ffffff",
        "tree_row_alt": "#f7f7f7"
    }
}

DYNAMIC_THEMES = {}


# --- Theme Loader ---
def load_themes():
    """Scans `/themes/` folder and loads all dynamic themes."""
    global DYNAMIC_THEMES
    DYNAMIC_THEMES.clear()

    base_path = core.get_base_path()
    themes_dir = os.path.join(base_path, "themes")

    # Passively load existing theme files if directory exists
    if os.path.exists(themes_dir):
        try:
            existing_files = [f for f in os.listdir(themes_dir) if f.lower().endswith(".json")]
            for filename in existing_files:
                file_path = os.path.join(themes_dir, filename)
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        theme_data = json.load(f)
                    if isinstance(theme_data, dict) and "name" in theme_data:
                        name = theme_data["name"]
                        palette = {k: v for k, v in theme_data.items() if k != "name"}
                        DYNAMIC_THEMES[name] = palette
                except Exception:
                    pass
        except Exception:
            pass

    # Safety Fallback to compiled Light theme if folder is missing or unreadable
    if not DYNAMIC_THEMES:
        DYNAMIC_THEMES.update(DEFAULT_PALETTES)

    constants.THEME_MODES_LIST.clear()
    constants.THEME_MODES_LIST.extend(list(DYNAMIC_THEMES.keys()))


def is_dark_color(hex_color):
    """Calculates if a hex color is dark based on perceived luminance."""
    if not hex_color or not hex_color.startswith("#"):
        return True
    try:
        hex_color = hex_color.lstrip('#')
        lv = len(hex_color)
        if lv == 3:
            r, g, b = [int(hex_color[i]*2, 16) for i in range(3)]
        elif lv == 6:
            r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        else:
            return True
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        return luminance < 128
    except Exception:
        return True


def _reset_combobox_popdowns(parent):
    """
    Recursively finds all ttk.Combobox widgets and destroys their cached popdown windows.
    This forces Tcl/Tk to redraw the dropdown lists with the fresh theme colors on the next interaction.
    """
    for child in parent.winfo_children():
        if isinstance(child, ttk.Combobox):
            try:
                popdown = child.tk.call('ttk::combobox::PopdownWindow', child)
                if popdown:
                    child.tk.call('destroy', popdown)
            except Exception:
                pass
        _reset_combobox_popdowns(child)

def _apply_flat_theme(style: ttk.Style, root: tk.Tk, colors: dict, is_dark: bool):
    """Configures the entire ttk style hierarchy to match the requested color palette."""

    style.theme_use('clam')
    style.configure(".", background=colors["bg"], foreground=colors["fg"], font=("Segoe UI", 9))
    style.configure("TFrame", background=colors["bg"])

    style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], padding=2)
    style.map("TLabel", 
              background=[('disabled', colors["bg"])], 
              foreground=[('disabled', colors["disabled_fg"])])

    indicator_bg = colors["entry_bg"]
    style.configure("TCheckbutton", background=colors["bg"], foreground=colors["fg"], 
                    indicatorcolor=indicator_bg, bordercolor=colors["separator"], focuscolor=colors["bg"])
    style.map("TCheckbutton", 
              background=[('active', colors["bg"])], 
              foreground=[('active', colors["fg"])],
              indicatorcolor=[('active', colors["button_hover"]), ('selected', colors["accent"])])

    style.configure("TRadiobutton", background=colors["bg"], foreground=colors["fg"], 
                    indicatorcolor=indicator_bg, bordercolor=colors["separator"], focuscolor=colors["bg"])
    style.map("TRadiobutton", 
              background=[('active', colors["bg"])], 
              foreground=[('active', colors["fg"])],
              indicatorcolor=[('active', colors["button_hover"]), ('selected', colors["accent"])])

    style.configure("TLabelframe", background=colors["bg"], bordercolor=colors["separator"], 
                    relief="flat", borderwidth=1)

    style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["accent"], font=("Segoe UI", 9, "bold"))

    style.configure("TButton", background=colors["button_bg"], foreground=colors["fg"], 
                    bordercolor=colors["separator"], lightcolor=colors["button_bg"], 
                    darkcolor=colors["button_bg"], relief="flat", borderwidth=1, padding=(0, 4))
    style.map("TButton", 
              background=[('active', colors["button_hover"]), ('pressed', colors["separator"]), ('disabled', colors["bg"])], 
              bordercolor=[('active', colors["accent"]), ('focus', colors["accent"])],
              foreground=[('disabled', colors["disabled_fg"])])

    style.configure("Accent.TButton", background=colors["accent"], foreground="#ffffff" if not is_dark else colors["bg"], 
                    bordercolor=colors["accent"], relief="flat", borderwidth=1, padding=(0, 4), font=("Segoe UI", 9, "bold"))
    style.map("Accent.TButton", 
              background=[('active', colors["fg"]), ('disabled', colors["bg"])],
              bordercolor=[('disabled', colors["separator"])],
              foreground=[('disabled', colors["disabled_fg"]), ('active', colors["bg"])])

    style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["fg"], 
                    bordercolor=colors["separator"], lightcolor=colors["entry_bg"], 
                    darkcolor=colors["entry_bg"], relief="flat", borderwidth=1, padding=4,
                    insertcolor=colors["accent"])
    style.map("TEntry", 
              fieldbackground=[('disabled', colors["bg"])], 
              foreground=[('disabled', colors["disabled_fg"])],
              bordercolor=[('focus', colors["accent"])])

    style.configure("Error.TEntry", fieldbackground=colors["error_bg"], foreground=colors["fg"], bordercolor="#ef4444")

    style.configure("TCombobox", fieldbackground=colors["entry_bg"], foreground=colors["fg"], 
                    background=colors["button_bg"], bordercolor=colors["separator"], arrowcolor=colors["fg"], 
                    lightcolor=colors["entry_bg"], darkcolor=colors["entry_bg"], relief="flat", padding=4)
    style.map("TCombobox",
        fieldbackground=[('disabled', colors["bg"]), ('readonly', colors["entry_bg"])],
        foreground=[('disabled', colors["disabled_fg"]), ('readonly', colors["fg"])],
        bordercolor=[('focus', colors["accent"]), ('hover', colors["accent"])],
        background=[('active', colors["button_hover"]), ('pressed', colors["button_hover"]), ('disabled', colors["bg"])],
        arrowcolor=[('active', colors["accent"]), ('pressed', colors["accent"]), ('disabled', colors["disabled_fg"])]
    )

    style.configure("Horizontal.TSeparator", background=colors["separator"])

    style.configure("TScrollbar",
                    troughcolor=colors["entry_bg"],
                    background=colors["button_bg"],
                    bordercolor=colors["separator"],
                    arrowcolor=colors["fg"],
                    lightcolor=colors["button_bg"],
                    darkcolor=colors["button_bg"],
                    relief="flat",
                    arrowsize=12,
                    width=12)
    style.map("TScrollbar",
              background=[('active', colors["button_hover"]), ('disabled', colors["bg"])],
              arrowcolor=[('active', colors["accent"]), ('disabled', colors["disabled_fg"])],
              bordercolor=[('disabled', colors["bg"])])

    style.configure("TNotebook", background=colors["bg"], borderwidth=0, lightcolor=colors["bg"], darkcolor=colors["bg"])
    style.configure("TNotebook.Tab", background=colors["button_bg"], foreground=colors["fg"], 
                    bordercolor=colors["separator"], lightcolor=colors["button_bg"], darkcolor=colors["button_bg"],
                    padding=(12, 4), focuscolor=colors["bg"])
    style.map("TNotebook.Tab", 
              background=[('selected', colors["bg"]), ('active', colors["button_hover"])],
              foreground=[('selected', colors["accent"]), ('disabled', colors["disabled_fg"])],
              bordercolor=[('selected', colors["separator"])])

    style.configure("Treeview", background=colors["entry_bg"], foreground=colors["fg"], 
                    fieldbackground=colors["entry_bg"], rowheight=28,
                    bordercolor=colors["separator"], relief="flat", borderwidth=1)
    style.map("Treeview", 
              background=[('selected', colors["tree_selected"])], 
              foreground=[('selected', colors["tree_selected_fg"])])

    style.configure("Treeview.Heading", background=colors["bg"], foreground=colors["disabled_fg"], 
                    bordercolor=colors["separator"], relief="flat", borderwidth=1, font=("Segoe UI", 9, "bold"))
    style.map("Treeview.Heading", 
              background=[('active', colors["button_hover"])], 
              foreground=[('active', colors["fg"])])

    style.configure("Horizontal.TProgressbar", 
                    troughcolor=colors["entry_bg"], 
                    background=colors["accent"], 
                    bordercolor=colors["separator"], 
                    lightcolor=colors["accent"], 
                    darkcolor=colors["accent"], 
                    relief="flat")

def apply_theme(style: ttk.Style, root: tk.Tk, mode: str = "light") -> dict:
    """Entry point to configure ttk styles. Translates the requested mode string into the corresponding color palette."""
    colors = DYNAMIC_THEMES.get(mode, DYNAMIC_THEMES.get("light", DEFAULT_PALETTES["light"]))
    is_dark_theme = is_dark_color(colors.get("bg", "#171717"))

    root.config(bg=colors["bg"])
    root.option_add("*TCombobox*Listbox*Background", colors["entry_bg"])
    root.option_add("*TCombobox*Listbox*Foreground", colors["fg"])
    root.option_add("*TCombobox*Listbox*selectBackground", colors["accent"])

    root.option_add("*TCombobox*Listbox*selectForeground", colors["bg"] if is_dark_theme else "#ffffff")
    root.option_add("*TCombobox*Listbox*borderwidth", "0")

    _apply_flat_theme(style, root, colors, is_dark=is_dark_theme)

    try:
        _reset_combobox_popdowns(root)
    except Exception:
        pass

    return colors


# Initialize themes on module import
load_themes()