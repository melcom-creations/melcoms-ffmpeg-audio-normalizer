# -*- coding: utf-8 -*-
"""
theme.py
Handles the application stylesheets, theme color palettes, and structural theme assignments.
"""

import tkinter as tk
from tkinter import ttk

# Universal Accent Color
ACCENT_BLUE = "#3b82f6"
ACCENT_BLUE_HOVER = "#2563eb"

# Color Palettes
LIGHT_PALETTE = {
    "bg": "#E0E0E0",               # Classic light gray background
    "fg": "#000000",               # Deep black text
    "info_bg": "#ffffff",          # Pure white for text areas
    "separator": "#808080",        # Distinct gray for borders
    "entry_bg": "#ffffff",         # Input fields
    "disabled_fg": "#6d6d6d",      # Muted gray for inactive elements
    "error_bg": "#f2b8b5",         # Bright red indicator for errors
    "button_bg": "#d3d1ce",        # Standard Windows button gray
    "button_hover": "#e4e0d8",     # Slightly brighter on hover
    "text_relief": "sunken",       # Restores legacy 3D text area appearance
    "accent": "#0a64ad",           # Classic deep blue highlight
    "tree_selected": "#0a64ad",    # Highlight color for list selection
    "tree_selected_fg": "#ffffff"
}

MODERNLIGHT_PALETTE = {
    "bg": "#f3f4f6",               # Soft, modern light gray background
    "fg": "#1f2937",               # Dark gray text for optimal readability
    "info_bg": "#ffffff",          # Pure white text areas
    "separator": "#e5e7eb",        # Subtle dividers
    "entry_bg": "#ffffff",         # Flat input fields
    "disabled_fg": "#9ca3af",      # Light gray for inactive elements
    "error_bg": "#fee2e2",         # Pastel red for errors
    "button_bg": "#ffffff",        # Flat white buttons
    "button_hover": "#f9fafb",     # Very slight tint on hover
    "text_relief": "flat",
    "accent": ACCENT_BLUE,
    "tree_selected": "#eff6ff",    # Soft blue highlight for lists
    "tree_selected_fg": "#1d4ed8"
}

MELCOM_PALETTE = {
    "bg": "#02131b",               # Deep oceanic dark background
    "fg": "#d7f7ff",               # High-contrast light cyan text
    "info_bg": "#0a1c24",          # Slightly elevated background for areas
    "separator": "#0e4c63",        # Submerged blue borders
    "entry_bg": "#102734",         # Deep blue input fields
    "disabled_fg": "#6b94a3",      # Muted cyan for inactive states
    "error_bg": "#7f1d1d",         # Deep crimson for errors
    "button_bg": "#102734",        # Button base
    "button_hover": "#154055",     # Button hover state
    "text_relief": "flat",
    "accent": "#00b7ff",           # Bright neon cyan highlight
    "tree_selected": "#006d8f",    # Electric blue list highlight
    "tree_selected_fg": "#ffffff"
}

AQUAMARINE_BLUE_PALETTE = {
    "bg": "#12202b",               # Classic Tracker Slate Blue background
    "fg": "#84c6c2",               # Aquamarine text
    "info_bg": "#0c151c",          # Darker inset background for logs
    "separator": "#21394a",        # Visible but subtle tracker borders
    "entry_bg": "#0e1922",         # Deep tracker input fields
    "disabled_fg": "#416361",      # Dimmed Aquamarine for inactive states
    "error_bg": "#6b2222",         # Muted Tracker Red for errors
    "button_bg": "#182a38",        # Button Base
    "button_hover": "#223b4f",     # Button Hover
    "text_relief": "flat",
    "accent": "#4bd1ca",           # Bright Aquamarine Highlight
    "tree_selected": "#2e506b",    # Dusty Blue Highlight (Tracker Row)
    "tree_selected_fg": "#e6f7f7"  # Bright Cyan readable text
}

MIDNIGHT_PALETTE = {
    "bg": "#0f172a",               # Modern dark slate background
    "fg": "#f8fafc",               # Crisp white text
    "info_bg": "#1e293b",          # Elevated dark panels
    "separator": "#334155",        # Clear dividing lines
    "entry_bg": "#1e293b",         # Flat dark input fields
    "disabled_fg": "#64748b",      # Slate gray inactive elements
    "error_bg": "#7f1d1d",         # Deep red for errors
    "button_bg": "#1e293b",        # Dark button base
    "button_hover": "#334155",     # Lighter hover state
    "text_relief": "flat",
    "accent": "#3b82f6",           # Modern Royal Blue highlight
    "tree_selected": "#1d4ed8",    # Strong blue selection
    "tree_selected_fg": "#ffffff"
}

