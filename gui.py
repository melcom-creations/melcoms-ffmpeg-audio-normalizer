"""
gui.py
Tkinter application shell, queue management, and background task routing.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
import subprocess
import webbrowser
import datetime
import threading
import winsound
import re
import json
import random
from queue import Queue, Empty
from typing import Optional

from constants import *
import core
import i18n
import theme
from audio import FFMpegProcessor
import utils
import dialogs
import update_checker
from player import AudioPlayer
from widgets import TreeviewTooltip, HoverTooltip, AudioVisualizer
from profiles import save_profile, load_profile, reset_profile_to_defaults

try:
    from tkinterdnd2 import DND_FILES
except Exception:
    DND_FILES = None

get_text = i18n.get_text
config = core.app_config


class AudioNormalizerApp:
    """Main Tkinter controller for the audio normalizer interface, queue, playback, and background jobs."""
    def __init__(self, root):
        """Initializes the main application window and connects the core managers."""
        self.root = root
        
        icon_path = os.path.join(core.get_base_path(), "favicon", "melcom.ico")
        if not os.path.exists(icon_path):
            icon_path = os.path.join(core.get_base_path(), "custom", "favicon", "melcom.ico")
        if os.path.exists(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except Exception:
                pass

        self.file_list = []
        self.is_cancelled = False

        self.gui_queue = Queue()
        self.player = AudioPlayer(config.ffmpeg_path, self.gui_queue)
        self.current_track_index = -1

        self.is_processing = False
        self.spinner_frames = ["⏳", "⌛"]
        self.spinner_idx = 0

        self.col_duration_visible = tk.BooleanVar(value=True)
        self.col_format_visible = tk.BooleanVar(value=True)
        self.col_samplerate_visible = tk.BooleanVar(value=True)

        self.current_norm_process: Optional[subprocess.Popen] = None
        self.task_generation = 0
        self.current_task_id = None
        self.current_task_type = None
        self.active_task_total = 0
        self.progress_mode_switched = False

        self.current_playback_file = ""
        self._playback_stop_requested = False
        self._playback_suppress_finish = False
        self._playback_error_received = False
        self._update_check_in_progress = False

        self._status_hover_active = False
        self._status_state = ("status_program_start_no_files", {})

        self.options_window = None
        self.about_window = None
        self.inspector_window = None

        self.setup_styles()
        self.create_widgets()
        self.apply_language()
        self.process_gui_queue()
        self.root.after(UPDATE_CHECK_STARTUP_DELAY_MS, self._run_automatic_update_check)
        utils.center_window(self.root)

    def setup_styles(self):
        """Applies the selected theme and refreshes dependent style state."""
        self.style = ttk.Style()
        self.style.theme_use('clam')

        theme_mode = getattr(config, "theme_mode", "light")
        if theme_mode not in THEME_MODES_LIST:
            theme_mode = DEFAULT_THEME_MODE
            config.theme_mode = theme_mode
            config.save_options()

        self.colors = theme.apply_theme(self.style, self.root, theme_mode)

    def create_widgets(self):
        """Builds the main window layout and wires the primary controls."""
        self.root.title(f"{get_text('app_title')} v{VERSION} - {EDITION_NAME}")
        self.root.geometry("1280x860") 
        self.root.minsize(1240, 820)

        self.root.bind("<F1>", self.open_help_file)

        self.main_frame = ttk.Frame(self.root, padding=GUI_PADY, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(self.main_frame, style="TFrame")
        top_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)
        top_frame.columnconfigure(0, weight=3)
        top_frame.columnconfigure(1, weight=2)

        self.file_frame = ttk.LabelFrame(top_frame, text=get_text("file_selection_group"), style="TLabelframe")
        self.file_frame.configure(width=610)
        self.file_frame.grid(row=0, column=0, sticky="nsew", padx=(0, GUI_PADX))
        self.file_frame.grid_propagate(False)
        self.file_frame.columnconfigure(0, weight=1)
        self.file_frame.rowconfigure(0, weight=1)

        self.file_listbox = ttk.Treeview(
            self.file_frame, 
            columns=("filename", "duration", "format", "samplerate"), 
            show="headings", 
            selectmode="extended", 
            height=6
        )
        self.file_listbox.heading("filename", text=get_text("file_list_header_filename"))
        self.file_listbox.heading("duration", text=get_text("file_list_header_duration"))
        self.file_listbox.heading("format", text=get_text("file_list_header_format"))
        self.file_listbox.heading("samplerate", text=get_text("file_list_header_samplerate"))

        self.file_listbox.column("filename", anchor="w", width=260)
        self.file_listbox.column("duration", anchor="center", width=90, stretch=False)
        self.file_listbox.column("format", anchor="center", width=80, stretch=False)
        self.file_listbox.column("samplerate", anchor="center", width=120, stretch=False)

        self.file_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(8, 10))

        self.empty_queue_label = tk.Label(
            self.file_frame,
            text=get_text("empty_queue_placeholder"),
            fg=self.colors["disabled_fg"],
            bg=self.colors["entry_bg"],
            font=("Segoe UI", 10, "italic")
        )
        self.empty_queue_label.place(relx=0.5, rely=0.42, anchor="center")

        self.file_listbox.bind("<Delete>", self.remove_selected_files)
        self.file_listbox.bind("<Control-a>", self.select_all_files)
        self.file_listbox.bind("<Control-d>", self.clear_file_selection)
        self.file_listbox.bind("<<TreeviewSelect>>", self.update_player_button_states)
        self.file_listbox.bind("<Button-3>", self.show_context_menu)
        self.file_listbox.bind("<Double-1>", self.open_inspector)
        self.file_tooltip = TreeviewTooltip(self.file_listbox)
        self.file_listbox.bind("<Motion>", self._on_treeview_hover)
        self.file_listbox.bind("<Leave>", lambda e: self.file_tooltip.hide())
        self.file_listbox.bind("<ButtonRelease-1>", self._on_treeview_release, add="+")
        self.file_listbox.bind("<Configure>", self._reset_treeview_layout, add="+")

        self._init_drag_and_drop()

        list_scrollbar = ttk.Scrollbar(self.file_frame, orient="vertical", command=self.file_listbox.yview)
        list_scrollbar.grid(row=0, column=2, sticky="ns", pady=(8, 10))
        self.file_listbox.config(yscrollcommand=list_scrollbar.set)

        file_button_frame = ttk.Frame(self.file_frame, style="TFrame")
        file_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")

        self.add_files_button = ttk.Button(file_button_frame, text=get_text("add_files_button"), command=self.add_files)
        self.add_folder_button = ttk.Button(file_button_frame, text=get_text("add_folder_button"), command=self.add_folder)
        self.remove_files_button = ttk.Button(file_button_frame, text=get_text("remove_files_button"), command=self.remove_selected_files)

        self.info_button = ttk.Button(file_button_frame, text="ℹ", command=self.open_inspector, width=4, state=tk.DISABLED)

        self.info_button.bind("<Enter>", self._on_info_button_enter)
        self.info_button.bind("<Motion>", self._on_info_button_motion)
        self.info_button.bind("<Leave>", self._on_info_button_leave)

        self.add_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.add_folder_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.remove_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.info_button.pack(side=tk.LEFT, padx=2)

        ttk.Separator(self.file_frame, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=5)

        player_frame = ttk.Frame(self.file_frame, style="TFrame")
        player_frame.grid(row=3, column=0, columnspan=2, sticky='ew')
        player_frame.columnconfigure(0, weight=1)
        player_frame.columnconfigure(1, weight=1)
        player_frame.columnconfigure(2, weight=1)

        self.time_label_var = tk.StringVar(value="00:00:00 / 00:00:00")
        time_label = ttk.Label(player_frame, textvariable=self.time_label_var, font=("Courier", 10))
        time_label.grid(row=0, column=0, sticky='w', padx=5)

        controls_subframe = ttk.Frame(player_frame, style="TFrame")
        controls_subframe.grid(row=0, column=1)

        self.play_button = ttk.Button(controls_subframe, text="▶", command=self.play_audio, width=4)
        self.pause_button = ttk.Button(controls_subframe, text="⏸", command=self.pause_audio, width=4)
        self.stop_button = ttk.Button(controls_subframe, text="■", command=self.stop_audio, width=4)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.pause_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.pack(side=tk.LEFT)

        nav_subframe = ttk.Frame(player_frame, style="TFrame")
        nav_subframe.grid(row=0, column=2, sticky='e')

        self.prev_button = ttk.Button(nav_subframe, text="«", command=self.play_previous, width=4)
        self.next_button = ttk.Button(nav_subframe, text="»", command=self.play_next, width=4)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button.pack(side=tk.LEFT)

        self.player_progress = ttk.Progressbar(player_frame, orient="horizontal", mode="determinate")
        self.player_progress.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(8, 2), padx=5)

        self.player_progress.bind("<ButtonRelease-1>", self.seek_audio)
        self.player_progress.bind("<Enter>", lambda e: self.player_progress.config(cursor="hand2"))
        self.player_progress.bind("<Leave>", lambda e: self.player_progress.config(cursor=""))

        self.visualizer = AudioVisualizer(
            player_frame,
            num_bars=15,
            bar_width=3,
            bar_spacing=2,
            max_height=18,
            color=self.colors["accent"],
            bg_color=self.colors["bg"]
        )
        self.visualizer.grid(row=2, column=0, columnspan=3, sticky="e", pady=(4, 0), padx=5)
        self.visualizer_tooltip = HoverTooltip(self.visualizer)
        self.info_button_tooltip = HoverTooltip(self.info_button)
        self.visualizer.bind("<Button-1>", self.show_visualizer_joke)
        self.visualizer.bind("<Enter>", self._on_visualizer_enter)
        self.visualizer.bind("<Motion>", self._on_visualizer_motion)
        self.visualizer.bind("<Leave>", self._on_visualizer_leave)

        settings_frame = ttk.Frame(top_frame, style="TFrame")
        settings_frame.grid(row=0, column=1, sticky="nsew")
        settings_frame.grid_propagate(False)
        settings_frame.columnconfigure(0, weight=1)

        self.loudness_frame = ttk.LabelFrame(settings_frame, text=get_text("loudness_settings_group"), style="TLabelframe")
        self.loudness_frame.pack(fill=tk.X, expand=True, pady=(0, 12))

        self.lufs_preset_var = tk.StringVar()
        self.true_peak_preset_var = tk.StringVar()
        self.mastering_preset_var = tk.StringVar(value=DEFAULT_MASTERING_PRESET)

        ttk.Label(self.loudness_frame, text=get_text("lufs_preset_label"), style="TLabel").grid(row=0, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.lufs_combobox = ttk.Combobox(self.loudness_frame, textvariable=self.lufs_preset_var, state="readonly", width=GUI_COMBOBOX_WIDTH_LUFS_PRESET)
        self.lufs_combobox.grid(row=0, column=1, sticky="ew", padx=GUI_PADX, pady=GUI_PADY)
        self.lufs_combobox.bind("<<ComboboxSelected>>", self.update_entry_states)

        ttk.Label(self.loudness_frame, text=get_text("true_peak_preset_label"), style="TLabel").grid(row=1, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.tp_combobox = ttk.Combobox(self.loudness_frame, textvariable=self.true_peak_preset_var, state="readonly", width=GUI_COMBOBOX_WIDTH_TP_PRESET)
        self.tp_combobox.grid(row=1, column=1, sticky="ew", padx=GUI_PADX, pady=GUI_PADY)
        self.tp_combobox.bind("<<ComboboxSelected>>", self.update_entry_states)

        ttk.Label(self.loudness_frame, text=get_text("mastering_character_label"), style="TLabel").grid(row=2, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.mastering_combobox = ttk.Combobox(
            self.loudness_frame,
            textvariable=self.mastering_preset_var,
            values=i18n.MASTERING_PRESET_DISPLAY_NAMES,
            state="readonly",
            width=GUI_COMBOBOX_WIDTH_LUFS_PRESET,
        )
        self.mastering_combobox.grid(row=2, column=1, sticky="ew", padx=GUI_PADX, pady=GUI_PADY)
        self.mastering_combobox.bind("<<ComboboxSelected>>", self.update_mastering_help_text)

        self.mastering_help_frame = ttk.Frame(self.loudness_frame, style="TFrame", height=55)
        self.mastering_help_frame.grid(row=3, column=0, columnspan=4, sticky="ew", padx=GUI_PADX, pady=(0, GUI_PADY))
        self.mastering_help_frame.columnconfigure(0, weight=1)
        self.mastering_help_frame.grid_propagate(False)

        self.mastering_help_label = ttk.Label(
            self.mastering_help_frame, text="", style="TLabel", justify=tk.LEFT, wraplength=520, anchor="nw"
        )
        self.mastering_help_label.grid(row=0, column=0, sticky="nsew")

        self.lufs_entry_var = tk.StringVar()
        self.tp_entry_var = tk.StringVar()

        lufs_vcmd = (self.root.register(lambda P: self._validate_entry(self.lufs_entry, P, -70.0, 0.0)), '%P')
        tp_vcmd = (self.root.register(lambda P: self._validate_entry(self.tp_entry, P, -9.0, 0.0)), '%P')

        self.lufs_label = ttk.Label(self.loudness_frame, text=get_text("target_lufs_label_custom_short"), style="TLabel")
        self.lufs_entry = ttk.Entry(self.loudness_frame, textvariable=self.lufs_entry_var, width=GUI_ENTRY_WIDTH_LUFS_TP, validate="focusout", validatecommand=lufs_vcmd)
        self.tp_label = ttk.Label(self.loudness_frame, text=get_text("true_peak_label"), style="TLabel")
        self.tp_entry = ttk.Entry(self.loudness_frame, textvariable=self.tp_entry_var, width=GUI_ENTRY_WIDTH_LUFS_TP, validate="focusout", validatecommand=tp_vcmd)

        self.lufs_label.grid(row=0, column=2, padx=(GUI_PADX, 2), pady=GUI_PADY)
        self.lufs_entry.grid(row=0, column=3, padx=(0, GUI_PADX), pady=GUI_PADY)
        self.tp_label.grid(row=1, column=2, padx=(GUI_PADX, 2), pady=GUI_PADY)
        self.tp_entry.grid(row=1, column=3, padx=(0, GUI_PADX), pady=GUI_PADY)

        self.mode_frame = ttk.LabelFrame(settings_frame, text=get_text("mode_selection_group"), style="TLabelframe")
        self.mode_frame.pack(fill=tk.X, expand=True, pady=(0, 12))

        self.mode_var = tk.StringVar(value="linear")
        self.radio_linear = ttk.Radiobutton(self.mode_frame, text=get_text("mode_linear"), variable=self.mode_var, value="linear")
        self.radio_dynamic = ttk.Radiobutton(self.mode_frame, text=get_text("mode_dynamic"), variable=self.mode_var, value="dynamic")
        self.radio_linear.pack(anchor=tk.W, padx=GUI_PADX, pady=(GUI_PADY, 0))
        self.radio_dynamic.pack(anchor=tk.W, padx=GUI_PADX, pady=GUI_PADY)

        self.output_frame = ttk.LabelFrame(settings_frame, text=get_text("output_format_group"), style="TLabelframe")
        self.output_frame.pack(fill=tk.BOTH, expand=True, pady=GUI_PADY)
        self.output_frame.columnconfigure(1, weight=1)

        self.output_format_var = tk.StringVar()
        self.output_format_label = ttk.Label(self.output_frame, text=get_text("output_format_file_format_label"), style="TLabel")
        self.output_format_label.grid(row=0, column=0, sticky="w", padx=GUI_PADX, pady=(GUI_PADY, 3))

        self.output_combobox = ttk.Combobox(self.output_frame, textvariable=self.output_format_var, values=OUTPUT_FORMATS_LIST, state="readonly", width=18)
        self.output_combobox.grid(row=0, column=1, sticky="w", padx=GUI_PADX, pady=(GUI_PADY, 3))
        self.output_combobox.set(OUTPUT_FORMATS_LIST[0])
        self.output_combobox.bind("<<ComboboxSelected>>", self.on_format_changed)

        self.output_samplerate_var = tk.StringVar()
        self.output_samplerate_label = ttk.Label(self.output_frame, text=get_text("output_format_samplerate_label"), style="TLabel")
        self.output_samplerate_label.grid(row=1, column=0, sticky="w", padx=GUI_PADX, pady=3)

        self.samplerate_combobox = ttk.Combobox(self.output_frame, textvariable=self.output_samplerate_var, state="readonly", width=24)
        self.samplerate_combobox.grid(row=1, column=1, sticky="w", padx=GUI_PADX, pady=3)
        self.samplerate_combobox.bind("<<ComboboxSelected>>", self.update_output_format_info)

        self.output_quality_var = tk.StringVar()
        self.output_quality_label = ttk.Label(self.output_frame, text=get_text("output_format_quality_label"), style="TLabel")
        self.output_quality_label.grid(row=2, column=0, sticky="w", padx=GUI_PADX, pady=3)

        self.quality_combobox = ttk.Combobox(self.output_frame, textvariable=self.output_quality_var, state="readonly", width=28)
        self.quality_combobox.grid(row=2, column=1, sticky="w", padx=GUI_PADX, pady=3)
        self.quality_combobox.bind("<<ComboboxSelected>>", self.update_output_format_info)

        self.output_info_frame = ttk.Frame(self.output_frame, style="TFrame", height=90)
        self.output_info_frame.grid(row=3, column=0, columnspan=2, sticky="ew", padx=GUI_PADX, pady=(GUI_PADY, 0))
        self.output_info_frame.columnconfigure(0, weight=1)
        self.output_info_frame.grid_propagate(False)

        self.output_specs_label = ttk.Label(self.output_info_frame, text="", style="TLabel", justify=tk.LEFT)
        self.output_specs_label.grid(row=0, column=0, sticky="ew")

        ttk.Separator(self.output_info_frame, orient='horizontal').grid(row=1, column=0, sticky="ew", pady=3)

        self.output_desc_label = ttk.Label(
            self.output_info_frame,
            text="",
            style="TLabel",
            justify=tk.LEFT,
            anchor="w",
            wraplength=560
        )
        self.output_desc_label.grid(row=2, column=0, sticky="ew")

        bottom_frame = ttk.Frame(self.main_frame, style="TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=GUI_PADX, pady=GUI_PADY)
        bottom_frame.rowconfigure(0, weight=1)
        bottom_frame.columnconfigure(0, weight=1)

        self.info_frame = ttk.LabelFrame(bottom_frame, text=get_text("process_information_group"), style="TLabelframe")
        self.info_frame.grid(row=0, column=0, sticky="nsew", pady=GUI_PADY)
        self.info_frame.rowconfigure(0, weight=1)
        self.info_frame.columnconfigure(0, weight=1)

        self.process_info = tk.Text(self.info_frame, wrap=tk.WORD, state=tk.DISABLED, height=12, 
                                    bg=self.colors["info_bg"], fg=self.colors["fg"], 
                                    highlightthickness=0, relief=self.colors.get("text_relief", "sunken"), borderwidth=1)
        self.process_info.grid(row=0, column=0, sticky="nsew")
        info_scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.process_info.yview)
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        self.process_info.config(yscrollcommand=info_scrollbar.set)

        self.log_context_menu = tk.Menu(self.root, tearoff=0)
        self.log_context_menu.add_command(label="Copy", command=self._copy_log)
        self.log_context_menu.add_separator()
        self.log_context_menu.add_command(label="Select All", command=self._select_all_log)

        self.process_info.bind("<Button-3>", self._show_log_context_menu)
        self.process_info.bind("<Control-a>", self._select_all_log)
        self.process_info.bind("<Control-A>", self._select_all_log)

        control_frame = ttk.Frame(bottom_frame, style="TFrame")
        control_frame.grid(row=1, column=0, sticky="ew", pady=(12, 4))

        self.analyze_button = ttk.Button(control_frame, text=get_text("analyze_audio_button"), command=lambda: self.start_task("analyze"))

        self.start_button = ttk.Button(control_frame, text="▶ " + get_text("start_normalization_button"), command=lambda: self.start_task("normalize"), style="Accent.TButton")
        self.cancel_button = ttk.Button(control_frame, text=get_text("cancel_normalization_button"), command=self.cancel_task, state=tk.DISABLED)

        self.analyze_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        self.status_frame = ttk.Frame(self.main_frame, style="TFrame")
        self.status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=GUI_PADX)

        self.status_bar = ttk.Label(self.status_frame, text=get_text("status_program_start_no_files"), anchor=tk.W, style="TLabel")
        self.status_bar.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.spinner_label = ttk.Label(self.status_frame, text="", anchor=tk.E, style="TLabel")
        self.spinner_label.pack(side=tk.RIGHT, padx=(5, 0))

        self.progressbar = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progressbar.pack(side=tk.BOTTOM, fill=tk.X, padx=GUI_PADX, pady=(0, GUI_PADY))

        self.create_menu()
        self.update_output_format_info()
        self.update_player_button_states()
        self._schedule_empty_queue_placeholder_update()
        self.update_visible_columns()

        self.root.bind("<<ComboboxSelected>>", self._clear_combobox_focus, add="+")

    def show_visualizer_joke(self, event=None):
        """Opens the small visualizer easter egg dialog."""
        self._hide_visualizer_tooltip()
        if self.player.is_playing and not self.player.is_paused:
            winsound.MessageBeep(winsound.MB_ICONASTERISK)

            joke_win = tk.Toplevel(self.root)
            joke_win.title(get_text("joke_eq_title"))
            joke_win.geometry("380x180")
            joke_win.configure(bg=self.colors["bg"])
            joke_win.transient(self.root)
            joke_win.resizable(False, False)
            joke_win.grab_set()

            frame = ttk.Frame(joke_win, padding=15)
            frame.pack(fill=tk.BOTH, expand=True)

            msg_font = ("Segoe UI Emoji", 10) if os.name == 'nt' else ("Segoe UI", 10)

            btn = ttk.Button(frame, text="OK", command=joke_win.destroy, width=10)
            btn.pack(side=tk.BOTTOM, pady=(10, 0))

            lbl = ttk.Label(
                frame, 
                text=get_text("joke_eq_message"), 
                justify=tk.CENTER, 
                wraplength=340, 
                font=msg_font
            )
            lbl.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

            utils.center_window(joke_win)

    def _sync_visualizers(self):
        """Keeps both playback visualizers aligned with the current state."""
        if self.player.is_playing and not self.player.is_paused:
            self.visualizer.start()
        else:
            self.visualizer.stop()
            self._hide_visualizer_tooltip()

    def _is_visualizer_tooltip_allowed(self):
        """Returns whether the visualizer tooltip may be shown."""
        return self.player.is_playing and not self.player.is_paused and self.current_track_index != -1

    def _show_visualizer_tooltip(self, event=None):
        """Shows the visualizer tooltip near the pointer."""
        if event is None:
            x_root = self.visualizer.winfo_rootx()
            y_root = self.visualizer.winfo_rooty()
        else:
            x_root = event.x_root
            y_root = event.y_root

        tooltip_key = "fake_equalizer_tooltip_playing" if self._is_visualizer_tooltip_allowed() else "fake_equalizer_tooltip_idle"
        self.visualizer_tooltip.show(get_text(tooltip_key), x_root, y_root)

    def _hide_visualizer_tooltip(self):
        """Hides the visualizer tooltip if it is visible."""
        if hasattr(self, "visualizer_tooltip") and self.visualizer_tooltip is not None:
            self.visualizer_tooltip.hide()

    def _on_visualizer_enter(self, event):
        """Stores the pointer position when entering the visualizer."""
        self.visualizer.config(cursor="hand2")
        self._show_visualizer_tooltip(event)

    def _on_visualizer_motion(self, event):
        """Updates the tooltip anchor while the pointer moves."""
        self._show_visualizer_tooltip(event)

    def _on_visualizer_leave(self, event):
        """Closes the visualizer tooltip when the pointer leaves."""
        self.visualizer.config(cursor="")
        self._hide_visualizer_tooltip()

    def _clear_combobox_focus(self, event):
        """Clears keyboard focus from the active combobox."""
        self.root.focus_set()
        if hasattr(event.widget, 'selection_clear'):
            event.widget.after(10, event.widget.selection_clear)

    def _copy_log(self):
        """Copies the visible log text to the clipboard."""
        try:
            selected_text = self.process_info.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
        except tk.TclError:
            pass

    def _select_all_log(self, event=None):
        """Selects all text in the log view."""
        self.process_info.tag_add(tk.SEL, "1.0", tk.END)
        self.process_info.mark_set(tk.INSERT, "1.0")
        self.process_info.see(tk.INSERT)
        return "break"

    def _show_log_context_menu(self, event):
        """Shows the context menu for the log view."""
        copy_text = get_text("inspect_btn_copy")
        copy_text = "Copy" if copy_text.startswith("[") else copy_text
        sel_all_text = get_text("menu_context_select_all")
        sel_all_text = "Select All" if sel_all_text.startswith("[") else sel_all_text

        self.log_context_menu.entryconfig(0, label=copy_text)
        self.log_context_menu.entryconfig(2, label=sel_all_text)

        self.log_context_menu.post(event.x_root, event.y_root)

    def _animate_spinner(self):
        """Advances the loading spinner used during background work."""
        if self.is_processing:
            self.spinner_label.config(text=self.spinner_frames[self.spinner_idx])
            self.spinner_idx = (self.spinner_idx + 1) % len(self.spinner_frames)
            self.root.after(500, self._animate_spinner)
        else:
            self.spinner_label.config(text="")

    def on_closing(self):
        """Stops playback and background work before closing the app."""
        self._hide_visualizer_tooltip()
        self.player.stop()
        self.cancel_task()
        self.root.destroy()

    def _check_ffmpeg_path(self):
        """Validates the configured FFmpeg directory and updates the UI."""
        ffmpeg_file_path = os.path.join(config.ffmpeg_path, FFMPEG_EXECUTABLE_NAME)
        if not config.ffmpeg_path or not os.path.exists(ffmpeg_file_path):
            messagebox.showerror(
                get_text("options_error_ffmpeg_executable_title"),
                get_text("options_error_ffmpeg_executable_message") + "\n\n" + get_text("error_help_reference_msg"),
                parent=self.root
            )
            return False
        return True

    def create_menu(self):
        """Builds the main menu bar."""
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)

        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label=get_text("menu_file_options"), command=self.show_options)
        file_menu.add_separator()
        file_menu.add_command(label=get_text("menu_file_exit"), command=self.on_closing)
        self.menubar.add_cascade(label=get_text("menu_file"), menu=file_menu)

        profile_menu = tk.Menu(self.menubar, tearoff=0)
        profile_menu.add_command(label=get_text("menu_profile_save"), command=lambda: save_profile(self))
        profile_menu.add_command(label=get_text("menu_profile_load"), command=lambda: load_profile(self))
        profile_menu.add_separator()
        profile_menu.add_command(label=get_text("menu_profile_reset"), command=lambda: reset_profile_to_defaults(self))
        self.menubar.add_cascade(label=get_text("menu_profile"), menu=profile_menu)

        info_menu = tk.Menu(self.menubar, tearoff=0)
        info_menu.add_command(label=get_text("menu_info_help"), command=self.open_help_file)
        info_menu.add_command(label=get_text("menu_info_updates"), command=lambda: self.check_for_updates(manual=True))
        info_menu.add_separator()
        info_menu.add_command(label=get_text("menu_info_about"), command=self.show_about)
        self.menubar.add_cascade(label=get_text("menu_info"), menu=info_menu)

    def _run_automatic_update_check(self):
        """Starts the silent startup check when the preference is enabled."""
        if config.check_for_updates_automatically:
            self.check_for_updates(manual=False)

    def check_for_updates(self, manual=False):
        """Checks GitHub Releases without blocking the Tkinter event loop."""
        if self._update_check_in_progress:
            if manual:
                messagebox.showinfo(
                    get_text("update_check_in_progress_title"),
                    get_text("update_check_in_progress_message"),
                    parent=self.root
                )
            return

        self._update_check_in_progress = True

        def worker():
            result = update_checker.check_for_updates(
                VERSION,
                GITHUB_RELEASES_API,
                UPDATE_CHECK_TIMEOUT_SECONDS,
                include_prereleases=config.include_prerelease_updates
            )
            self.gui_queue.put(("update_check_result", (manual, result)))

        threading.Thread(target=worker, daemon=True).start()

    def _handle_update_check_result(self, manual, result):
        """Displays update results according to automatic or manual check behavior."""
        self._update_check_in_progress = False
        if result.status == "available":
            dialogs.UpdateAvailableDialog(
                self.root,
                self.colors,
                result.current_version,
                result.latest_version,
                result.release_url
            )
        elif result.status == "current" and manual:
            messagebox.showinfo(
                get_text("update_up_to_date_title"),
                get_text("update_up_to_date_message", current_version=VERSION),
                parent=self.root
            )
        elif result.status == "error" and manual:
            messagebox.showerror(
                get_text("update_check_failed_title"),
                get_text("update_check_failed_message"),
                parent=self.root
            )

    def apply_language(self):
        """Refreshes all visible text after a language change."""
        self.player.update_ffmpeg_path(config.ffmpeg_path)

        i18n.load_language(config.language)
        self.root.title(f"{get_text('app_title')} v{VERSION} - {EDITION_NAME}")
        self.menubar.destroy()
        self.create_menu()

        self.file_frame.config(text=get_text("file_selection_group"))
        self.loudness_frame.config(text=get_text("loudness_settings_group"))
        self.mode_frame.config(text=get_text("mode_selection_group"))
        self.output_frame.config(text=get_text("output_format_group"))
        self.info_frame.config(text=get_text("process_information_group"))

        self.add_files_button.config(text=get_text("add_files_button"))
        self.add_folder_button.config(text=get_text("add_folder_button"))
        self.remove_files_button.config(text=get_text("remove_files_button"))

        self.output_format_label.config(text=get_text("output_format_file_format_label"))
        self.output_samplerate_label.config(text=get_text("output_format_samplerate_label"))
        self.output_quality_label.config(text=get_text("output_format_quality_label"))

        self.lufs_combobox.config(values=i18n.LUFS_PRESET_NAMES)
        self.lufs_combobox.set(i18n.LUFS_PRESET_NAMES[0] if i18n.LUFS_PRESET_NAMES else "")

        self.tp_combobox.config(values=i18n.TRUE_PEAK_PRESET_NAMES)
        self.tp_combobox.set(i18n.TRUE_PEAK_PRESET_NAMES[0] if i18n.TRUE_PEAK_PRESET_NAMES else "")

        self.mastering_combobox.config(values=i18n.MASTERING_PRESET_DISPLAY_NAMES)
        self.mastering_combobox.set(i18n.get_mastering_preset_display_name(self.mastering_preset_var.get()))
        self.update_mastering_help_text()

        self.analyze_button.config(text=get_text("analyze_audio_button"))
        self.start_button.config(text=get_text("start_normalization_button"))
        self.cancel_button.config(text=get_text("cancel_normalization_button"))
        self.update_status_bar_default()

        self.radio_linear.config(text=get_text("mode_linear"))
        self.radio_dynamic.config(text=get_text("mode_dynamic"))

        self.file_listbox.heading("filename", text=get_text("file_list_header_filename"))
        self.file_listbox.heading("duration", text=get_text("file_list_header_duration"))
        self.file_listbox.heading("format", text=get_text("file_list_header_format"))
        self.file_listbox.heading("samplerate", text=get_text("file_list_header_samplerate"))

        self.play_button.config(text="▶")
        self.pause_button.config(text="⏸")
        self.stop_button.config(text="■")
        self.prev_button.config(text="«")
        self.next_button.config(text="»")

        if hasattr(self, "empty_queue_label"):
            self.empty_queue_label.config(text=get_text("empty_queue_placeholder"))

        sr_options = SAMPLE_RATES_LIST.copy()
        sr_options[0] = get_text("output_original_default")
        self.samplerate_combobox.config(values=sr_options)

        if not self.output_samplerate_var.get():
            self.samplerate_combobox.set(sr_options[0])
        else:
            current_idx = self.samplerate_combobox.current()
            if current_idx == 0:
                self.samplerate_combobox.set(sr_options[0])

        self.update_entry_states()
        self.update_quality_options()
        self.update_output_format_info()

        for attr in ("inspector_window", "about_window", "options_window"):
            window = getattr(self, attr, None)
            if window is None:
                continue
            top = getattr(window, "win", None)
            if top is None:
                continue
            try:
                if top.winfo_exists():
                    refresh = getattr(window, "refresh_language", None)
                    if callable(refresh):
                        refresh()
            except Exception:
                pass

    def update_visible_columns(self):
        """Rebuilds the queue columns for the active output format."""
        display_cols = ["filename"]
        if self.col_duration_visible.get():
            display_cols.append("duration")
        if self.col_format_visible.get():
            display_cols.append("format")
        if self.col_samplerate_visible.get():
            display_cols.append("samplerate")
        self.file_listbox["displaycolumns"] = tuple(display_cols)

    def _insert_file_to_tree(self, filepath):
        """Adds a file entry to the queue tree."""
        if filepath in self.file_list:
            return
        self.file_list.append(filepath)
        item_id = self.file_listbox.insert("", tk.END, values=(os.path.basename(filepath), "⏳", "⏳", "⏳"))

        self._schedule_empty_queue_placeholder_update()
        threading.Thread(target=self._load_metadata_async, args=(filepath, item_id), daemon=True).start()

    def _load_metadata_async(self, filepath, item_id):
        """Loads file metadata on a worker thread and updates the queue row."""
        processor = FFMpegProcessor(config.ffmpeg_path, lambda msg: None)
        meta = processor.get_track_metadata(filepath)
        if meta:
            dur_str = utils.format_time(meta.get("duration", 0))

            raw_container = meta.get("container", "Unknown").upper()
            ext = os.path.splitext(filepath)[1].upper().replace(".", "")

            if "MP2/3" in raw_container or "MP3" in raw_container:
                fmt_str = "MP3"
            elif "QUICKTIME" in raw_container or "M4A" in raw_container or "MP4" in raw_container:
                fmt_str = "M4A"
            elif "FLAC" in raw_container:
                fmt_str = "FLAC"
            elif "OGG" in raw_container:
                fmt_str = "OGG"
            elif "ADTS" in raw_container or "AAC" in raw_container:
                fmt_str = "AAC"
            elif "WAV" in raw_container or "WAVE" in raw_container or "PCM" in raw_container:
                fmt_str = "WAV"
            else:
                fmt_str = ext if ext else raw_container.split("/")[0].strip()[:8]

            sr_val = meta.get("sample_rate", 0)
            sr_str = f"{sr_val // 1000} kHz" if sr_val > 0 else "N/A"
            self.gui_queue.put(("update_tree_item", (item_id, dur_str, fmt_str, sr_str)))
        else:
            self.gui_queue.put(("update_tree_item", (item_id, "N/A", "N/A", "N/A")))

    def _on_treeview_hover(self, event):
        """Tracks hover state for queue rows."""
        row_id = self.file_listbox.identify_row(event.y)
        column = self.file_listbox.identify_column(event.x)

        if not row_id or column != "#1":
            self.file_tooltip.hide()
            return

        values = self.file_listbox.item(row_id, "values")
        if not values:
            self.file_tooltip.hide()
            return

        self.file_tooltip.show(values[0], event.x_root, event.y_root)

    def _on_treeview_release(self, event=None):
        """Handles treeview clicks and selection changes."""
        self.root.after(10, self._reset_treeview_layout)

    def _reset_treeview_layout(self, event=None):
        """Restores the default queue tree layout."""
        if hasattr(self, "file_listbox") and self.file_listbox.winfo_exists():
            try:
                total_w = self.file_listbox.winfo_width()
                if total_w <= 1:
                    total_w = 590
                
                other_w = 0
                if self.col_duration_visible.get():
                    other_w += 90
                if self.col_format_visible.get():
                    other_w += 80
                if self.col_samplerate_visible.get():
                    other_w += 120
                    
                filename_w = max(150, total_w - other_w)
                
                self.file_listbox.column("filename", width=filename_w, stretch=True)
                self.file_listbox.column("duration", width=90, stretch=False)
                self.file_listbox.column("format", width=80, stretch=False)
                self.file_listbox.column("samplerate", width=120, stretch=False)
                
                self.update_visible_columns()
            except Exception:
                pass

    def on_format_changed(self, event=None):
        """Updates controls that depend on the selected output format."""
        self.samplerate_combobox.current(0)
        self.update_quality_options()
        self.update_output_format_info()

    def update_quality_options(self):
        """Refreshes the available output-quality presets."""
        selected_format = self.output_format_var.get()
        options = FORMAT_QUALITY_OPTIONS.get(selected_format, []).copy()

        if options and options[0] == "Original / Default":
            translated_options = [get_text("output_original_default")] + options[1:]
        else:
            translated_options = options

        self.quality_combobox.config(values=translated_options)
        if translated_options:
            self.quality_combobox.set(translated_options[0])

    def add_files(self):
        """Prompts the user to add one or more audio files."""
        if not self._check_ffmpeg_path():
            return
        filetypes = [(get_text("file_dialog_audio_files"), " ".join([ext for ext, _ in AUDIO_FILE_EXTENSIONS]))]
        files = filedialog.askopenfilenames(title=get_text("file_dialog_title"), filetypes=filetypes)
        for f in files:
            self._insert_file_to_tree(f)
        self.update_status_bar()
        self.update_player_button_states()
        self._schedule_empty_queue_placeholder_update()

    def add_folder(self):
        """Adds supported audio files from a selected folder."""
        if not self._check_ffmpeg_path():
            return
        folder = filedialog.askdirectory(title=get_text("folder_dialog_title"))
        if not folder: return
        for root_dir, _, files in os.walk(folder):
            for f in files:
                if any(f.lower().endswith(ext) for ext, _ in AUDIO_FILE_EXTENSIONS):
                    self._insert_file_to_tree(os.path.join(root_dir, f))
        self.update_status_bar()
        self.update_player_button_states()
        self._schedule_empty_queue_placeholder_update()

    def _init_drag_and_drop(self):
        """Registers drag-and-drop handlers for the file queue."""
        if DND_FILES is None:
            return
        register_drop_target = getattr(self.file_listbox, "drop_target_register", None)
        bind_drop = getattr(self.file_listbox, "dnd_bind", None)
        if not callable(register_drop_target) or not callable(bind_drop):
            return
        try:
            register_drop_target(DND_FILES)
            bind_drop("<<Drop>>", self._on_drop_files)
        except Exception:
            pass

    def _add_path_to_queue(self, path):
        """Adds a filesystem path to the processing queue."""
        if os.path.isdir(path):
            for root_dir, _, files in os.walk(path):
                for filename in files:
                    if any(filename.lower().endswith(ext) for ext, _ in AUDIO_FILE_EXTENSIONS):
                        self._insert_file_to_tree(os.path.join(root_dir, filename))
            return

        if os.path.isfile(path) and any(path.lower().endswith(ext) for ext, _ in AUDIO_FILE_EXTENSIONS):
            self._insert_file_to_tree(path)

    def _on_drop_files(self, event):
        """Processes files and folders dropped onto the queue."""
        if not self._check_ffmpeg_path():
            return
        data = self.root.tk.splitlist(event.data)
        for item in data:
            self._add_path_to_queue(item)
        self.update_status_bar()
        self.update_player_button_states()
        self._schedule_empty_queue_placeholder_update()

    def select_all_files(self, event=None):
        """Selects every item in the queue."""
        items = self.file_listbox.get_children()
        if items:
            self.file_listbox.selection_set(items)
        return "break"

    def clear_file_selection(self, event=None):
        """Clears the current queue selection."""
        selection = self.file_listbox.selection()
        if selection:
            self.file_listbox.selection_remove(selection)
        self.update_player_button_states()
        return "break"

    def remove_selected_files(self, event=None):
        """Removes the selected queue items."""
        selected_items = self.file_listbox.selection()
        if not selected_items: return

        indices_to_delete = sorted([self.file_listbox.index(i) for i in selected_items], reverse=True)

        stopped_due_to_removal = False
        if self.player.is_playing or self.player.is_paused:
            for index in indices_to_delete:
                if index == self.current_track_index:
                    self.stop_audio()
                    stopped_due_to_removal = True
                elif index < self.current_track_index:
                    self.current_track_index -= 1

        for index in indices_to_delete:
            del self.file_list[index]
        for item in selected_items:
            self.file_listbox.delete(item)

        self.update_status_bar()
        self.update_player_button_states()
        self._schedule_empty_queue_placeholder_update()

    def open_file_location(self, event=None):
        """Opens the selected file in the system file manager."""
        selection = self.file_listbox.selection()
        if not selection: return
        index = self.file_listbox.index(selection[0])
        file_path = self.file_list[index]

        if os.path.exists(file_path):
            if os.name == 'nt':
                subprocess.Popen(f'explorer /select,"{os.path.abspath(file_path)}"')
            else:
                webbrowser.open("file://" + os.path.dirname(os.path.abspath(file_path)))

    def _queue_item_count(self):
        """Returns the number of queue entries, excluding the placeholder."""
        if hasattr(self, "file_listbox"):
            try:
                return len(self.file_listbox.get_children())
            except Exception:
                pass
        return len(self.file_list)

    def _schedule_empty_queue_placeholder_update(self):
        """Schedules a deferred refresh of the empty-queue placeholder."""
        if hasattr(self, "root") and self.root is not None:
            try:
                self.root.after_idle(self.update_empty_queue_placeholder)
                return
            except Exception:
                pass
        try:
            self.update_empty_queue_placeholder()
        except Exception:
            pass

    def update_empty_queue_placeholder(self):
        """Shows or hides the empty-queue placeholder."""
        if not hasattr(self, "empty_queue_label"):
            return

        has_items = len(self.file_listbox.get_children()) > 0 if hasattr(self, "file_listbox") else len(self.file_list) > 0
        if has_items:
            self.empty_queue_label.place_forget()
            try:
                self.file_listbox.lift()
            except Exception:
                pass
        else:
            self.empty_queue_label.place(relx=0.5, rely=0.42, anchor="center")
            try:
                self.empty_queue_label.lift()
            except Exception:
                pass

    def _build_column_selector_menu(self, menu):
        """Builds the column visibility menu."""
        menu.add_checkbutton(
            label=get_text("file_list_header_duration"),
            variable=self.col_duration_visible,
            command=self.update_visible_columns
        )
        menu.add_checkbutton(
            label=get_text("file_list_header_format"),
            variable=self.col_format_visible,
            command=self.update_visible_columns
        )
        menu.add_checkbutton(
            label=get_text("file_list_header_samplerate"),
            variable=self.col_samplerate_visible,
            command=self.update_visible_columns
        )


    def _on_info_button_enter(self, event):
        """Shows tooltip and status hint for the information button."""
        if self.info_button.cget("state") == "disabled":
            return
        self._show_status_hint("menu_context_inspect")
        self.info_button_tooltip.show(get_text("info_button_tooltip"), event.x_root, event.y_root)

    def _on_info_button_motion(self, event):
        """Updates the information button tooltip position."""
        if self.info_button.cget("state") == "disabled":
            self.info_button_tooltip.hide()
            return
        self.info_button_tooltip.show(get_text("info_button_tooltip"), event.x_root, event.y_root)

    def _on_info_button_leave(self, event):
        """Hides the information button tooltip."""
        self.info_button_tooltip.hide()
        self.update_status_bar_default()

    def show_context_menu(self, event):
        """Shows the queue context menu."""
        item = self.file_listbox.identify_row(event.y)
        region = self.file_listbox.identify_region(event.x, event.y)

        menu = tk.Menu(self.root, tearoff=0)

        if region == "heading" or not item:
            self._build_column_selector_menu(menu)
        else:
            if item not in self.file_listbox.selection():
                self.file_listbox.selection_set(item)

            inspect_lbl = get_text("menu_context_inspect")
            if inspect_lbl.startswith("[") and inspect_lbl.endswith("]"):
                inspect_lbl = "Show Audio Information..."
            menu.add_command(label=inspect_lbl, command=self.open_inspector)

            prop_lbl = get_text("menu_context_properties")
            if prop_lbl.startswith("[") and prop_lbl.endswith("]"):
                prop_lbl = "Properties"
            menu.add_command(label=prop_lbl, command=self.show_file_properties)

            menu.add_separator()

            loc_lbl = get_text("menu_context_open_location")
            if loc_lbl.startswith("[") and loc_lbl.endswith("]"):
                loc_lbl = "Open file location"
            menu.add_command(label=loc_lbl, command=self.open_file_location)

            menu.add_separator()

            cols_submenu = tk.Menu(menu, tearoff=0)
            self._build_column_selector_menu(cols_submenu)
            menu.add_cascade(label=get_text("menu_context_columns"), menu=cols_submenu)

            menu.add_separator()
            remove_lbl = get_text("remove_files_button")
            if remove_lbl.startswith("[") and remove_lbl.endswith("]"):
                remove_lbl = "Remove Selected"
            menu.add_command(label=remove_lbl, command=self.remove_selected_files)

        try:
            menu.post(event.x_root, event.y_root)
        finally:
            try:
                menu.grab_release()
            except Exception:
                pass

    def open_inspector(self, event=None):
        """Opens the audio inspector for the selected file."""
        selection = self.file_listbox.selection()
        if not selection:
            return
        if not self._check_ffmpeg_path():
            return
        index = self.file_listbox.index(selection[0])
        file_path = self.file_list[index]

        if self.inspector_window is not None and self.inspector_window.win.winfo_exists():
            self.inspector_window.update_file(file_path)
            self.inspector_window.win.lift()
            self.inspector_window.win.focus_set()
        else:
            from inspector import AudioInspectorDialog
            self.inspector_window = AudioInspectorDialog(self.root, self, file_path, self.colors, config.ffmpeg_path)

    def open_help_file(self, event=None):
        """Opens the bundled help file if it exists."""
        base_path = core.get_base_path()
        lang_code = config.language
        help_file = os.path.join(base_path, "help", f"help_{lang_code}.html")
        if not os.path.exists(help_file):
            help_file = os.path.join(base_path, "help", "help_en_US.html")
        if not os.path.exists(help_file):
            help_file = os.path.join(base_path, f"help_{lang_code}.html")
        if not os.path.exists(help_file):
            help_file = os.path.join(base_path, "help_en_US.html")

        if os.path.exists(help_file):
            webbrowser.open("file://" + os.path.abspath(help_file))
        else:
            messagebox.showerror(
                get_text("error_help_not_found_title"),
                get_text("error_help_not_found_message")
            )

    def show_file_properties(self, event=None):
        """Displays the standard file properties for the selected item."""
        selection = self.file_listbox.selection()
        if not selection: return
        index = self.file_listbox.index(selection[0])
        file_path = self.file_list[index]

        if os.path.exists(file_path):
            if os.name == 'nt':
                try:
                    import ctypes
                    from ctypes import wintypes
                    class SHELLEXECUTEINFOW(ctypes.Structure):
                        _fields_ = [
                            ("cbSize", wintypes.DWORD),
                            ("fMask", ctypes.c_ulong),
                            ("hwnd", wintypes.HWND),
                            ("lpVerb", ctypes.c_wchar_p),
                            ("lpFile", ctypes.c_wchar_p),
                            ("lpParameters", ctypes.c_wchar_p),
                            ("lpDirectory", ctypes.c_wchar_p),
                            ("nShow", ctypes.c_int),
                            ("hInstApp", wintypes.HINSTANCE),
                            ("lpIDList", ctypes.c_void_p),
                            ("lpClass", ctypes.c_wchar_p),
                            ("hkeyClass", wintypes.HKEY),
                            ("dwHotKey", wintypes.DWORD),
                            ("hIconOrMonitor", wintypes.HANDLE),
                            ("hProcess", wintypes.HANDLE)
                        ]
                    info = SHELLEXECUTEINFOW()
                    info.cbSize = ctypes.sizeof(SHELLEXECUTEINFOW)
                    info.fMask = 0x0000000C 
                    info.lpVerb = "properties"
                    info.lpFile = os.path.abspath(file_path)
                    info.nShow = 5 
                    ctypes.windll.shell32.ShellExecuteExW(ctypes.byref(info))
                except Exception:
                    pass

    def _validate_entry(self, widget, new_value, min_val, max_val):
        """Validates a numeric entry field and applies its visual state."""
        if str(widget.cget('state')) == 'disabled':
            widget.config(style="TEntry")
            return True
        try:
            val = float(new_value)
            if min_val <= val <= max_val: widget.config(style="TEntry")
            else: widget.config(style="Error.TEntry")
        except (ValueError, TypeError):
            widget.config(style="Error.TEntry")
        return True

    def update_entry_states(self, event=None):
        """Refreshes the preset entry states after a mode change."""
        is_lufs_custom = self.lufs_preset_var.get() == get_text("preset_custom")
        is_tp_custom = self.true_peak_preset_var.get() == get_text("preset_custom")

        self.lufs_entry.config(state=tk.NORMAL if is_lufs_custom else tk.DISABLED)
        self.lufs_label.config(state=tk.NORMAL if is_lufs_custom else tk.DISABLED)
        self.tp_entry.config(state=tk.NORMAL if is_tp_custom else tk.DISABLED)
        self.tp_label.config(state=tk.NORMAL if is_tp_custom else tk.DISABLED)

        self.lufs_entry.config(style="TEntry")
        self.tp_entry.config(style="TEntry")

        if not is_lufs_custom: self.lufs_entry_var.set(i18n.LUFS_PRESETS.get(self.lufs_preset_var.get(), ""))
        if not is_tp_custom: self.tp_entry_var.set(i18n.TRUE_PEAK_PRESETS.get(self.true_peak_preset_var.get(), ""))

    def _set_status_state(self, key, **kwargs):
        """Applies the requested visual state to the status bar."""
        self._status_state = (key, kwargs)
        if not self._status_hover_active:
            self.status_bar.config(text=get_text(key, **kwargs))

    def _set_status_text(self, text):
        """Updates the status bar text."""
        self._status_state = ("__literal__", {"text": text})
        if not self._status_hover_active:
            self.status_bar.config(text=text)

    def _show_status_hint(self, key, **kwargs):
        """Shows a temporary hint in the status bar."""
        self._status_hover_active = True
        self.status_bar.config(text=get_text(key, **kwargs))

    def _restore_status_bar(self):
        """Restores the default status bar contents."""
        self._status_hover_active = False
        key, kwargs = self._status_state
        if key == "__literal__":
            self.status_bar.config(text=kwargs.get("text", ""))
        else:
            self.status_bar.config(text=get_text(key, **kwargs))

    def update_status_bar(self):
        """Refreshes the status bar with the current process information."""
        if self.is_processing or self.player.is_playing or self.player.is_paused:
            return
        if self.file_list:
            self._set_status_state("status_files_selected", count=len(self.file_list))
        else:
            self._set_status_state("status_program_start_no_files")

    def update_status_bar_default(self):
        """Restores the default status bar message."""
        self._restore_status_bar()

    def _apply_status_message(self, payload):
        """Applies a status message and optional timeout handling."""
        if isinstance(payload, tuple) and len(payload) == 2 and isinstance(payload[0], str):
            key, kwargs = payload
            if isinstance(kwargs, dict):
                self._set_status_state(key, **kwargs)
                return
        if isinstance(payload, str):
            self._set_status_text(payload)
        else:
            self._set_status_text(str(payload))

    def update_process_info(self, message):
        """Updates the process information label."""
        self.process_info.config(state=tk.NORMAL)
        self.process_info.insert(tk.END, message)
        self.process_info.see(tk.END)
        self.process_info.config(state=tk.DISABLED)

    def update_output_format_info(self, event=None):
        """Refreshes the output format summary text."""
        selected_format = self.output_format_var.get()
        details = i18n.language_data.get("output_format_details", {}).get(selected_format, None)
        if details:
            sr_choice = self.output_samplerate_var.get()
            quality_choice = self.output_quality_var.get()

            specs_parts = []

            if self.quality_combobox.current() == 0:
                if selected_format in ("WAV", "FLAC"):
                    specs_parts.append(get_text("output_original_bitdepth"))
                else:
                    specs_parts.append(get_text("output_original_bitrate"))
            else:
                specs_parts.append(quality_choice)

            if self.samplerate_combobox.current() == 0:
                specs_parts.append(get_text("output_original_samplerate"))
            else:
                specs_parts.append(sr_choice)

            if selected_format in ("WAV", "FLAC"):
                specs_parts.append(get_text("output_original_channels"))
            else:
                specs_parts.append(get_text("output_stereo_channels"))

            specs_str = f"{get_text('output_specs_header')} " + ", ".join(specs_parts)

            self.output_specs_label.config(text=specs_str)
            self.output_desc_label.config(text=details['description'])
            self.output_info_frame.grid()
        else:
            self.output_specs_label.config(text="")
            self.output_desc_label.config(text="")
            self.output_info_frame.grid_remove()

    def update_mastering_help_text(self, event=None):
        """Refreshes the mastering help text for the active preset."""
        if not hasattr(self, "mastering_help_label"): return
        self.mastering_help_label.config(text=i18n.get_mastering_help_text(self.mastering_preset_var.get()))

    def toggle_controls(self, enable=True, for_playback=False):
        """Enables or disables controls while a task is running."""
        state = tk.NORMAL if enable else "disabled"
        readonly_state = "readonly" if enable else "disabled"

        queue_btn_state = tk.NORMAL if for_playback else state

        self.add_files_button.config(state=queue_btn_state)
        self.add_folder_button.config(state=queue_btn_state)
        self.remove_files_button.config(state=queue_btn_state)

        self.analyze_button.config(state=state)
        self.start_button.config(state=state)

        if for_playback:
            selection = self.file_listbox.selection()
            self.info_button.config(state="normal" if selection else "disabled")
        else:
            self.info_button.config(state=state)

        for combo in [self.lufs_combobox, self.tp_combobox, self.mastering_combobox, self.output_combobox, self.samplerate_combobox, self.quality_combobox]:
            combo.config(state=readonly_state)

        self.radio_linear.config(state=state)
        self.radio_dynamic.config(state=state)

        if not for_playback:
            self.cancel_button.config(state="normal" if not enable else "disabled")

        if enable: 
            self.update_entry_states()
            self.update_player_button_states()

    def update_player_button_states(self, event=None):
        """Synchronizes playback button states with the player."""
        selection = self.file_listbox.selection()
        if selection:
            index = self.file_listbox.index(selection[0])
            file_path = self.file_list[index]
            if self.inspector_window is not None and self.inspector_window.win.winfo_exists():
                self.inspector_window.update_file(file_path)

        if self.player.is_playing:
            if self.player.is_paused:
                self.play_button.config(state='normal')
                self.pause_button.config(state='normal')
                self.stop_button.config(state='normal')
            else:
                self.play_button.config(state='disabled')
                self.pause_button.config(state='normal')
                self.stop_button.config(state='normal')

            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')

            self.info_button.config(state='normal' if selection else 'disabled')
            return

        play_state = 'normal' if selection else 'disabled'
        nav_state = 'normal' if len(self.file_list) > 1 else 'disabled'

        self.play_button.config(state=play_state)
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.prev_button.config(state=nav_state)
        self.next_button.config(state=nav_state)
        self.info_button.config(state=play_state)

    def play_audio(self):
        """Starts playback of the current selection."""
        if self.player.is_paused:
            self.pause_audio()
            return

        if self.player.is_playing or not self.file_listbox.selection(): return
        selected_item = self.file_listbox.selection()[0]
        self.current_track_index = self.file_listbox.index(selected_item)
        self._start_playback(self.current_track_index)

    def pause_audio(self):
        """Toggles playback pause state."""
        if not self.player.is_playing: return
        paused = self.player.toggle_pause()
        if paused is not None:
            playback_file = os.path.basename(self.current_playback_file) if self.current_playback_file else ""
            self._set_status_state("status_playback_paused" if paused else "status_playback_started", file=playback_file)
            self.update_player_button_states()
            self._sync_visualizers()

    def stop_audio(self, show_status=True):
        """Stops playback."""
        self._playback_stop_requested = show_status
        self._playback_suppress_finish = not show_status
        self.player.stop()
        if show_status:
            playback_file = os.path.basename(self.current_playback_file) if self.current_playback_file else ""
            self._set_status_state("status_playback_stopped", file=playback_file)
        self.update_player_button_states()
        self.time_label_var.set("00:00:00 / 00:00:00")
        self.player_progress.config(value=0)
        self._sync_visualizers()

    def seek_audio(self, event):
        """Seeks playback to the requested position."""
        if not self.file_list or self.current_track_index == -1: return
        if self.player.total_duration_sec <= 0: return

        width = self.player_progress.winfo_width()
        if width <= 0: return

        percentage = max(0.0, min(1.0, event.x / width))
        target_sec = percentage * self.player.total_duration_sec

        self.stop_audio(show_status=False)
        self._start_playback(self.current_track_index, start_time_sec=target_sec)

    def play_next(self):
        """Moves playback to the next queue item."""
        if not self.file_list: return
        next_index = (self.current_track_index + 1) % len(self.file_list)
        self._start_playback(next_index)    

    def play_previous(self):
        """Moves playback to the previous queue item."""
        if not self.file_list: return
        prev_index = (self.current_track_index - 1 + len(self.file_list)) % len(self.file_list)
        self._start_playback(prev_index)

    def _start_playback(self, track_index: int, start_time_sec: float = 0.0):
        """Starts playback for the active queue item."""
        if self.player.is_playing: self.stop_audio(show_status=False)

        self.play_button.config(state='disabled')
        self.pause_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')

        self.current_track_index = track_index

        try:
            item_id = self.file_listbox.get_children()[track_index]
            self.file_listbox.selection_set(item_id)
            self.file_listbox.focus(item_id)
            self.file_listbox.see(item_id)
        except IndexError:
            return

        filepath = self.file_list[track_index]
        self.current_playback_file = filepath
        self._playback_stop_requested = False
        self._playback_suppress_finish = False
        self._playback_error_received = False
        self.player.play(filepath, start_time_sec)
        self._set_status_state("status_playback_started", file=os.path.basename(filepath))
        self._sync_visualizers()

    def show_about(self):
        """Opens the About dialog."""
        if self.about_window is not None and self.about_window.win.winfo_exists():
            self.about_window.win.lift()
            self.about_window.win.focus_set()
            return
        self.about_window = dialogs.AboutDialog(self.root, self.colors)

    def show_options(self):
        """Opens the Options dialog."""
        if self.options_window is not None and self.options_window.win.winfo_exists():
            self.options_window.win.lift()
            self.options_window.win.focus_set()
            return
        self.options_window = dialogs.OptionsDialog(self.root, self, self.colors)

    def start_task(self, task_type):
        """Starts the selected processing task in the background."""
        if self.player.is_playing: self.stop_audio()

        if not self._check_ffmpeg_path():
            return

        if not self.file_list:
            messagebox.showwarning(get_text("error_no_files_title"), get_text("error_no_files_message"))
            return

        try:
            lufs, tp = float(self.lufs_entry_var.get()), float(self.tp_entry_var.get())
            if not -70 <= lufs <= 0 or not -9 <= tp <= 0: raise ValueError
        except (ValueError, TypeError):
            messagebox.showerror(get_text("normalization_invalid_lufs_error_title"), get_text("normalization_invalid_lufs_error_message"))
            return

        files_to_process = []
        if task_type == 'normalize':
            output_format = self.output_format_var.get()
            output_ext = next((ext for ext, name in AUDIO_FILE_EXTENSIONS if name == output_format), ".tmp")

            for file_path in self.file_list:
                output_file = os.path.splitext(file_path)[0] + "-Normalized" + output_ext
                if os.path.exists(output_file):
                    if messagebox.askyesno(
                        title=get_text("normalization_overwrite_title"),
                        message=get_text("normalization_overwrite_message", file=os.path.basename(output_file)),
                        parent=self.root):
                        files_to_process.append(file_path)
                else:
                    files_to_process.append(file_path)
        else:
            files_to_process = self.file_list.copy()

        if not files_to_process:
            self.update_status_bar_default()
            return

        self.is_cancelled = False
        self.toggle_controls(enable=False)
        self.process_info.config(state=tk.NORMAL); self.process_info.delete("1.0", tk.END); self.process_info.config(state=tk.DISABLED)

        self.task_generation += 1
        task_id = self.task_generation
        self.current_task_id = task_id
        self.active_task_total = len(files_to_process)
        self.progress_mode_switched = False

        self.current_task_type = task_type
        self.is_processing = True
        self._animate_spinner()

        self._set_status_state("status_analysis_ready" if task_type == "analyze" else "status_normalization_ready")

        self.progressbar.stop()

        self.progressbar.configure(
            mode='determinate',
            maximum=100,
            value=0
        )

        self.root.update_idletasks()

        self.progressbar.configure(
            mode='indeterminate'
        )

        self.progressbar.start(12)

        log_filename = ANALYSIS_LOG_FILE_NAME if task_type == "analyze" else LOG_FILE_NAME

        if config.single_log_entry_enabled and core.app_logger:
            core.app_logger.log(log_filename, f"--- {datetime.datetime.now()} | {VERSION}-{INTERNAL_VERSION} | Starting {task_type} batch ---\n", "w")

        processor = FFMpegProcessor(
            config.ffmpeg_path, 
            update_callback=lambda msg, task_id=task_id: self.gui_queue.put(("task", task_id, "info", msg)),
            process_callback=lambda proc: setattr(self, 'current_norm_process', proc)
        )

        mode = self.mode_var.get()
        mastering_preset = i18n.get_mastering_preset_name_from_display(self.mastering_preset_var.get()) or DEFAULT_MASTERING_PRESET

        sr_index = self.samplerate_combobox.current()
        quality_index = self.quality_combobox.current()

        task_thread = threading.Thread(
            target=self.task_runner,
            args=(task_type, files_to_process, processor, lufs, tp, mode, mastering_preset, task_id, sr_index, quality_index),
        )
        task_thread.daemon = True
        task_thread.start()

    def task_runner(self, task_type, files, processor, lufs, tp, mode, mastering_preset, task_id, sr_index, quality_index):
        """Runs the active task and streams updates back to the UI."""
        was_cancelled = False
        for i, file_path in enumerate(files):
            if self.is_cancelled:
                was_cancelled = True; break

            base_name = os.path.basename(file_path)
            status_key = "status_analyze_running" if task_type == "analyze" else "status_normalize_running"
            self.gui_queue.put(("task", task_id, "status", (status_key, {"file": base_name})))
            self.gui_queue.put(("task", task_id, "info", f"\n--- {get_text(f'status_{task_type}_running', file=base_name)} ---\n"))

            log_file = ANALYSIS_LOG_FILE_NAME if task_type == "analyze" else LOG_FILE_NAME

            if task_type == "analyze":
                return_code, stderr = processor.analyze(file_path)
            else:
                output_format = self.output_format_var.get()
                output_ext = next((ext for ext, name in AUDIO_FILE_EXTENSIONS if name == output_format), ".tmp")
                output_file = os.path.splitext(file_path)[0] + "-Normalized" + output_ext

                return_code, stderr = processor.normalize(
                    file_path, output_file, lufs, tp, output_format, sr_index, quality_index, mode, mastering_preset
                )

            log_content = f"\n--- File: {file_path} ---\n{stderr}\n"
            self.gui_queue.put(("task", task_id, "log", (log_file, log_content, "a")))

            if self.is_cancelled:
                was_cancelled = True; break

            if return_code != 0:
                error_msg = stderr if "ffmpeg_not_found" not in stderr else get_text("options_error_ffmpeg_executable_message")
                error_title = get_text(f"{task_type}_ffmpeg_error_title") if "ffmpeg_not_found" not in stderr else get_text("options_error_ffmpeg_executable_title")
                self.gui_queue.put(("task", task_id, "error", (error_title, error_msg)))
                return

            self.gui_queue.put(("task", task_id, "progress", i + 1))

        self.gui_queue.put(("task", task_id, "finish", "cancelled" if was_cancelled else "completed"))

    def cancel_task(self):
        """Requests cancellation of the active background task."""
        self.is_cancelled = True
        if self.current_norm_process and self.current_norm_process.poll() is None:
            try:
                self.current_norm_process.terminate()
            except Exception:
                pass
            if os.name == 'nt':
                try:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.current_norm_process.pid)], creationflags=subprocess.CREATE_NO_WINDOW)
                except Exception:
                    pass
            self.update_process_info(get_text("normalization_cancel_process_message"))

    def process_gui_queue(self):
        """Processes pending GUI events from background workers."""
        try:
            count = 0
            while count < 30:
                message = self.gui_queue.get_nowait()
                task = message[0]
                if task == "task":
                    _, msg_task_id, msg_type, data = message
                    if msg_task_id != self.current_task_id:
                        continue

                    if msg_type == "info":
                        self.update_process_info(data)
                    elif msg_type == "status":
                        self._apply_status_message(data)
                    elif msg_type == "progress":
                        if not self.progress_mode_switched:
                            self.progressbar.stop()
                            self.progressbar.config(mode='determinate', maximum=max(1, self.active_task_total), value=0)
                            self.progress_mode_switched = True
                        self.progressbar.config(value=data)
                    elif msg_type == "log":
                        if core.app_logger:
                            core.app_logger.log(*data)
                    elif msg_type == "error":
                        self.task_finished(status="error", message=data)
                    elif msg_type == "finish":
                        self.task_finished(status=data)
                elif task == "info":
                    self.update_process_info(message[1])
                elif task == "status":
                    self._apply_status_message(message[1])
                elif task == "progress":
                    self.progressbar.config(value=message[1])
                elif task == "log":
                    if core.app_logger: core.app_logger.log(*message[1])
                elif task == "error":
                    if self.is_processing:
                        self.task_finished(status="error", message=message[1])
                    else:
                        self._playback_error_received = True
                        messagebox.showerror(message[1][0], message[1][1], parent=self.root)
                elif task == "finish": self.task_finished(status=message[1])
                elif task == "toggle_playback_controls":
                    self.toggle_controls(enable=message[1], for_playback=True)
                    self.update_player_button_states()
                elif task == "update_time":
                    current_sec, total_sec = message[1]
                    self.time_label_var.set(f"{utils.format_time(current_sec)} / {utils.format_time(total_sec)}")
                    if total_sec > 0:
                        self.player_progress.config(maximum=total_sec, value=current_sec)
                    else:
                        self.player_progress.config(maximum=100, value=0)
                elif task == "update_tree_item":
                    item_id, dur_str, fmt_str, sr_str = message[1]
                    try:
                        if self.file_listbox.exists(item_id):
                            current_values = self.file_listbox.item(item_id, "values")
                            if current_values:
                                self.file_listbox.item(item_id, values=(current_values[0], dur_str, fmt_str, sr_str))
                    except Exception:
                        pass
                elif task == "update_check_result":
                    manual, result = message[1]
                    self._handle_update_check_result(manual, result)
                elif task == "playback_finished":
                    finished_id = message[1] if len(message) > 1 else 0
                    if finished_id == self.player.current_playback_id or finished_id == 0:
                        was_error = self._playback_error_received
                        was_stopped = self._playback_stop_requested
                        suppress_finish = self._playback_suppress_finish
                        self._playback_error_received = False
                        self._playback_stop_requested = False
                        self._playback_suppress_finish = False
                        self.player.is_playing = False
                        self.player.is_paused = False
                        self.toggle_controls(enable=True)
                        self.update_player_button_states()
                        self.time_label_var.set("00:00:00 / 00:00:00")
                        self.player_progress.config(value=0)
                        self._sync_visualizers()
                        if not was_error and not suppress_finish:
                            playback_file = os.path.basename(self.current_playback_file) if self.current_playback_file else ""
                            self._set_status_state("status_playback_stopped" if was_stopped else "status_playback_finished", file=playback_file)

                count += 1
        except Empty:
            pass
        except Exception as e:
            self.update_process_info(f"\n[GUI Queue Error]: {str(e)}\n")

        self.root.after(100, self.process_gui_queue)

    def task_finished(self, status, message=None):
        """Finalizes the UI after a task completes."""
        self.toggle_controls(enable=True)
        self.progressbar.stop()
        self.is_processing = False
        self.spinner_label.config(text="")

        completed_tasks = self.active_task_total

        if status == "completed":
            if completed_tasks > 1:
                self.progressbar.config(
                    mode='determinate',
                    maximum=max(1, completed_tasks),
                    value=completed_tasks
                )
            else:
                self.progressbar.config(mode='determinate', value=0)

            completed_key = "status_analysis_completed" if self.current_task_type == "analyze" else "status_normalization_completed" if self.current_task_type == "normalize" else "status_completed"
            self._set_status_state(completed_key)
            self.update_process_info(f"\n--- {get_text(completed_key)} ---")
            winsound.MessageBeep(winsound.MB_OK)
        elif status == "cancelled":
             self.progressbar.config(mode='determinate', value=0)
             self._set_status_state("status_cancelled")
             self.update_process_info(f"\n--- {get_text('status_cancelled')} ---")
        elif status == "error":
            self.progressbar.config(mode='determinate', value=0)
            self._set_status_state("status_error")
            if message: messagebox.showerror(message[0], message[1])
            winsound.MessageBeep(winsound.MB_ICONERROR)

        self.current_norm_process = None
        self.current_task_id = None
        self.current_task_type = None
        self.active_task_total = 0
        self.progress_mode_switched = False
