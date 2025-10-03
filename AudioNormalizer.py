# Import necessary modules for GUI, file operations, subprocess management, configuration, web browsing, date/time, threading and JSON handling
# -*- coding: utf-8 -*-
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.ttk import Progressbar, Combobox, Style, Scrollbar
import tkinter.ttk as ttk
import subprocess
import os
import configparser
import webbrowser
import datetime
import threading
import json
import winsound

# Define the version of the application
VERSION = "2.2.2"
# Define the build date of the application
BUILD_DATE = "2025-10-03"

# Define padding values for GUI elements
GUI_PADX = 15
GUI_PADY = 8
GUI_LABEL_PADX = 3
GUI_LABEL_PADY = 3
GUI_BUTTON_PADX = 5
GUI_BUTTON_PADY = 8
# Define width for file path entry
GUI_ENTRY_WIDTH_FILE = 58
# Define width for LUFS and True Peak value entries
GUI_ENTRY_WIDTH_LUFS_TP = 10
# Define width for LUFS and True Peak preset comboboxes
GUI_COMBOBOX_WIDTH_LUFS_PRESET = 28
GUI_COMBOBOX_WIDTH_TP_PRESET = 30
# Define height and width for process information text area
GUI_PROCESS_INFO_HEIGHT = 6
GUI_PROCESS_INFO_WIDTH = 60
# Define dimensions and padding for options dialog
DIALOG_WIDTH_OPTIONS = 450
DIALOG_HEIGHT_OPTIONS = 220
DIALOG_PADX_OPTIONS = 10
DIALOG_PADY_OPTIONS = 5
# Define dimensions and vertical offset for info dialog
DIALOG_WIDTH_INFO = 450
DIALOG_HEIGHT_INFO = 420
DIALOG_VERTICAL_OFFSET_INFO = -100
# Define standard and maximum log file size in KB
STANDARD_LOG_FILE_SIZE_KB = 1024
MAX_LOG_FILE_SIZE_KB = 10240

# Define configuration and log file names
CONFIG_FILE_NAME = "options.ini"
LOG_FILE_NAME = "normalization.log"
ANALYSIS_LOG_FILE_NAME = "analysis.log"

# Define the name of the FFmpeg executable
FFMPEG_EXECUTABLE_NAME = "ffmpeg.exe"
FFPLAY_EXECUTABLE_NAME = "ffplay.exe"
# Define temporary file extension used during processing
TEMP_FILE_EXTENSION = ".temp"

# Define common audio file extensions
AUDIO_FILE_EXTENSION_WAV = ".wav"
AUDIO_FILE_EXTENSION_MP3 = ".mp3"
AUDIO_FILE_EXTENSION_FLAC = ".flac"
AUDIO_FILE_EXTENSION_AAC = ".aac"
AUDIO_FILE_EXTENSION_OGG = ".ogg"
AUDIO_FILE_EXTENSION_M4A = ".m4a"
# Define wildcard for all supported audio file extensions
AUDIO_FILE_EXTENSIONS_ALL = "*.wav *.mp3 *.flac *.aac *.ogg *.m4a"
# Define wildcard for all files
ALL_FILES_WILDCARD = "*.*"

# Define output format names
OUTPUT_FORMAT_WAV = "WAV"
OUTPUT_FORMAT_MP3 = "MP3"
OUTPUT_FORMAT_FLAC = "FLAC"
OUTPUT_FORMAT_AAC = "AAC"
OUTPUT_FORMAT_OGG = "OGG"
# List of available output formats
OUTPUT_FORMATS_LIST = [OUTPUT_FORMAT_WAV, OUTPUT_FORMAT_MP3, OUTPUT_FORMAT_FLAC, OUTPUT_FORMAT_AAC, OUTPUT_FORMAT_OGG]

# Define configuration section and keys
CONFIG_SECTION_SETTINGS = "Settings"
CONFIG_KEY_FFMPEG_PATH = "ffmpeg_path"
CONFIG_KEY_LOG_FILE_SIZE = "log_file_size_kb"
CONFIG_KEY_SINGLE_LOG_ENTRY = "single_log_entry_enabled"
CONFIG_KEY_LANGUAGE = "language"

# Define language codes
LANGUAGE_CODE_EN_US = "en_US"
LANGUAGE_CODE_DE_DE = "de_DE"
LANGUAGE_CODE_PL_PL = "pl_PL"
# List of available language codes
LANGUAGE_CODES_LIST = [LANGUAGE_CODE_EN_US, LANGUAGE_CODE_DE_DE, LANGUAGE_CODE_PL_PL]
# Define default language code
DEFAULT_LANGUAGE_CODE = LANGUAGE_CODE_EN_US
# Define language file folder name and extension
LANG_FOLDER_NAME = "lang"
LANG_FILE_EXTENSION = ".json"

# Define style theme name for Tkinter
STYLE_THEME_NAME = 'clam'
# Define background color for process information text area
PROCESS_INFO_BACKGROUND_COLOR = "lightgrey"

# Define audio codecs for FFmpeg
CODEC_PCM_F32LE = "pcm_f32le"
CODEC_LIBMP3LAME = "libmp3lame"
CODEC_FLAC = "flac"
CODEC_AAC = "aac"
CODEC_LIBVORBIS = "libvorbis"

# Define FFmpeg options for MP3 and OGG encoding
FFMPEG_OPTION_BITRATE_MP3 = "-b:a"
FFMPEG_BITRATE_320K = "320k"
FFMPEG_OPTION_QSCALE_OGG = "-qscale:a"
FFMPEG_QSCALE_10 = "10"

# Global variables for language data and current language
language_data = {}
current_language = DEFAULT_LANGUAGE_CODE

# Define default LUFS presets in English
LUFS_PRESETS_EN = {
    "Default (-14 LUFS)": "-14",
    "Apple Music (-16 LUFS)": "-16",
    "Amazon Music (-16 LUFS)": "-16",
    "Broadcast EBU R128 (-23 LUFS)": "-23",
    "Custom": "custom",
    "Gaming (-20 LUFS)": "-20",
    "Podcast (-16 LUFS)": "-16",
    "Podcast (Speech, -19 LUFS)": "-19",
    "Spotify (-14 LUFS)": "-14",
    "Tidal (-14 LUFS)": "-14",
    "YouTube (-14 LUFS)": "-14",
}
# Define default True Peak presets in English
TRUE_PEAK_PRESETS_EN = {
    "Default (-1 dBTP)": "-1",
    "Broadcast (-2 dBTP)": "-2",
    "CD Mastering (Standard, -1 dBTP)": "-1",
    "CD Mastering (Strict, -0.3 dBTP)": "-0.3",
    "No Limit (0 dBTP)": "0",
    "Custom": "custom",
}
# Initialize LUFS and True Peak presets with English defaults
LUFS_PRESETS = LUFS_PRESETS_EN
TRUE_PEAK_PRESETS = TRUE_PEAK_PRESETS_EN
# Extract preset names for combobox population
LUFS_PRESET_NAMES = list(LUFS_PRESETS.keys())
TRUE_PEAK_PRESET_NAMES = list(TRUE_PEAK_PRESETS.keys())

# --- NEUE HILFSFUNKTION ---
def update_process_info(message):
    """Fügt eine Nachricht zum Prozess-Infofenster hinzu und scrollt nach unten."""
    if not message: # Leere Zeilen ignorieren
        return
        
    process_info_field.config(state=tk.NORMAL)
    process_info_field.insert(tk.END, message + "\n")
    process_info_field.see(tk.END) # Auto-scroll
    process_info_field.config(state=tk.DISABLED)

# Define a class to manage application configuration
class Config:
    def __init__(self):
        # Initialize configuration attributes with default values
        self.ffmpeg_path = FFMPEG_EXECUTABLE_NAME
        self.log_file_size_kb = STANDARD_LOG_FILE_SIZE_KB
        self.single_log_entry_enabled = True
        # Load options from configuration file on initialization
        self.load_options()

    def load_options(self):
        # Create a ConfigParser object to handle INI file
        config = configparser.ConfigParser()
        # Check if the configuration file exists
        if os.path.exists(CONFIG_FILE_NAME):
            # Read configuration from the file
            config.read(CONFIG_FILE_NAME)
            # Check if the 'Settings' section exists in the config file
            if CONFIG_SECTION_SETTINGS in config:
                # Load FFmpeg path from config if available
                if CONFIG_KEY_FFMPEG_PATH in config[CONFIG_SECTION_SETTINGS]:
                    self.ffmpeg_path = config[CONFIG_SECTION_SETTINGS][CONFIG_KEY_FFMPEG_PATH]
                # Load log file size from config, handling potential errors
                if CONFIG_KEY_LOG_FILE_SIZE in config[CONFIG_SECTION_SETTINGS]:
                    try:
                        self.log_file_size_kb = int(config[CONFIG_SECTION_SETTINGS][CONFIG_KEY_LOG_FILE_SIZE])
                    except ValueError:
                        self.log_file_size_kb = STANDARD_LOG_FILE_SIZE_KB
                # Load single log entry setting from config
                if CONFIG_KEY_SINGLE_LOG_ENTRY in config[CONFIG_SECTION_SETTINGS]:
                    self.single_log_entry_enabled = config[CONFIG_SECTION_SETTINGS][CONFIG_KEY_SINGLE_LOG_ENTRY].lower() == "true"
                # Load language setting from config
                if CONFIG_KEY_LANGUAGE in config[CONFIG_SECTION_SETTINGS]:
                    global current_language
                    current_language = config[CONFIG_SECTION_SETTINGS][CONFIG_KEY_LANGUAGE]
        # Ensure log file size is valid after loading options
        self.ensure_log_size_valid()

    def save_options(self):
        # Create a ConfigParser object to save settings
        config = configparser.ConfigParser()
        # Set values in the 'Settings' section
        config[CONFIG_SECTION_SETTINGS] = {CONFIG_KEY_FFMPEG_PATH: self.ffmpeg_path,
                                  CONFIG_KEY_LOG_FILE_SIZE: self.log_file_size_kb,
                                  CONFIG_KEY_SINGLE_LOG_ENTRY: str(self.single_log_entry_enabled),
                                  CONFIG_KEY_LANGUAGE: current_language
                                  }
        # Write the configuration to the options file
        with open(CONFIG_FILE_NAME, "w") as configfile:
            config.write(configfile)

    def ensure_log_size_valid(self):
        # Validate log file size, reset to default if invalid
        if not isinstance(self.log_file_size_kb, int) or self.log_file_size_kb <= 0:
            self.log_file_size_kb = STANDARD_LOG_FILE_SIZE_KB