LADERLAPPEN_PALETTE = {
    "bg": "#171717",               # True dark carbon background
    "fg": "#f5f5f5",               # Off-white highly readable text
    "info_bg": "#222222",          # Raised carbon panels
    "separator": "#4a4a4a",        # Distinct neutral gray borders
    "entry_bg": "#2a2a2a",         # Slightly elevated input fields
    "disabled_fg": "#7b7b7b",      # Distinct inactive gray
    "error_bg": "#7f1d1d",         # Strong crimson error state
    "button_bg": "#303038",        # Heavy industrial button base
    "button_hover": "#3a3a44",     # Industrial hover glow
    "text_relief": "flat",
    "accent": "#CB850C",           # Signature golden bat accent
    "tree_selected": "#50505c",    # Deep gray selection highlight
    "tree_selected_fg": "#ffffff"
}

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
    
    # Labels
    style.configure("TLabel", background=colors["bg"], foreground=colors["fg"], padding=2)
    style.map("TLabel", 
              background=[('disabled', colors["bg"])], 
              foreground=[('disabled', colors["disabled_fg"])])
    
    # Checkbuttons & Radiobuttons
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
    
    # LabelFrames
    style.configure("TLabelframe", background=colors["bg"], bordercolor=colors["separator"], 
                    relief="flat", borderwidth=1)
    
    # Bold titles for structural hierarchy
    style.configure("TLabelframe.Label", background=colors["bg"], foreground=colors["accent"], font=("Segoe UI", 9, "bold"))
    
    # Buttons
    style.configure("TButton", background=colors["button_bg"], foreground=colors["fg"], 
                    bordercolor=colors["separator"], lightcolor=colors["button_bg"], 
                    darkcolor=colors["button_bg"], relief="flat", borderwidth=1, padding=(0, 4))
    style.map("TButton", 
              background=[('active', colors["button_hover"]), ('pressed', colors["separator"]), ('disabled', colors["bg"])], 
              bordercolor=[('active', colors["accent"]), ('focus', colors["accent"])],
              foreground=[('disabled', colors["disabled_fg"])])
              
    # Accent Button (Used to highlight primary workflow actions)
    style.configure("Accent.TButton", background=colors["accent"], foreground="#ffffff" if not is_dark else colors["bg"], 
                    bordercolor=colors["accent"], relief="flat", borderwidth=1, padding=(0, 4), font=("Segoe UI", 9, "bold"))
    style.map("Accent.TButton", 
              background=[('active', colors["fg"]), ('disabled', colors["bg"])],
              bordercolor=[('disabled', colors["separator"])],
              foreground=[('disabled', colors["disabled_fg"]), ('active', colors["bg"])])
    
    # Entries
    style.configure("TEntry", fieldbackground=colors["entry_bg"], foreground=colors["fg"], 
                    bordercolor=colors["separator"], lightcolor=colors["entry_bg"], 
                    darkcolor=colors["entry_bg"], relief="flat", borderwidth=1, padding=4,
                    insertcolor=colors["accent"])
    style.map("TEntry", 
              fieldbackground=[('disabled', colors["bg"])], 
              foreground=[('disabled', colors["disabled_fg"])],
              bordercolor=[('focus', colors["accent"])])
              
    style.configure("Error.TEntry", fieldbackground=colors["error_bg"], foreground=colors["fg"], bordercolor="#ef4444")
    
    # Comboboxes
    style.configure("TCombobox", fieldbackground=colors["entry_bg"], foreground=colors["fg"], 
                    bordercolor=colors["separator"], arrowcolor=colors["fg"], 
                    lightcolor=colors["entry_bg"], darkcolor=colors["entry_bg"], relief="flat", padding=4)
    style.map("TCombobox",
        fieldbackground=[('disabled', colors["bg"]), ('readonly', colors["entry_bg"])],
        foreground=[('disabled', colors["disabled_fg"]), ('readonly', colors["fg"])],
        bordercolor=[('focus', colors["accent"]), ('hover', colors["accent"])]
    )
    
    # Separators
    style.configure("Horizontal.TSeparator", background=colors["separator"])
    
    # Treeview (File List)
    style.configure("Treeview", background=colors["entry_bg"], foreground=colors["fg"], 
                    fieldbackground=colors["entry_bg"], rowheight=28,
                    bordercolor=colors["separator"], relief="flat", borderwidth=1)
    style.map("Treeview", 
              background=[('selected', colors["tree_selected"])], 
              foreground=[('selected', colors["tree_selected_fg"])])
    
    # Treeview Headers
    style.configure("Treeview.Heading", background=colors["bg"], foreground=colors["disabled_fg"], 
                    bordercolor=colors["separator"], relief="flat", borderwidth=1, font=("Segoe UI", 9, "bold"))
    style.map("Treeview.Heading", 
              background=[('active', colors["button_hover"])], 
              foreground=[('active', colors["fg"])])
              
    # Progressbar
    style.configure("Horizontal.TProgressbar", 
                    troughcolor=colors["entry_bg"], 
                    background=colors["accent"], 
                    bordercolor=colors["separator"], 
                    lightcolor=colors["accent"], 
                    darkcolor=colors["accent"], 
                    relief="flat")

def apply_theme(style: ttk.Style, root: tk.Tk, mode: str = "light") -> dict:
    """Entry point to configure ttk styles. Translates the requested mode string into the corresponding color palette."""
    if mode == "melcom":
        colors = MELCOM_PALETTE
    elif mode == "läderlappen":
        colors = LADERLAPPEN_PALETTE
    elif mode == "midnight":
        colors = MIDNIGHT_PALETTE
    elif mode == "modernlight":
        colors = MODERNLIGHT_PALETTE
    elif mode == "aquamarine & blue":
        colors = AQUAMARINE_BLUE_PALETTE
    else:
        colors = LIGHT_PALETTE
    
    root.config(bg=colors["bg"])
    root.option_add("*TCombobox*Listbox*Background", colors["entry_bg"])
    root.option_add("*TCombobox*Listbox*Foreground", colors["fg"])
    root.option_add("*TCombobox*Listbox*selectBackground", colors["accent"])
    
    is_dark_theme = mode in ("midnight", "melcom", "läderlappen", "aquamarine & blue")
    root.option_add("*TCombobox*Listbox*selectForeground", colors["bg"] if is_dark_theme else "#ffffff")
    root.option_add("*TCombobox*Listbox*borderwidth", "0")
    
    _apply_flat_theme(style, root, colors, is_dark=is_dark_theme)
        
    try:
        _reset_combobox_popdowns(root)
    except Exception:
        pass
        
    return colors