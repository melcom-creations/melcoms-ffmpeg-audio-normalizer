"""
i18n.py
Handles language loading, translation mapping, and dynamic preset translations.
"""

import json
import os
import constants
from core import get_base_path, app_config

# --- Translation State ---
language_data = {}
LUFS_PRESETS = {}
TRUE_PEAK_PRESETS = {}
LUFS_PRESET_NAMES = []
TRUE_PEAK_PRESET_NAMES = []
MASTERING_PRESET_DISPLAY_NAMES = []
MASTERING_PRESET_DISPLAY_TO_INTERNAL = {}

_VALIDATED_LANGUAGE_CODES = []


# --- Language Discovery ---
def load_languages():
    """Scans /lang/ for valid JSON files and refreshes the runtime language list."""
    global _VALIDATED_LANGUAGE_CODES

    base_path = get_base_path()
    lang_dir = os.path.join(base_path, constants.LANG_FOLDER_NAME)
    discovered_codes = []

    if os.path.isdir(lang_dir):
        try:
            for filename in sorted(os.listdir(lang_dir), key=lambda name: name.lower()):
                if not filename.lower().endswith(constants.LANG_FILE_EXTENSION):
                    continue

                file_path = os.path.join(lang_dir, filename)
                if not os.path.isfile(file_path):
                    continue

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    if isinstance(data, dict):
                        discovered_codes.append(os.path.splitext(filename)[0])
                except Exception:
                    # Broken or incomplete JSON files are ignored by design.
                    continue
        except Exception:
            discovered_codes = []

    if constants.DEFAULT_LANGUAGE_CODE in discovered_codes:
        ordered_codes = [constants.DEFAULT_LANGUAGE_CODE] + sorted(
            [code for code in discovered_codes if code != constants.DEFAULT_LANGUAGE_CODE],
            key=str.lower
        )
    elif discovered_codes:
        ordered_codes = sorted(discovered_codes, key=str.lower)
    else:
        ordered_codes = [constants.DEFAULT_LANGUAGE_CODE]

    _VALIDATED_LANGUAGE_CODES = ordered_codes
    constants.LANGUAGE_CODES_LIST.clear()
    constants.LANGUAGE_CODES_LIST.extend(ordered_codes)
    return list(constants.LANGUAGE_CODES_LIST)


def get_available_language_codes(refresh=False):
    """Returns the currently available language codes, optionally rescanning /lang/."""
    if refresh or not constants.LANGUAGE_CODES_LIST:
        return load_languages()
    return list(constants.LANGUAGE_CODES_LIST)


def _normalize_language_code(language_code):
    """Returns a safe language code that is present in the available runtime list."""
    available_codes = get_available_language_codes()
    if language_code in available_codes:
        return language_code
    if constants.DEFAULT_LANGUAGE_CODE in available_codes:
        return constants.DEFAULT_LANGUAGE_CODE
    return available_codes[0] if available_codes else constants.DEFAULT_LANGUAGE_CODE


# --- Translation Loading ---
def load_language(language_code):
    """Loads localized strings and preset values from the selected JSON language file."""
    global language_data, LUFS_PRESETS, TRUE_PEAK_PRESETS
    global LUFS_PRESET_NAMES, TRUE_PEAK_PRESET_NAMES

    load_languages()
    selected_code = _normalize_language_code(language_code)

    language_payload = None
    for candidate_code in (selected_code, constants.DEFAULT_LANGUAGE_CODE):
        path = os.path.join(
            get_base_path(),
            constants.LANG_FOLDER_NAME,
            f"{candidate_code}{constants.LANG_FILE_EXTENSION}"
        )
        try:
            with open(path, "r", encoding="utf-8") as f:
                loaded_data = json.load(f)
            if not isinstance(loaded_data, dict):
                raise ValueError("Language file must contain a JSON object.")
            language_payload = loaded_data
            break
        except Exception:
            continue

    if language_payload is None:
        language_payload = {}

    language_data = language_payload
    LUFS_PRESETS = language_data.get("lufs_presets", {}) if isinstance(language_data, dict) else {}
    TRUE_PEAK_PRESETS = language_data.get("true_peak_presets", {}) if isinstance(language_data, dict) else {}

    LUFS_PRESET_NAMES.clear()
    LUFS_PRESET_NAMES.extend(list(LUFS_PRESETS.keys()))

    TRUE_PEAK_PRESET_NAMES.clear()
    TRUE_PEAK_PRESET_NAMES.extend(list(TRUE_PEAK_PRESETS.keys()))

    _refresh_mastering_display_mappings()

    if selected_code != language_code and getattr(app_config, "language", None) != selected_code:
        app_config.language = selected_code


def _ensure_language_data_loaded():
    """Ensures that translation data has been loaded before use."""
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
    """Resolves a localized mastering preset label to its internal preset key."""
    if not mastering_preset_name:
        return constants.DEFAULT_MASTERING_PRESET
    if mastering_preset_name in constants.MASTERING_PRESETS:
        return mastering_preset_name
    _ensure_language_data_loaded()
    return MASTERING_PRESET_DISPLAY_TO_INTERNAL.get(mastering_preset_name, constants.DEFAULT_MASTERING_PRESET)


def get_mastering_preset_display_name(mastering_preset_name):
    """Returns the localized display name for a mastering preset."""
    preset_name = get_mastering_preset_name_from_display(mastering_preset_name)
    _ensure_language_data_loaded()
    display_name = get_text(f"mastering_character_preset_{preset_name.lower().replace(' ', '_')}")
    if display_name.startswith("[") and display_name.endswith("]"):
        return preset_name
    return display_name


def get_mastering_help_text(mastering_preset_name):
    """Returns the localized help text for a mastering preset."""
    preset_name = get_mastering_preset_name_from_display(mastering_preset_name)
    key = f"mastering_character_help_{preset_name.lower().replace(' ', '_')}"
    text = get_text(key)
    if text.startswith("[") and text.endswith("]"):
        return constants.MASTERING_HELP_FALLBACKS.get(preset_name, "")
    return text


load_languages()
load_language(app_config.language)