# Create a global Config instance to manage application settings
config = Config()
# Global variable to store the normalization process, allowing for cancellation
normalization_process = None
# Global variable to store the playback process
playback_process = None

# Function to load language data from JSON file
def load_language(language_code):
    global language_data, LUFS_PRESET_NAMES, TRUE_PEAK_PRESET_NAMES, LUFS_PRESETS, TRUE_PEAK_PRESETS
    try:
        # Construct path to the language file
        language_file_path = os.path.join(LANG_FOLDER_NAME, f"{language_code}{LANG_FILE_EXTENSION}")
        # Open and load JSON language file
        with open(language_file_path, "r", encoding="utf-8") as f:
            language_data = json.load(f)

        # Language specific preset adjustments (German)
        if language_code == LANGUAGE_CODE_DE_DE:
            LUFS_PRESETS = {
                get_text("lufs_preset_default_long").format(lufs_value="-14"): "-14",
                get_text("lufs_preset_youtube"): "-14",
                get_text("lufs_preset_spotify"): "-14",
                get_text("lufs_preset_applemusic"): "-16",
                get_text("lufs_preset_tidal"): "-14",
                get_text("lufs_preset_amazonmusic"): "-16",
                get_text("lufs_preset_podcast"): "-16",
                get_text("lufs_preset_podcast_speech"): "-19",
                get_text("lufs_preset_gaming"): "-20",
                get_text("lufs_preset_broadcast_long").format(lufs_value="-23"): "-23",
                get_text("lufs_preset_custom"): "custom"
            }
            TRUE_PEAK_PRESETS = {
                get_text("true_peak_preset_default_long").format(tp_value="-1"): "-1",
                get_text("true_peak_preset_broadcast_long").format(tp_value="-2"): "-2",
                get_text("true_peak_preset_cdmastering"): "-1",
                get_text("true_peak_preset_cdmastering_strict"): "-0.3",
                get_text("true_peak_preset_nolimit"): "0",
                get_text("true_peak_preset_custom"): "custom"
            }
        # Language specific preset adjustments (Polish)
        elif language_code == LANGUAGE_CODE_PL_PL:
            LUFS_PRESETS = {
                get_text("lufs_preset_default_long").format(lufs_value="-14"): "-14",
                get_text("lufs_preset_youtube"): "-14",
                get_text("lufs_preset_spotify"): "-14",
                get_text("lufs_preset_applemusic"): "-16",
                get_text("lufs_preset_tidal"): "-14",
                get_text("lufs_preset_amazonmusic"): "-16",
                get_text("lufs_preset_podcast"): "-16",
                get_text("lufs_preset_podcast_speech"): "-19",
                get_text("lufs_preset_gaming"): "-20",
                get_text("lufs_preset_broadcast_long").format(lufs_value="-23"): "-23",
                get_text("lufs_preset_custom"): "custom"
            }
            TRUE_PEAK_PRESETS = {
                get_text("true_peak_preset_default_long").format(tp_value="-1"): "-1",
                get_text("true_peak_preset_broadcast_long").format(tp_value="-2"): "-2",
                get_text("true_peak_preset_cdmastering"): "-1",
                get_text("true_peak_preset_cdmastering_strict"): "-0.3",
                get_text("true_peak_preset_nolimit"): "0",
                get_text("true_peak_preset_custom"): "custom"
            }
        # Default to English presets for other or unknown languages
        else:
            LUFS_PRESETS = LUFS_PRESETS_EN
            TRUE_PEAK_PRESETS = TRUE_PEAK_PRESETS_EN

        # Sort LUFS presets for consistent display order
        lufs_presets_sorted_keys = sorted(LUFS_PRESETS.keys(), key=lambda x: (x != get_text("lufs_preset_default_long").format(lufs_value="-14"), x != "Default (-14 LUFS)", x == get_text("lufs_preset_custom"), x == "Custom", x))
        TRUE_PEAK_PRESET_NAMES = sorted(TRUE_PEAK_PRESETS.keys(), key=lambda x: (x != get_text("true_peak_preset_default_long").format(tp_value="-1"), x != "Default (-1 dBTP)", x == get_text("true_peak_preset_custom"),  x == "Custom", x))

        LUFS_PRESET_NAMES = lufs_presets_sorted_keys
        TRUE_PEAK_PRESET_NAMES = TRUE_PEAK_PRESET_NAMES

    # Fallback to default language if language file not found
    except FileNotFoundError:
        load_language(DEFAULT_LANGUAGE_CODE)
    # Fallback to default language if JSON decoding fails
    except json.JSONDecodeError:
        load_language(DEFAULT_LANGUAGE_CODE)

# Function to get localized text based on key
def get_text(key):
    global language_data
    # Return localized text from language data, or key in brackets if not found
    return language_data.get(key, f"[{key}]")

# Function to open the update webpage
def check_for_updates():
    webbrowser.open("http://melcom-creations.github.io/melcom-music/creations.html#ffmpeg")

# Function to apply the loaded language to the GUI elements
def apply_language(dialog_type):
    global window, menubar, filemenu, infomenu, file_frame_group, loudness_settings_frame_group
    global output_format_frame_group, process_information_frame_group, file_label, browse_button
    global lufs_preset_label, true_peak_preset_label, lufs_label, true_peak_label, output_format_label
    global analyze_button, start_button, cancel_button, lufs_preset_combobox, true_peak_preset_combobox
    global play_button, stop_button

    # Set the main window title with localized app title and version
    window.title(f"{get_text('app_title')} v{VERSION}")

    # Configure the menu bar with localized labels
    menubar = tk.Menu(window)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label=get_text("menu_file_options"), command=show_options_dialog)
    filemenu.add_separator()
    filemenu.add_command(label=get_text("menu_file_exit"), command=exit_program)
    menubar.add_cascade(label=get_text("menu_file"), menu=filemenu)

    infomenu = tk.Menu(menubar, tearoff=0)
    infomenu.add_command(label=get_text("menu_info_about"), command=show_info_box)
    infomenu.add_command(label=get_text("menu_info_updates"), command=check_for_updates)
    menubar.add_cascade(label=get_text("menu_info"), menu=infomenu)
    window.config(menu=menubar)

    # Apply language to the options dialog if it's open
    if dialog_type == "options":
        options_dialog = window.children.get("!toplevel")
        if options_dialog:
            try:
                options_dialog.title(get_text("options_dialog_title"))
                options_dialog.children["language_frame"].config(text=get_text("options_language_group"))
                options_dialog.children["ffmpeg_frame"].config(text=get_text("options_ffmpeg_path_group"))
                options_dialog.children["log_frame"].config(text=get_text("options_log_settings_group"))
                options_dialog.children["language_frame"].children["language_label"].config(text=get_text("options_language_label"))
                options_dialog.children["ffmpeg_frame"].children["ffmpeg_path_label"].config(text=get_text("options_ffmpeg_path_label"))
                options_dialog.children["log_frame"].children["single_log_check"].config(text=get_text("options_log_single_entry_check"))
                options_dialog.children["log_frame"].children["log_size_label"].config(text=get_text("options_log_size_label"))
                options_dialog.children["ffmpeg_frame"].children["browse_ffmpeg_button"].config(text=get_text("options_browse_button"))
                options_dialog.children["save_options_button"].config(text=get_text("options_save_button"))
            except KeyError:
                pass

    # Apply language to the info dialog if it's open
    elif dialog_type == "info":
        info_dialog = window.children.get("!toplevel2")
        if info_dialog:
            try:
                info_dialog.title(get_text("menu_info_about"))
                info_dialog.children["info_label_frame"].config(text=get_text("app_title_long"))
                info_dialog.children["info_label_frame"].children["info_text_label"].config(text=get_text("about_text").format(version=VERSION, build_date=BUILD_DATE))
                info_dialog.children["info_label_frame"].children["website_label_1"].config(text=get_text("about_website_1"))
                info_dialog.children["info_label_frame"].children["website_label_2"].config(text=get_text("about_website_2"))
                info_dialog.children["info_label_frame"].children["opensource_label"].config(text=get_text("about_opensource").format(year=datetime.datetime.now().year))
                info_dialog.children["ok_info_button"].config(text=get_text("about_ok_button"))
            except KeyError:
                pass

    # Apply language to the main application window elements
    elif dialog_type == "main":
        file_frame_group.config(text=get_text("file_selection_group"))
        loudness_settings_frame_group.config(text=get_text("loudness_settings_group"))
        output_format_frame_group.config(text=get_text("output_format_group"))
        process_information_frame_group.config(text=get_text("process_information_group"))

        file_label.config(text=get_text("select_audio_file_label"))
        browse_button.config(text=get_text("browse_file_button"))
        play_button.config(text=get_text("play_audio_button"))
        stop_button.config(text=get_text("stop_audio_button"))
        lufs_preset_label.config(text=get_text("lufs_preset_label"))
        true_peak_preset_label.config(text=get_text("true_peak_preset_label"))
        lufs_label.config(text=get_text("target_lufs_label_custom"))
        true_peak_label.config(text=get_text("true_peak_label"))
        output_format_label.config(text=get_text("output_format_file_format_label"))
        analyze_button.config(text=get_text("analyze_audio_button"))
        start_button.config(text=get_text("start_normalization_button"))
        cancel_button.config(text=get_text("cancel_normalization_button"))

        lufs_preset_combobox.config(values=LUFS_PRESET_NAMES)
        true_peak_preset_combobox.config(values=TRUE_PEAK_PRESET_NAMES)
        if lufs_preset_var.get() not in LUFS_PRESET_NAMES:
            lufs_preset_var.set(LUFS_PRESET_NAMES[0])
        if true_peak_preset_var.get() not in TRUE_PEAK_PRESET_NAMES:
            true_peak_preset_var.set(TRUE_PEAK_PRESET_NAMES[0])

        update_lufs_entry_state()
        update_true_peak_entry_state()

