# -*- coding: utf-8 -*-
"""
i18n.py
Handles language loading, translation mapping, and dynamic preset translations.
"""

import json
import os
import constants
from core import get_base_path, app_config

language_data = {}
LUFS_PRESETS = {}
TRUE_PEAK_PRESETS = {}
LUFS_PRESET_NAMES = []
TRUE_PEAK_PRESET_NAMES = []
MASTERING_PRESET_DISPLAY_NAMES = []
MASTERING_PRESET_DISPLAY_TO_INTERNAL = {}

def load_language(language_code):
    """Loads localized strings and preset values from the selected JSON language file."""
    global language_data, LUFS_PRESETS, TRUE_PEAK_PRESETS
    global LUFS_PRESET_NAMES, TRUE_PEAK_PRESET_NAMES
    try:
        base_path = get_base_path()
        path = os.path.join(base_path, constants.LANG_FOLDER_NAME, f"{language_code}{constants.LANG_FILE_EXTENSION}")
        with open(path, "r", encoding="utf-8") as f:
            language_data = json.load(f)
            
        LUFS_PRESETS = language_data.get("lufs_presets", {})
        TRUE_PEAK_PRESETS = language_data.get("true_peak_presets", {})
        
        LUFS_PRESET_NAMES.clear()
        LUFS_PRESET_NAMES.extend(list(LUFS_PRESETS.keys()))
        
        TRUE_PEAK_PRESET_NAMES.clear()
        TRUE_PEAK_PRESET_NAMES.extend(list(TRUE_PEAK_PRESETS.keys()))
        
        _refresh_mastering_display_mappings()
    except (FileNotFoundError, json.JSONDecodeError):
        if language_code != constants.DEFAULT_LANGUAGE_CODE:
            load_language(constants.DEFAULT_LANGUAGE_CODE)

def _ensure_language_data_loaded():
    if not language_data:
        load_language(app_config.language)

def _refresh_mastering_display_mappings():
    """Maps internal preset keys to their current localized UI display names."""
    global MASTERING_PRESET_DISPLAY_NAMES, MASTERING_PRESET_DISPLAY_TO_INTERNAL
    MASTERING_PRESET_DISPLAY_NAMES.clear()
    MASTERING_PRESET_DISPLAY_NAMES.extend([
        get_text(f"mastering_character_preset_{preset_name.lower().replace(' ', '_')}")
        for preset_name in constants.MASTERING_PRESET_NAMES
    ])
    MASTERING_PRESET_DISPLAY_TO_INTERNAL.clear()
    MASTERING_PRESET_DISPLAY_TO_INTERNAL.update(dict(zip(MASTERING_PRESET_DISPLAY_NAMES, constants.MASTERING_PRESET_NAMES)))

def get_text(key: str, **kwargs) -> str:
    """Retrieves and formats a localized string from the loaded dictionary."""
    return language_data.get(key, f"[{key}]").format(**kwargs)

def get_mastering_preset_name_from_display(mastering_preset_name):
    if not mastering_preset_name: return constants.DEFAULT_MASTERING_PRESET
    if mastering_preset_name in constants.MASTERING_PRESETS: return mastering_preset_name
    _ensure_language_data_loaded()
    return MASTERING_PRESET_DISPLAY_TO_INTERNAL.get(mastering_preset_name, constants.DEFAULT_MASTERING_PRESET)

def get_mastering_preset_display_name(mastering_preset_name):
    preset_name = get_mastering_preset_name_from_display(mastering_preset_name)
    _ensure_language_data_loaded()
    display_name = get_text(f"mastering_character_preset_{preset_name.lower().replace(' ', '_')}")
    if display_name.startswith("[") and display_name.endswith("]"): return preset_name
    return display_name

def get_mastering_help_text(mastering_preset_name):
    preset_name = get_mastering_preset_name_from_display(mastering_preset_name)
    key = f"mastering_character_help_{preset_name.lower().replace(' ', '_')}"
    text = get_text(key)
    if text.startswith("[") and text.endswith("]"): return constants.MASTERING_HELP_FALLBACKS.get(preset_name, "")
    return text

# Initializes the default language on module import
load_language(app_config.language)