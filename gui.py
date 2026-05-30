# -*- coding: utf-8 -*-
"""
gui.py
Handles the Tkinter User Interface and Background Task routing.
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
from queue import Queue, Empty
from typing import Optional

from constants import *
import core
import i18n
import theme
from audio import FFMpegProcessor

get_text = i18n.get_text
config = core.app_config

def center_window(window):
    """Centers the application window on the primary display."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def format_time(seconds):
    """Converts a float duration in seconds into a HH:MM:SS format."""
    if seconds is None: return "00:00:00"
    try:
        secs = float(seconds)
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    except (ValueError, TypeError):
        return "00:00:00"

class AudioNormalizerApp:
    def __init__(self, root):
        self.root = root
        self.file_list = []
        self.is_cancelled = False
        
        # Audio Player States
        self.is_playing = False
        self.playback_thread = None
        self.current_track_index = -1
        self.total_duration_sec = 0
        self.ffprobe_checked = False

        # State Encapsulation
        self.gui_queue = Queue()
        self.current_playback_process: Optional[subprocess.Popen] = None
        self.current_norm_process: Optional[subprocess.Popen] = None
        self.task_generation = 0
        self.current_task_id = None
        self.active_task_total = 0
        self.progress_mode_switched = False
        
        # Trackers for single-instance dialog windows
        self.options_window = None
        self.about_window = None
        
        self.setup_styles()
        self.create_widgets()
        self.apply_language()
        self.process_gui_queue()
        center_window(self.root)

    def setup_styles(self):
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        theme_mode = getattr(config, "theme_mode", "light")
        self.colors = theme.apply_theme(self.style, self.root, theme_mode)

    def create_widgets(self):
        # Set the main application window size and minimum constraints
        self.root.title(f"{get_text('app_title')} v{VERSION} - {EDITION_NAME}")
        self.root.geometry("1120x760") 
        self.root.minsize(1080, 740)
        
        self.main_frame = ttk.Frame(self.root, padding=GUI_PADY, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        top_frame = ttk.Frame(self.main_frame, style="TFrame")
        top_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)
        top_frame.columnconfigure(0, weight=3)
        top_frame.columnconfigure(1, weight=2)
        
        self.file_frame = ttk.LabelFrame(top_frame, text=get_text("file_selection_group"), style="TLabelframe")
        self.file_frame.grid(row=0, column=0, sticky="nsew", padx=(0, GUI_PADX))
        self.file_frame.columnconfigure(0, weight=1)
        self.file_frame.rowconfigure(0, weight=1)

        # Limit the file list to six rows to preserve a compact layout
        self.file_listbox = ttk.Treeview(self.file_frame, columns=("filename",), show="headings", selectmode="extended", height=6)
        self.file_listbox.heading("filename", text=get_text("file_list_header_filename"))
        self.file_listbox.column("filename", anchor="w")
        self.file_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=(8, 10))
        self.file_listbox.bind("<Delete>", self.remove_selected_files)
        self.file_listbox.bind("<<TreeviewSelect>>", self.update_player_button_states)
        
        list_scrollbar = ttk.Scrollbar(self.file_frame, orient="vertical", command=self.file_listbox.yview)
        list_scrollbar.grid(row=0, column=2, sticky="ns")
        self.file_listbox.config(yscrollcommand=list_scrollbar.set)
        
        file_button_frame = ttk.Frame(self.file_frame, style="TFrame")
        file_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.add_files_button = ttk.Button(file_button_frame, text=get_text("add_files_button"), command=self.add_files)
        self.add_folder_button = ttk.Button(file_button_frame, text=get_text("add_folder_button"), command=self.add_folder)
        self.remove_files_button = ttk.Button(file_button_frame, text=get_text("remove_files_button"), command=self.remove_selected_files)
        
        self.add_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.add_folder_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.remove_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

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
        self.stop_button = ttk.Button(controls_subframe, text="■", command=self.stop_audio, width=4)
        self.play_button.pack(side=tk.LEFT, padx=5)
        self.stop_button.pack(side=tk.LEFT)
        
        nav_subframe = ttk.Frame(player_frame, style="TFrame")
        nav_subframe.grid(row=0, column=2, sticky='e')
        
        self.prev_button = ttk.Button(nav_subframe, text="«", command=self.play_previous, width=4)
        self.next_button = ttk.Button(nav_subframe, text="»", command=self.play_next, width=4)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        self.next_button.pack(side=tk.LEFT)
        
        settings_frame = ttk.Frame(top_frame, style="TFrame")
        settings_frame.grid(row=0, column=1, sticky="nsew")
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
        self.mastering_help_label = ttk.Label(
            self.loudness_frame, text="", style="TLabel", justify=tk.LEFT, wraplength=520, anchor="w"
        )
        self.mastering_help_label.grid(row=3, column=0, columnspan=4, sticky="we", padx=GUI_PADX, pady=(0, GUI_PADY))

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
        self.output_frame.pack(fill=tk.X, expand=True, pady=GUI_PADY)
        
        self.output_format_var = tk.StringVar()
        ttk.Label(self.output_frame, text=get_text("output_format_file_format_label"), style="TLabel").grid(row=0, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.output_combobox = ttk.Combobox(self.output_frame, textvariable=self.output_format_var, values=OUTPUT_FORMATS_LIST, state="readonly")
        self.output_combobox.grid(row=0, column=1, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.output_combobox.set(OUTPUT_FORMATS_LIST[0])
        self.output_combobox.bind("<<ComboboxSelected>>", self.update_output_format_info)
        
        self.output_info_frame = ttk.Frame(self.output_frame, style="TFrame")
        self.output_info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=GUI_PADX, pady=(GUI_PADY, 0))
        self.output_info_frame.columnconfigure(0, weight=1)
        
        self.output_specs_label = ttk.Label(self.output_info_frame, text="", style="TLabel", justify=tk.LEFT)
        self.output_specs_label.pack(fill='x')
        ttk.Separator(self.output_info_frame, orient='horizontal').pack(fill='x', pady=3)
        self.output_desc_label = ttk.Label(self.output_info_frame, text="", style="TLabel", wraplength=350, justify=tk.LEFT)
        self.output_desc_label.pack(fill='x')

        bottom_frame = ttk.Frame(self.main_frame, style="TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=GUI_PADX, pady=GUI_PADY)
        bottom_frame.rowconfigure(0, weight=1)
        bottom_frame.columnconfigure(0, weight=1)
        
        self.info_frame = ttk.LabelFrame(bottom_frame, text=get_text("process_information_group"), style="TLabelframe")
        self.info_frame.grid(row=0, column=0, sticky="nsew", pady=GUI_PADY)
        self.info_frame.rowconfigure(0, weight=1)
        self.info_frame.columnconfigure(0, weight=1)

        # Limit the process log height to preserve space for bottom controls
        self.process_info = tk.Text(self.info_frame, wrap=tk.WORD, state=tk.DISABLED, height=8, 
                                    bg=self.colors["info_bg"], fg=self.colors["fg"], 
                                    highlightthickness=0, relief=self.colors.get("text_relief", "sunken"), borderwidth=1)
        self.process_info.grid(row=0, column=0, sticky="nsew")
        info_scrollbar = ttk.Scrollbar(self.info_frame, orient="vertical", command=self.process_info.yview)
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        self.process_info.config(yscrollcommand=info_scrollbar.set)
        
        control_frame = ttk.Frame(bottom_frame, style="TFrame")
        control_frame.grid(row=1, column=0, sticky="ew", pady=(12, 4))
        
        self.analyze_button = ttk.Button(control_frame, text=get_text("analyze_audio_button"), command=lambda: self.start_task("analyze"))
        
        # Highlight the primary action button using the accent style
        self.start_button = ttk.Button(control_frame, text="▶ " + get_text("start_normalization_button"), command=lambda: self.start_task("normalize"), style="Accent.TButton")
        self.cancel_button = ttk.Button(control_frame, text=get_text("cancel_normalization_button"), command=self.cancel_task, state=tk.DISABLED)
        
        self.analyze_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        # Attach the status bar and progress bar to the main frame for layout stability
        self.status_bar = ttk.Label(self.main_frame, text=get_text("status_ready"), anchor=tk.W, style="TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=GUI_PADX)
        
        self.progressbar = ttk.Progressbar(self.main_frame, mode='determinate')
        self.progressbar.pack(side=tk.BOTTOM, fill=tk.X, padx=GUI_PADX, pady=(0, GUI_PADY))

        self.create_menu()
        self.update_output_format_info()
        self.update_player_button_states()

    def on_closing(self):
        self.stop_audio()
        self.cancel_task()
        self.root.destroy()

    def create_menu(self):
        self.menubar = tk.Menu(self.root)
        self.root.config(menu=self.menubar)
        file_menu = tk.Menu(self.menubar, tearoff=0)
        file_menu.add_command(label=get_text("menu_file_options"), command=self.show_options)
        file_menu.add_separator()
        file_menu.add_command(label=get_text("menu_file_exit"), command=self.on_closing)
        self.menubar.add_cascade(label=get_text("menu_file"), menu=file_menu)
        info_menu = tk.Menu(self.menubar, tearoff=0)
        info_menu.add_command(label=get_text("menu_info_about"), command=self.show_about)
        info_menu.add_command(label=get_text("menu_info_updates"), command=lambda: webbrowser.open("http://melcom-creations.github.io/melcom-music/creations.html#ffmpeg"))
        self.menubar.add_cascade(label=get_text("menu_info"), menu=info_menu)

    def apply_language(self):
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
        self.status_bar.config(text=get_text("status_ready"))
        
        self.radio_linear.config(text=get_text("mode_linear"))
        self.radio_dynamic.config(text=get_text("mode_dynamic"))
        
        self.file_listbox.heading("filename", text=get_text("file_list_header_filename"))
        self.play_button.config(text="▶")
        self.stop_button.config(text="■")
        self.prev_button.config(text="«")
        self.next_button.config(text="»")

        self.update_entry_states()
        self.update_output_format_info()

    def add_files(self):
        filetypes = [(get_text("file_dialog_audio_files"), " ".join([ext for ext, _ in AUDIO_FILE_EXTENSIONS]))]
        files = filedialog.askopenfilenames(title=get_text("file_dialog_title"), filetypes=filetypes)
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.file_listbox.insert("", tk.END, values=(os.path.basename(f),))
        self.update_status_bar()
        self.update_player_button_states()

    def add_folder(self):
        folder = filedialog.askdirectory(title=get_text("folder_dialog_title"))
        if not folder: return
        for root_dir, _, files in os.walk(folder):
            for f in files:
                if any(f.lower().endswith(ext) for ext, _ in AUDIO_FILE_EXTENSIONS):
                    full_path = os.path.join(root_dir, f)
                    if full_path not in self.file_list:
                        self.file_list.append(full_path)
                        self.file_listbox.insert("", tk.END, values=(os.path.basename(f),))
        self.update_status_bar()
        self.update_player_button_states()

    def remove_selected_files(self, event=None):
        selected_items = self.file_listbox.selection()
        if not selected_items: return
            
        indices_to_delete = sorted([self.file_listbox.index(i) for i in selected_items], reverse=True)
        for index in indices_to_delete:
            del self.file_list[index]
        for item in selected_items:
            self.file_listbox.delete(item)
            
        self.update_status_bar()
        self.update_player_button_states()

    def _validate_entry(self, widget, new_value, min_val, max_val):
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

    def update_status_bar(self):
        self.status_bar.config(text=get_text("status_files_selected", count=len(self.file_list)))

    def update_process_info(self, message):
        self.process_info.config(state=tk.NORMAL)
        self.process_info.insert(tk.END, message)
        self.process_info.see(tk.END)
        self.process_info.config(state=tk.DISABLED)

    def update_output_format_info(self, event=None):
        selected_format = self.output_format_var.get()
        details = i18n.language_data.get("output_format_details", {}).get(selected_format, None)
        if details:
            self.output_specs_label.config(text=details['specs'])
            self.output_desc_label.config(text=details['description'])
            self.output_info_frame.grid()
        else:
            self.output_specs_label.config(text="")
            self.output_desc_label.config(text="")
            self.output_info_frame.grid_remove()

    def update_mastering_help_text(self, event=None):
        if not hasattr(self, "mastering_help_label"): return
        self.mastering_help_label.config(text=i18n.get_mastering_help_text(self.mastering_preset_var.get()))

    def toggle_controls(self, enable=True, for_playback=False):
        state = tk.NORMAL if enable else "disabled"
        readonly_state = "readonly" if enable else "disabled"
        
        self.add_files_button.config(state=state)
        self.add_folder_button.config(state=state)
        self.remove_files_button.config(state=state)
        self.analyze_button.config(state=state)
        self.start_button.config(state=state)
        for combo in [self.lufs_combobox, self.tp_combobox, self.mastering_combobox, self.output_combobox]:
            combo.config(state=readonly_state)
            
        self.radio_linear.config(state=state)
        self.radio_dynamic.config(state=state)
        
        if not for_playback:
            self.cancel_button.config(state="normal" if not enable else "disabled")
        
        if enable: self.update_entry_states()

    def update_player_button_states(self, event=None):
        if self.is_playing:
            self.play_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.prev_button.config(state='disabled')
            self.next_button.config(state='disabled')
            return

        selection = self.file_listbox.selection()
        play_state = 'normal' if selection else 'disabled'
        nav_state = 'normal' if len(self.file_list) > 1 else 'disabled'

        self.play_button.config(state=play_state)
        self.stop_button.config(state='disabled')
        self.prev_button.config(state=nav_state)
        self.next_button.config(state=nav_state)

    def play_audio(self):
        if self.is_playing or not self.file_listbox.selection(): return
        selected_item = self.file_listbox.selection()[0]
        self.current_track_index = self.file_listbox.index(selected_item)
        self._start_playback(self.current_track_index)
        
    def stop_audio(self):
        self.is_playing = False
        if self.current_playback_process and self.current_playback_process.poll() is None:
            self.current_playback_process.terminate()

        self.update_player_button_states()
        self.time_label_var.set("00:00:00 / 00:00:00")

    def play_next(self):
        if not self.file_list: return
        next_index = (self.current_track_index + 1) % len(self.file_list)
        self._start_playback(next_index)    

    def play_previous(self):
        if not self.file_list: return
        prev_index = (self.current_track_index - 1 + len(self.file_list)) % len(self.file_list)
        self._start_playback(prev_index)

    def _start_playback(self, track_index):
        if self.is_playing: self.stop_audio()

        self.play_button.config(state='disabled')
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
        self.playback_thread = threading.Thread(target=self._playback_worker, args=(filepath,))
        self.playback_thread.daemon = True
        self.is_playing = True
        self.playback_thread.start()

    def _playback_worker(self, filepath):
        self.gui_queue.put(("toggle_playback_controls", False))
        
        ffprobe_path = os.path.join(config.ffmpeg_path, FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path):
            if not self.ffprobe_checked:
                self.gui_queue.put(("error", (get_text("error_ffprobe_not_found_title"), get_text("error_ffprobe_not_found_message"))))
                self.ffprobe_checked = True
            self.total_duration_sec = 0
        else:
            try:
                cmd = [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
                result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.total_duration_sec = float(result.stdout.strip())
            except Exception as e:
                self.gui_queue.put(("info", f"\n[FFprobe Analysis Error]: {str(e)}\n"))
                self.total_duration_sec = 0
        
        self.gui_queue.put(("update_time", (0, self.total_duration_sec)))
        
        ffplay_path = os.path.join(config.ffmpeg_path, FFPLAY_EXECUTABLE_NAME)
        if not os.path.exists(ffplay_path):
             self.gui_queue.put(("error", (get_text("play_error_ffplay_not_found_title"), get_text("play_error_ffplay_not_found_message"))))
             self.gui_queue.put(("playback_finished", None))
             return
             
        try:
            cmd = [ffplay_path, "-nodisp", "-autoexit", "-loglevel", "info", filepath]
            self.current_playback_process = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='utf-8')
            
            for line in iter(self.current_playback_process.stderr.readline, ''):
                if not self.is_playing: break
                match = re.search(r'^\s*([0-9]+\.[0-9]+)', line)
                if match:
                    current_time_sec = float(match.group(1))
                    self.gui_queue.put(("update_time", (current_time_sec, self.total_duration_sec)))
            
            self.current_playback_process.wait()
        except FileNotFoundError:
            self.gui_queue.put(("error", ("Playback Error", "ffplay.exe could not be executed.")))
        except Exception as e:
            self.gui_queue.put(("info", f"\n[Playback Worker Error]: {str(e)}\n"))
        finally:
            self.gui_queue.put(("playback_finished", None))

    def start_task(self, task_type):
        if self.is_playing: self.stop_audio()
        
        if not self.file_list:
            messagebox.showwarning(get_text("error_no_files_title"), get_text("error_no_files_message"))
            return
        if not config.ffmpeg_path or not os.path.exists(os.path.join(config.ffmpeg_path, FFMPEG_EXECUTABLE_NAME)):
            messagebox.showerror(get_text("options_error_invalid_ffmpeg_path_title"), get_text("options_error_invalid_ffmpeg_path_message"))
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
            self.status_bar.config(text=get_text("status_ready"))
            return

        self.is_cancelled = False
        self.toggle_controls(enable=False)
        self.process_info.config(state=tk.NORMAL); self.process_info.delete("1.0", tk.END); self.process_info.config(state=tk.DISABLED)

        self.task_generation += 1
        task_id = self.task_generation
        self.current_task_id = task_id
        self.active_task_total = len(files_to_process)
        self.progress_mode_switched = False

        
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
        
        task_thread = threading.Thread(
            target=self.task_runner,
            args=(task_type, files_to_process, processor, lufs, tp, mode, mastering_preset, task_id),
        )
        task_thread.daemon = True
        task_thread.start()
    def task_runner(self, task_type, files, processor, lufs, tp, mode, mastering_preset, task_id):
        was_cancelled = False
        for i, file_path in enumerate(files):
            if self.is_cancelled:
                was_cancelled = True; break
            
            base_name = os.path.basename(file_path)
            self.gui_queue.put(("task", task_id, "status", get_text(f"status_{task_type}_running", file=base_name)))
            self.gui_queue.put(("task", task_id, "info", f"\n--- {get_text(f'status_{task_type}_running', file=base_name)} ---\n"))
            
            log_file = ANALYSIS_LOG_FILE_NAME if task_type == "analyze" else LOG_FILE_NAME
            
            if task_type == "analyze":
                return_code, stderr = processor.analyze(file_path)
            else:
                output_format = self.output_format_var.get()
                codec = CODECS[output_format]
                options = FFMPEG_OPTIONS.get(output_format, [])
                output_ext = next((ext for ext, name in AUDIO_FILE_EXTENSIONS if name == output_format), ".tmp")
                output_file = os.path.splitext(file_path)[0] + "-Normalized" + output_ext
                
                return_code, stderr = processor.normalize(
                    file_path, output_file, lufs, tp, codec, options, mode, output_format, mastering_preset,
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
        self.is_cancelled = True
        if self.current_norm_process and self.current_norm_process.poll() is None:
            self.current_norm_process.terminate()
            if os.name == 'nt':
                try:
                    subprocess.run(['taskkill', '/F', '/T', '/PID', str(self.current_norm_process.pid)], capture_output=True, creationflags=subprocess.CREATE_NO_WINDOW)
                except Exception:
                    pass
            self.update_process_info(get_text("normalization_cancel_process_message"))

    def process_gui_queue(self):
        try:
            while True:
                message = self.gui_queue.get_nowait()
                task = message[0]
                if task == "task":
                    _, msg_task_id, msg_type, data = message
                    if msg_task_id != self.current_task_id:
                        continue

                    if msg_type == "info":
                        self.update_process_info(data)
                    elif msg_type == "status":
                        self.status_bar.config(text=data)
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
                    self.status_bar.config(text=message[1])
                elif task == "progress":
                    self.progressbar.config(value=message[1])
                elif task == "log":
                    if core.app_logger: core.app_logger.log(*message[1])
                elif task == "error": self.task_finished(status="error", message=message[1])
                elif task == "finish": self.task_finished(status=message[1])
                elif task == "toggle_playback_controls":
                    self.toggle_controls(enable=message[1], for_playback=True)
                    self.update_player_button_states()
                elif task == "update_time":
                    current_sec, total_sec = message[1]
                    self.time_label_var.set(f"{format_time(current_sec)} / {format_time(total_sec)}")
                elif task == "playback_finished":
                    self.is_playing = False
                    self.toggle_controls(enable=True)
                    self.update_player_button_states()
                    self.time_label_var.set("00:00:00 / 00:00:00")
        except Empty:
            pass
        except Exception as e:
            self.update_process_info(f"\n[GUI Queue Error]: {str(e)}\n")
        
        self.root.after(100, self.process_gui_queue)

    def task_finished(self, status, message=None):
        self.toggle_controls(enable=True)
        self.progressbar.stop()

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

            self.status_bar.config(text=get_text("status_completed"))
            self.update_process_info(f"\n--- {get_text('status_completed')} ---")
            winsound.MessageBeep(winsound.MB_OK)
        elif status == "cancelled":
             self.progressbar.config(mode='determinate', value=0)
             self.status_bar.config(text=get_text("status_cancelled"))
             self.update_process_info(f"\n--- {get_text('status_cancelled')} ---")
        elif status == "error":
            self.progressbar.config(mode='determinate', value=0)
            self.status_bar.config(text=get_text("status_error"))
            if message: messagebox.showerror(message[0], message[1])
            winsound.MessageBeep(winsound.MB_ICONERROR)

        self.current_norm_process = None
        self.current_task_id = None
        self.active_task_total = 0
        self.progress_mode_switched = False

    def show_about(self):
        if self.about_window is not None and self.about_window.winfo_exists():
            self.about_window.lift()
            self.about_window.focus_set()
            return

        self.about_window = tk.Toplevel(self.root)
        about_window = self.about_window
        
        # Use a fixed size for the About dialog
        about_window.geometry("455x585") 
        about_window.title(get_text("menu_info_about"))
        about_window.configure(bg=self.colors["bg"])
        about_window.transient(self.root)
        about_window.grab_set()

        def on_close_about():
            self.about_window = None
            about_window.destroy()

        about_window.protocol("WM_DELETE_WINDOW", on_close_about)

        about_frame = ttk.LabelFrame(about_window, text=f" {get_text('app_title')} ")
        about_frame.pack(padx=GUI_PADX, pady=GUI_PADY, fill=tk.BOTH, expand=True)
        
        bold_font = ("Helvetica", 9, "bold")
        large_bold_font = ("Helvetica", 11, "bold")

        ttk.Label(about_frame, text=get_text("app_title_long"), font=large_bold_font).pack(pady=(GUI_PADY, 2))

        version_frame = ttk.Frame(about_frame)
        version_frame.pack()
        emoji_font = ("Segoe UI Emoji", 10)
        ttk.Label(version_frame, text=f"{get_text('about_version', version=VERSION)} ", font=bold_font).pack(side=tk.LEFT)
        ttk.Label(version_frame, text=EDITION_NAME, font=emoji_font).pack(side=tk.LEFT)

        ttk.Label(about_frame, text=get_text("about_build_date", build_date=BUILD_DATE)).pack(pady=(0, GUI_PADY))
        
        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=GUI_PADX, pady=GUI_PADY)

        desc_frame = ttk.Frame(about_frame)
        desc_frame.pack(fill='x', padx=GUI_PADX)
        for line in get_text("about_description").splitlines():
            ttk.Label(desc_frame, text=line, justify=tk.LEFT).pack(anchor="w")

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=GUI_PADX, pady=GUI_PADY)

        ttk.Label(about_frame, text=get_text("about_author", author=AUTHOR), font=bold_font).pack(anchor="w", padx=GUI_PADX)
        ttk.Label(about_frame, text=get_text("about_email", email="melcom [@] vodafonemail.de")).pack(anchor="w", padx=GUI_PADX, pady=(0, GUI_PADY))

        for header_key, links in [("about_website_header", [("about_website_1", "https://www.melcom-music.de"), ("about_website_2", "https://scenes.at/melcom")]),
                                  ("about_youtube_header", [("about_youtube_link", "https://youtube.com/@melcom")]),
                                  ("about_bluesky_header", [("about_bluesky_link", "https://melcom-music.bsky.social")])]:
            ttk.Label(about_frame, text=get_text(header_key), font=bold_font).pack(anchor="w", padx=GUI_PADX, pady=(GUI_PADY, 0))
            for text_key, url in links:
                link = ttk.Label(about_frame, text=get_text(text_key), foreground="#4a90e2", cursor="hand2")
                link.pack(anchor="w", padx=GUI_PADX)
                link.bind("<Button-1>", lambda e, link_url=url: webbrowser.open(link_url))

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=GUI_PADX, pady=GUI_PADY)

        ttk.Label(about_frame, text=get_text("about_opensource", year=datetime.datetime.now().year)).pack()
        ttk.Label(about_frame, text=get_text("about_license")).pack()
        ttk.Label(about_frame, text=get_text("about_copyright", year=datetime.datetime.now().year)).pack()

        ttk.Button(about_frame, text=get_text("about_ok_button"), command=on_close_about).pack(pady=GUI_PADY)
        
        center_window(about_window)
        self.root.wait_window(about_window)

    def show_options(self):
        if self.options_window is not None and self.options_window.winfo_exists():
            self.options_window.lift()
            self.options_window.focus_set()
            return

        self.options_window = tk.Toplevel(self.root)
        options_window = self.options_window
        
        # Use a fixed size for the Options dialog
        options_window.geometry("600x320")
        options_window.title(get_text("options_dialog_title"))
        options_window.configure(bg=self.colors["bg"])
        options_window.transient(self.root)
        options_window.grab_set()

        def on_close_options():
            self.options_window = None
            options_window.destroy()

        options_window.protocol("WM_DELETE_WINDOW", on_close_options)

        # Container for side-by-side language and theme selection
        top_row_frame = ttk.Frame(options_window, style="TFrame")
        top_row_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)

        lang_frame = ttk.LabelFrame(top_row_frame, text=f" {get_text('options_language_group')} ")
        lang_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        theme_group_text = get_text("options_theme_group")
        if theme_group_text.startswith("["): theme_group_text = "Theme Settings"
        theme_label_text = get_text("options_theme_label")
        if theme_label_text.startswith("["): theme_label_text = "App Theme:"

        theme_frame = ttk.LabelFrame(top_row_frame, text=f" {theme_group_text} ")
        theme_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(5, 0))
        
        ffmpeg_frame = ttk.LabelFrame(options_window, text=f" {get_text('options_ffmpeg_path_group')} ")
        ffmpeg_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)

        log_frame = ttk.LabelFrame(options_window, text=f" {get_text('options_log_settings_group')} ")
        log_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)

        lang_var = tk.StringVar(value=config.language)
        ttk.Label(lang_frame, text=get_text("options_language_label")).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(lang_frame, textvariable=lang_var, values=LANGUAGE_CODES_LIST, state="readonly", width=12).pack(side=tk.LEFT, padx=5, pady=5)

        theme_var = tk.StringVar(value=config.theme_mode)
        ttk.Label(theme_frame, text=theme_label_text).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(theme_frame, textvariable=theme_var, values=THEME_MODES_LIST, state="readonly", width=18).pack(side=tk.LEFT, padx=5, pady=5)

        ffmpeg_path_var = tk.StringVar(value=config.ffmpeg_path)
        ttk.Entry(ffmpeg_frame, textvariable=ffmpeg_path_var, width=50).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=5, pady=5)
        
        def browse_ffmpeg():
            path = filedialog.askdirectory(title=get_text("options_ffmpeg_path_dialog_title"))
            if path: ffmpeg_path_var.set(path)
        ttk.Button(ffmpeg_frame, text=get_text("options_browse_button"), command=browse_ffmpeg).pack(side=tk.LEFT, padx=5)

        single_log_var = tk.BooleanVar(value=config.single_log_entry_enabled)
        log_size_var = tk.IntVar(value=config.log_file_size_kb)
        
        log_size_entry = ttk.Entry(log_frame, textvariable=log_size_var, width=10)
        
        def toggle_log_size():
            log_size_entry.config(state=tk.DISABLED if single_log_var.get() else tk.NORMAL)

        chk = ttk.Checkbutton(log_frame, text=get_text("options_log_single_entry_check"), variable=single_log_var, command=toggle_log_size)
        chk.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        ttk.Label(log_frame, text=get_text("options_log_size_label")).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        log_size_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        toggle_log_size()

        def save_and_close():
            ffmpeg_path = ffmpeg_path_var.get()
            if not os.path.exists(os.path.join(ffmpeg_path, FFMPEG_EXECUTABLE_NAME)):
                messagebox.showerror(get_text("options_error_invalid_ffmpeg_path_title"), get_text("options_error_invalid_ffmpeg_path_message"), parent=options_window)
                return
            
            config.ffmpeg_path = ffmpeg_path
            config.log_file_size_kb = log_size_var.get()
            config.single_log_entry_enabled = single_log_var.get()
            
            core.reinit_logger()
            
            lang_changed = config.language != lang_var.get()
            config.language = lang_var.get()
            
            theme_changed = config.theme_mode != theme_var.get()
            config.theme_mode = theme_var.get()
            
            config.save_options()
            
            if theme_changed:
                self.setup_styles()
                self.process_info.config(bg=self.colors["info_bg"], fg=self.colors["fg"], relief=self.colors.get("text_relief", "sunken"))
                
            if lang_changed:
                i18n.load_language(config.language)
                self.apply_language()
            elif theme_changed:
                self.apply_language()
            
            self.options_window = None
            options_window.destroy()

        ttk.Button(options_window, text=get_text("options_save_button"), command=save_and_close).pack(pady=GUI_PADY)
        
        center_window(options_window)
        options_window.wait_window(options_window)