# Function to display the options dialog window
def show_options_dialog():
    # Create a toplevel window for options dialog
    options_window = tk.Toplevel(window)
    options_window.title(get_text("options_dialog_title"))
    # Make the dialog modal to the main window
    options_window.transient(window)
    options_window.grab_set()
    options_window.configure(bg=background_color)

    # Calculate position to center the options dialog over the main window
    window_x = window.winfo_rootx()
    window_y = window.winfo_rooty()
    window_width = window.winfo_width()
    window_height = window.winfo_height()

    dialog_width = DIALOG_WIDTH_OPTIONS
    dialog_height = DIALOG_HEIGHT_OPTIONS

    x_position = window_x + (window_width - dialog_width) // 2
    y_position = window_y + (window_height - dialog_height) // 2
    options_window.geometry(f"+{x_position}+{y_position}")

    # Create frames for grouping options
    language_frame = tk.LabelFrame(options_window, text=get_text("options_language_group"), padx=DIALOG_PADX_OPTIONS,
                                     pady=DIALOG_PADY_OPTIONS, name="language_frame", bg=background_color)
    language_frame.grid(row=0, column=0, columnspan=3, padx=GUI_PADX, pady=GUI_PADY,
                         sticky="ew")

    ffmpeg_frame = tk.LabelFrame(options_window, text=get_text("options_ffmpeg_path_group"), padx=DIALOG_PADX_OPTIONS,
                                 pady=DIALOG_PADY_OPTIONS, name="ffmpeg_frame", bg=background_color)
    ffmpeg_frame.grid(row=1, column=0, columnspan=3, padx=GUI_PADX, pady=GUI_PADY,
                        sticky="ew")

    log_frame = tk.LabelFrame(options_window, text=get_text("options_log_settings_group"), padx=DIALOG_PADX_OPTIONS,
                              pady=DIALOG_PADY_OPTIONS, name="log_frame", bg=background_color)
    log_frame.grid(row=2, column=0, columnspan=3, padx=GUI_PADX, pady=GUI_PADY,
                    sticky="ew")

    # Language selection options
    language_label = tk.Label(language_frame, text=get_text("options_language_label"), name="language_label", bg=background_color)
    language_label.grid(row=0, column=0, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS,
                            sticky="w")

    language_var = tk.StringVar(value=current_language)
    language_combobox = Combobox(language_frame, textvariable=language_var,
                                    values=LANGUAGE_CODES_LIST, state="readonly", width=20, name="language_combobox")
    language_combobox.grid(row=0, column=1, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS,
                            sticky="ew")
    language_combobox.bind("<<ComboboxSelected>>", lambda event, var=language_var: update_language_selection(event, var))

    # FFmpeg path selection options
    ffmpeg_path_label = tk.Label(ffmpeg_frame, text=get_text("options_ffmpeg_path_label"), name="ffmpeg_path_label", bg=background_color)
    ffmpeg_path_label.grid(row=0, column=0, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS,
                            sticky="w")
    ffmpeg_path_input = tk.Entry(ffmpeg_frame, width=50, name="ffmpeg_path_input")
    ffmpeg_path_input.grid(row=0, column=1, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS,
                            sticky="ew")

    # Set default FFmpeg path in the input field
    if config.ffmpeg_path == FFMPEG_EXECUTABLE_NAME:
        program_path = os.path.dirname(os.path.abspath(__file__))
        ffmpeg_path_input.insert(0, program_path)
    else:
        ffmpeg_path_input.insert(0, config.ffmpeg_path)

    # Log settings options
    single_log_check_var = tk.BooleanVar(
        value=config.single_log_entry_enabled)
    single_log_check = tk.Checkbutton(log_frame, text=get_text("options_log_single_entry_check"),
                                      variable=single_log_check_var,
                                      command=lambda: update_log_size_state(single_log_check_var,
                                                                               log_size_input), name="single_log_check", bg=background_color)
    single_log_check.grid(row=1, column=0, columnspan=2, padx=DIALOG_PADX_OPTIONS,
                            pady=(DIALOG_PADY_OPTIONS, DIALOG_PADY_OPTIONS),
                            sticky="w")

    log_size_label = tk.Label(log_frame, text=get_text("options_log_size_label"), name="log_size_label", bg=background_color)
    log_size_label.grid(row=0, column=0, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS,
                            sticky="w")
    log_size_input = tk.Entry(log_frame, width=10, name="log_size_input")
    log_size_input.grid(row=0, column=1, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS,
                            sticky="w")
    log_size_input.insert(0, str(config.log_file_size_kb))

    # Function to enable/disable log size input based on single log entry checkbox
    def update_log_size_state(check_variable, size_input_field):
        if check_variable.get():
            size_input_field.config(state=tk.DISABLED)
        else:
            size_input_field.config(state=tk.NORMAL)

    # Initialize log size input state based on configuration
    update_log_size_state(single_log_check_var, log_size_input)

    # Function to browse for FFmpeg path
    def browse_ffmpeg_path():
        path = filedialog.askdirectory(title=get_text("options_ffmpeg_path_dialog_title"))
        if path:
            ffmpeg_path_input.delete(0, tk.END)
            ffmpeg_path_input.insert(0, path)

    browse_button = ttk.Button(ffmpeg_frame, text=get_text("options_browse_button"), command=browse_ffmpeg_path, name="browse_ffmpeg_button")
    browse_button.grid(row=0, column=2, padx=DIALOG_PADX_OPTIONS, pady=DIALOG_PADY_OPTIONS)

    # Function to save options and close the options dialog
    def save_and_close_options():
        global current_language
        ffmpeg_path_input_value = ffmpeg_path_input.get()
        ffmpeg_executable_path = os.path.join(ffmpeg_path_input_value, FFMPEG_EXECUTABLE_NAME)

        # Validate FFmpeg path
        if not os.path.exists(ffmpeg_executable_path):
            messagebox.showerror(get_text("options_error_invalid_ffmpeg_path_title"),
                                 get_text("options_error_invalid_ffmpeg_path_message"),
                                 parent=options_window)
            return

        # Check if FFmpeg executable is working
        try:
            subprocess.run([ffmpeg_executable_path, "-version"], capture_output=True,
                             check=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            messagebox.showerror(get_text("options_error_ffmpeg_executable_title"),
                                 get_text("options_error_ffmpeg_executable_message"),
                                 parent=options_window)
            return

        config.ffmpeg_path = ffmpeg_path_input_value

        # Validate log file size if single log entry is disabled
        if not single_log_check_var.get():
            try:
                log_file_size_kb_input = log_size_input.get()
                log_file_size_kb_value = int(log_file_size_kb_input)
                if log_file_size_kb_value <= 0:
                    messagebox.showerror(get_text("options_error_invalid_log_size_title"),
                                         get_text("options_error_invalid_log_size_positive_message"),
                                         parent=options_window)
                    return
                if log_file_size_kb_value > MAX_LOG_FILE_SIZE_KB:
                    messagebox.showerror(get_text("options_error_invalid_log_size_title"),
                                         get_text("options_error_invalid_log_size_maximum_message").format(max_size_kb=MAX_LOG_FILE_SIZE_KB),
                                         parent=options_window)
                    return
                config.log_file_size_kb = log_file_size_kb_value
            except ValueError:
                messagebox.showerror(get_text("options_error_invalid_log_size_title"),
                                     get_text("options_error_invalid_log_size_integer_message"),
                                     parent=options_window)
                return

        config.single_log_entry_enabled = single_log_check_var.get()
        current_language = language_var.get()

        config.save_options()
        apply_language("options")
        apply_language("main")
        if window.children.get("!toplevel2"):
            apply_language("info")
        options_window.destroy()

    save_button = ttk.Button(options_window, text=get_text("options_save_button"),
                                 command=save_and_close_options, name="save_options_button")
    save_button.grid(row=3, column=0, columnspan=3, pady=GUI_PADY)

    # Configure column resizing for options dialog
    options_window.columnconfigure(1, weight=1)
    # Make the dialog window wait until it is closed
    options_window.wait_window(options_window)

# Function to display the info dialog box
def show_info_box():
    # Create a toplevel window for info dialog
    info_window = tk.Toplevel(window)
    info_window.title(get_text("menu_info_about"))
    # Make the dialog modal to the main window
    info_window.transient(window)
    info_window.grab_set()

    # Calculate position to center the info dialog, with vertical offset
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    dialog_width = DIALOG_WIDTH_INFO
    dialog_height = DIALOG_HEIGHT_INFO
    x_position = (screen_width - dialog_width) // 2
    y_position = (screen_height - dialog_height) // 2 + DIALOG_VERTICAL_OFFSET_INFO
    info_window.geometry(f"+{x_position}+{y_position}")

    info_frame = tk.LabelFrame(info_window, text=get_text("app_title_long"), padx=GUI_PADX,
                                pady=GUI_PADY, name="info_label_frame")
    info_frame.pack(padx=GUI_PADX, pady=GUI_PADY, fill=tk.BOTH,
                     expand=True)

    # Define fonts for different text styles
    bold_font = ("Helvetica", 9, "bold")
    large_bold_font = ("Helvetica", 11, "bold")
    normal_font = ("Helvetica", 9)

    # Add labels with application information
    tk.Label(info_frame, text=get_text("app_title_long"), font=large_bold_font).pack(pady=(GUI_PADY, 2), anchor="center")

    tk.Label(info_frame, text=get_text("about_version").format(version=VERSION), font=bold_font).pack(anchor="center")
    tk.Label(info_frame, text=get_text("about_build_date").format(build_date=BUILD_DATE)).pack(pady=(0, GUI_PADY), anchor="center")

    separator_line_info_1 = tk.Frame(info_frame, bg=separator_color, height=1)
    separator_line_info_1.pack(fill="x", padx=GUI_PADX, pady=GUI_PADY)

    description_text = get_text("about_description")
    for line in description_text.splitlines():
        if line.strip():
            tk.Label(info_frame, text=line, justify=tk.LEFT, anchor="w").pack(padx=GUI_PADX, pady=2, fill="x")

    separator_line_info_2 = tk.Frame(info_frame, bg=separator_color, height=1)
    separator_line_info_2.pack(fill="x", padx=GUI_PADX, pady=GUI_PADY)

    tk.Label(info_frame, text=get_text("about_author").format(author="melcom (Andreas Thomas Urban)"), anchor="w", font=bold_font).pack(padx=GUI_PADX, pady=(GUI_PADY, 2), fill="x")
    tk.Label(info_frame, text=get_text("about_email").format(email="melcom [@] vodafonemail.de"), anchor="w").pack(padx=GUI_PADX, pady=(0, GUI_PADY), fill="x")

    tk.Label(info_frame, text=get_text("about_website_header"), anchor="w", font=bold_font).pack(padx=GUI_PADX, pady=(GUI_PADY, 2), fill="x")

    website_label_1 = tk.Label(info_frame, text=get_text("about_website_1"), fg="blue", cursor="hand2", anchor="w")
    website_label_1.pack(anchor="w", padx=GUI_PADX, pady=2, fill="x")
    website_label_1.bind("<Button-1>", lambda e: webbrowser.open("https://www.melcom-music.de"))

    website_label_2 = tk.Label(info_frame, text=get_text("about_website_2"), fg="blue", cursor="hand2", anchor="w")
    website_label_2.pack(anchor="w", padx=GUI_PADX, pady=2, fill="x")
    website_label_2.bind("<Button-1>", lambda e: webbrowser.open("https://scenes.at/melcom"))

    tk.Label(info_frame, text=get_text("about_youtube_header"), anchor="w", font=bold_font).pack(padx=GUI_PADX, pady=(GUI_PADY, 2), fill="x")
    website_label_3 = tk.Label(info_frame, text=get_text("about_youtube_link"), fg="blue", cursor="hand2", anchor="w")
    website_label_3.pack(anchor="w", padx=GUI_PADX, pady=2, fill="x")
    website_label_3.bind("<Button-1>", lambda e: webbrowser.open("https://youtube.com/@melcom"))

    website_label_4 = tk.Label(info_frame, text=get_text("about_bluesky_link"), fg="blue", cursor="hand2", anchor="w")
    website_label_4.pack(anchor="w", padx=GUI_PADX, pady=2, fill="x")
    website_label_4.bind("<Button-1>", lambda e: webbrowser.open("https://melcom-music.bsky.social/"))


    separator_line_info_3 = tk.Frame(info_frame, bg=separator_color, height=1)
    separator_line_info_3.pack(fill="x", padx=GUI_PADX, pady=GUI_PADY)

    opensource_label = tk.Label(info_frame,
                                 text=get_text("about_opensource").format(year=datetime.datetime.now().year), anchor="center")
    opensource_label.pack(pady=(GUI_PADY, GUI_PADY), anchor="center")
    license_label = tk.Label(info_frame, text=get_text("about_license"), anchor="center")
    license_label.pack(pady=(0, GUI_PADY), anchor="center")
    copyright_label = tk.Label(info_frame, text=get_text("about_copyright").format(year=datetime.datetime.now().year), anchor="center")
    copyright_label.pack(anchor="center")

    ok_button = ttk.Button(info_frame, text=get_text("about_ok_button"), command=info_window.destroy, name="ok_info_button")
    ok_button.pack(pady=GUI_PADY, anchor="center")

    # Make the dialog window wait until it is closed
    info_window.wait_window(info_window)
    apply_language("info")

# Function to open file dialog for audio file selection
def browse_file():
    # Stop any ongoing playback before opening a new file
    stop_audio()
    # Open file dialog to select an audio file
    file_path = filedialog.askopenfilename(
        defaultextension=AUDIO_FILE_EXTENSION_WAV, # Default file extension
        filetypes=[ # Define file types filter for the dialog
            (get_text("file_dialog_audio_files"), AUDIO_FILE_EXTENSIONS_ALL), # All supported audio files
            (get_text("file_dialog_wav_files"), AUDIO_FILE_EXTENSION_WAV), # WAV files
            (get_text("file_dialog_mp3_files"), AUDIO_FILE_EXTENSION_MP3), # MP3 files
            (get_text("file_dialog_flac_files"), AUDIO_FILE_EXTENSION_FLAC), # FLAC files
            (get_text("file_dialog_aac_files"), f"{AUDIO_FILE_EXTENSION_AAC} {AUDIO_FILE_EXTENSION_M4A}"), # AAC/M4A files
            (get_text("file_dialog_ogg_files"), AUDIO_FILE_EXTENSION_OGG), # OGG files
            (get_text("file_dialog_all_files"), ALL_FILES_WILDCARD) # All files wildcard
        ],
        title=get_text("file_dialog_title"), # Set dialog title from localized text
        parent=window # Set parent window for modality
    )
    # If a file path is selected
    if file_path:
        file_input.delete(0, tk.END) # Clear the file input field
        file_input.insert(0, file_path) # Insert the selected file path into the input field
        play_button.config(state=tk.NORMAL) # Enable the play button
        stop_button.config(state=tk.DISABLED)

# Function to start audio playback
def play_audio():
    global playback_process
    file = file_input.get()

    if not file:
        return

    # Stop any existing playback
    stop_audio()

    ffplay_path = os.path.join(config.ffmpeg_path, FFPLAY_EXECUTABLE_NAME)
    if not os.path.exists(ffplay_path):
        messagebox.showerror(get_text("play_error_ffplay_not_found_title"),
                             get_text("play_error_ffplay_not_found_message"),
                             parent=window)
        return

    try:
        command = [ffplay_path, "-nodisp", "-autoexit", file]
        playback_process = subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                                            creationflags=subprocess.CREATE_NO_WINDOW)
        
        # Update button states
        play_button.config(state=tk.DISABLED)
        stop_button.config(state=tk.NORMAL)
        browse_button.config(state=tk.DISABLED)
        analyze_button.config(state=tk.DISABLED)
        start_button.config(state=tk.DISABLED)

        # Start a thread to monitor when playback finishes
        monitor_thread = threading.Thread(target=_monitor_playback)
        monitor_thread.daemon = True
        monitor_thread.start()

    except Exception as e:
        messagebox.showerror("Playback Error", f"Failed to start playback:\n{e}", parent=window)

