# -*- coding: utf-8 -*-
"""
constants.py
Contains all static application data, metadata, format lists, and layout constants.
"""

# --- Metadata ---
VERSION = "4.0.2"
INTERNAL_VERSION = "dev.02"
EDITION_NAME = "Läderlappen Edition 🦇"
BUILD_DATE = "2026-05-28"
AUTHOR = "melcom (Andreas Thomas Urban)"

# --- GUI Layout Constants ---
GUI_PADX = 15
GUI_PADY = 6
GUI_ENTRY_WIDTH_FILE = 58
GUI_ENTRY_WIDTH_LUFS_TP = 10
GUI_COMBOBOX_WIDTH_LUFS_PRESET = 34
GUI_COMBOBOX_WIDTH_TP_PRESET = 42
DIALOG_PADX_OPTIONS = 10
DIALOG_PADY_OPTIONS = 5

# --- File System & Configuration Constants ---
CONFIG_FILE_NAME = "options.ini"
LOG_FILE_NAME = "normalization.log"
ANALYSIS_LOG_FILE_NAME = "analysis.log"
FFMPEG_EXECUTABLE_NAME = "ffmpeg.exe"
FFPLAY_EXECUTABLE_NAME = "ffplay.exe"
FFPROBE_EXECUTABLE_NAME = "ffprobe.exe"
TEMP_FILE_EXTENSION = ".temp"

# --- Supported Media Extensions ---
AUDIO_FILE_EXTENSIONS = [
    (".wav", "WAV"),
    (".mp3", "MP3"),
    (".flac", "FLAC"),
    (".aac", "AAC"),
    (".ogg", "OGG"),
    (".m4a", "M4A")
]

# --- Supported Output Formats ---
OUTPUT_FORMATS_LIST = ["WAV", "MP3", "FLAC", "AAC", "OGG"]

# --- Configuration Keys (INI) ---
CONFIG_SECTION_SETTINGS = "Settings"
CONFIG_KEY_FFMPEG_PATH = "ffmpeg_path"
CONFIG_KEY_LOG_FILE_SIZE = "log_file_size_kb"
CONFIG_KEY_SINGLE_LOG_ENTRY = "single_log_entry_enabled"
CONFIG_KEY_LANGUAGE = "language"

# --- Language Settings ---
LANGUAGE_CODES_LIST = ["en_US", "de_DE", "pl_PL", "sv_SE"]
DEFAULT_LANGUAGE_CODE = "en_US"
LANG_FOLDER_NAME = "lang"
LANG_FILE_EXTENSION = ".json"

# --- Theme Settings ---
CONFIG_KEY_THEME_MODE = "theme_mode"
DEFAULT_THEME_MODE = "light"
THEME_MODES_LIST = ["light", "läderlappen", "melcom", "aquamarine & blue", "midnight", "modernlight"]

# --- FFmpeg Codec Mappings & Options ---
CODECS = {
    "WAV": "pcm_f32le",
    "MP3": "libmp3lame",
    "FLAC": "flac",
    "AAC": "aac",
    "OGG": "libvorbis"
}

FFMPEG_OPTIONS = {
    "MP3": ["-b:a", "320k"],
    "AAC": ["-b:a", "256k"],
    "OGG": ["-b:a", "500k"]
}

# --- Mastering Presets ---
MASTERING_PRESETS = {
    "Transparent": {
        "enabled": False,
    },
    "Cohesive": {
        "enabled": True,
        "compressor": {
            "threshold": "-16dB",
            "ratio": 1.7,
            "attack": 30,
            "release": 350,
            "makeup": 1.0,
        },
        "softclip": {
            "type": "tanh",
            "threshold": 0.985,
            "output": 0.98,
        },
    },
    "Punchy": {
        "enabled": True,
        "compressor": {
            "threshold": "-18dB",
            "ratio": 2.5,
            "attack": 20,
            "release": 250,
            "makeup": 1.5,
        },
        "softclip": {
            "type": "tanh",
            "threshold": 0.96,
            "output": 0.98,
        },
    },
    "Aggressive": {
        "enabled": True,
        "compressor": {
            "threshold": "-22dB",
            "ratio": 3.5,
            "attack": 10,
            "release": 180,
            "makeup": 2.0,
        },
        "softclip": {
            "type": "cubic",
            "threshold": 0.94,
            "output": 0.97,
        },
    },
}

DEFAULT_MASTERING_PRESET = "Transparent"
MASTERING_PRESET_NAMES = list(MASTERING_PRESETS.keys())

MASTERING_HELP_FALLBACKS = {
    "Transparent": "Pure loudness normalization without additional coloration.",
    "Cohesive": "Adds gentle glue and smoothness with subtle compression and soft clipping.",
    "Punchy": "Enhances punch and energy with stronger compression and a tighter transient response.",
    "Aggressive": "Adds heavy compression and stronger saturation for a louder, denser sound.",
}