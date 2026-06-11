"""
dialogs.py
Contains all secondary popup windows like Options and About.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import webbrowser
import datetime

import constants
import core
import i18n
import utils

get_text = i18n.get_text
config = core.app_config

# --- About Dialog ---
class AboutDialog:
    """Displays the application's about window."""
    def __init__(self, parent, colors):
        """Initializes the AboutDialog."""
        self.parent = parent
        self.colors = colors
        self.win = tk.Toplevel(self.parent)

        self.win.geometry("455x585") 
        self.win.title(get_text("menu_info_about"))
        self.win.configure(bg=self.colors["bg"])
        self.win.transient(self.parent)
        self.win.grab_set()

        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        utils.center_window(self.win)

    def on_close(self):
        """Closes the dialog window."""
        self.win.destroy()

    def refresh_language(self):
        """Refreshes all visible options-dialog texts after a language switch."""
        if not self.win.winfo_exists():
            return
        self.win.title(get_text("menu_info_about"))
        self.win.configure(bg=self.colors["bg"])
        for child in self.win.winfo_children():
            child.destroy()
        self.create_widgets()

    def create_widgets(self):
        """Creates the dialog widgets."""
        about_frame = ttk.LabelFrame(self.win, text=f" {get_text('app_title')} ")
        about_frame.pack(padx=constants.GUI_PADX, pady=constants.GUI_PADY, fill=tk.BOTH, expand=True)

        bold_font = ("Helvetica", 9, "bold")
        large_bold_font = ("Helvetica", 11, "bold")

        ttk.Label(about_frame, text=get_text("app_title_long"), font=large_bold_font).pack(pady=(constants.GUI_PADY, 2))

        version_frame = ttk.Frame(about_frame)
        version_frame.pack()
        emoji_font = ("Segoe UI Emoji", 10)
        ttk.Label(version_frame, text=f"{get_text('about_version', version=constants.VERSION)} ", font=bold_font).pack(side=tk.LEFT)
        ttk.Label(version_frame, text=constants.EDITION_NAME, font=emoji_font).pack(side=tk.LEFT)

        ttk.Label(about_frame, text=get_text("about_build_date", build_date=constants.BUILD_DATE)).pack(pady=(0, constants.GUI_PADY))

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        desc_frame = ttk.Frame(about_frame)
        desc_frame.pack(fill='x', padx=constants.GUI_PADX)
        for line in get_text("about_description").splitlines():
            ttk.Label(desc_frame, text=line, justify=tk.LEFT).pack(anchor="w")

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        ttk.Label(about_frame, text=get_text("about_author", author=constants.AUTHOR), font=bold_font).pack(anchor="w", padx=constants.GUI_PADX)
        ttk.Label(about_frame, text=get_text("about_email", email="melcom [@] vodafonemail.de")).pack(anchor="w", padx=constants.GUI_PADX, pady=(0, constants.GUI_PADY))

        for header_key, links in [("about_website_header", [("about_website_1", "https://www.melcom-music.de"), ("about_website_2", "https://scenes.at/melcom")]),
                                  ("about_youtube_header", [("about_youtube_link", "https://youtube.com/@melcom")]),
                                  ("about_bluesky_header", [("about_bluesky_link", "https://melcom-music.bsky.social")])]:
            ttk.Label(about_frame, text=get_text(header_key), font=bold_font).pack(anchor="w", padx=constants.GUI_PADX, pady=(constants.GUI_PADY, 0))
            for text_key, url in links:
                link = ttk.Label(about_frame, text=get_text(text_key), foreground="#4a90e2", cursor="hand2")
                link.pack(anchor="w", padx=constants.GUI_PADX)
                link.bind("<Button-1>", lambda e, link_url=url: webbrowser.open(link_url))

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        ttk.Label(about_frame, text=get_text("about_opensource", year=datetime.datetime.now().year)).pack()
        ttk.Label(about_frame, text=get_text("about_license")).pack()
        ttk.Label(about_frame, text=get_text("about_copyright", year=datetime.datetime.now().year)).pack()

        ttk.Button(about_frame, text=get_text("about_ok_button"), command=self.on_close).pack(pady=constants.GUI_PADY)