# Function to stop audio playback
def stop_audio():
    global playback_process
    if playback_process:
        try:
            playback_process.terminate()
        except OSError:
            pass # Process might have already terminated
        playback_process = None
        # Reset button states via the main thread
        window.after(0, _reset_playback_buttons)

# Helper function to monitor playback process in a separate thread
def _monitor_playback():
    if playback_process:
        playback_process.wait() # Wait for the process to complete
        # When done, schedule the button state reset on the main thread
        window.after(0, _reset_playback_buttons)

# Helper function to reset button states after playback stops/finishes
def _reset_playback_buttons():
    global playback_process
    playback_process = None
    if file_input.get(): # Only enable play if there is a file path
        play_button.config(state=tk.NORMAL)
    else:
        play_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    browse_button.config(state=tk.NORMAL)
    analyze_button.config(state=tk.NORMAL)
    start_button.config(state=tk.NORMAL)

# Function to initiate audio analysis process
def analyze_audio():
    stop_audio() # Stop any playback before starting analysis
    file = file_input.get() # Get the file path from the input field

    # Check if a file is selected
    if not file:
        messagebox.showerror(get_text("analysis_no_file_error_title"), # Show error message if no file selected
                             get_text("analysis_no_file_error_message"),
                             parent=window)
        return

    # Disable buttons to prevent multiple actions during analysis
    analyze_button.config(state=tk.DISABLED)
    start_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.DISABLED)
    play_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    progressbar.grid(row=7, column=0, columnspan=3, sticky="ew", padx=GUI_PADX, pady=GUI_PADY) # Show progress bar
    progressbar.start() # Start progress bar animation

    # --- GEÄNDERT ---
    process_info_field.config(state=tk.NORMAL) # Enable process info text field for writing
    process_info_field.delete("1.0", tk.END) # Clear previous process info text
    process_info_field.config(state=tk.DISABLED) # Disable process info text field after writing
    update_process_info(get_text("analysis_start_message").format(filename=os.path.basename(file))) # Display analysis start message

    # Prepare log entry for analysis start
    log_entry_start = f"======================== {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ========================\n"
    log_entry_start += get_text("analysis_start_message").format(filename=file) + "\n"
    log_entry_start += get_text("analysis_log_ffmpeg_command_generating") + "\n"
    append_analysis_log(log_entry_start) # Append start log entry to analysis log

    # Create and start a thread for audio analysis to prevent GUI blocking
    analysis_thread = threading.Thread(target=audio_analysis_thread_function,
                                      args=(file,))
    analysis_thread.start()

