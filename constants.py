"""
constants.py
Contains all static application data, metadata, format lists, and layout constants.
"""

# --- Build Metadata ---
VERSION = "4.1.0"
INTERNAL_VERSION = "dev.10b"
EDITION_NAME = "Kontrollraum Edition 🖥️"
BUILD_DATE = "2026-06-11"
AUTHOR = "melcom (Andreas Thomas Urban)"


# --- User Interface Spacing ---
GUI_PADX = 15
GUI_PADY = 6
GUI_ENTRY_WIDTH_FILE = 58
GUI_ENTRY_WIDTH_LUFS_TP = 10
GUI_COMBOBOX_WIDTH_LUFS_PRESET = 34
GUI_COMBOBOX_WIDTH_TP_PRESET = 42
DIALOG_PADX_OPTIONS = 10
DIALOG_PADY_OPTIONS = 5


# --- Runtime Files ---
CONFIG_FILE_NAME = "options.ini"
LOG_FILE_NAME = "normalization.log"
ANALYSIS_LOG_FILE_NAME = "analysis.log"
FFMPEG_EXECUTABLE_NAME = "ffmpeg.exe"
FFPLAY_EXECUTABLE_NAME = "ffplay.exe"
FFPROBE_EXECUTABLE_NAME = "ffprobe.exe"
TEMP_FILE_EXTENSION = ".temp"
PROFILE_FOLDER_NAME = "profile"
PROFILE_ORIGINAL_VALUE = "__ORIGINAL__"


# --- Audio Formats ---
AUDIO_FILE_EXTENSIONS = [
    (".wav", "WAV"),
    (".mp3", "MP3"),
    (".flac", "FLAC"),
    (".aac", "AAC"),
    (".ogg", "OGG"),
    (".m4a", "M4A")
]


# --- Output Formats ---
OUTPUT_FORMATS_LIST = ["WAV", "MP3", "FLAC", "M4A", "OGG"]


# --- Configuration Keys ---
CONFIG_SECTION_SETTINGS = "Settings"
CONFIG_KEY_FFMPEG_PATH = "ffmpeg_path"
CONFIG_KEY_LOG_FILE_SIZE = "log_file_size_kb"
CONFIG_KEY_SINGLE_LOG_ENTRY = "single_log_entry_enabled"
CONFIG_KEY_LANGUAGE = "language"


# --- Localization ---
LANGUAGE_CODES_LIST = []  # Populated dynamically from /lang/ at runtime.
DEFAULT_LANGUAGE_CODE = "en_US"
LANG_FOLDER_NAME = "lang"
LANG_FILE_EXTENSION = ".json"


# --- Theme Modes ---
CONFIG_KEY_THEME_MODE = "theme_mode"
DEFAULT_THEME_MODE = "light"
THEME_MODES_LIST = []


# --- Sample Rates ---
SAMPLE_RATES_LIST = [
    "Original / Default",
    "192000 Hz",
    "176400 Hz",
    "96000 Hz",
    "88200 Hz",
    "48000 Hz",
    "44100 Hz",
    "32000 Hz",
    "24000 Hz",
    "22050 Hz",
    "16000 Hz",
    "11025 Hz",
    "8000 Hz"
]


# --- Output Quality Presets ---
FORMAT_QUALITY_OPTIONS = {
    "WAV": [
        "Original / Default",
        "64 Bit Floating Point",
        "32 Bit Floating Point",
        "32 Bit Integer (linear)",
        "24 Bit Integer (linear)",
        "16 Bit Integer (linear)",
        "8 Bit Unsigned (linear)"
    ],
    "FLAC": [
        "Original / Default",
        "24 Bit Lossless",
        "16 Bit Lossless"
    ],
    "MP3": [
        "Original / Default",
        "320 kbps (CBR)",
        "256 kbps (CBR)",
        "192 kbps (CBR)",
        "128 kbps (CBR)",
        "V0 (~245 kbps, VBR)",
        "V2 (~190 kbps, VBR)",
        "V4 (~165 kbps, VBR)",
        "V6 (~115 kbps, VBR)"
    ],
    "M4A": [
        "Original / Default",
        "320 kbps (CBR)",
        "256 kbps (CBR)",
        "192 kbps (CBR)",
        "128 kbps (CBR)"
    ],
    "OGG": [
        "Original / Default",
        "q10 (~500 kbps, VBR)",
        "320 kbps (CBR)",
        "q6 (~192 kbps, VBR)",
        "q4 (~128 kbps, VBR)"
    ]
}

WAV_CODEC_MAP = {
    "Original / Default": None,
    "64 Bit Floating Point": "pcm_f64le",
    "32 Bit Floating Point": "pcm_f32le",
    "32 Bit Integer (linear)": "pcm_s32le",
    "24 Bit Integer (linear)": "pcm_s24le",
    "16 Bit Integer (linear)": "pcm_s16le",
    "8 Bit Unsigned (linear)": "pcm_u8"
}

FLAC_AF_MAP = {
    "Original / Default": [],
    "24 Bit Lossless": ["-af", "aformat=s32"],
    "16 Bit Lossless": ["-af", "aformat=s16"]
}

MP3_ENCODER_MAP = {
    "Original / Default": None,
    "320 kbps (CBR)": ["-b:a", "320k"],
    "256 kbps (CBR)": ["-b:a", "256k"],
    "192 kbps (CBR)": ["-b:a", "192k"],
    "128 kbps (CBR)": ["-b:a", "128k"],
    "V0 (~245 kbps, VBR)": ["-q:a", "0"],
    "V2 (~190 kbps, VBR)": ["-q:a", "2"],
    "V4 (~165 kbps, VBR)": ["-q:a", "4"],
    "V6 (~115 kbps, VBR)": ["-q:a", "6"]
}

M4A_ENCODER_MAP = {
    "Original / Default": None,
    "320 kbps (CBR)": ["-b:a", "320k"],
    "256 kbps (CBR)": ["-b:a", "256k"],
    "192 kbps (CBR)": ["-b:a", "192k"],
    "128 kbps (CBR)": ["-b:a", "128k"]
}

OGG_ENCODER_MAP = {
    "Original / Default": None,
    "q10 (~500 kbps, VBR)": ["-q:a", "10"],
    "320 kbps (CBR)": ["-b:a", "320k"],
    "q6 (~192 kbps, VBR)": ["-q:a", "6"],
    "q4 (~128 kbps, VBR)": ["-q:a", "4"]
}

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