# --- Options Dialog ---
class OptionsDialog:
    """Displays the options window for application preferences."""
    def __init__(self, parent, app, colors):
        """Initializes the OptionsDialog."""
        self.parent = parent
        self.app = app
        self.colors = colors
        self.win = tk.Toplevel(self.parent)

        self.win.geometry("600x320")
        self.win.title(get_text("options_dialog_title"))
        self.win.configure(bg=self.colors["bg"])
        self.win.transient(self.parent)
        self.win.grab_set()

        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

        i18n.load_languages()
        available_languages = i18n.get_available_language_codes()
        initial_language = config.language if config.language in available_languages else constants.DEFAULT_LANGUAGE_CODE
        self.lang_var = tk.StringVar(value=initial_language)
        self.theme_var = tk.StringVar(value=config.theme_mode)
        self.ffmpeg_path_var = tk.StringVar(value=config.ffmpeg_path)
        self.single_log_var = tk.BooleanVar(value=config.single_log_entry_enabled)
        self.log_size_var = tk.IntVar(value=config.log_file_size_kb)

        self.create_widgets()
        utils.center_window(self.win)

    def on_close(self):
        """Closes the dialog window."""
        self.win.destroy()

    def refresh_language(self):
        """Refreshes all visible about-dialog texts after a language switch."""
        if not self.win.winfo_exists():
            return
        self.win.title(get_text("options_dialog_title"))
        self.win.configure(bg=self.colors["bg"])
        for child in self.win.winfo_children():
            child.destroy()
        self.create_widgets()

    def create_widgets(self):
        """Creates the dialog widgets."""
        top_row_frame = ttk.Frame(self.win, style="TFrame")
        top_row_frame.pack(fill=tk.X, padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        lang_frame = ttk.LabelFrame(top_row_frame, text=f" {get_text('options_language_group')} ")
        lang_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        theme_group_text = get_text("options_theme_group")
        if theme_group_text.startswith("["): theme_group_text = "Theme Settings"
        theme_label_text = get_text("options_theme_label")
        if theme_label_text.startswith("["): theme_label_text = "App Theme:"

        theme_frame = ttk.LabelFrame(top_row_frame, text=f" {theme_group_text} ")
        theme_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))

        ffmpeg_frame = ttk.LabelFrame(self.win, text=f" {get_text('options_ffmpeg_path_group')} ")
        ffmpeg_frame.pack(fill=tk.X, padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        log_frame = ttk.LabelFrame(self.win, text=f" {get_text('options_log_settings_group')} ")
        log_frame.pack(fill=tk.X, padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        ttk.Label(lang_frame, text=get_text("options_language_label")).pack(side=tk.LEFT, padx=5, pady=5)
        language_values = i18n.get_available_language_codes(refresh=True)
        ttk.Combobox(lang_frame, textvariable=self.lang_var, values=language_values, state="readonly", width=12).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Label(theme_frame, text=theme_label_text).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(theme_frame, textvariable=self.theme_var, values=constants.THEME_MODES_LIST, state="readonly", width=18).pack(side=tk.LEFT, padx=5, pady=5)

        ttk.Entry(ffmpeg_frame, textvariable=self.ffmpeg_path_var, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        ttk.Button(ffmpeg_frame, text=get_text("options_browse_button"), command=self.browse_ffmpeg).pack(side=tk.LEFT, padx=5)

        self.log_size_entry = ttk.Entry(log_frame, textvariable=self.log_size_var, width=10)

        chk = ttk.Checkbutton(log_frame, text=get_text("options_log_single_entry_check"), variable=self.single_log_var, command=self.toggle_log_size)
        chk.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)

        ttk.Label(log_frame, text=get_text("options_log_size_label")).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.log_size_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        self.toggle_log_size()

        ttk.Button(self.win, text=get_text("options_save_button"), command=self.save_and_close).pack(pady=constants.GUI_PADY)

    def browse_ffmpeg(self):
        """Performs browse ffmpeg."""
        path = filedialog.askdirectory(title=get_text("options_ffmpeg_path_dialog_title"))
        if path: 
            self.ffmpeg_path_var.set(path)

    def toggle_log_size(self):
        """Toggles the associated setting or state."""
        self.log_size_entry.config(state=tk.DISABLED if self.single_log_var.get() else tk.NORMAL)

    def save_and_close(self):
        """Saves the current data or settings."""
        ffmpeg_path = self.ffmpeg_path_var.get()
        if not os.path.exists(os.path.join(ffmpeg_path, constants.FFMPEG_EXECUTABLE_NAME)):
            messagebox.showerror(get_text("options_error_invalid_ffmpeg_path_title"), get_text("options_error_invalid_ffmpeg_path_message"), parent=self.win)
            return

        config.ffmpeg_path = ffmpeg_path
        config.log_file_size_kb = self.log_size_var.get()
        config.single_log_entry_enabled = self.single_log_var.get()

        core.reinit_logger()

        available_languages = i18n.get_available_language_codes(refresh=True)
        selected_language = self.lang_var.get().strip() or constants.DEFAULT_LANGUAGE_CODE
        if selected_language not in available_languages:
            selected_language = constants.DEFAULT_LANGUAGE_CODE if constants.DEFAULT_LANGUAGE_CODE in available_languages else (available_languages[0] if available_languages else constants.DEFAULT_LANGUAGE_CODE)

        lang_changed = config.language != selected_language
        config.language = selected_language

        theme_changed = config.theme_mode != self.theme_var.get()
        config.theme_mode = self.theme_var.get()

        config.save_options()

        if theme_changed:
            self.app.setup_styles()
            self.app.process_info.config(bg=self.app.colors["info_bg"], fg=self.app.colors["fg"], relief=self.app.colors.get("text_relief", "sunken"))
            if hasattr(self.app, "empty_queue_label"):
                self.app.empty_queue_label.config(bg=self.app.colors["entry_bg"], fg=self.app.colors["disabled_fg"])
            if hasattr(self.app, "visualizer"):
                self.app.visualizer.update_colors(self.app.colors["bg"], self.app.colors["accent"])
            if hasattr(self.app, "inspector_window") and self.app.inspector_window is not None:
                try:
                    if self.app.inspector_window.win.winfo_exists():
                        self.app.inspector_window.update_theme_colors(self.app.colors)
                except Exception:
                    pass

        if lang_changed:
            i18n.load_language(config.language)
            self.app.apply_language()
        elif theme_changed:
            self.app.apply_language()

        self.on_close()