# --- STARK GEÄNDERTE FUNKTION ---
def audio_analysis_thread_function(file):
    global normalization_process, config

    ffmpeg_analysis_command = [
        os.path.join(config.ffmpeg_path, FFMPEG_EXECUTABLE_NAME),
        "-i", file,
        "-af", "loudnorm=print_format=json",
        "-f", "null", "-"
    ]
    log_entry_command = get_text("analysis_log_ffmpeg_command") + "\n" + " ".join(ffmpeg_analysis_command) + "\n\n"
    append_analysis_log(log_entry_command)

    try:
        # Popen statt run, um die Ausgabe live zu verarbeiten
        process = subprocess.Popen(
            ffmpeg_analysis_command,
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        full_stderr_output = ""
        # Lese die Ausgabe Zeile für Zeile in Echtzeit
        for line in iter(process.stderr.readline, ''):
            full_stderr_output += line
            window.after(0, update_process_info, line.strip()) # Sende die Zeile an die GUI

        process.wait() # Warte auf das Ende des Prozesses
        
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, cmd=ffmpeg_analysis_command, stderr=full_stderr_output)
            
        append_analysis_log(get_text("analysis_log_ffmpeg_output") + "\n" + full_stderr_output + "\n")

        try:
            start_index = full_stderr_output.find("{")
            end_index = full_stderr_output.rfind("}") + 1
            json_string = full_stderr_output[start_index:end_index]
            json_output = json.loads(json_string)

            analysis_results = {
                "input_i": json_output.get("input_i"),
                "input_tp": json_output.get("input_tp"),
                "lra": json_output.get("input_lra")
            }
            window.after(0, _update_gui_on_analysis_completion, "Success", file, analysis_results)

        except json.JSONDecodeError:
            error_message_json = get_text("analysis_log_json_error")
            append_analysis_log("ERROR: " + error_message_json + "\n")
            window.after(0, _update_gui_on_analysis_completion, "Error", file, error_message_json)

    except subprocess.CalledProcessError as e:
        error_message_ffmpeg = get_text("analysis_ffmpeg_error_message").format(return_code=e.returncode, stderr=e.stderr)
        append_log("ERROR: " + error_message_ffmpeg + "\n")
        window.after(0, _update_gui_on_analysis_completion, "Error", file, error_message_ffmpeg)
    except FileNotFoundError:
        error_message_ffmpeg_path = get_text("analysis_ffmpeg_not_found_error_message")
        append_log("ERROR: " + error_message_ffmpeg_path + "\n")
        window.after(0, _update_gui_on_analysis_completion, "FileNotFound", file, error_message_ffmpeg_path)
    except Exception as e:
        error_message_unknown = get_text("analysis_unknown_error_message").format(error=e)
        append_log("ERROR: " + error_message_unknown + "\n")
        window.after(0, _update_gui_on_analysis_completion, "UnknownError", file, error_message_unknown)
    finally:
        normalization_process = None

# Function to update GUI after process completion (analysis or normalization)
def _update_gui_after_process(status, process_type, message_text="", error_message="", output_file=None):
    # Re-enable buttons after process completion
    _reset_playback_buttons() # This handles play, stop, browse, analyze, start
    cancel_button.config(state=tk.DISABLED)
    progressbar.stop() # Stop progress bar animation
    progressbar.grid_forget() # Hide progress bar
    
    # Hier wird das Fenster nicht mehr geleert, nur noch die Erfolgs/Fehlermeldung hinzugefügt
    # process_info_field.config(state=tk.NORMAL)
    # process_info_field.delete("1.0", tk.END)

    # Handle different process statuses (Success, Error, File Not Found, Unknown Error, Cancel)
    if status == "Success":
        update_process_info(f"\n>>>> {message_text} <<<<") # Hebt die Nachricht hervor
        winsound.Beep(1000, 200) # Play a short beep sound for success
    elif status == "Error":
        update_process_info(f"\n>>>> ERROR: {error_message} <<<<")
        error_title_key = f"{process_type.lower()}_ffmpeg_error_title" # Construct error title key based on process type
        messagebox.showerror(get_text(error_title_key), error_message, parent=window) # Show error message box
        winsound.Beep(1500, 500) # Play error beep sound
    elif status == "FileNotFound":
        update_process_info(f"\n>>>> ERROR: {error_message} <<<<")
        error_title_key = f"{process_type.lower()}_ffmpeg_not_found_error_title" # Construct file not found error title key
        messagebox.showerror(get_text(error_title_key), error_message, parent=window) # Show file not found error message box
        winsound.Beep(1500, 500) # Play error beep sound
    elif status == "UnknownError":
        update_process_info(f"\n>>>> ERROR: {error_message} <<<<")
        error_title_key = f"{process_type.lower()}_unknown_error_title" # Construct unknown error title key
        messagebox.showerror(get_text(error_title_key), get_text(f"{process_type.lower()}_unknown_error_message_title_only"), parent=window) # Show unknown error message box (title only from localized text)
        winsound.Beep(1500, 500) # Play error beep sound
    elif status == "Cancel":
        update_process_info(f"\n>>>> {message_text} <<<<")
        winsound.Beep(500, 300) # Play cancel beep sound

    window.after(100, lambda: window.focus_force()) # Force focus back to main window
    window.after(100, lambda: window.update()) # Update window to reflect changes

# Function to update GUI specifically after audio analysis completion
def _update_gui_on_analysis_completion(status=None, file=None, result=None):
    if status == "Success":
        analysis_results = result # Get analysis results
        output_text = get_text("analysis_completed_message_process_info").format(
                                     filename=os.path.basename(file)
                                 )
        if analysis_results:
            output_text += f"\n{get_text('analysis_result_input_i').format(input_i=analysis_results['input_i'])}"
            output_text += f"\n{get_text('analysis_result_input_tp').format(input_tp=analysis_results['input_tp'])}"
            output_text += f"\n{get_text('analysis_result_lra').format(lra=analysis_results['lra'])}"
        output_text += f"\n{get_text('analysis_hint_log_file')}"
        _update_gui_after_process(status, "Analysis", message_text=output_text) # Update GUI with success status and message
    elif status == "Error":
        _update_gui_after_process(status, "Analysis", error_message=result) # Update GUI with error status and message
    elif status == "FileNotFound":
        _update_gui_after_process(status, "Analysis", error_message=result) # Update GUI with file not found status and message
    elif status == "UnknownError":
        _update_gui_after_process(status, "Analysis", error_message=result) # Update GUI with unknown error status and message
    elif status == "Cancel":
        _update_gui_after_process(status, "Analysis", message_text=get_text("normalization_canceled_by_user_message")) # Update GUI with cancel status and message

# Function to update GUI after normalization completion (reusing _update_gui_after_process)
def update_gui_on_completion(status=None, output_file=None, error_message=None):
    if status == "Success":
        output_text = get_text("normalization_completed_message_process_info").format(output_filename=os.path.basename(output_file))
        output_text += f"\n{get_text('normalization_hint_log_file')}"
        _update_gui_after_process(status, "Normalization", message_text=output_text, output_file=output_file) # Update GUI with success status and message
    elif status == "Error":
        _update_gui_after_process(status, "Normalization", error_message=error_message) # Update GUI with error status and message
    elif status == "FileNotFound":
        _update_gui_after_process(status, "Normalization", error_message=error_message) # Update GUI with file not found status and message
    elif status == "UnknownError":
        _update_gui_after_process(status, "Normalization", error_message=error_message) # Update GUI with unknown error status and message
    elif status == "Cancel":
        _update_gui_after_process(status, "Normalization", message_text=get_text("normalization_canceled_by_user_message")) # Update GUI with cancel status and message

