"""
profiles.py
Persistence helpers for saving, loading, and resetting user presets.
"""

import os
import json
from tkinter import filedialog, messagebox
import core
import i18n
import constants
from constants import PROFILE_FOLDER_NAME, DEFAULT_MASTERING_PRESET, PROFILE_ORIGINAL_VALUE

get_text = i18n.get_text

def get_profile_dir():
    """Returns the profile storage directory, creating it on demand."""
    profile_dir = os.path.join(core.get_base_path(), PROFILE_FOLDER_NAME)
    if not os.path.exists(profile_dir):
        try:
            os.makedirs(profile_dir)
        except Exception:
            pass
    return profile_dir

def _get_original_profile_aliases():
    """Returns every known legacy value that should be treated as the original/default selection."""
    aliases = {PROFILE_ORIGINAL_VALUE, "Original / Default"}
    try:
        current_original = get_text("output_original_default")
        if current_original and not current_original.startswith("["):
            aliases.add(current_original)
    except Exception:
        pass

    try:
        lang_dir = os.path.join(core.get_base_path(), constants.LANG_FOLDER_NAME)
        if os.path.isdir(lang_dir):
            for filename in os.listdir(lang_dir):
                if not filename.lower().endswith(constants.LANG_FILE_EXTENSION):
                    continue
                file_path = os.path.join(lang_dir, filename)
                if not os.path.isfile(file_path):
                    continue
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lang_data = json.load(f)
                    legacy_value = lang_data.get("output_original_default")
                    if isinstance(legacy_value, str) and legacy_value.strip():
                        aliases.add(legacy_value.strip())
                except Exception:
                    continue
    except Exception:
        pass

    return {str(alias).strip() for alias in aliases if str(alias).strip()}

def _is_original_profile_value(value):
    """Checks whether a stored profile value means 'original/default'."""
    if value is None:
        return False
    return str(value).strip() in _get_original_profile_aliases()

def _apply_loaded_output_setting(combo, variable, value):
    """Restores a combobox value while preserving legacy original/default selections."""
    if _is_original_profile_value(value):
        combo.current(0)
    elif value is not None:
        variable.set(value)

def save_profile(app):
    """Serializes the current UI state to a profile JSON file."""
    profile_dir = get_profile_dir()
    filetypes = [(get_text("profile_json_files"), "*.json")]
    filepath = filedialog.asksaveasfilename(
        title=get_text("profile_dialog_save_title"),
        initialdir=profile_dir,
        defaultextension=".json",
        filetypes=filetypes,
        parent=app.root
    )
    if not filepath:
        return

    profile_data = {
        "lufs_preset": app.lufs_preset_var.get(),
        "true_peak_preset": app.true_peak_preset_var.get(),
        "mastering_preset": i18n.get_mastering_preset_name_from_display(app.mastering_preset_var.get()),
        "lufs_entry": app.lufs_entry_var.get(),
        "tp_entry": app.tp_entry_var.get(),
        "mode": app.mode_var.get(),
        "output_format": app.output_format_var.get(),
        "output_samplerate": PROFILE_ORIGINAL_VALUE if app.samplerate_combobox.current() == 0 else app.output_samplerate_var.get(),
        "output_quality": PROFILE_ORIGINAL_VALUE if app.quality_combobox.current() == 0 else app.output_quality_var.get()
    }

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(profile_data, f, indent=4, ensure_ascii=False)
    except Exception as e:
        messagebox.showerror(get_text("profile_error_title"), str(e), parent=app.root)

def set_lufs_preset(app, preset_display_val, lufs_val):
    """Restores the LUFS preset from saved profile data or by matching the stored value."""
    current_presets = i18n.LUFS_PRESETS
    if preset_display_val in current_presets:
        app.lufs_preset_var.set(preset_display_val)
    else:
        found = False
        for disp, val in current_presets.items():
            if val == lufs_val:
                app.lufs_preset_var.set(disp)
                found = True
                break
        if not found:
            app.lufs_preset_var.set(get_text("preset_custom"))

def set_tp_preset(app, preset_display_val, tp_val):
    """Restores the true-peak preset from saved profile data or by matching the stored value."""
    current_presets = i18n.TRUE_PEAK_PRESETS
    if preset_display_val in current_presets:
        app.true_peak_preset_var.set(preset_display_val)
    else:
        found = False
        for disp, val in current_presets.items():
            if val == tp_val:
                app.true_peak_preset_var.set(disp)
                found = True
                break
        if not found:
            app.true_peak_preset_var.set(get_text("preset_custom"))

def load_profile(app):
    """Loads a saved profile and applies it to the active UI."""
    profile_dir = get_profile_dir()
    filetypes = [(get_text("profile_json_files"), "*.json")]
    filepath = filedialog.askopenfilename(
        title=get_text("profile_dialog_load_title"),
        initialdir=profile_dir,
        filetypes=filetypes,
        parent=app.root
    )
    if not filepath:
        return

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        messagebox.showerror(
            get_text("profile_error_title"),
            get_text("profile_error_invalid_file"),
            parent=app.root
        )
        return

    required_keys = ["lufs_preset", "true_peak_preset", "mode", "output_format"]
    if not isinstance(data, dict) or not all(k in data for k in required_keys):
        messagebox.showerror(
            get_text("profile_error_title"),
            get_text("profile_error_invalid_file"),
            parent=app.root
        )
        return

    set_lufs_preset(app, data.get("lufs_preset", ""), data.get("lufs_entry", ""))
    set_tp_preset(app, data.get("true_peak_preset", ""), data.get("tp_entry", ""))

    internal_mastering = data.get("mastering_preset", DEFAULT_MASTERING_PRESET)
    app.mastering_preset_var.set(i18n.get_mastering_preset_display_name(internal_mastering))
    app.update_mastering_help_text()

    app.update_entry_states()

    if app.lufs_preset_var.get() == get_text("preset_custom"):
        app.lufs_entry_var.set(data.get("lufs_entry", ""))
    if app.true_peak_preset_var.get() == get_text("preset_custom"):
        app.tp_entry_var.set(data.get("tp_entry", ""))

    app.mode_var.set(data.get("mode", "linear"))

    app.output_format_var.set(data.get("output_format", "WAV"))
    app.on_format_changed()

    loaded_sr = data.get("output_samplerate", "")
    _apply_loaded_output_setting(app.samplerate_combobox, app.output_samplerate_var, loaded_sr)

    loaded_quality = data.get("output_quality", "")
    _apply_loaded_output_setting(app.quality_combobox, app.output_quality_var, loaded_quality)

    app.update_output_format_info()

def reset_profile_to_defaults(app):
    """Restores all profile-related controls to their defaults."""
    if i18n.LUFS_PRESET_NAMES:
        app.lufs_preset_var.set(i18n.LUFS_PRESET_NAMES[0])
    if i18n.TRUE_PEAK_PRESET_NAMES:
        app.true_peak_preset_var.set(i18n.TRUE_PEAK_PRESET_NAMES[0])
    app.mastering_preset_var.set(i18n.get_mastering_preset_display_name(DEFAULT_MASTERING_PRESET))
    app.update_mastering_help_text()
    app.update_entry_states()

    app.mode_var.set("linear")

    app.output_format_var.set("WAV")
    app.on_format_changed()
    app.samplerate_combobox.current(0)
    app.quality_combobox.current(0)
    app.update_output_format_info()