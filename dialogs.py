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


def _set_window_icon(window):
    """Applies the application icon to a secondary window when available."""
    icon_path = os.path.join(core.get_base_path(), "favicon", "melcom.ico")
    if not os.path.exists(icon_path):
        icon_path = os.path.join(core.get_base_path(), "custom", "favicon", "melcom.ico")
    if os.path.exists(icon_path):
        try:
            window.iconbitmap(icon_path)
        except Exception:
            pass
# --- About Dialog ---
class AboutDialog:
    """Displays the application's about window."""
    def __init__(self, parent, colors):
        """Initializes the AboutDialog."""
        self.parent = parent
        self.colors = colors
        self.win = tk.Toplevel(self.parent)
        utils.prepare_window(self.win)
        _set_window_icon(self.win)

        self.win.geometry("455x585") 
        self.win.title(get_text("menu_info_about"))
        self.win.configure(bg=self.colors["bg"])
        self.win.transient(self.parent)

        self.win.protocol("WM_DELETE_WINDOW", self.on_close)
        self.create_widgets()
        utils.center_window(self.win)
        utils.show_prepared_window(self.win)
        self.win.grab_set()

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


# --- Update Dialog ---
class UpdateAvailableDialog:
    """Displays a localized notification for a newer GitHub release."""

    def __init__(self, parent, colors, current_version, latest_version, release_url):
        """Initializes the update notification dialog."""
        self.parent = parent
        self.release_url = release_url
        self.win = tk.Toplevel(parent)
        utils.prepare_window(self.win)
        _set_window_icon(self.win)


        self.win.geometry("520x230")
        self.win.title(get_text("update_available_title"))
        self.win.configure(bg=colors["bg"])
        self.win.transient(parent)
        self.win.protocol("WM_DELETE_WINDOW", self.close)

        frame = ttk.LabelFrame(self.win, text=f" {get_text('update_available_title')} ")
        frame.pack(fill=tk.BOTH, expand=True, padx=constants.GUI_PADX, pady=constants.GUI_PADY)

        message = get_text(
            "update_available_message",
            current_version=current_version,
            latest_version=latest_version
        )
        ttk.Label(
            frame,
            text=message,
            justify=tk.LEFT,
            wraplength=460
        ).pack(fill=tk.X, padx=constants.GUI_PADX, pady=(constants.GUI_PADY * 2, constants.GUI_PADY))

        button_frame = ttk.Frame(frame)
        button_frame.pack(pady=constants.GUI_PADY)
        ttk.Button(
            button_frame,
            text=get_text("update_open_release_button"),
            command=self.open_release
        ).pack(side=tk.LEFT, padx=5)
        ttk.Button(
            button_frame,
            text=get_text("update_later_button"),
            command=self.close
        ).pack(side=tk.LEFT, padx=5)

        utils.center_window(self.win)
        utils.show_prepared_window(self.win)
        self.win.grab_set()

    def open_release(self):
        """Opens the matching GitHub release page and closes the dialog."""
        webbrowser.open(self.release_url)
        self.close()

    def close(self):
        """Closes the update notification dialog."""
        self.win.destroy()


