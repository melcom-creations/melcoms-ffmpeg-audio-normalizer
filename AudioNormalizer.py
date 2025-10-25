# -*- coding: utf-8 -*-
"""
AudioNormalizer.py

A graphical user interface for normalizing audio files to a target loudness (LUFS)
and true peak (dBTP) using FFmpeg.

This application allows users to add audio files, select loudness presets or
custom values, choose an output format, and process the files in a batch.
It also includes a simple audio player for previewing files.
"""

# --- STANDARD LIBRARY IMPORTS ---
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import subprocess
import os
import configparser
import webbrowser
import datetime
import threading
import json
import winsound
from queue import Queue
import re

# --- METADATA ---
# Application version and build information.
VERSION = "3.0.0"
EDITION_NAME = "👻 Halloween Edition 🎃"
BUILD_DATE = "2025-10-24"
AUTHOR = "melcom (Andreas Thomas Urban)"

# --- GUI CONSTANTS ---
# Defines padding and sizing for Tkinter widgets for a consistent look and feel.
GUI_PADX = 10
GUI_PADY = 5
GUI_ENTRY_WIDTH_FILE = 58
GUI_ENTRY_WIDTH_LUFS_TP = 10
GUI_COMBOBOX_WIDTH_LUFS_PRESET = 28
GUI_COMBOBOX_WIDTH_TP_PRESET = 30
DIALOG_PADX_OPTIONS = 10
DIALOG_PADY_OPTIONS = 5

# --- FILE & CONFIG CONSTANTS ---
# Defines filenames and extensions used for configuration, logging, and processing.
CONFIG_FILE_NAME = "options.ini"
LOG_FILE_NAME = "normalization.log"
ANALYSIS_LOG_FILE_NAME = "analysis.log"
FFMPEG_EXECUTABLE_NAME = "ffmpeg.exe"
FFPLAY_EXECUTABLE_NAME = "ffplay.exe"
FFPROBE_EXECUTABLE_NAME = "ffprobe.exe"
TEMP_FILE_EXTENSION = ".temp"
# Supported audio file types for input.
AUDIO_FILE_EXTENSIONS = [
    (".wav", "WAV"),
    (".mp3", "MP3"),
    (".flac", "FLAC"),
    (".aac", "AAC"),
    (".ogg", "OGG"),
    (".m4a", "M4A")
]
# Supported audio formats for output.
OUTPUT_FORMATS_LIST = ["WAV", "MP3", "FLAC", "AAC", "OGG"]

# --- CONFIG KEYS ---
# Keys for accessing settings in the options.ini file.
CONFIG_SECTION_SETTINGS = "Settings"
CONFIG_KEY_FFMPEG_PATH = "ffmpeg_path"
CONFIG_KEY_LOG_FILE_SIZE = "log_file_size_kb"
CONFIG_KEY_SINGLE_LOG_ENTRY = "single_log_entry_enabled"
CONFIG_KEY_LANGUAGE = "language"

# --- LANGUAGE CONSTANTS ---
# Defines constants for internationalization (i18n).
LANGUAGE_CODES_LIST = ["en_US", "de_DE", "pl_PL"]
DEFAULT_LANGUAGE_CODE = "en_US"
LANG_FOLDER_NAME = "lang"
LANG_FILE_EXTENSION = ".json"

# --- FFMPEG CONSTANTS ---
# Maps output formats to their respective FFmpeg codecs and specific options.
CODECS = {
    "WAV": "pcm_f32le",
    "MP3": "libmp3lame",
    "FLAC": "flac",
    "AAC": "aac",
    "OGG": "libvorbis"
}
# Additional FFmpeg options for specific codecs to ensure quality.
FFMPEG_OPTIONS = {
    "MP3": ["-b:a", "320k"],
    "AAC": ["-b:a", "256k"],
    "OGG": ["-b:a", "500k"]
}

# --- GLOBAL VARIABLES ---
# Global state variables used throughout the application.
language_data = {}
current_language = DEFAULT_LANGUAGE_CODE
config = None
normalization_process = None
playback_process = None
gui_queue = Queue()

# --- PRESET DEFINITIONS ---
# Dictionaries populated by the load_language function.
LUFS_PRESETS = {}
TRUE_PEAK_PRESETS = {}
LUFS_PRESET_NAMES = []
TRUE_PEAK_PRESET_NAMES = []


# --- CORE CLASSES ---

class Config:
    """Manages application settings, loading from and saving to an INI file."""
    
    def __init__(self):
        """Initializes the configuration object by loading settings."""
        self.ffmpeg_path = ""
        self.log_file_size_kb = 1024
        self.single_log_entry_enabled = True
        self.load_options()

    def load_options(self):
        """Reads settings from options.ini or sets defaults if the file is missing."""
        parser = configparser.ConfigParser()
        if os.path.exists(CONFIG_FILE_NAME):
            parser.read(CONFIG_FILE_NAME, encoding='utf-8')
            settings = parser[CONFIG_SECTION_SETTINGS] if CONFIG_SECTION_SETTINGS in parser else {}
            self.ffmpeg_path = settings.get(CONFIG_KEY_FFMPEG_PATH, self._find_ffmpeg_path())
            self.log_file_size_kb = settings.getint(CONFIG_KEY_LOG_FILE_SIZE, 1024)
            self.single_log_entry_enabled = settings.getboolean(CONFIG_KEY_SINGLE_LOG_ENTRY, True)
            global current_language
            current_language = settings.get(CONFIG_KEY_LANGUAGE, DEFAULT_LANGUAGE_CODE)
        else:
            self.ffmpeg_path = self._find_ffmpeg_path()
        self.ensure_log_size_valid()

    def _find_ffmpeg_path(self):
        """Attempts to locate the FFmpeg executable in the script's directory."""
        program_path = os.path.dirname(os.path.abspath(__file__))
        if os.path.exists(os.path.join(program_path, FFMPEG_EXECUTABLE_NAME)):
            return program_path
        return ""

    def save_options(self):
        """Writes the current settings to the options.ini file."""
        parser = configparser.ConfigParser()
        parser[CONFIG_SECTION_SETTINGS] = {
            CONFIG_KEY_FFMPEG_PATH: self.ffmpeg_path,
            CONFIG_KEY_LOG_FILE_SIZE: self.log_file_size_kb,
            CONFIG_KEY_SINGLE_LOG_ENTRY: str(self.single_log_entry_enabled),
            CONFIG_KEY_LANGUAGE: current_language
        }
        with open(CONFIG_FILE_NAME, "w", encoding='utf-8') as f:
            parser.write(f)

    def ensure_log_size_valid(self):
        """Ensures the log file size is a positive integer, defaulting if not."""
        if not isinstance(self.log_file_size_kb, int) or self.log_file_size_kb <= 0:
            self.log_file_size_kb = 1024