# Function to start the audio normalization process
def start_normalization():
    stop_audio() # Stop any playback before starting normalization
    file = file_input.get() # Get input file path
    output_format = output_format_var.get() # Get selected output format
    lufs_preset_name = lufs_preset_var.get() # Get selected LUFS preset name
    target_lufs_input = ""
    true_peak_preset_name = true_peak_preset_var.get() # Get selected True Peak preset name
    target_true_peak_input = ""
    target_lufs = ""
    target_true_peak = ""

    # Check if input file is selected
    if not file:
        messagebox.showerror(get_text("normalization_no_file_error_title"), # Show error if no file selected
                             get_text("normalization_no_file_error_message"),
                             parent=window)
        return

    # Handle custom LUFS target value if "Custom" preset is selected
    if lufs_preset_name == get_text("lufs_preset_custom"):
        target_lufs_input = lufs_input.get() # Get custom LUFS value from input field
        if not target_lufs_input:
            target_lufs = "-14" # Default to -14 LUFS if custom input is empty
            messagebox.showinfo(get_text("normalization_custom_lufs_note_title"), # Show info message about default LUFS
                                 get_text("normalization_custom_lufs_note_message"), parent=window)
        else:
            try:
                target_lufs_value = float(target_lufs_input) # Convert custom LUFS input to float
                if not -70 <= target_lufs_value <= -5: # Validate LUFS value range
                    messagebox.showerror(
                        get_text("normalization_invalid_lufs_error_title"), # Show error if LUFS value is out of range
                        get_text("normalization_invalid_lufs_error_message"),
                        parent=window)
                    return
                target_lufs = str(target_lufs_value) # Convert valid LUFS value to string
            except ValueError:
                messagebox.showerror(
                    get_text("normalization_invalid_lufs_error_title"), # Show error if LUFS input is not a valid number
                    get_text("normalization_invalid_lufs_error_message"),
                    parent=window)
                return

    else:
        target_lufs = LUFS_PRESETS[ # Get LUFS target value from presets dictionary based on selected preset name
            lufs_preset_name]

    # Handle custom True Peak target value if "Custom" preset is selected
    if true_peak_preset_name == get_text("true_peak_preset_custom"):
        target_true_peak_input = true_peak_input.get() # Get custom True Peak value from input field
        if not target_true_peak_input:
            target_true_peak = "-1" # Default to -1 dBTP if custom input is empty
            messagebox.showinfo(get_text("normalization_custom_tp_note_title"), # Show info message about default True Peak
                                 get_text("normalization_custom_tp_note_message"), parent=window)
        else:
            try:
                target_true_peak_value = float(target_true_peak_input) # Convert custom True Peak input to float
                if not -9 <= target_true_peak_value <= 0: # Validate True Peak value range
                    messagebox.showerror(get_text("normalization_invalid_tp_error_title"), # Show error if True Peak value is out of range
                                         get_text("normalization_invalid_tp_error_message"), parent=window)
                    return
                target_true_peak = str(target_true_peak_value) # Convert valid True Peak value to string
            except ValueError:
                messagebox.showerror(
                    get_text("normalization_invalid_tp_error_title"), # Show error if True Peak input is not a valid number
                    get_text("normalization_invalid_tp_error_message"),
                    parent=window)
                return
    else:
        target_true_peak = TRUE_PEAK_PRESETS[ # Get True Peak target value from presets dictionary based on selected preset name
            true_peak_preset_name]

    # Define format options for different output formats
    format_options = {
        OUTPUT_FORMAT_WAV: {"extension": AUDIO_FILE_EXTENSION_WAV, "codec": CODEC_PCM_F32LE}, # WAV format options
        OUTPUT_FORMAT_MP3: {"extension": AUDIO_FILE_EXTENSION_MP3, "codec": CODEC_LIBMP3LAME, "options": [FFMPEG_OPTION_BITRATE_MP3, FFMPEG_BITRATE_320K]}, # MP3: 320k CBR
        OUTPUT_FORMAT_FLAC: {"extension": AUDIO_FILE_EXTENSION_FLAC, "codec": CODEC_FLAC}, # FLAC format options
        OUTPUT_FORMAT_AAC: {"extension": AUDIO_FILE_EXTENSION_M4A, "codec": CODEC_AAC, "options": [FFMPEG_OPTION_BITRATE_MP3, "512k"]}, # AAC: 512k CBR
        OUTPUT_FORMAT_OGG: {"extension": AUDIO_FILE_EXTENSION_OGG, "codec": CODEC_LIBVORBIS, "options": [FFMPEG_OPTION_BITRATE_MP3, "500k"]} # OGG: Zielbitrate 500k (managed mode)
    }
    selected_format = format_options[
        output_format] # Get format options based on selected output format
    output_file_name_without_extension = os.path.splitext(file)[0] + "-Normalized" # Construct output file name without extension
    output_file = output_file_name_without_extension + selected_format[
        "extension"] # Construct full output file name with extension
    temporary_output_file = output_file_name_without_extension + TEMP_FILE_EXTENSION + selected_format[
        "extension"] # Construct temporary output file name (used during processing)

    # Check if output file already exists and ask for overwrite confirmation
    if os.path.exists(output_file):
        winsound.Beep(1500, 500) # Play warning beep sound
        confirmation = messagebox.askyesno(
             get_text("normalization_overwrite_confirmation_title"), # Show overwrite confirmation dialog
             get_text("normalization_overwrite_confirmation_message").format(output_filename=os.path.basename(output_file)),
             parent=window
         )
        if not confirmation:
             return # Cancel normalization if overwrite is not confirmed

    # Construct FFmpeg command for normalization
    ffmpeg_command = [
        os.path.join(config.ffmpeg_path, FFMPEG_EXECUTABLE_NAME), # Path to FFmpeg executable from config
        "-i", file, # Input audio file path
        "-af", f"loudnorm=I={target_lufs}:TP={target_true_peak}", # Apply loudnorm filter with target LUFS and True Peak values
        "-ar", "48000", # Set output audio sample rate to 48kHz
        "-ac", "2", # Set output audio channels to stereo
    ]

    # Add format-specific options to FFmpeg command if defined
    if "options" in selected_format:
        ffmpeg_command.extend(selected_format["options"])

    ffmpeg_command.extend(["-c:a", selected_format["codec"], temporary_output_file]) # Set audio codec and output temporary file

    # Disable buttons and show progress bar during normalization
    start_button.config(state=tk.DISABLED)
    analyze_button.config(state=tk.DISABLED)
    cancel_button.config(state=tk.NORMAL) # Enable cancel button
    play_button.config(state=tk.DISABLED)
    stop_button.config(state=tk.DISABLED)
    progressbar.grid(row=7, column=0, columnspan=3, sticky="ew", padx=GUI_PADX, pady=GUI_PADY) # Show progress bar
    progressbar.start() # Start progress bar animation

    # --- GEÄNDERT ---
    process_info_field.config(state=tk.NORMAL) # Enable process info field for writing
    process_info_field.delete("1.0", tk.END) # Clear process info field
    process_info_field.config(state=tk.DISABLED) # Disable process info field after writing
    
    start_message = get_text("normalization_start_message").format(
                                 filename=os.path.basename(file_input.get()),
                                 target_lufs=target_lufs,
                                 target_true_peak=target_true_peak,
                                 output_format=output_format,
                                 lufs_preset_name=lufs_preset_name,
                                 true_peak_preset_name=true_peak_preset_name
                             )
    # Zeilenweise in die Info-Box schreiben für bessere Lesbarkeit
    for line in start_message.split('\n'):
        update_process_info(line)
        
    process_info_field.grid() # Ensure process info field is visible

    # Prepare log entry for normalization start
    log_entry_start = f"======================== {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ========================\n"
    log_entry_start += get_text("normalization_start_message").format(
                                 filename=file,
                                 target_lufs=target_lufs,
                                 output_format=output_format,
                                 target_true_peak=target_true_peak,
                                 lufs_preset_name=lufs_preset_name,
                                 true_peak_preset_name=true_peak_preset_name
                             ) + "\n" # Format normalization start message for log
    log_entry_start += get_text("normalization_log_ffmpeg_command") + "\n" + " ".join(ffmpeg_command) + "\n\n" # Add FFmpeg command to log
    append_log(log_entry_start) # Append start log entry to normalization log

    # Create and start a thread for audio normalization to prevent GUI blocking
    thread = threading.Thread(target=normalize_audio_thread_function,
                              args=(ffmpeg_command, temporary_output_file, output_file))
    thread.start()