# --- Options Dialog ---
class OptionsDialog:
    """Displays the options window for application preferences."""
    def __init__(self, parent, app, colors):
        """Initializes the OptionsDialog."""
        self.parent = parent
        self.app = app
        self.colors = colors
        self.win = tk.Toplevel(self.parent)
        utils.prepare_window(self.win)
        _set_window_icon(self.win)

        self.win.geometry("780x700")
        self.win.minsize(760, 680)
        self.win.title(get_text("options_dialog_title"))
        self.win.configure(bg=self.colors["bg"])
        self.win.transient(self.parent)

        self.win.protocol("WM_DELETE_WINDOW", self.on_close)

        i18n.load_languages()
        available_languages = i18n.get_available_language_codes()
        initial_language = config.language if config.language in available_languages else constants.DEFAULT_LANGUAGE_CODE
        self.lang_var = tk.StringVar(value=initial_language)
        self.theme_var = tk.StringVar(value=config.theme_mode)
        self.ffmpeg_path_var = tk.StringVar(value=config.ffmpeg_path)
        self.single_log_var = tk.BooleanVar(value=config.single_log_entry_enabled)
        self.log_size_var = tk.IntVar(value=config.log_file_size_kb)
        self.update_check_var = tk.BooleanVar(value=config.check_for_updates_automatically)
        self.include_prerelease_var = tk.BooleanVar(value=config.include_prerelease_updates)

        self.create_widgets()
        utils.center_window(self.win)
        utils.show_prepared_window(self.win)
        self.win.grab_set()

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

    def _configure_option_styles(self):
        """Configures dialog-specific styles for the active application theme."""
        style = ttk.Style(self.win)
        card_bg = self.colors["bg"]
        style.configure("OptionsHeader.TLabel", font=("Segoe UI", 17, "bold"), foreground=self.colors["accent"])
        style.configure("OptionsSubtitle.TLabel", font=("Segoe UI", 9), foreground=self.colors["disabled_fg"])
        style.configure(
            "OptionsCard.TFrame",
            background=card_bg,
            bordercolor=self.colors["separator"],
            relief="flat"
        )
        style.configure(
            "OptionsCardTitle.TLabel",
            background=card_bg,
            foreground=self.colors["accent"],
            font=("Segoe UI", 10, "bold")
        )
        style.configure(
            "OptionsCardText.TLabel",
            background=card_bg,
            foreground=self.colors["fg"]
        )
        style.configure(
            "OptionsCardMuted.TLabel",
            background=card_bg,
            foreground=self.colors["disabled_fg"],
            font=("Segoe UI", 8)
        )
        style.configure(
            "OptionsCard.TCheckbutton",
            background=card_bg,
            foreground=self.colors["fg"],
            indicatorcolor=card_bg,
            bordercolor=self.colors["separator"],
            focuscolor=card_bg
        )
        style.map(
            "OptionsCard.TCheckbutton",
            background=[("active", card_bg)],
            foreground=[("active", self.colors["fg"])],
            indicatorcolor=[
                ("active", self.colors["button_hover"]),
                ("selected", self.colors["accent"])
            ]
        )

    def _create_option_card(self, parent, title, description, row):
        """Creates a themed settings card and returns its content frame."""
        card = ttk.Frame(parent, style="OptionsCard.TFrame", padding=(18, 14))
        card.grid(row=row, column=0, sticky="nsew", pady=(0, 12))
        card.columnconfigure(0, weight=1)

        ttk.Label(card, text=title, style="OptionsCardTitle.TLabel").grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            card,
            text=description,
            style="OptionsCardMuted.TLabel",
            wraplength=690,
            justify=tk.LEFT
        ).grid(row=1, column=0, sticky="ew", pady=(1, 10))

        body = ttk.Frame(card, style="OptionsCard.TFrame")
        body.grid(row=2, column=0, sticky="nsew")
        return body

    def create_widgets(self):
        """Builds the modern card-based options layout."""
        self._configure_option_styles()

        container = ttk.Frame(self.win, padding=(24, 18))
        container.pack(fill=tk.BOTH, expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(2, weight=1)

        header = ttk.Frame(container)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        ttk.Label(
            header,
            text=get_text("options_dialog_title"),
            style="OptionsHeader.TLabel"
        ).pack(anchor="w")
        ttk.Label(
            header,
            text=get_text("options_dialog_subtitle"),
            style="OptionsSubtitle.TLabel"
        ).pack(anchor="w", pady=(2, 0))

        ttk.Separator(container, orient=tk.HORIZONTAL).grid(
            row=1, column=0, sticky="ew", pady=(0, 14)
        )

        cards = ttk.Frame(container)
        cards.grid(row=2, column=0, sticky="nsew")
        cards.columnconfigure(0, weight=1)

        appearance_body = self._create_option_card(
            cards,
            get_text("options_appearance_section"),
            get_text("options_appearance_description"),
            0
        )
        appearance_body.columnconfigure(0, weight=1)
        appearance_body.columnconfigure(1, weight=1)

        ttk.Label(
            appearance_body,
            text=get_text("options_language_label"),
            style="OptionsCardText.TLabel"
        ).grid(row=0, column=0, sticky="w", padx=(0, 12))
        ttk.Label(
            appearance_body,
            text=get_text("options_theme_label"),
            style="OptionsCardText.TLabel"
        ).grid(row=0, column=1, sticky="w", padx=(12, 0))

        language_values = i18n.get_available_language_codes(refresh=True)
        ttk.Combobox(
            appearance_body,
            textvariable=self.lang_var,
            values=language_values,
            state="readonly"
        ).grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(4, 0))
        ttk.Combobox(
            appearance_body,
            textvariable=self.theme_var,
            values=constants.THEME_MODES_LIST,
            state="readonly"
        ).grid(row=1, column=1, sticky="ew", padx=(12, 0), pady=(4, 0))

        ffmpeg_body = self._create_option_card(
            cards,
            get_text("options_ffmpeg_path_group"),
            get_text("options_ffmpeg_path_description"),
            1
        )
        ffmpeg_body.columnconfigure(0, weight=1)
        ttk.Entry(
            ffmpeg_body,
            textvariable=self.ffmpeg_path_var
        ).grid(row=0, column=0, sticky="ew", padx=(0, 10))
        ttk.Button(
            ffmpeg_body,
            text=get_text("options_browse_button"),
            command=self.browse_ffmpeg
        ).grid(row=0, column=1, sticky="e")

        behavior_body = self._create_option_card(
            cards,
            get_text("options_behavior_section"),
            get_text("options_behavior_description"),
            2
        )
        behavior_body.columnconfigure(0, weight=1)
        behavior_body.columnconfigure(2, weight=1)

        log_frame = ttk.Frame(behavior_body, style="OptionsCard.TFrame")
        log_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 18))
        log_frame.columnconfigure(0, weight=1)
        ttk.Label(
            log_frame,
            text=get_text("options_log_settings_group"),
            style="OptionsCardTitle.TLabel"
        ).grid(row=0, column=0, columnspan=2, sticky="w")
        ttk.Label(
            log_frame,
            text=get_text("options_log_settings_description"),
            style="OptionsCardMuted.TLabel",
            wraplength=300,
            justify=tk.LEFT
        ).grid(row=1, column=0, columnspan=2, sticky="ew", pady=(1, 6))
        ttk.Checkbutton(
            log_frame,
            text=get_text("options_log_single_entry_check"),
            variable=self.single_log_var,
            command=self.toggle_log_size,
            style="OptionsCard.TCheckbutton"
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=(0, 5))
        ttk.Label(
            log_frame,
            text=get_text("options_log_size_label"),
            style="OptionsCardText.TLabel"
        ).grid(row=3, column=0, sticky="w")
        self.log_size_entry = ttk.Entry(log_frame, textvariable=self.log_size_var, width=10)
        self.log_size_entry.grid(row=3, column=1, sticky="w", padx=(8, 0))
        self.toggle_log_size()

        ttk.Separator(behavior_body, orient=tk.VERTICAL).grid(
            row=0, column=1, sticky="ns", padx=4
        )

        update_frame = ttk.Frame(behavior_body, style="OptionsCard.TFrame")
        update_frame.grid(row=0, column=2, sticky="nsew", padx=(18, 0))
        update_frame.columnconfigure(0, weight=1)
        ttk.Label(
            update_frame,
            text=get_text("options_update_settings_group"),
            style="OptionsCardTitle.TLabel"
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            update_frame,
            text=get_text("options_update_settings_description"),
            style="OptionsCardMuted.TLabel",
            wraplength=300,
            justify=tk.LEFT
        ).grid(row=1, column=0, sticky="ew", pady=(1, 6))
        ttk.Checkbutton(
            update_frame,
            text=get_text("options_update_check_automatically"),
            variable=self.update_check_var,
            style="OptionsCard.TCheckbutton"
        ).grid(row=2, column=0, sticky="w", pady=(0, 5))
        ttk.Checkbutton(
            update_frame,
            text=get_text("options_update_include_prereleases"),
            variable=self.include_prerelease_var,
            style="OptionsCard.TCheckbutton"
        ).grid(row=3, column=0, sticky="w")

        footer = ttk.Frame(container)
        footer.grid(row=3, column=0, sticky="ew", pady=(14, 0))
        ttk.Separator(footer, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=(0, 12))
        button_row = ttk.Frame(footer)
        button_row.pack(fill=tk.X)
        ttk.Button(
            button_row,
            text=get_text("options_cancel_button"),
            command=self.on_close
        ).pack(side=tk.RIGHT)
        ttk.Button(
            button_row,
            text=get_text("options_save_button"),
            command=self.save_and_close,
            style="Accent.TButton"
        ).pack(side=tk.RIGHT, padx=(0, 8))

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
        ffmpeg_path = os.path.normpath(self.ffmpeg_path_var.get().strip())
        if not os.path.exists(os.path.join(ffmpeg_path, constants.FFMPEG_EXECUTABLE_NAME)):
            messagebox.showerror(get_text("options_error_invalid_ffmpeg_path_title"), get_text("options_error_invalid_ffmpeg_path_message"), parent=self.win)
            return

        config.ffmpeg_path = ffmpeg_path
        self.app.player.update_ffmpeg_path(ffmpeg_path)
        config.log_file_size_kb = self.log_size_var.get()
        config.single_log_entry_enabled = self.single_log_var.get()
        config.check_for_updates_automatically = self.update_check_var.get()
        config.include_prerelease_updates = self.include_prerelease_var.get()

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