class FFMpegProcessor:
    """Handles all interactions with FFmpeg for analysis and normalization."""
    
    def __init__(self, ffmpeg_path, update_callback):
        """
        Initializes the processor.
        
        Args:
            ffmpeg_path (str): The directory containing the FFmpeg executables.
            update_callback (function): A function to call with real-time FFmpeg output.
        """
        self.ffmpeg_path = os.path.join(ffmpeg_path, FFMPEG_EXECUTABLE_NAME)
        self.update_callback = update_callback

    def _run_process(self, command):
        """
        Executes an FFmpeg command as a subprocess and captures its stderr output.
        
        Args:
            command (list): The command and its arguments to execute.
        
        Returns:
            A tuple containing the process return code and the full stderr output.
        """
        global normalization_process
        try:
            # CREATE_NO_WINDOW prevents a console from appearing on Windows.
            normalization_process = subprocess.Popen(
                command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            full_stderr = ""
            for line in iter(normalization_process.stderr.readline, ''):
                full_stderr += line
                self.update_callback(line)
            
            return_code = normalization_process.wait()
            return return_code, full_stderr
        except FileNotFoundError:
            return -1, "ffmpeg_not_found"
        except Exception as e:
            return -1, str(e)

    def analyze(self, file_path):
        """
        Analyzes an audio file for loudness information using FFmpeg's loudnorm filter.
        """
        command = [self.ffmpeg_path, "-i", file_path, "-af", "loudnorm=print_format=json", "-f", "null", "-"]
        return self._run_process(command)

    def normalize(self, input_file, output_file, lufs, tp, codec, options):
        """
        Normalizes an audio file to the specified LUFS and True Peak values.
        
        It writes to a temporary file first and renames it on success to avoid
        corrupting the output file if the process is interrupted.
        """
        temp_file = os.path.splitext(output_file)[0] + TEMP_FILE_EXTENSION + os.path.splitext(output_file)[1]
        command = [
            self.ffmpeg_path, "-i", input_file,
            "-af", f"loudnorm=I={lufs}:TP={tp}:print_format=summary",
            "-ar", "48000", "-ac", "2", "-c:a", codec
        ]
        if options: command.extend(options)
        command.extend(["-y", temp_file])
        
        return_code, stderr = self._run_process(command)

        if return_code == 0:
            try:
                if os.path.exists(output_file): os.remove(output_file)
                os.rename(temp_file, output_file)
            except OSError as e:
                return -1, str(e)
        
        if os.path.exists(temp_file):
            try: os.remove(temp_file)
            except OSError: pass
             
        return return_code, stderr

# --- HELPER FUNCTIONS ---

def load_language(language_code):
    """
    Loads language strings from a JSON file based on the provided language code.
    Falls back to the default language if the specified file is not found.
    """
    global language_data, LUFS_PRESETS, TRUE_PEAK_PRESETS, LUFS_PRESET_NAMES, TRUE_PEAK_PRESET_NAMES
    try:
        path = os.path.join(LANG_FOLDER_NAME, f"{language_code}{LANG_FILE_EXTENSION}")
        with open(path, "r", encoding="utf-8") as f:
            language_data = json.load(f)
        LUFS_PRESETS = language_data.get("lufs_presets", {})
        TRUE_PEAK_PRESETS = language_data.get("true_peak_presets", {})
        LUFS_PRESET_NAMES = list(LUFS_PRESETS.keys())
        TRUE_PEAK_PRESET_NAMES = list(TRUE_PEAK_PRESETS.keys())
    except (FileNotFoundError, json.JSONDecodeError):
        if language_code != DEFAULT_LANGUAGE_CODE:
            load_language(DEFAULT_LANGUAGE_CODE)

def get_text(key, **kwargs):
    """
    Retrieves a string from the loaded language data by its key.
    Supports simple string formatting.
    """
    return language_data.get(key, f"[{key}]").format(**kwargs)

def append_to_log(log_file, text, mode):
    """
    Appends text to a specified log file, trimming it if it exceeds the size limit.
    """
    try:
        if mode == "a":
            limit_bytes = config.log_file_size_kb * 1024
            if not config.single_log_entry_enabled and os.path.exists(log_file) and os.path.getsize(log_file) > limit_bytes:
                with open(log_file, "r", encoding="utf-8") as f: lines = f.readlines()
                with open(log_file, "w", encoding="utf-8") as f: f.writelines(lines[len(lines)//2:])
        with open(log_file, mode, encoding="utf-8") as f:
            f.write(text)
    except Exception as e:
        print(f"Error writing to log {log_file}: {e}")

def center_window(window):
    """Centers a Tkinter window on the screen."""
    window.update_idletasks()
    width = window.winfo_width()
    height = window.winfo_height()
    x = (window.winfo_screenwidth() // 2) - (width // 2)
    y = (window.winfo_screenheight() // 2) - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')

def format_time(seconds):
    """Formats a duration in seconds into an HH:MM:SS string."""
    if seconds is None: return "00:00:00"
    try:
        secs = float(seconds)
        m, s = divmod(secs, 60)
        h, m = divmod(m, 60)
        return f"{int(h):02d}:{int(m):02d}:{int(s):02d}"
    except (ValueError, TypeError):
        return "00:00:00"

# --- GUI APPLICATION CLASS ---

class AudioNormalizerApp:
    """The main application class that builds and manages the GUI."""
    
    def __init__(self, root):
        """Initializes the main application GUI."""
        self.root = root
        self.file_list = []
        self.is_cancelled = False
        
        # --- Player State ---
        self.is_playing = False
        self.playback_thread = None
        self.current_track_index = -1
        self.total_duration_sec = 0
        self.ffprobe_checked = False
        
        self.setup_styles()
        self.create_widgets()
        self.apply_language()
        self.process_gui_queue()
        center_window(self.root)

    def setup_styles(self):
        """Configures the visual style and color scheme for ttk widgets."""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        self.colors = {
            "bg": "#e0e0e0",
            "fg": "#424242",
            "info_bg": "#d3d3d3",
            "separator": "#cccccc",
            "entry_bg": "#ffffff",
            "disabled_fg": "#a3a3a3",
            "error_bg": "#ffdddd"
        }

        self.root.config(bg=self.colors["bg"])
        
        self.root.option_add("*TCombobox*Listbox*Background", self.colors["entry_bg"])
        self.root.option_add("*TCombobox*Listbox*Foreground", self.colors["fg"])

        self.style.configure(".", background=self.colors["bg"], foreground=self.colors["fg"])
        self.style.configure("TFrame", background=self.colors["bg"])
        self.style.configure("TLabel", background=self.colors["bg"], foreground=self.colors["fg"])
        self.style.configure("TCheckbutton", background=self.colors["bg"], foreground=self.colors["fg"])
        self.style.configure("TLabelframe", background=self.colors["bg"], bordercolor=self.colors["separator"])
        self.style.configure("TLabelframe.Label", background=self.colors["bg"], foreground=self.colors["fg"])
        self.style.configure("TButton", background="#f0f0f0", foreground=self.colors["fg"])
        self.style.map("TButton", background=[('active', '#e0e0e0')])
        self.style.configure("TEntry", fieldbackground=self.colors["entry_bg"], foreground=self.colors["fg"])
        # A specific style for entry widgets with invalid input.
        self.style.configure("Error.TEntry", fieldbackground=self.colors["error_bg"], foreground=self.colors["fg"])
        
        self.style.configure("TCombobox", fieldbackground=self.colors["entry_bg"], foreground=self.colors["fg"])
        self.style.map("TCombobox",
            fieldbackground=[('disabled', self.colors["bg"]), ('readonly', self.colors["entry_bg"])],
            foreground=[('disabled', self.colors["disabled_fg"]), ('readonly', self.colors["fg"])]
        )
        
        self.style.configure("Horizontal.TSeparator", background=self.colors["separator"])

    def create_widgets(self):
        """Creates and arranges all the widgets in the main window."""
        self.root.title(f"{get_text('app_title')} v{VERSION}")
        self.root.geometry("900x680")
        self.root.minsize(900, 680)
        
        self.main_frame = ttk.Frame(self.root, padding=GUI_PADY, style="TFrame")
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Top Frame (File List and Settings) ---
        top_frame = ttk.Frame(self.main_frame, style="TFrame")
        top_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        
        # --- File Selection Frame ---
        file_frame = ttk.LabelFrame(top_frame, text=get_text("file_selection_group"), style="TLabelframe")
        file_frame.grid(row=0, column=0, sticky="nsew", padx=(0, GUI_PADX))
        file_frame.columnconfigure(0, weight=1)
        file_frame.rowconfigure(0, weight=1)

        self.file_listbox = ttk.Treeview(file_frame, columns=("filename",), show="headings", selectmode="extended")
        self.file_listbox.heading("filename", text=get_text("file_list_header_filename"))
        self.file_listbox.column("filename", anchor="w")
        self.file_listbox.grid(row=0, column=0, columnspan=2, sticky="nsew", pady=GUI_PADY)
        self.file_listbox.bind("<Delete>", self.remove_selected_files)
        self.file_listbox.bind("<<TreeviewSelect>>", self.update_player_button_states)
        
        list_scrollbar = ttk.Scrollbar(file_frame, orient="vertical", command=self.file_listbox.yview)
        list_scrollbar.grid(row=0, column=2, sticky="ns")
        self.file_listbox.config(yscrollcommand=list_scrollbar.set)
        
        file_button_frame = ttk.Frame(file_frame, style="TFrame")
        file_button_frame.grid(row=1, column=0, columnspan=2, sticky="ew")
        
        self.add_files_button = ttk.Button(file_button_frame, text=get_text("add_files_button"), command=self.add_files)
        self.add_folder_button = ttk.Button(file_button_frame, text=get_text("add_folder_button"), command=self.add_folder)
        self.remove_files_button = ttk.Button(file_button_frame, text=get_text("remove_files_button"), command=self.remove_selected_files)
        
        self.add_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.add_folder_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.remove_files_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        ttk.Separator(file_frame, orient='horizontal').grid(row=2, column=0, columnspan=3, sticky='ew', pady=5)
        
        # --- Audio Player Frame ---
        player_frame = ttk.Frame(file_frame, style="TFrame")
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
        
        # --- Settings Frame (Right side) ---
        settings_frame = ttk.Frame(top_frame, style="TFrame")
        settings_frame.grid(row=0, column=1, sticky="nsew")
        settings_frame.columnconfigure(0, weight=1)

        # --- Loudness Settings ---
        loudness_frame = ttk.LabelFrame(settings_frame, text=get_text("loudness_settings_group"), style="TLabelframe")
        loudness_frame.pack(fill=tk.X, expand=True, pady=GUI_PADY)
        
        self.lufs_preset_var = tk.StringVar()
        self.true_peak_preset_var = tk.StringVar()
        
        ttk.Label(loudness_frame, text=get_text("lufs_preset_label"), style="TLabel").grid(row=0, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.lufs_combobox = ttk.Combobox(loudness_frame, textvariable=self.lufs_preset_var, state="readonly", width=GUI_COMBOBOX_WIDTH_LUFS_PRESET)
        self.lufs_combobox.grid(row=0, column=1, sticky="ew", padx=GUI_PADX, pady=GUI_PADY)
        self.lufs_combobox.bind("<<ComboboxSelected>>", self.update_entry_states)

        ttk.Label(loudness_frame, text=get_text("true_peak_preset_label"), style="TLabel").grid(row=1, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.tp_combobox = ttk.Combobox(loudness_frame, textvariable=self.true_peak_preset_var, state="readonly", width=GUI_COMBOBOX_WIDTH_TP_PRESET)
        self.tp_combobox.grid(row=1, column=1, sticky="ew", padx=GUI_PADX, pady=GUI_PADY)
        self.tp_combobox.bind("<<ComboboxSelected>>", self.update_entry_states)

        self.lufs_entry_var = tk.StringVar()
        self.tp_entry_var = tk.StringVar()

        lufs_vcmd = (self.root.register(lambda P: self._validate_entry(self.lufs_entry, P, -70.0, 0.0)), '%P')
        tp_vcmd = (self.root.register(lambda P: self._validate_entry(self.tp_entry, P, -9.0, 0.0)), '%P')
        
        self.lufs_label = ttk.Label(loudness_frame, text=get_text("target_lufs_label_custom_short"), style="TLabel")
        self.lufs_entry = ttk.Entry(loudness_frame, textvariable=self.lufs_entry_var, width=GUI_ENTRY_WIDTH_LUFS_TP, validate="focusout", validatecommand=lufs_vcmd)
        self.tp_label = ttk.Label(loudness_frame, text=get_text("true_peak_label"), style="TLabel")
        self.tp_entry = ttk.Entry(loudness_frame, textvariable=self.tp_entry_var, width=GUI_ENTRY_WIDTH_LUFS_TP, validate="focusout", validatecommand=tp_vcmd)

        self.lufs_label.grid(row=0, column=2, padx=(GUI_PADX, 2), pady=GUI_PADY)
        self.lufs_entry.grid(row=0, column=3, padx=(0, GUI_PADX), pady=GUI_PADY)
        self.tp_label.grid(row=1, column=2, padx=(GUI_PADX, 2), pady=GUI_PADY)
        self.tp_entry.grid(row=1, column=3, padx=(0, GUI_PADX), pady=GUI_PADY)
        
        # --- Output Format Settings ---
        output_frame = ttk.LabelFrame(settings_frame, text=get_text("output_format_group"), style="TLabelframe")
        output_frame.pack(fill=tk.X, expand=True, pady=GUI_PADY)
        
        self.output_format_var = tk.StringVar()
        ttk.Label(output_frame, text=get_text("output_format_file_format_label"), style="TLabel").grid(row=0, column=0, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.output_combobox = ttk.Combobox(output_frame, textvariable=self.output_format_var, values=OUTPUT_FORMATS_LIST, state="readonly")
        self.output_combobox.grid(row=0, column=1, sticky="w", padx=GUI_PADX, pady=GUI_PADY)
        self.output_combobox.set(OUTPUT_FORMATS_LIST[0])
        self.output_combobox.bind("<<ComboboxSelected>>", self.update_output_format_info)
        
        self.output_info_frame = ttk.Frame(output_frame, style="TFrame")
        self.output_info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=GUI_PADX, pady=(GUI_PADY, 0))
        self.output_info_frame.columnconfigure(0, weight=1)
        
        self.output_specs_label = ttk.Label(self.output_info_frame, text="", style="TLabel", justify=tk.LEFT)
        self.output_specs_label.pack(fill='x')
        
        ttk.Separator(self.output_info_frame, orient='horizontal').pack(fill='x', pady=3)
        
        self.output_desc_label = ttk.Label(self.output_info_frame, text="", style="TLabel", wraplength=350, justify=tk.LEFT)
        self.output_desc_label.pack(fill='x')

        # --- Bottom Frame (Process Info and Controls) ---
        bottom_frame = ttk.Frame(self.main_frame, style="TFrame")
        bottom_frame.pack(fill=tk.BOTH, expand=True, padx=GUI_PADX, pady=GUI_PADY)
        bottom_frame.rowconfigure(0, weight=1)
        bottom_frame.columnconfigure(0, weight=1)
        
        info_frame = ttk.LabelFrame(bottom_frame, text=get_text("process_information_group"), style="TLabelframe")
        info_frame.grid(row=0, column=0, sticky="nsew", pady=GUI_PADY)
        info_frame.rowconfigure(0, weight=1)
        info_frame.columnconfigure(0, weight=1)

        self.process_info = tk.Text(info_frame, wrap=tk.WORD, state=tk.DISABLED, height=10, bg=self.colors["info_bg"], fg=self.colors["fg"], highlightthickness=0, borderwidth=1)
        self.process_info.grid(row=0, column=0, sticky="nsew")
        info_scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.process_info.yview)
        info_scrollbar.grid(row=0, column=1, sticky="ns")
        self.process_info.config(yscrollcommand=info_scrollbar.set)
        
        control_frame = ttk.Frame(bottom_frame, style="TFrame")
        control_frame.grid(row=1, column=0, sticky="ew", pady=GUI_PADY)
        
        self.analyze_button = ttk.Button(control_frame, text=get_text("analyze_audio_button"), command=lambda: self.start_task("analyze"))
        self.start_button = ttk.Button(control_frame, text=get_text("start_normalization_button"), command=lambda: self.start_task("normalize"))
        self.cancel_button = ttk.Button(control_frame, text=get_text("cancel_normalization_button"), command=self.cancel_task, state=tk.DISABLED)
        
        self.analyze_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.start_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        self.cancel_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        
        self.status_bar = ttk.Label(self.root, text=get_text("status_ready"), anchor=tk.W, style="TLabel")
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=GUI_PADX)
        
        self.progressbar = ttk.Progressbar(self.root, mode='determinate')
        self.progressbar.pack(side=tk.BOTTOM, fill=tk.X, padx=GUI_PADX, pady=(0, GUI_PADY))

        self.create_menu()
        self.update_output_format_info()
        self.update_player_button_states()

    def on_closing(self):
        """Custom close handler to ensure child processes are terminated."""
        self.stop_audio()
        self.cancel_task()
        self.root.destroy()

    def create_menu(self):
        """Creates the main application menu bar."""
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
        """Reloads all UI text elements with strings from the current language."""
        load_language(current_language)
        self.root.title(f"{get_text('app_title')} v{VERSION}")
        self.menubar.destroy()
        self.create_menu()
        
        for frame, text_key in [(self.main_frame.winfo_children()[0].winfo_children()[0], "file_selection_group"),
                                (self.main_frame.winfo_children()[0].winfo_children()[1].winfo_children()[0], "loudness_settings_group"),
                                (self.main_frame.winfo_children()[0].winfo_children()[1].winfo_children()[1], "output_format_group"),
                                (self.main_frame.winfo_children()[1].winfo_children()[0], "process_information_group")]:
            frame.config(text=get_text(text_key))
            
        self.add_files_button.config(text=get_text("add_files_button"))
        self.add_folder_button.config(text=get_text("add_folder_button"))
        self.remove_files_button.config(text=get_text("remove_files_button"))
        self.lufs_combobox.config(values=LUFS_PRESET_NAMES)
        self.lufs_combobox.set(LUFS_PRESET_NAMES[0] if LUFS_PRESET_NAMES else "")
        self.tp_combobox.config(values=TRUE_PEAK_PRESET_NAMES)
        self.tp_combobox.set(TRUE_PEAK_PRESET_NAMES[0] if TRUE_PEAK_PRESET_NAMES else "")
        self.analyze_button.config(text=get_text("analyze_audio_button"))
        self.start_button.config(text=get_text("start_normalization_button"))
        self.cancel_button.config(text=get_text("cancel_normalization_button"))
        self.status_bar.config(text=get_text("status_ready"))
        
        self.file_listbox.heading("filename", text=get_text("file_list_header_filename"))
        self.play_button.config(text="▶")
        self.stop_button.config(text="■")
        self.prev_button.config(text="«")
        self.next_button.config(text="»")

        self.update_entry_states()
        self.update_output_format_info()

    def add_files(self):
        """Opens a file dialog to add one or more audio files to the list."""
        filetypes = [(get_text("file_dialog_audio_files"), " ".join([ext for ext, _ in AUDIO_FILE_EXTENSIONS]))]
        files = filedialog.askopenfilenames(title=get_text("file_dialog_title"), filetypes=filetypes)
        for f in files:
            if f not in self.file_list:
                self.file_list.append(f)
                self.file_listbox.insert("", tk.END, values=(os.path.basename(f),))
        self.update_status_bar()
        self.update_player_button_states()

    def add_folder(self):
        """Opens a folder dialog and recursively adds all supported audio files."""
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
        """Removes all selected files from the list."""
        selected_items = self.file_listbox.selection()
        if not selected_items:
            return
            
        # Sort indices in reverse to avoid index shifting issues during deletion.
        indices_to_delete = sorted([self.file_listbox.index(i) for i in selected_items], reverse=True)
        
        for index in indices_to_delete:
            del self.file_list[index]
            
        for item in selected_items:
            self.file_listbox.delete(item)
            
        self.update_status_bar()
        self.update_player_button_states()

    def _validate_entry(self, widget, new_value, min_val, max_val):
        """
        Validates the input of a numerical entry field on focus out.
        Changes the widget's style to 'Error.TEntry' if the value is invalid.
        """
        if str(widget.cget('state')) == 'disabled':
            widget.config(style="TEntry")
            return True
        try:
            val = float(new_value)
            if min_val <= val <= max_val:
                widget.config(style="TEntry")
            else:
                widget.config(style="Error.TEntry")
        except (ValueError, TypeError):
            widget.config(style="Error.TEntry")
        return True

    def update_entry_states(self, event=None):
        """
        Enables or disables the custom LUFS/TP entry fields based on whether
        the "Custom" preset is selected.
        """
        is_lufs_custom = self.lufs_preset_var.get() == get_text("preset_custom")
        is_tp_custom = self.true_peak_preset_var.get() == get_text("preset_custom")
        
        self.lufs_entry.config(state=tk.NORMAL if is_lufs_custom else tk.DISABLED)
        self.lufs_label.config(state=tk.NORMAL if is_lufs_custom else tk.DISABLED)
        self.tp_entry.config(state=tk.NORMAL if is_tp_custom else tk.DISABLED)
        self.tp_label.config(state=tk.NORMAL if is_tp_custom else tk.DISABLED)

        self.lufs_entry.config(style="TEntry")
        self.tp_entry.config(style="TEntry")

        if not is_lufs_custom: self.lufs_entry_var.set(LUFS_PRESETS.get(self.lufs_preset_var.get(), ""))
        if not is_tp_custom: self.tp_entry_var.set(TRUE_PEAK_PRESETS.get(self.true_peak_preset_var.get(), ""))

    def update_status_bar(self):
        """Updates the status bar text to show the number of files in the list."""
        self.status_bar.config(text=get_text("status_files_selected", count=len(self.file_list)))

    def update_process_info(self, message):
        """Appends a message to the process information text box."""
        self.process_info.config(state=tk.NORMAL)
        self.process_info.insert(tk.END, message)
        self.process_info.see(tk.END)
        self.process_info.config(state=tk.DISABLED)

    def update_output_format_info(self, event=None):
        """Displays technical details about the selected output format."""
        selected_format = self.output_format_var.get()
        details = language_data.get("output_format_details", {}).get(selected_format, None)
        if details:
            self.output_specs_label.config(text=details['specs'])
            self.output_desc_label.config(text=details['description'])
            self.output_info_frame.grid()
        else:
            self.output_specs_label.config(text="")
            self.output_desc_label.config(text="")
            self.output_info_frame.grid_remove()

    def toggle_controls(self, enable=True, for_playback=False):
        """
        Enables or disables main UI controls to prevent user interaction
        during a running process.
        """
        state = tk.NORMAL if enable else "disabled"
        readonly_state = "readonly" if enable else "disabled"
        
        self.add_files_button.config(state=state)
        self.add_folder_button.config(state=state)
        self.remove_files_button.config(state=state)
        self.analyze_button.config(state=state)
        self.start_button.config(state=state)
        for combo in [self.lufs_combobox, self.tp_combobox, self.output_combobox]:
            combo.config(state=readonly_state)
        
        if not for_playback:
            self.cancel_button.config(state="normal" if not enable else "disabled")
        
        if enable: self.update_entry_states()

    def update_player_button_states(self, event=None):
        """Updates the state of the audio player buttons based on context."""
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
        """Plays the currently selected audio file."""
        if self.is_playing or not self.file_listbox.selection():
            return
        
        selected_item = self.file_listbox.selection()[0]
        self.current_track_index = self.file_listbox.index(selected_item)
        self._start_playback(self.current_track_index)
        
    def stop_audio(self):
        """Stops the currently playing audio."""
        global playback_process
        self.is_playing = False
        if playback_process and playback_process.poll() is None:
            playback_process.terminate()

        # --- RACE CONDITION FIX ---
        # Immediately update the UI after stopping. This ensures the player
        # controls are responsive and correctly reflect the "stopped" state
        # without waiting for the worker thread to finish.
        self.update_player_button_states()
        self.time_label_var.set("00:00:00 / 00:00:00")
        # --- END FIX ---

    def play_next(self):
        """Plays the next track in the list."""
        if not self.file_list: return
        next_index = (self.current_track_index + 1) % len(self.file_list)
        self._start_playback(next_index)

    def play_previous(self):
        """Plays the previous track in the list."""
        if not self.file_list: return
        prev_index = (self.current_track_index - 1 + len(self.file_list)) % len(self.file_list)
        self._start_playback(prev_index)

    def _start_playback(self, track_index):
        """Handles the logic of starting a new playback thread."""
        if self.is_playing:
            self.stop_audio()

        # --- RACE CONDITION FIX ---
        # Immediately disable all player controls to prevent rapid, successive
        # clicks from starting multiple playback threads. This acts as an
        # atomic lock on the UI. The buttons will be correctly updated later
        # by the worker thread via the GUI queue.
        self.play_button.config(state='disabled')
        self.stop_button.config(state='disabled')
        self.prev_button.config(state='disabled')
        self.next_button.config(state='disabled')
        # --- END FIX ---

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
        """
        Worker thread function that handles audio playback using ffprobe and ffplay.
        Communicates with the GUI thread via the `gui_queue`.
        """
        global playback_process
        gui_queue.put(("toggle_playback_controls", False))
        
        ffprobe_path = os.path.join(config.ffmpeg_path, FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path):
            if not self.ffprobe_checked:
                gui_queue.put(("error", (get_text("error_ffprobe_not_found_title"), get_text("error_ffprobe_not_found_message"))))
                self.ffprobe_checked = True
            self.total_duration_sec = 0
        else:
            try:
                command = [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
                result = subprocess.run(command, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
                self.total_duration_sec = float(result.stdout.strip())
            except Exception:
                self.total_duration_sec = 0
        
        gui_queue.put(("update_time", (0, self.total_duration_sec)))
        
        ffplay_path = os.path.join(config.ffmpeg_path, FFPLAY_EXECUTABLE_NAME)
        if not os.path.exists(ffplay_path):
             gui_queue.put(("error", (get_text("play_error_ffplay_not_found_title"), get_text("play_error_ffplay_not_found_message"))))
             gui_queue.put(("playback_finished", None))
             return
             
        try:
            command = [ffplay_path, "-nodisp", "-autoexit", "-loglevel", "info", filepath]
            playback_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='utf-8')
            
            for line in iter(playback_process.stderr.readline, ''):
                if not self.is_playing: break
                
                match = re.search(r'^\s*([0-9]+\.[0-9]+)', line)
                if match:
                    current_time_sec = float(match.group(1))
                    gui_queue.put(("update_time", (current_time_sec, self.total_duration_sec)))
            
            playback_process.wait()
        except Exception:
            pass
        
        gui_queue.put(("playback_finished", None))

    def start_task(self, task_type):
        """
        Starts an analysis or normalization task after performing validation checks.
        """
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
        self.progressbar.config(value=0, maximum=len(files_to_process))
        
        log_file = ANALYSIS_LOG_FILE_NAME if task_type == "analyze" else LOG_FILE_NAME
        if config.single_log_entry_enabled:
            with open(log_file, "w", encoding='utf-8') as f:
                f.write(f"--- {datetime.datetime.now()} | {VERSION} | Starting {task_type} batch ---\n")

        processor = FFMpegProcessor(config.ffmpeg_path, lambda msg: gui_queue.put(("info", msg)))
        task_thread = threading.Thread(target=self.task_runner, args=(task_type, files_to_process, processor, lufs, tp))
        task_thread.daemon = True
        task_thread.start()

    def task_runner(self, task_type, files, processor, lufs, tp):
        """
        Worker thread function that iterates through files and processes them.
        """
        was_cancelled = False
        for i, file_path in enumerate(files):
            if self.is_cancelled:
                was_cancelled = True; break
            
            base_name = os.path.basename(file_path)
            gui_queue.put(("status", get_text(f"status_{task_type}_running", file=base_name)))
            gui_queue.put(("info", f"\n--- {get_text(f'status_{task_type}_running', file=base_name)} ---\n"))
            
            log_file = ANALYSIS_LOG_FILE_NAME if task_type == "analyze" else LOG_FILE_NAME
            
            if task_type == "analyze":
                return_code, stderr = processor.analyze(file_path)
            else:
                output_format = self.output_format_var.get()
                codec = CODECS[output_format]
                options = FFMPEG_OPTIONS.get(output_format, [])
                output_ext = next((ext for ext, name in AUDIO_FILE_EXTENSIONS if name == output_format), ".tmp")
                output_file = os.path.splitext(file_path)[0] + "-Normalized" + output_ext
                return_code, stderr = processor.normalize(file_path, output_file, lufs, tp, codec, options)
            
            log_content = f"\n--- File: {file_path} ---\n{stderr}\n"
            gui_queue.put(("log", (log_file, log_content, "a")))

            if self.is_cancelled:
                was_cancelled = True; break
                
            if return_code != 0:
                error_msg = stderr if "ffmpeg_not_found" not in stderr else get_text("options_error_ffmpeg_executable_message")
                error_title = get_text(f"{task_type}_ffmpeg_error_title") if "ffmpeg_not_found" not in stderr else get_text("options_error_ffmpeg_executable_title")
                gui_queue.put(("error", (error_title, error_msg)))
                return

            gui_queue.put(("progress", i + 1))
        
        gui_queue.put(("finish", "cancelled" if was_cancelled else "completed"))

    def cancel_task(self):
        """Sets the cancellation flag and terminates the running FFmpeg process."""
        self.is_cancelled = True
        if normalization_process and normalization_process.poll() is None:
            normalization_process.terminate()
            self.update_process_info(get_text("normalization_cancel_process_message"))

    def process_gui_queue(self):
        """
        Periodically checks the GUI queue for messages from worker threads
        and updates the GUI accordingly.
        """
        try:
            while True:
                task, data = gui_queue.get_nowait()
                if task == "info": self.update_process_info(data)
                elif task == "status": self.status_bar.config(text=data)
                elif task == "progress": self.progressbar.config(value=data)
                elif task == "log": append_to_log(*data)
                elif task == "error": self.task_finished(status="error", message=data)
                elif task == "finish": self.task_finished(status=data)
                elif task == "toggle_playback_controls":
                    self.toggle_controls(enable=data, for_playback=True)
                    self.update_player_button_states()
                elif task == "update_time":
                    current_sec, total_sec = data
                    self.time_label_var.set(f"{format_time(current_sec)} / {format_time(total_sec)}")
                elif task == "playback_finished":
                    self.is_playing = False
                    self.toggle_controls(enable=True)
                    self.update_player_button_states()
                    self.time_label_var.set("00:00:00 / 00:00:00")
        except Exception:
            pass
        
        self.root.after(100, self.process_gui_queue)

    def task_finished(self, status, message=None):
        """
        Handles the completion, cancellation, or error of a task.
        """
        self.toggle_controls(enable=True)
        self.progressbar.config(value=0)
        global normalization_process
        normalization_process = None

        if status == "completed":
            self.status_bar.config(text=get_text("status_completed"))
            self.update_process_info(f"\n--- {get_text('status_completed')} ---")
            winsound.MessageBeep(winsound.MB_OK)
        elif status == "cancelled":
             self.status_bar.config(text=get_text("status_cancelled"))
             self.update_process_info(f"\n--- {get_text('status_cancelled')} ---")
        elif status == "error":
            self.status_bar.config(text=get_text("status_error"))
            if message: messagebox.showerror(message[0], message[1])
            winsound.MessageBeep(winsound.MB_ICONERROR)

    def show_about(self):
        """Displays the 'About' window with application information."""
        about_window = tk.Toplevel(self.root)
        about_window.geometry("455x585") 
        about_window.title(get_text("menu_info_about"))
        about_window.configure(bg=self.colors["bg"])
        about_window.transient(self.root)
        about_window.grab_set()

        about_frame = tk.LabelFrame(about_window, text=f" {get_text('app_title')} ", bg=self.colors["bg"], fg=self.colors["fg"], relief='solid', borderwidth=1)
        about_frame.pack(padx=GUI_PADX, pady=GUI_PADY, fill=tk.BOTH, expand=True)
        
        bold_font = ("Helvetica", 9, "bold")
        large_bold_font = ("Helvetica", 11, "bold")

        tk.Label(about_frame, text=get_text("app_title_long"), font=large_bold_font, bg=self.colors["bg"], fg=self.colors["fg"]).pack(pady=(GUI_PADY, 2))

        # Display version with emojis by splitting the label into parts. This is
        # necessary because standard fonts do not render color emojis correctly.
        version_frame = tk.Frame(about_frame, bg=self.colors["bg"])
        version_frame.pack()
        emoji_font = ("Segoe UI Emoji", 10)
        tk.Label(version_frame, text=f"{get_text('about_version', version=VERSION)} ", font=bold_font, bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT)
        tk.Label(version_frame, text=EDITION_NAME, font=emoji_font, bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT)

        tk.Label(about_frame, text=get_text("about_build_date", build_date=BUILD_DATE), bg=self.colors["bg"], fg=self.colors["fg"]).pack(pady=(0, GUI_PADY))
        
        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=GUI_PADX, pady=GUI_PADY)

        desc_frame = tk.Frame(about_frame, bg=self.colors["bg"])
        desc_frame.pack(fill='x', padx=GUI_PADX)
        for line in get_text("about_description").splitlines():
            tk.Label(desc_frame, text=line, justify=tk.LEFT, bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w")

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=GUI_PADX, pady=GUI_PADY)

        tk.Label(about_frame, text=get_text("about_author", author=AUTHOR), font=bold_font, bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w", padx=GUI_PADX)
        tk.Label(about_frame, text=get_text("about_email", email="melcom [@] vodafonemail.de"), bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w", padx=GUI_PADX, pady=(0, GUI_PADY))

        for header_key, links in [("about_website_header", [("about_website_1", "https://www.melcom-music.de"), ("about_website_2", "https://scenes.at/melcom")]),
                                  ("about_youtube_header", [("about_youtube_link", "https://youtube.com/@melcom")]),
                                  ("about_bluesky_header", [("about_bluesky_link", "https://melcom-music.bsky.social")])]:
            tk.Label(about_frame, text=get_text(header_key), font=bold_font, bg=self.colors["bg"], fg=self.colors["fg"]).pack(anchor="w", padx=GUI_PADX, pady=(GUI_PADY, 0))
            for text_key, url in links:
                link = tk.Label(about_frame, text=get_text(text_key), fg="blue", cursor="hand2", bg=self.colors["bg"])
                link.pack(anchor="w", padx=GUI_PADX)
                link.bind("<Button-1>", lambda e, link_url=url: webbrowser.open(link_url))

        ttk.Separator(about_frame, orient='horizontal').pack(fill='x', padx=GUI_PADX, pady=GUI_PADY)

        tk.Label(about_frame, text=get_text("about_opensource", year=datetime.datetime.now().year), bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        tk.Label(about_frame, text=get_text("about_license"), bg=self.colors["bg"], fg=self.colors["fg"]).pack()
        tk.Label(about_frame, text=get_text("about_copyright", year=datetime.datetime.now().year), bg=self.colors["bg"], fg=self.colors["fg"]).pack()

        ttk.Button(about_frame, text=get_text("about_ok_button"), command=about_window.destroy).pack(pady=GUI_PADY)
        
        center_window(about_window)
        about_window.wait_window(about_window)

    def show_options(self):
        """Displays the 'Options' window for configuring the application."""
        options_window = tk.Toplevel(self.root)
        options_window.geometry("600x270")
        options_window.title(get_text("options_dialog_title"))
        options_window.configure(bg=self.colors["bg"])
        options_window.transient(self.root)
        options_window.grab_set()

        lang_frame = tk.LabelFrame(options_window, text=f" {get_text('options_language_group')} ", bg=self.colors["bg"], fg=self.colors["fg"])
        lang_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)
        
        ffmpeg_frame = tk.LabelFrame(options_window, text=f" {get_text('options_ffmpeg_path_group')} ", bg=self.colors["bg"], fg=self.colors["fg"])
        ffmpeg_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)

        log_frame = tk.LabelFrame(options_window, text=f" {get_text('options_log_settings_group')} ", bg=self.colors["bg"], fg=self.colors["fg"])
        log_frame.pack(fill=tk.X, padx=GUI_PADX, pady=GUI_PADY)

        lang_var = tk.StringVar(value=current_language)
        tk.Label(lang_frame, text=get_text("options_language_label"), bg=self.colors["bg"], fg=self.colors["fg"]).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Combobox(lang_frame, textvariable=lang_var, values=LANGUAGE_CODES_LIST, state="readonly").pack(side=tk.LEFT, padx=5, pady=5)

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

        chk = tk.Checkbutton(log_frame, text=get_text("options_log_single_entry_check"), variable=single_log_var, command=toggle_log_size, bg=self.colors["bg"], fg=self.colors["fg"], selectcolor=self.colors["bg"])
        chk.grid(row=0, column=0, columnspan=2, sticky='w', padx=5, pady=5)
        
        tk.Label(log_frame, text=get_text("options_log_size_label"), bg=self.colors["bg"], fg=self.colors["fg"]).grid(row=1, column=0, sticky='w', padx=5, pady=5)
        log_size_entry.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        toggle_log_size()

        def save_and_close():
            """Validates, saves, and applies settings, then closes the window."""
            global current_language
            ffmpeg_path = ffmpeg_path_var.get()
            if not os.path.exists(os.path.join(ffmpeg_path, FFMPEG_EXECUTABLE_NAME)):
                messagebox.showerror(get_text("options_error_invalid_ffmpeg_path_title"), get_text("options_error_invalid_ffmpeg_path_message"), parent=options_window)
                return
            
            config.ffmpeg_path = ffmpeg_path
            config.log_file_size_kb = log_size_var.get()
            config.single_log_entry_enabled = single_log_var.get()
            
            lang_changed = current_language != lang_var.get()
            current_language = lang_var.get()
            
            config.save_options()
            if lang_changed: self.apply_language()
            
            options_window.destroy()

        ttk.Button(options_window, text=get_text("options_save_button"), command=save_and_close).pack(pady=GUI_PADY)
        
        center_window(options_window)
        options_window.wait_window(options_window)

# --- MAIN EXECUTION ---
# This block runs when the script is executed directly.
if __name__ == "__main__":
    # Initialize the configuration.
    config = Config()
    # Load the language specified in the config.
    load_language(current_language)
    # Create the main Tkinter window and app instance.
    root = tk.Tk()
    app = AudioNormalizerApp(root)
    # Set the custom closing protocol.
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    # Start the Tkinter event loop.
    root.mainloop()