# --- STARK GEÄNDERTE FUNKTION ---
def normalize_audio_thread_function(ffmpeg_command, temporary_output_file, output_file):
    global normalization_process

    status = None  # Track the process status

    try:
        normalization_process = subprocess.Popen(
            ffmpeg_command, 
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True,
            encoding='utf-8',
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        # Live-Ausgabe verarbeiten
        full_stderr_output = ""
        for line in iter(normalization_process.stderr.readline, ''):
            full_stderr_output += line
            window.after(0, update_process_info, line.strip())

        result_code = normalization_process.wait()
        append_log(full_stderr_output)

        if result_code == 0:
            try:
                if os.path.exists(output_file):
                    os.remove(output_file)
                os.rename(temporary_output_file, output_file)
                status = "Success"
                window.after(0, update_gui_on_completion, "Success", output_file)
            except OSError as e:
                error_message_rename = get_text("normalization_rename_error").format(error=e)
                append_log("ERROR: " + error_message_rename + "\n")
                status = "Error"
                window.after(0, update_gui_on_completion, "Error", output_file, error_message_rename)

        elif result_code == 1 and normalization_process is not None:
             # FFmpeg kann mit Code 1 bei User-Abbruch enden
            if os.path.exists(temporary_output_file):
                os.remove(temporary_output_file)
            status = "Cancel"
            window.after(0, update_gui_on_completion, "Cancel", output_file)
        
        else:
            if os.path.exists(temporary_output_file):
                os.remove(temporary_output_file)
            # Nutze die bereits gesammelte Ausgabe für die Fehlermeldung
            error_message = get_text("normalization_ffmpeg_error_message").format(return_code=result_code, stderr=full_stderr_output)
            append_log("ERROR: " + error_message + "\n")
            status = "Error"
            window.after(0, update_gui_on_completion, "Error", output_file, error_message)

    except FileNotFoundError:
        error_message = get_text("normalization_ffmpeg_not_found_error_message")
        append_log("ERROR: " + error_message + "\n")
        status = "FileNotFound"
        window.after(0, update_gui_on_completion, "FileNotFound", output_file, error_message)
    except Exception as e:
        error_message = get_text("normalization_unknown_error_message").format(error=e)
        append_log("ERROR: " + error_message + "\n")
        status = "UnknownError"
        window.after(0, update_gui_on_completion, "UnknownError", output_file, error_message)
    finally:
        normalization_process = None
        if os.path.exists(temporary_output_file) and status not in ["Success", "Cancel"]:
            try:
                os.remove(temporary_output_file)
            except OSError:
                pass

# Function to cancel the normalization process
def cancel_normalization():
    global normalization_process

    if normalization_process:
        normalization_process.terminate() # Terminate the FFmpeg normalization process
        # Der Thread wird den Abbruch erkennen und die GUI aktualisieren
        update_process_info(get_text("normalization_cancel_process_message"))
    else:
        messagebox.showinfo(get_text("normalization_cancel_title"), # Show info message if no process to cancel
                             get_text("normalization_no_process_cancel_message"),
                             parent=window)

# Function to exit the application
def exit_program():
    stop_audio()
    window.destroy() # Destroy the main application window, exiting the program

# Function to update the state of LUFS input entry based on preset selection
def update_lufs_entry_state(*args):
    if lufs_preset_var.get() == get_text("lufs_preset_custom"): # Check if "Custom" LUFS preset is selected
        lufs_label.config(text=get_text("target_lufs_label_custom_short")) # Change LUFS label to short version for custom input
        lufs_label.grid(row=2, column=0, sticky="w", padx=(0, GUI_LABEL_PADX), pady=(GUI_LABEL_PADY, GUI_PADY)) # Ensure LUFS label is visible
        lufs_input.grid(row=2, column=1, sticky="w", padx=(0, GUI_PADX), pady=(GUI_LABEL_PADY, GUI_PADY)) # Ensure LUFS input is visible
        lufs_input.config(state=tk.NORMAL) # Enable LUFS input field
        lufs_input.delete(0, tk.END) # Clear LUFS input field
        lufs_input.insert(0, "-14") # Set default custom LUFS value to -14
    else:
        lufs_label.config(text=get_text("target_lufs_label_custom")) # Reset LUFS label to default
        lufs_label.grid_forget() # Hide LUFS label when not custom
        lufs_input.grid_forget() # Hide LUFS input field when not custom
        lufs_input.config(state=tk.DISABLED) # Disable LUFS input field when not custom

# Function to update the state of log size input entry based on single log entry checkbox
def update_log_size_state(check_variable, size_input_field):
    if check_variable.get(): # Check if single log entry checkbox is checked
        size_input_field.config(state=tk.DISABLED) # Disable log size input if single log entry is enabled
    else:
        size_input_field.config(state=tk.NORMAL) # Enable log size input if single log entry is disabled

# Function to update the state of True Peak input entry based on preset selection
def update_true_peak_entry_state(*args):
    if true_peak_preset_var.get() == get_text("true_peak_preset_custom"): # Check if "Custom" True Peak preset is selected
        true_peak_label.config(text=get_text("true_peak_label")) # Ensure True Peak label is set to correct text
        true_peak_label.grid(row=2, column=2, sticky="w", padx=(GUI_LABEL_PADX * 2, GUI_LABEL_PADX), pady=(GUI_LABEL_PADY, 0)) # Ensure True Peak label is visible
        true_peak_input.grid(row=2, column=3, sticky="w", padx=(0, GUI_PADX), pady=(GUI_LABEL_PADY, 0)) # Ensure True Peak input is visible
        true_peak_label.config(text=get_text("true_peak_label")) # Redundant line, label already configured above
        true_peak_input.config(state=tk.NORMAL) # Enable True Peak input field
        true_peak_input.delete(0, tk.END) # Clear True Peak input field
        true_peak_input.insert(0, "-1") # Set default custom True Peak value to -1
    else:
        true_peak_label.grid_forget() # Hide True Peak label when not custom
        true_peak_input.grid_forget() # Hide True Peak input field when not custom
        true_peak_input.config(state=tk.DISABLED) # Disable True Peak input field when not custom

# Function to append text to the normalization log file with rolling mechanism
def append_log(text):
    _append_log_with_rolling(LOG_FILE_NAME, text, config) # Call internal log append function with normalization log file name

# Function to append text to the analysis log file with rolling mechanism
def append_analysis_log(text):
    _append_analysis_log_with_rolling(ANALYSIS_LOG_FILE_NAME, text, config) # Call internal log append function with analysis log file name

# Internal function to append text to analysis log file with rolling mechanism
def _append_analysis_log_with_rolling(log_file_name, text, config_obj):
    try:
        log_file_path = log_file_name # Set log file path
        log_size_limit_bytes = config_obj.log_file_size_kb * 1024 # Calculate log file size limit in bytes

        # Handle single log entry mode (truncate log file on each new entry)
        if config_obj.single_log_entry_enabled:
            if os.path.exists(log_file_path):
                with open(log_file_path, "w", encoding="utf-8") as logfile_truncate: # Open log file in write mode to truncate
                    pass # Truncate file by doing nothing

        # Handle log rolling (keep log file size within limit)
        else:
            if os.path.exists(log_file_path) and os.path.getsize(log_file_path) >= log_size_limit_bytes: # Check if log file exists and exceeds size limit
                with open(log_file_path, "r", encoding="utf-8") as logfile_r: # Open log file in read mode
                    lines = logfile_r.readlines() # Read all lines from log file

                lines_to_write = lines[len(lines) // 2:] # Keep only the last half of the lines

                with open(log_file_path, "w", encoding="utf-8") as logfile_w: # Open log file in write mode
                    logfile_w.writelines(lines_to_write) # Write the last half of the lines back to the log file

        with open(log_file_path, "a", encoding="utf-8") as logfile: # Open log file in append mode
            logfile.write(text) # Append the new text to the log file

    except Exception as e:
        print(f"Error writing to log file {log_file_name}: {e}") # Print error message to console if logging fails

# Internal function to append text to log file with rolling mechanism (shared logic with analysis log)
def _append_log_with_rolling(log_file_name, text, config_obj):
    try:
        log_file_path = log_file_name # Set log file path
        log_file_size_bytes = config_obj.log_file_size_kb * 1024 # Calculate log file size limit in bytes

        # Handle single log entry mode (truncate log file on each new entry)
        if config_obj.single_log_entry_enabled:
            if os.path.exists(log_file_path):
                with open(log_file_path, "w", encoding="utf-8") as logfile_truncate: # Open log file in write mode to truncate
                    pass # Truncate file by doing nothing
        # Handle log rolling (keep log file size within limit)
        else:
            if os.path.exists(log_file_path) and os.path.getsize(log_file_path) >= log_file_size_bytes: # Check if log file exists and exceeds size limit
                with open(log_file_path, "r", encoding="utf-8") as logfile_r: # Open log file in read mode
                    lines = logfile_r.readlines() # Read all lines from log file

                lines_to_write = lines[len(lines) // 2:] # Keep only the last half of the lines

                with open(log_file_path, "w", encoding="utf-8") as logfile_w: # Open log file in write mode
                    logfile_w.writelines(lines_to_write) # Write the last half of the lines back to the log file

        with open(log_file_path, "a", encoding="utf-8") as logfile: # Open log file in append mode
            logfile.write(text) # Append the new text to the log file

    except Exception as e:
        print(f"Error writing to log file {log_file_name}: {e}") # Print error message to console if logging fails

# Function to update language selection and apply language changes to GUI
def update_language_selection(event, language_variable):
    global current_language, LUFS_PRESET_NAMES, TRUE_PEAK_PRESET_NAMES # Declare global variables that will be modified
    current_language = language_variable.get() # Get selected language code from combobox
    load_language(current_language) # Load language data for the selected language
    apply_language("options") # Apply language to options dialog
    apply_language("main") # Apply language to main window
    if window.children.get("!toplevel2"): # Check if info dialog is open
        apply_language("info") # Apply language to info dialog

    lufs_preset_var.set(LUFS_PRESET_NAMES[0]) # Reset LUFS preset selection to the first preset in the new language
    true_peak_preset_var.set(TRUE_PEAK_PRESET_NAMES[0]) # Reset True Peak preset selection to the first preset in the new language
    update_lufs_entry_state() # Update LUFS entry state based on new preset selection
    update_true_peak_entry_state() # Update True Peak entry state based on new preset selection

# Initialize main application window
window = tk.Tk()
window.title(f"{get_text('app_title')} v{VERSION}") # Set window title with localized app title and version
window_width = 890
window_height = 630
window.geometry(f"{window_width}x{window_height}") # Set initial window size

# Calculate window position to center on screen
screen_width = window.winfo_screenwidth()
screen_height = window.winfo_screenheight()
x_position = (screen_width - window_width) // 2
y_position = (screen_height - window_height) // 2
window.geometry(f"+{x_position}+{y_position}") # Set window position to center

# Apply style theme
style = Style()
style.theme_use(STYLE_THEME_NAME) # Set Tkinter style theme

# Define GUI color scheme
background_color = "#e0e0e0"
text_color = "#424242"
accent_color = "#b0bec5"
separator_color = "#cccccc"

window.configure(bg=background_color) # Set window background color

# Define standard font and apply to application
standard_font = ("Helvetica", 9)
window.option_add("*Font", standard_font) # Set default font for all widgets

# Configure styles for ttk widgets
style.configure("TButton", padding=4, font=('Helvetica', 9)) # Style for buttons
style.configure("TLabel", font=('Helvetica', 9)) # Style for labels
style.configure("TCombobox", font=('Helvetica', 9)) # Style for comboboxes
style.configure("TEntry", font=('Helvetica', 9)) # Style for entries
style.configure("TCheckbutton", font=('Helvetica', 9)) # Style for checkbuttons
style.configure("TLabelframe", font=('Helvetica', 9, 'bold')) # Style for labelframes
style.configure("TLabelframe.Label", font=('Helvetica', 9, 'bold')) # Style for labelframe labels

# Create menu bar
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label=get_text("menu_file_options"), command=show_options_dialog) # Add Options command to File menu
filemenu.add_separator()
filemenu.add_command(label=get_text("menu_file_exit"), command=exit_program) # Add Exit command to File menu
menubar.add_cascade(label=get_text("menu_file"), menu=filemenu) # Add File menu to menu bar

infomenu = tk.Menu(menubar, tearoff=0)
infomenu.add_command(label=get_text("menu_info_about"), command=show_info_box) # Add About command to Info menu
infomenu.add_command(label=get_text("menu_info_updates"), command=check_for_updates) # Add Updates command to Info menu
menubar.add_cascade(label=get_text("menu_info"), menu=infomenu) # Add Info menu to menu bar
window.config(menu=menubar) # Configure window with menu bar

# Create main content frame
content_frame = tk.Frame(window, padx=GUI_PADX, pady=GUI_PADY,
                            bg=background_color)
content_frame.grid(row=0, column=0, sticky="nsew") # Place content frame in grid

# Create File Selection frame group
file_frame_group = tk.LabelFrame(content_frame, text=get_text("file_selection_group"), padx=GUI_PADX, pady=GUI_PADY, bg=background_color)
file_frame_group.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, GUI_PADY)) # Place file frame group in grid
file_frame_group.columnconfigure(1, weight=1)

file_label = tk.Label(file_frame_group, text=get_text("select_audio_file_label"), anchor="w", bg=background_color)
file_label.grid(row=0, column=0, sticky="w", padx=(0, GUI_LABEL_PADX)) # Place file label in file frame group
file_input = ttk.Entry(file_frame_group, width=GUI_ENTRY_WIDTH_FILE)
file_input.grid(row=0, column=1, sticky="ew") # Place file input entry in file frame group
browse_button = ttk.Button(file_frame_group, text=get_text("browse_file_button"), command=browse_file)
browse_button.grid(row=0, column=2, padx=(GUI_LABEL_PADX*2, 0)) # Place browse button in file frame group

play_button = ttk.Button(file_frame_group, text=get_text("play_audio_button"), command=play_audio, state=tk.DISABLED)
play_button.grid(row=0, column=3, padx=(40, 0))

stop_button = ttk.Button(file_frame_group, text=get_text("stop_audio_button"), command=stop_audio, state=tk.DISABLED)
stop_button.grid(row=0, column=4, padx=(GUI_LABEL_PADX, 0))

# Separator line 1
separator_line_1 = tk.Frame(content_frame, bg=separator_color, height=1)
separator_line_1.grid(row=1, column=0, columnspan=3, sticky="ew", pady=GUI_PADY) # Place separator line in grid

# Loudness Settings frame group
loudness_settings_frame_group = tk.LabelFrame(content_frame, text=get_text("loudness_settings_group"), padx=GUI_PADX, pady=GUI_PADY, bg=background_color)
loudness_settings_frame_group.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(0, GUI_PADY)) # Place loudness settings frame group in grid

lufs_preset_label = tk.Label(loudness_settings_frame_group, text=get_text("lufs_preset_label"), anchor="w", bg=background_color)
lufs_preset_label.grid(row=1, column=0, sticky="w", padx=(0, GUI_LABEL_PADX), pady=(0, GUI_LABEL_PADY)) # Place LUFS preset label
lufs_preset_var = tk.StringVar()
lufs_preset_combobox = Combobox(loudness_settings_frame_group, textvariable=lufs_preset_var, values=LUFS_PRESET_NAMES,
                                  state="readonly", width=GUI_COMBOBOX_WIDTH_LUFS_PRESET)
lufs_preset_combobox.set(LUFS_PRESET_NAMES[0]) # Set default LUFS preset
lufs_preset_combobox.grid(row=1, column=1, sticky="ew", padx=(0, GUI_PADX), pady=(0, GUI_LABEL_PADY)) # Place LUFS preset combobox
lufs_preset_combobox.bind("<<ComboboxSelected>>", update_lufs_entry_state) # Bind LUFS preset combobox selection event

true_peak_preset_label = tk.Label(loudness_settings_frame_group, text=get_text("true_peak_preset_label"), anchor="w", bg=background_color)
true_peak_preset_label.grid(row=1, column=2, sticky="w", padx=(GUI_LABEL_PADX * 2, GUI_LABEL_PADX), pady=(0, GUI_LABEL_PADY)) # Place True Peak preset label
true_peak_preset_var = tk.StringVar()
true_peak_preset_combobox = Combobox(loudness_settings_frame_group, textvariable=true_peak_preset_var,
                                     values=TRUE_PEAK_PRESET_NAMES, state="readonly",
                                     width=GUI_COMBOBOX_WIDTH_TP_PRESET)
true_peak_preset_combobox.set(TRUE_PEAK_PRESET_NAMES[0]) # Set default True Peak preset
true_peak_preset_combobox.grid(row=1, column=3, sticky="ew", padx=(0, GUI_PADX), pady=(0, GUI_LABEL_PADY)) # Place True Peak preset combobox
true_peak_preset_combobox.bind("<<ComboboxSelected>>", update_true_peak_entry_state) # Bind True Peak preset combobox selection event

lufs_label = tk.Label(loudness_settings_frame_group, text=get_text("target_lufs_label_custom"), anchor="w", bg=background_color)
lufs_label.grid(row=2, column=0, sticky="w", padx=(0, GUI_LABEL_PADX), pady=(GUI_LABEL_PADY, GUI_PADY)) # Place LUFS label
lufs_input = ttk.Entry(loudness_settings_frame_group, width=GUI_ENTRY_WIDTH_LUFS_TP, state=tk.DISABLED)
lufs_input.insert(0, "-14") # Set default custom LUFS input value

true_peak_label = tk.Label(loudness_settings_frame_group, text=get_text("true_peak_label"), anchor="w", bg=background_color)
true_peak_label.grid(row=2, column=2, sticky="w", padx=(GUI_LABEL_PADX * 2, GUI_LABEL_PADX), pady=(GUI_LABEL_PADY, 0)) # Place True Peak label

true_peak_input = ttk.Entry(loudness_settings_frame_group, width=GUI_ENTRY_WIDTH_LUFS_TP, state=tk.DISABLED)
true_peak_input.insert(0, "-1") # Set default custom True Peak input value

# Separator line 2
separator_line_2 = tk.Frame(content_frame, bg=separator_color, height=1)
separator_line_2.grid(row=3, column=0, columnspan=3, sticky="ew", pady=GUI_PADY) # Place separator line in grid

# Output Format frame group
output_format_frame_group = tk.LabelFrame(content_frame, text=get_text("output_format_group"), padx=GUI_PADX, pady=GUI_PADY, bg=background_color)
output_format_frame_group.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(0, GUI_PADY)) # Place output format frame group in grid

output_format_label = tk.Label(output_format_frame_group, text=get_text("output_format_file_format_label"), anchor="w", bg=background_color)
output_format_label.grid(row=1, column=0, sticky="w", padx=(0, GUI_LABEL_PADX), pady=(0, GUI_LABEL_PADY)) # Place output format label
output_format_var = tk.StringVar()
output_format_combobox = Combobox(output_format_frame_group, textvariable=output_format_var,
                                   values=OUTPUT_FORMATS_LIST, state="readonly")
output_format_combobox.set(OUTPUT_FORMAT_WAV) # Set default output format to WAV
output_format_combobox.grid(row=1, column=1, sticky="w", padx=(0, GUI_PADX), pady=(0, GUI_LABEL_PADY)) # Place output format combobox

# Separator line 3
separator_line_3 = tk.Frame(content_frame, bg=separator_color, height=1)
separator_line_3.grid(row=5, column=0, columnspan=3, sticky="ew", pady=GUI_PADY) # Place separator line in grid

# Buttons frame
buttons_frame = tk.Frame(content_frame, bg=background_color)
buttons_frame.grid(row=6, column=0, columnspan=3, pady=(GUI_PADY, GUI_PADY),
                    sticky="ew") # Place buttons frame in grid

analyze_button = ttk.Button(buttons_frame, text=get_text("analyze_audio_button"), command=analyze_audio)
analyze_button.grid(row=0, column=0, sticky="ew", padx=(0, GUI_BUTTON_PADX)) # Place analyze button

start_button = ttk.Button(buttons_frame, text=get_text("start_normalization_button"), command=start_normalization)
start_button.grid(row=0, column=1, sticky="ew", padx=(0, GUI_BUTTON_PADX)) # Place start normalization button

cancel_button = ttk.Button(buttons_frame, text=get_text("cancel_normalization_button"), command=cancel_normalization, state=tk.DISABLED)
cancel_button.grid(row=0, column=2, sticky="ew") # Place cancel normalization button

buttons_frame.columnconfigure(0, weight=1) # Configure button frame column weights for resizing
buttons_frame.columnconfigure(1, weight=1)
buttons_frame.columnconfigure(2, weight=1)

# Progress bar
progressbar = Progressbar(content_frame, mode='indeterminate') # Create progress bar widget

# --- GEÄNDERT: Process Information Frame mit Scrollbar ---
process_information_frame_group = tk.LabelFrame(content_frame, text=get_text("process_information_group"), padx=GUI_PADX, pady=GUI_PADY, bg=background_color)
process_information_frame_group.grid(row=8, column=0, columnspan=3, sticky="nsew") # Place process information frame group in grid

process_info_field = tk.Text(process_information_frame_group, height=GUI_PROCESS_INFO_HEIGHT, width=GUI_PROCESS_INFO_WIDTH,
                              wrap=tk.WORD, state=tk.DISABLED, bg=PROCESS_INFO_BACKGROUND_COLOR, font=('Helvetica', 9))
process_info_field.grid(row=0, column=0, sticky="nsew") # Textfeld in Spalte 0

# Scrollbar hinzufügen
scrollbar = Scrollbar(process_information_frame_group, orient="vertical", command=process_info_field.yview)
scrollbar.grid(row=0, column=1, sticky="ns") # Scrollbar in Spalte 1
process_info_field.config(yscrollcommand=scrollbar.set) # Scrollbar mit Textfeld verbinden

process_information_frame_group.columnconfigure(0, weight=1) # Textfeld soll sich ausdehnen
process_information_frame_group.rowconfigure(0, weight=1) # Zeile soll sich ausdehnen


content_frame.columnconfigure(1, weight=1) # Configure content frame column and row weights for resizing
content_frame.rowconfigure(8, weight=1)
window.columnconfigure(0, weight=1) # Configure window column and row weights for resizing
window.rowconfigure(0, weight=1)

# Load language and apply to GUI
load_language(current_language) # Load initial language data
apply_language("main") # Apply initial language to main window

# Initialize LUFS and True Peak entry states
update_lufs_entry_state() # Set initial LUFS entry state
update_true_peak_entry_state() # Set initial True Peak entry state

# Re-create menu bar after applying language (to ensure localized menu labels)
menubar = tk.Menu(window)
filemenu = tk.Menu(menubar, tearoff=0)
filemenu.add_command(label=get_text("menu_file_options"), command=show_options_dialog) # Re-add Options command to File menu
filemenu.add_separator()
filemenu.add_command(label=get_text("menu_file_exit"), command=exit_program) # Re-add Exit command to File menu
menubar.add_cascade(label=get_text("menu_file"), menu=filemenu) # Re-add File menu to menu bar

infomenu = tk.Menu(menubar, tearoff=0)
infomenu.add_command(label=get_text("menu_info_about"), command=show_info_box) # Re-add About command to Info menu
infomenu.add_command(label=get_text("menu_info_updates"), command=check_for_updates) # Re-add Updates command to Info menu
menubar.add_cascade(label=get_text("menu_info"), menu=infomenu) # Re-add Info menu to menu bar
window.config(menu=menubar) # Re-configure window with menu bar

# Start the Tkinter main event loop, which runs the GUI
window.mainloop()
