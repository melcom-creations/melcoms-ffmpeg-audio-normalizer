"""
inspector.py
UI, metadata editing, artwork visualization, and background analysis for the Audio Properties Inspector window.
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import threading
import json
import re
import tempfile

from audio import FFMpegProcessor
import i18n
import core
import utils

def get_inspect_text(key, fallback):
    """Safely retrieves a localized key or falls back to a default value if missing."""
    text = i18n.get_text(key)
    if text.startswith("[") and text.endswith("]"):
        return fallback
    return text

# --- Inspector Dialog ---
class AudioInspectorDialog:
    """Displays metadata editing, artwork, and analysis tools for a selected audio file."""
    def __init__(self, parent, app, file_path, colors, ffmpeg_dir):
        """Initializes the AudioInspectorDialog."""
        self.parent = parent
        self.app = app
        self.file_path = file_path
        self.colors = colors
        self.ffmpeg_dir = ffmpeg_dir

        temp_dir = tempfile.gettempdir()
        # --- Temporary Artwork Files ---
        self.temp_thumb_path = os.path.join(temp_dir, f"melcom_norm_thumb_{os.getpid()}.png")
        self.temp_full_path = os.path.join(temp_dir, f"melcom_norm_full_{os.getpid()}.png")

        self.new_artwork_path = None
        self.artwork_deleted_pending = False

        self.current_analysis_id = 0
        self.stats_loaded = False
        self.analysis_running = False
        self.current_stats = None
        self.stats_failed = False
        self.preview_window = None

        # --- Editable Metadata Fields ---
        self.title_var = tk.StringVar()
        self.artist_var = tk.StringVar()
        self.album_var = tk.StringVar()
        self.album_artist_var = tk.StringVar()
        self.composer_var = tk.StringVar()
        self.work_var = tk.StringVar()
        self.genre_var = tk.StringVar()
        self.track_num_var = tk.StringVar()
        self.track_total_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.disc_num_var = tk.StringVar()
        self.disc_total_var = tk.StringVar()
        self.bpm_var = tk.StringVar()
        self.compilation_var = tk.BooleanVar()
        self.encoded_by_var = tk.StringVar()
        self.url_var = tk.StringVar()
        self.comment_var = tk.StringVar()

        self.win = tk.Toplevel(self.parent)
        self.win.title(get_inspect_text("inspect_title", "Audio Properties"))
        self.win.geometry("560x740")
        self.win.configure(bg=self.colors["bg"])
        self.win.transient(self.parent)

        self.win.protocol("WM_DELETE_WINDOW", self.on_close_win)

        self.create_widgets()
        self.reload_data()

        self.win.update_idletasks()
        width = self.win.winfo_width()
        height = self.win.winfo_height()
        x = (self.win.winfo_screenwidth() // 2) - (width // 2)
        y = (self.win.winfo_screenheight() // 2) - (height // 2)
        self.win.geometry(f'{width}x{height}+{x}+{y}')
        self.win.after_idle(self._remove_initial_focus)

    def on_close_win(self):
        """Closes the inspector window and cleans up temporary files."""
        for p in (self.temp_thumb_path, self.temp_full_path):
            if os.path.exists(p):
                try: os.remove(p)
                except OSError: pass
        self.preview_window = None
        if self.app:
            self.app.inspector_window = None
        self.win.destroy()

    def update_file(self, file_path):
        """Dynamically switches the active file and triggers a full UI reload."""
        if self.file_path == file_path:
            return
        self.file_path = file_path
        self.reload_data()

    def refresh_language(self):
        """Refreshes every visible inspector text after a language switch."""
        if not self.win.winfo_exists():
            return

        self.win.title(get_inspect_text("inspect_title", "Audio Properties"))
        if self.preview_window is not None and self.preview_window.winfo_exists():
            self.preview_window.title(get_inspect_text("inspect_cover_preview_title", "Cover Preview"))

        self.notebook.tab(self.tab_general, text=get_inspect_text("inspect_tab_general", "General"))
        self.notebook.tab(self.tab_details, text=get_inspect_text("inspect_tab_details", "Details"))
        self.notebook.tab(self.tab_artwork, text=get_inspect_text("inspect_tab_artwork", "Artwork"))
        self.notebook.tab(self.tab_stats, text=get_inspect_text("inspect_tab_stats", "Statistics"))

        self.btn_reload.config(text=get_inspect_text("inspect_btn_reload", "Reload"))
        self.btn_copy.config(text=get_inspect_text("inspect_btn_copy", "Copy"))
        self.btn_close.config(text=get_inspect_text("inspect_btn_close", "Close"))
        self.btn_save.config(text=get_inspect_text("inspect_btn_save", "Save"))

        self._refresh_header_texts()

        for child in self.tab_general.winfo_children():
            child.destroy()
        self.populate_general_tab()

        for child in self.tab_details.winfo_children():
            child.destroy()
        self.create_details_tab_widgets()

        if hasattr(self, "art_group"):
            self.art_group.config(text=get_inspect_text("inspect_group_artwork", " Album Artwork "))
        if hasattr(self, "btn_change_artwork"):
            self.btn_change_artwork.config(text=get_inspect_text("inspect_btn_change_artwork", "Change Artwork..."))
        if hasattr(self, "btn_export_artwork"):
            self.btn_export_artwork.config(text=get_inspect_text("inspect_btn_export_artwork", "Export..."))
        if hasattr(self, "lbl_artwork_warning"):
            self.lbl_artwork_warning.config(
                text=get_inspect_text(
                    "inspect_lbl_unsupported_artwork",
                    "Artwork editing is only supported for MP3, FLAC, and M4A files."
                )
            )
        if hasattr(self, "lbl_artwork_img"):
            has_artwork = (os.path.exists(self.temp_thumb_path) or self.new_artwork_path) and not self.artwork_deleted_pending
            if has_artwork:
                self.lbl_artwork_img.config(text="", cursor="hand2")
            else:
                self.lbl_artwork_img.config(text=get_inspect_text("inspect_lbl_no_artwork", "No Artwork"), cursor="")
        self.apply_format_restrictions()
        self.update_artwork_ui_states()

        for child in self.tab_stats.winfo_children():
            child.destroy()
        if self.stats_failed:
            self._render_stats_failure()
        elif self.stats_loaded and self.current_stats is not None:
            self._render_stats_success(self.current_stats)
        else:
            self.populate_stats_tab_loading()

        self._update_footer_buttons()
        self.win.after_idle(self._remove_initial_focus)

    def _refresh_header_texts(self):
        """Refreshes the header labels that summarize the current file."""
        if not hasattr(self, "metadata") or not self.metadata:
            return

        title_text = self.metadata.get("title") or os.path.splitext(self.metadata.get("filename", ""))[0]
        artist_text = self.metadata.get("artist") or get_inspect_text("inspect_unknown_artist", "Unknown Artist")
        if self.metadata.get("album"):
            artist_text += f" / {self.metadata['album']}"

        if hasattr(self, "title_label"):
            self.title_label.config(text=title_text)
        if hasattr(self, "artist_label"):
            self.artist_label.config(text=artist_text)
        if hasattr(self, "filename_val_lbl"):
            self.filename_val_lbl.config(text=self.metadata.get("filename", ""))

    def _render_stats_success(self, data):
        """Renders the translated statistics view for the current analysis data."""
        if not self.win.winfo_exists():
            return

        if hasattr(self, "loading_frame") and self.loading_frame.winfo_exists():
            self.loading_frame.destroy()

        for child in self.tab_stats.winfo_children():
            child.destroy()

        stats_group = ttk.LabelFrame(self.tab_stats, text=get_inspect_text("inspect_group_loudness", " Loudness Analysis (EBU R128) "), padding=10)
        stats_group.pack(fill=tk.X, pady=(5, 5))

        loudness_data = [
            (get_inspect_text("inspect_lbl_integrated", "Integrated Loudness:"), f"{data['input_i']} LUFS"),
            (get_inspect_text("inspect_lbl_lra", "Loudness Range (LRA):"), f"{data['input_lra']} LU"),
            (get_inspect_text("inspect_lbl_threshold", "Loudness Threshold:"), f"{data['input_thresh']} LUFS")
        ]

        for r, (lbl, val) in enumerate(loudness_data):
            ttk.Label(stats_group, text=lbl, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="e", padx=10, pady=3)
            ttk.Label(stats_group, text=val).grid(row=r, column=1, sticky="w", padx=10, pady=3)

        levels_group = ttk.LabelFrame(self.tab_stats, text=get_inspect_text("inspect_group_levels", " Signal Levels & Peaks "), padding=10)
        levels_group.pack(fill=tk.X, pady=(5, 5))

        tp_val = f"{data['input_tp']} dBTP"
        peak_val = f"{data.get('peak_db', 'N/A')} dBFS" if data.get('peak_db') != "N/A" else "N/A"
        min_max_val = f"{data.get('min_level', 'N/A')} / {data.get('max_level', 'N/A')}"

        levels_data = [
            (get_inspect_text("inspect_lbl_truepeak", "True Peak Level:"), tp_val),
            (get_inspect_text("inspect_lbl_samplepeak", "Sample Peak:"), peak_val),
            (get_inspect_text("inspect_lbl_minmax", "Min / Max Level:"), min_max_val)
        ]

        for r, (lbl, val) in enumerate(levels_data):
            ttk.Label(levels_group, text=lbl, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="e", padx=10, pady=3)
            ttk.Label(levels_group, text=val).grid(row=r, column=1, sticky="w", padx=10, pady=3)

        dynamics_group = ttk.LabelFrame(self.tab_stats, text=get_inspect_text("inspect_group_dynamics", " Signal Dynamics & Power "), padding=10)
        dynamics_group.pack(fill=tk.X, pady=(5, 5))

        rms_val = f"{data.get('rms_db', 'N/A')} dB" if data.get('rms_db') != "N/A" else "N/A"
        crest_val = data.get('crest_factor', 'N/A')
        dc_val = data.get('dc_offset', 'N/A')
        depth_val = data.get('bit_depth_measured', 'N/A')

        dynamics_data = [
            (get_inspect_text("inspect_lbl_rmsaverage", "Average RMS Power:"), rms_val),
            (get_inspect_text("inspect_lbl_crest", "Crest Factor:"), crest_val),
            (get_inspect_text("inspect_lbl_dc", "DC Offset:"), dc_val),
            (get_inspect_text("inspect_lbl_bitdepth_measured", "Measured Bit Depth:"), depth_val)
        ]

        for r, (lbl, val) in enumerate(dynamics_data):
            ttk.Label(dynamics_group, text=lbl, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="e", padx=10, pady=3)
            ttk.Label(dynamics_group, text=val).grid(row=r, column=1, sticky="w", padx=10, pady=3)

    def _render_stats_failure(self):
        """Renders the translated failure state for the statistics tab."""
        if not self.win.winfo_exists():
            return

        if hasattr(self, "loading_frame") and self.loading_frame.winfo_exists():
            self.loading_frame.destroy()

        for child in self.tab_stats.winfo_children():
            child.destroy()

        error_lbl = ttk.Label(self.tab_stats, text="❌", font=("Segoe UI", 24), foreground=self.colors["error_bg"])
        error_lbl.pack(pady=(80, 10))

        error_txt = ttk.Label(self.tab_stats, text=get_inspect_text("inspect_analysis_failed", "Analysis failed.\nCould not read loudness data."), justify=tk.CENTER)
        error_txt.pack()

    def _clear_all_field_selection(self):
        """Performs internal helper work for  clear all field selection."""
        widgets = [
            getattr(self, "entry_songname", None),
            getattr(self, "entry_artist", None),
            getattr(self, "entry_album", None),
            getattr(self, "entry_album_artist", None),
            getattr(self, "entry_composer", None),
            getattr(self, "entry_work", None),
            getattr(self, "genre_dropdown", None),
            getattr(self, "entry_track_num", None),
            getattr(self, "entry_track_total", None),
            getattr(self, "entry_year", None),
            getattr(self, "entry_disc_num", None),
            getattr(self, "entry_disc_total", None),
            getattr(self, "entry_bpm", None),
            getattr(self, "entry_encoded_by", None),
            getattr(self, "entry_url", None),
            getattr(self, "entry_comment", None)
        ]

        for widget in widgets:
            if widget is None:
                continue
            try:
                widget.selection_clear()
            except Exception:
                pass

    def _remove_initial_focus(self):
        """Performs internal helper work for  remove initial focus."""
        try:
            self.notebook.focus_set()
            self.win.after(25, self._clear_all_field_selection)
            self.win.after(100, self._clear_all_field_selection)
        except Exception:
            pass

    def load_metadata_to_vars(self):
        """Copies loaded metadata into the editing variables."""
        self.title_var.set(self.metadata.get("title", ""))
        self.artist_var.set(self.metadata.get("artist", ""))
        self.album_var.set(self.metadata.get("album", ""))
        self.album_artist_var.set(self.metadata.get("album_artist", ""))
        self.composer_var.set(self.metadata.get("composer", ""))
        self.work_var.set(self.metadata.get("work", ""))
        self.genre_var.set(self.metadata.get("genre", ""))
        self.year_var.set(self.metadata.get("year", ""))
        self.bpm_var.set(self.metadata.get("bpm", ""))
        self.encoded_by_var.set(self.metadata.get("encoded_by",""))
        self.url_var.set(self.metadata.get("url",""))
        self.comment_var.set(self.metadata.get("comment",""))

        track_raw = str(self.metadata.get("track", ""))
        if "/" in track_raw:
            parts = track_raw.split("/")
            self.track_num_var.set(parts[0])
            self.track_total_var.set(parts[1])
        else:
            self.track_num_var.set(track_raw)
            self.track_total_var.set("")

        disc_raw = str(self.metadata.get("disc", ""))
        if "/" in disc_raw:
            parts = disc_raw.split("/")
            self.disc_num_var.set(parts[0])
            self.disc_total_var.set(parts[1])
        else:
            self.disc_num_var.set(disc_raw)
            self.disc_total_var.set("")

        comp = str(self.metadata.get("compilation", ""))
        self.compilation_var.set(comp == "1" or comp.lower() == "yes" or comp.lower() == "true")

    def create_widgets(self):
        """Creates the dialog widgets."""
        self.header_frame = ttk.Frame(self.win, style="TFrame", padding=(15, 15, 15, 5))
        self.header_frame.pack(fill=tk.X)

        self.title_label = ttk.Label(self.header_frame, text="", font=("Segoe UI", 12, "bold"))
        self.title_label.pack(anchor="w")

        self.artist_label = ttk.Label(self.header_frame, text="", font=("Segoe UI", 9, "italic"), foreground=self.colors["disabled_fg"])
        self.artist_label.pack(anchor="w", pady=(2, 0))

        self.notebook = ttk.Notebook(self.win)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=(5, 10))

        self.tab_general = ttk.Frame(self.notebook, style="TFrame", padding=15)
        self.notebook.add(self.tab_general, text=get_inspect_text("inspect_tab_general", "General"))

        self.tab_details = ttk.Frame(self.notebook, style="TFrame", padding=15)
        self.notebook.add(self.tab_details, text=get_inspect_text("inspect_tab_details", "Details"))
        self.create_details_tab_widgets()

        self.tab_artwork = ttk.Frame(self.notebook, style="TFrame", padding=15)
        self.notebook.add(self.tab_artwork, text=get_inspect_text("inspect_tab_artwork", "Artwork"))
        self.create_artwork_tab_widgets()

        self.tab_stats = ttk.Frame(self.notebook, style="TFrame", padding=15)
        self.notebook.add(self.tab_stats, text=get_inspect_text("inspect_tab_stats", "Statistics"))
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)

        self.footer_frame = ttk.Frame(self.win, style="TFrame", padding=10)
        self.footer_frame.pack(fill=tk.X)

        self.btn_reload = ttk.Button(
            self.footer_frame, 
            text=get_inspect_text("inspect_btn_reload", "Reload"), 
            command=self.reload_data
        )
        self.btn_reload.pack(side=tk.LEFT, padx=5)

        self.btn_copy = ttk.Button(
            self.footer_frame, 
            text=get_inspect_text("inspect_btn_copy", "Copy"), 
            command=self.copy_to_clipboard
        )
        self.btn_copy.pack(side=tk.LEFT, padx=0)

        self.btn_close = ttk.Button(
            self.footer_frame, 
            text=get_inspect_text("inspect_btn_close", "Close"), 
            command=self.on_close_win
        )
        self.btn_close.pack(side=tk.RIGHT, padx=5)

        self.btn_save = ttk.Button(
            self.footer_frame, 
            text=get_inspect_text("inspect_btn_save", "Save"), 
            style="Accent.TButton",
            command=self.save_data
        )
        self.btn_save.pack(side=tk.RIGHT, padx=5)

        self._update_footer_buttons()

    def create_details_tab_widgets(self):
        """Creates the metadata editing widgets for the details tab."""
        self.tab_details.columnconfigure(0, weight=1)
        self.tab_details.columnconfigure(1, weight=3)
        self.tab_details.columnconfigure(2, weight=1)
        self.tab_details.columnconfigure(3, weight=1)
        self.tab_details.columnconfigure(4, weight=1)
        self.tab_details.columnconfigure(5, weight=2)

        ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_filename", "File Name:"), font=("Segoe UI", 9, "bold")).grid(row=0, column=0, sticky="e", padx=5, pady=4)
        self.filename_val_lbl = ttk.Label(self.tab_details, text="", font=("Segoe UI", 9, "italic"), foreground=self.colors["disabled_fg"])
        self.filename_val_lbl.grid(row=0, column=1, columnspan=5, sticky="w", padx=10, pady=4)

        self.lbl_songname = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_songname", "Song Name:"), font=("Segoe UI", 9, "bold"))
        self.lbl_songname.grid(row=1, column=0, sticky="e", padx=5, pady=4)
        self.entry_songname = ttk.Entry(self.tab_details, textvariable=self.title_var)
        self.entry_songname.grid(row=1, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_artist = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_artist", "Artist:"), font=("Segoe UI", 9, "bold"))
        self.lbl_artist.grid(row=2, column=0, sticky="e", padx=5, pady=4)
        self.entry_artist = ttk.Entry(self.tab_details, textvariable=self.artist_var)
        self.entry_artist.grid(row=2, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_album = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_album", "Album:"), font=("Segoe UI", 9, "bold"))
        self.lbl_album.grid(row=3, column=0, sticky="e", padx=5, pady=4)
        self.entry_album = ttk.Entry(self.tab_details, textvariable=self.album_var)
        self.entry_album.grid(row=3, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_album_artist = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_albumartist", "Album Artist:"), font=("Segoe UI", 9, "bold"))
        self.lbl_album_artist.grid(row=4, column=0, sticky="e", padx=5, pady=4)
        self.entry_album_artist = ttk.Entry(self.tab_details, textvariable=self.album_artist_var)
        self.entry_album_artist.grid(row=4, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_composer = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_composer", "Composer:"), font=("Segoe UI", 9, "bold"))
        self.lbl_composer.grid(row=5, column=0, sticky="e", padx=5, pady=4)
        self.entry_composer = ttk.Entry(self.tab_details, textvariable=self.composer_var)
        self.entry_composer.grid(row=5, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_work = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_work", "Work/Grouping:"), font=("Segoe UI", 9, "bold"))
        self.lbl_work.grid(row=6, column=0, sticky="e", padx=5, pady=4)
        self.entry_work = ttk.Entry(self.tab_details, textvariable=self.work_var)
        self.entry_work.grid(row=6, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_genre = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_genre", "Genre:"), font=("Segoe UI", 9, "bold"))
        self.lbl_genre.grid(row=7, column=0, sticky="e", padx=5, pady=4)
        self.genre_dropdown = ttk.Combobox(self.tab_details, textvariable=self.genre_var, state="normal")
        self.genre_dropdown.grid(row=7, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        default_genres = ("Demoscene", "Electronic", "Synthwave", "Chiptune", "Ambient", "Rock", "Pop", "Metal", "Jazz", "Classical", "Podcast", "Speech")
        self.genre_dropdown['values'] = i18n.language_data.get("inspect_genre_list", default_genres)
        self.genre_dropdown.bind("<<ComboboxSelected>>", self._clear_combobox_focus, add="+")

        self.lbl_track = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_track_num", "Track:"), font=("Segoe UI", 9, "bold"))
        self.lbl_track.grid(row=8, column=0, sticky="e", padx=5, pady=4)
        self.entry_track_num = ttk.Entry(self.tab_details, textvariable=self.track_num_var, width=6)
        self.entry_track_num.grid(row=8, column=1, sticky="w", padx=10, pady=4)

        self.lbl_track_of = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_track_total", "of"))
        self.lbl_track_of.grid(row=8, column=2, pady=4)

        self.entry_track_total = ttk.Entry(self.tab_details, textvariable=self.track_total_var, width=6)
        self.entry_track_total.grid(row=8, column=3, sticky="w", pady=4)

        self.lbl_year = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_year", "Year:"), font=("Segoe UI", 9, "bold"))
        self.lbl_year.grid(row=8, column=4, sticky="e", padx=5, pady=4)
        self.entry_year = ttk.Entry(self.tab_details, textvariable=self.year_var, width=10)
        self.entry_year.grid(row=8, column=5, sticky="w", padx=10, pady=4)

        self.lbl_disc = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_disc_num", "Disc:"), font=("Segoe UI", 9, "bold"))
        self.lbl_disc.grid(row=9, column=0, sticky="e", padx=5, pady=4)
        self.entry_disc_num = ttk.Entry(self.tab_details, textvariable=self.disc_num_var, width=6)
        self.entry_disc_num.grid(row=9, column=1, sticky="w", padx=10, pady=4)

        self.lbl_disc_of = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_disc_total", "of"))
        self.lbl_disc_of.grid(row=9, column=2, pady=4)

        self.entry_disc_total = ttk.Entry(self.tab_details, textvariable=self.disc_total_var, width=6)
        self.entry_disc_total.grid(row=9, column=3, sticky="w", pady=4)

        self.lbl_bpm = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_bpm", "BPM:"), font=("Segoe UI", 9, "bold"))
        self.lbl_bpm.grid(row=9, column=4, sticky="e", padx=5, pady=4)
        self.entry_bpm = ttk.Entry(self.tab_details, textvariable=self.bpm_var, width=10)
        self.entry_bpm.grid(row=9, column=5, sticky="w", padx=10, pady=4)

        self.lbl_encoded_by = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_encoded_by", "Encoded by:"), font=("Segoe UI", 9, "bold"))
        self.lbl_encoded_by.grid(row=10, column=0, sticky="e", padx=5, pady=4)
        self.entry_encoded_by = ttk.Entry(self.tab_details, textvariable=self.encoded_by_var)
        self.entry_encoded_by.grid(row=10, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_url = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_url", "URL:"), font=("Segoe UI", 9, "bold"))
        self.lbl_url.grid(row=11, column=0, sticky="e", padx=5, pady=4)
        self.entry_url = ttk.Entry(self.tab_details, textvariable=self.url_var)
        self.entry_url.grid(row=11, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.lbl_comment = ttk.Label(self.tab_details, text=get_inspect_text("inspect_lbl_comment", "Comment:"), font=("Segoe UI", 9, "bold"))
        self.lbl_comment.grid(row=12, column=0, sticky="e", padx=5, pady=4)
        self.entry_comment = ttk.Entry(self.tab_details, textvariable=self.comment_var)
        self.entry_comment.grid(row=12, column=1, columnspan=5, sticky="ew", padx=10, pady=4)

        self.chk_comp = ttk.Checkbutton(
            self.tab_details, 
            text=get_inspect_text("inspect_lbl_compilation", "Album is a compilation of songs by various artists"), 
            variable=self.compilation_var
        )
        self.chk_comp.grid(row=13, column=1, columnspan=5, sticky="w", padx=10, pady=12)

    def _clear_combobox_focus(self, event):
        """Removes the focus rectangle from themed combo boxes."""
        self.notebook.focus_set()
        if hasattr(event.widget, 'selection_clear'):
            event.widget.after(10, event.widget.selection_clear)

    def create_artwork_tab_widgets(self):
        """Creates the artwork management widgets for the artwork tab."""
        self.tab_artwork.rowconfigure(0, weight=1)
        self.tab_artwork.columnconfigure(0, weight=1)

        self.art_group = ttk.LabelFrame(self.tab_artwork, text=get_inspect_text("inspect_group_artwork", " Album Artwork "), padding=15)
        self.art_group.pack(fill=tk.BOTH, expand=True, pady=5)

        self.lbl_artwork_img = ttk.Label(self.art_group, text=get_inspect_text("inspect_lbl_no_artwork", "No Artwork"), anchor=tk.CENTER, justify=tk.CENTER)
        self.lbl_artwork_img.pack(fill=tk.BOTH, expand=True, pady=5)
        self.lbl_artwork_img.bind("<Button-1>", self.show_large_artwork)

        self.btn_delete_artwork = tk.Button(
            self.art_group, text="✕", bg=self.colors["bg"], fg="#ef4444", 
            activeforeground="#b91c1c", activebackground=self.colors["button_hover"],
            font=("Segoe UI", 12, "bold"), relief="flat", bd=0, cursor="hand2",
            command=self.delete_artwork_action
        )

        ctrl_frame = ttk.Frame(self.tab_artwork, style="TFrame", padding=(5, 5, 5, 0))
        ctrl_frame.pack(fill=tk.X)

        self.lbl_artwork_info = ttk.Label(ctrl_frame, text="", font=("Segoe UI", 9, "italic"), foreground=self.colors["disabled_fg"])
        self.lbl_artwork_info.pack(side=tk.LEFT)

        self.btn_export_artwork = ttk.Button(
            ctrl_frame,
            text=get_inspect_text("inspect_btn_export_artwork", "Export..."),
            command=self.export_artwork,
            state="disabled" 
        )
        self.btn_export_artwork.pack(side=tk.RIGHT, padx=5)

        self.btn_change_artwork = ttk.Button(
            ctrl_frame,
            text=get_inspect_text("inspect_btn_change_artwork", "Change Artwork..."),
            command=self.change_artwork
        )
        self.btn_change_artwork.pack(side=tk.RIGHT)

        self.lbl_artwork_warning = ttk.Label(
            self.tab_artwork,
            text=get_inspect_text("inspect_lbl_unsupported_artwork", "Artwork editing is only supported for MP3, FLAC, and M4A files."),
            font=("Segoe UI", 8, "italic"),
            foreground=self.colors["disabled_fg"],
            wraplength=480,
            justify=tk.CENTER
        )

        self.apply_format_restrictions()

    def apply_format_restrictions(self):
        """Applies format-specific field and artwork restrictions."""
        ext = os.path.splitext(self.file_path)[1].lower()

        state_normal = "normal"
        color_normal = self.colors["fg"]
        disabled_state = "disabled"
        color_disabled = self.colors["disabled_fg"]

        all_entries = [
            self.entry_songname, self.entry_artist, self.entry_album, 
            self.entry_album_artist, self.entry_composer, self.entry_work, 
            self.genre_dropdown, self.entry_track_num, self.entry_track_total, 
            self.entry_year, self.entry_disc_num, self.entry_disc_total, 
            self.entry_bpm, self.chk_comp, self.entry_encoded_by, 
            self.entry_url, self.entry_comment
        ]
        for widget in all_entries:
            widget.config(state=state_normal)

        all_labels = [
            self.lbl_songname, self.lbl_artist, self.lbl_album,
            self.lbl_album_artist, self.lbl_composer, self.lbl_work, self.lbl_genre,
            self.lbl_track, self.lbl_track_of, self.lbl_year, self.lbl_disc,
            self.lbl_disc_of, self.lbl_bpm, self.lbl_encoded_by,
            self.lbl_url, self.lbl_comment
        ]
        for label in all_labels:
            label.config(foreground=color_normal)

        if ext == ".wav":
            wav_disabled = [
                (self.entry_album_artist, self.lbl_album_artist),
                (self.entry_composer, self.lbl_composer),
                (self.entry_work, self.lbl_work),
                (self.entry_disc_num, self.lbl_disc),
                (self.entry_disc_total, self.lbl_disc_of),
                (self.entry_bpm, self.lbl_bpm),
                (self.chk_comp, None),
                (self.entry_encoded_by, self.lbl_encoded_by),
                (self.entry_url, self.lbl_url)
            ]
            for widget, label in wav_disabled:
                widget.config(state=disabled_state)
                if label:
                    label.config(foreground=color_disabled)

        elif ext in [".flac", ".m4a", ".ogg", ".aac"]:
            self.entry_encoded_by.config(state=disabled_state)
            self.lbl_encoded_by.config(foreground=color_disabled)
            self.entry_url.config(state=disabled_state)
            self.lbl_url.config(foreground=color_disabled)

            if ext == ".aac":
                for widget in all_entries:
                    widget.config(state=disabled_state)
                for label in all_labels:
                    label.config(foreground=color_disabled)

        supported_artwork = [".mp3", ".flac", ".m4a"]
        if ext not in supported_artwork:
            self.btn_change_artwork.config(state=disabled_state)
            self.lbl_artwork_warning.config(
                text=get_inspect_text("inspect_lbl_unsupported_artwork", "Artwork editing is only supported for MP3, FLAC, and M4A files.")
            )
            self.lbl_artwork_warning.pack(pady=(5, 0))
        else:
            self.btn_change_artwork.config(state=state_normal)
            self.lbl_artwork_warning.pack_forget()

    def update_theme_colors(self, colors):
        """Updates the inspector window with new theme colors."""
        self.colors = colors
        self.win.configure(bg=colors["bg"])

        if hasattr(self, "artist_label") and self.artist_label.winfo_exists():
            self.artist_label.config(foreground=colors["disabled_fg"])

        if hasattr(self, "filename_val_lbl") and self.filename_val_lbl.winfo_exists():
            self.filename_val_lbl.config(foreground=colors["disabled_fg"])

        if hasattr(self, "lbl_artwork_info") and self.lbl_artwork_info.winfo_exists():
            self.lbl_artwork_info.config(foreground=colors["disabled_fg"])

        if hasattr(self, "lbl_artwork_warning") and self.lbl_artwork_warning.winfo_exists():
            self.lbl_artwork_warning.config(foreground=colors["disabled_fg"])

        if hasattr(self, "btn_delete_artwork") and self.btn_delete_artwork.winfo_exists():
            self.btn_delete_artwork.config(bg=colors["bg"], activebackground=colors["button_hover"])

        self.apply_format_restrictions()

    def _update_footer_buttons(self):
        """Updates the footer button state to match the current file context."""
        current_tab = self.notebook.select()

        self.btn_reload.pack_forget()
        self.btn_copy.pack_forget()
        self.btn_close.pack_forget()
        self.btn_save.pack_forget()

        self.btn_reload.pack(side=tk.LEFT, padx=5)

        if current_tab != str(self.tab_artwork):
            self.btn_copy.pack(side=tk.LEFT, padx=0)

        self.btn_close.pack(side=tk.RIGHT, padx=5)

        ext = os.path.splitext(self.file_path)[1].lower()
        show_save = (current_tab == str(self.tab_details)) or (current_tab == str(self.tab_artwork) and ext in [".mp3", ".flac", ".m4a"])
        if show_save:
            self.btn_save.pack(side=tk.RIGHT, padx=5)

    def reload_data(self):
        """Reloads metadata, artwork, and analysis data from the current file."""
        self.btn_reload.config(state="disabled")
        self.btn_save.config(state="disabled")
        self.btn_copy.config(state="disabled")
        self.btn_export_artwork.config(state="disabled")
        self.btn_delete_artwork.place_forget()
        self.current_stats = None
        self.new_artwork_path = None
        self.artwork_deleted_pending = False

        self.current_analysis_id += 1
        analysis_id = self.current_analysis_id

        processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
        self.metadata = processor.get_track_metadata(self.file_path)

        if not self.metadata:
            self.metadata = {
                "filename": os.path.basename(self.file_path),
                "container": get_inspect_text("inspect_unknown_format", "Unknown Format"),
                "codec": get_inspect_text("inspect_unknown_codec", "Unknown Codec"),
                "sample_rate": 0,
                "channels": 0,
                "duration": 0,
                "size_bytes": os.path.getsize(self.file_path) if os.path.exists(self.file_path) else 0,
                "total_samples": 0
            }

        title_text = self.metadata.get("title") or os.path.splitext(self.metadata["filename"])[0]
        artist_text = self.metadata.get("artist") or get_inspect_text("inspect_unknown_artist", "Unknown Artist")
        if self.metadata.get("album"):
            artist_text += f" / {self.metadata['album']}"

        self.title_label.config(text=title_text)
        self.artist_label.config(text=artist_text)

        self.filename_val_lbl.config(text=self.metadata["filename"])
        self.load_metadata_to_vars()

        for child in self.tab_general.winfo_children():
            child.destroy()
        self.populate_general_tab()

        self.lbl_artwork_img.config(image="", text="⏳")
        self.lbl_artwork_info.config(text="")
        threading.Thread(target=self._extract_artwork_worker, daemon=True).start()

        for child in self.tab_stats.winfo_children():
            child.destroy()
        self.stats_loaded = False
        self.populate_stats_tab_loading()

        self.btn_reload.config(state="normal")
        self.btn_save.config(state="normal")
        self.btn_copy.config(state="normal")

        self.win.after_idle(self._remove_initial_focus)

        if self.notebook.select() == str(self.tab_stats):
            self._on_tab_changed()

    def _extract_artwork_worker(self):
        """Extracts artwork on a background thread."""
        processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
        if os.path.exists(self.temp_thumb_path):
            try: os.remove(self.temp_thumb_path)
            except OSError: pass

        success, info_str = processor.extract_artwork(self.file_path, self.temp_thumb_path, scale_size=280)
        if success and os.path.exists(self.temp_thumb_path):
            self.win.after(0, self._on_artwork_success, info_str)
        else:
            self.win.after(0, self._on_artwork_failed)

    def _on_artwork_success(self, info_str):
        """Handles a successful artwork extraction."""
        if not self.win.winfo_exists(): return
        try:
            self.thumb_img = tk.PhotoImage(file=self.temp_thumb_path)
            self.lbl_artwork_img.config(image=self.thumb_img, text="", cursor="hand2")
            self.lbl_artwork_info.config(text=info_str)
            self.update_artwork_ui_states()
        except Exception:
            self._on_artwork_failed()

    def _on_artwork_failed(self):
        """Handles a failed artwork extraction."""
        if not self.win.winfo_exists(): return
        self.lbl_artwork_img.config(image="", text=get_inspect_text("inspect_lbl_no_artwork", "No Artwork"), cursor="")
        self.lbl_artwork_info.config(text="")
        self.update_artwork_ui_states()

    def show_large_artwork(self, event=None):
        """Shows the artwork preview in a larger window."""
        if self.artwork_deleted_pending: return

        if self.new_artwork_path:
            large_path = self.new_artwork_path
        elif os.path.exists(self.temp_thumb_path):
            processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
            success, _ = processor.extract_artwork(self.file_path, self.temp_full_path)
            large_path = self.temp_full_path if success else None
        else:
            large_path = None

        if not large_path or not os.path.exists(large_path):
            return

        try:
            pop = tk.Toplevel(self.win)
            self.preview_window = pop
            pop.title(get_inspect_text("inspect_cover_preview_title", "Cover Preview"))
            pop.configure(bg="#000000")
            pop.transient(self.win)
            pop.grab_set()
            pop.lift()
            pop.focus_set()

            self.full_img = tk.PhotoImage(file=large_path)
            w = self.full_img.width()
            h = self.full_img.height()

            max_size = 720
            if w > max_size or h > max_size:
                processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
                processor.extract_artwork(self.file_path, self.temp_full_path, scale_size=max_size)
                self.full_img = tk.PhotoImage(file=self.temp_full_path)
                w = self.full_img.width()
                h = self.full_img.height()

            x = (self.win.winfo_screenwidth() // 2) - (w // 2)
            y = (self.win.winfo_screenheight() // 2) - (h // 2)
            pop.geometry(f"{w}x{h}+{x}+{y}")

            lbl = tk.Label(pop, image=self.full_img, bg="#000000", borderwidth=0, highlightthickness=0)
            lbl.pack(fill=tk.BOTH, expand=True)

            lbl.bind("<Button-1>", lambda e: pop.destroy())
            pop.bind("<Key>", lambda e: pop.destroy())

        except Exception as e:
            messagebox.showerror("Error", f"Failed to open image preview: {str(e)}", parent=self.win)

    def change_artwork(self):
        """Lets the user pick replacement artwork."""
        filetypes = [(get_inspect_text("inspect_image_files_filter", "Image Files"), "*.jpg;*.jpeg;*.png")]
        selected_img = filedialog.askopenfilename(
            title=get_inspect_text("inspect_btn_change_artwork", "Select Cover Image"),
            filetypes=filetypes,
            parent=self.win
        )
        if selected_img:
            processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)

            cmd_scale = [
                processor.ffmpeg_path, "-hide_banner", "-y", "-i", selected_img,
                "-vf", "scale=280:280:force_original_aspect_ratio=decrease",
                "-vcodec", "png", self.temp_thumb_path
            ]
            ret, _ = processor._run_process(cmd_scale)
            if ret == 0 and os.path.exists(self.temp_thumb_path):
                try:
                    self.thumb_img = tk.PhotoImage(file=self.temp_thumb_path)
                    self.lbl_artwork_img.config(image=self.thumb_img, text="", cursor="hand2")

                    ext = os.path.splitext(selected_img)[1].upper().replace(".", "")
                    self.lbl_artwork_info.config(text=f"{ext} {get_inspect_text('inspect_pending_save_suffix', '(Pending Save)')}")

                    self.new_artwork_path = selected_img
                    self.artwork_deleted_pending = False
                    self.update_artwork_ui_states()
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load image preview: {str(e)}", parent=self.win)

    def delete_artwork_action(self):
        """Mark artwork for deletion."""
        self.new_artwork_path = None
        self.artwork_deleted_pending = True
        self.lbl_artwork_img.config(image="", text=get_inspect_text("inspect_lbl_no_artwork", "No Artwork"), cursor="")
        self.lbl_artwork_info.config(text=get_inspect_text("inspect_lbl_deleted_pending", "Deleted (Pending Save)"))
        self.update_artwork_ui_states()

    def update_artwork_ui_states(self):
        """Updates artwork controls to match the current file state."""
        ext = os.path.splitext(self.file_path)[1].lower()
        is_supported = ext in [".mp3", ".flac", ".m4a"]
        has_artwork = (os.path.exists(self.temp_thumb_path) or self.new_artwork_path) and not self.artwork_deleted_pending

        if is_supported and has_artwork:
            self.btn_delete_artwork.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
        else:
            self.btn_delete_artwork.place_forget()

        if is_supported:
            self.btn_change_artwork.config(state="normal")
        else:
            self.btn_change_artwork.config(state="disabled")

        if has_artwork:
            self.btn_export_artwork.config(state="normal")
        else:
            self.btn_export_artwork.config(state="disabled")

    def export_artwork(self):
        """Exports the embedded artwork to an image file."""
        info_text = self.lbl_artwork_info.cget("text")
        ext = ".jpg"
        if "PNG" in info_text.upper():
            ext = ".png"
        elif "BMP" in info_text.upper():
            ext = ".bmp"

        res_str = ""
        match = re.search(r'(\d+)\s*[xX]\s*(\d+)', info_text)
        if match:
            res_str = f" - {match.group(1)}x{match.group(2)}"

        base_name = os.path.splitext(self.metadata.get("filename", "Artwork"))[0]
        init_file = f"{base_name}{res_str}{ext}"

        filename = filedialog.asksaveasfilename(
            title=get_inspect_text("inspect_title_export_artwork", "Export Cover Art"),
            defaultextension=ext,
            filetypes=[("Image Files", f"*{ext}")],
            initialfile=init_file,
            parent=self.win
        )
        if filename:
            processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)

            if self.new_artwork_path:
                try:
                    import shutil
                    shutil.copy(self.new_artwork_path, filename)
                    success = True
                except Exception:
                    success = False
            else:
                success, _ = processor.extract_artwork(self.file_path, filename)

            if success:
                messagebox.showinfo(
                    get_inspect_text("inspect_save_success_title", "Success"),
                    get_inspect_text("inspect_export_success_msg", "Cover art exported successfully!"),
                    parent=self.win
                )
            else:
                messagebox.showerror(
                    get_inspect_text("inspect_save_failed_title", "Error"),
                    get_inspect_text("inspect_export_failed_msg", "Failed to export cover art."),
                    parent=self.win
                )

    def populate_general_tab(self):
        """Populates the general-information tab."""
        signal_group = ttk.LabelFrame(self.tab_general, text=get_inspect_text("inspect_group_signal", " Signal Properties "), padding=10)
        signal_group.pack(fill=tk.X, pady=(0, 10))

        ch_text = get_inspect_text("inspect_channel_stereo", "Stereo") if self.metadata["channels"] == 2 else (get_inspect_text("inspect_channel_mono", "Mono") if self.metadata["channels"] == 1 else f"{self.metadata['channels']}{get_inspect_text('inspect_channel_ch_suffix', ' Ch')}")

        res_bits = self.metadata.get("bits_per_sample")
        sample_fmt = self.metadata.get("sample_fmt", "")
        bits_str = get_inspect_text("inspect_bits", "bits")
        float_str = get_inspect_text("inspect_float_suffix", " (Float)")

        ext = os.path.splitext(self.file_path)[1].lower()
        if ext in (".mp3", ".m4a", ".ogg", ".aac"):
            res_text = get_inspect_text("inspect_na", "N/A")
        else:
            if res_bits:
                res_text = f"{res_bits} {bits_str}"
                if "flt" in sample_fmt or "dbl" in sample_fmt:
                    res_text += float_str
            else:
                if "s16" in sample_fmt: res_text = f"16 {bits_str}"
                elif "s32" in sample_fmt: res_text = f"32 {bits_str}{float_str}" if "flt" in sample_fmt else f"32 {bits_str}"
                elif "flt" in sample_fmt: res_text = f"32 {bits_str}{float_str}"
                elif "dbl" in sample_fmt: res_text = f"64 {bits_str}{float_str}"
                else: res_text = get_inspect_text("inspect_na", "N/A")

        sig_data = [
            (get_inspect_text("inspect_lbl_samplerate", "Sample Rate:"), f"{self.metadata['sample_rate']} Hz"),
            (get_inspect_text("inspect_lbl_channels", "Channels:"), ch_text),
            (get_inspect_text("inspect_lbl_resolution", "Resolution:"), res_text),
            (get_inspect_text("inspect_lbl_length", "Duration:"), utils.format_duration(self.metadata["duration"])),
            (get_inspect_text("inspect_lbl_samples", "Total Samples:"), str(self.metadata.get("total_samples", "N/A")))
        ]

        for r, (lbl, val) in enumerate(sig_data):
            ttk.Label(signal_group, text=lbl, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="e", padx=5, pady=4)
            ttk.Label(signal_group, text=val).grid(row=r, column=1, sticky="w", padx=10, pady=4)

        file_group = ttk.LabelFrame(self.tab_general, text=get_inspect_text("inspect_group_file", " File Properties "), padding=10)
        file_group.pack(fill=tk.X, pady=5)

        br_val = self.metadata.get("bit_rate")
        br_text = f"{br_val // 1000} kbps" if br_val else get_inspect_text("inspect_na", "N/A")

        file_data = [
            (get_inspect_text("inspect_lbl_filename", "File Name:"), self.metadata["filename"]),
            (get_inspect_text("inspect_lbl_container", "Container:"), self.metadata["container"]),
            (get_inspect_text("inspect_lbl_codec", "Audio Codec:"), self.metadata["codec"]),
            (get_inspect_text("inspect_lbl_bitrate", "Bitrate:"), br_text),
            (get_inspect_text("inspect_lbl_size", "Size on Disk:"), utils.format_size(self.metadata["size_bytes"]))
        ]

        for r, (lbl, val) in enumerate(file_data):
            ttk.Label(file_group, text=lbl, font=("Segoe UI", 9, "bold")).grid(row=r, column=0, sticky="e", padx=5, pady=4)
            ttk.Label(file_group, text=val, wraplength=320, justify=tk.LEFT).grid(row=r, column=1, sticky="w", padx=10, pady=4)

    def populate_stats_tab_loading(self):
        """Shows the loading state for the statistics tab."""
        self.loading_frame = ttk.Frame(self.tab_stats, style="TFrame")
        self.loading_frame.pack(fill=tk.BOTH, expand=True)

        self.spinner_lbl = ttk.Label(self.loading_frame, text="⏳", font=("Segoe UI", 24))
        self.spinner_lbl.pack(pady=(80, 10))

        self.loading_txt = ttk.Label(self.loading_frame, text=get_inspect_text("inspect_loading_analysis", "Click the Statistics tab to start analysis."), justify=tk.CENTER)
        self.loading_txt.pack(pady=(0, 10))

        self.progress = ttk.Progressbar(self.loading_frame, mode="indeterminate", length=260)
        self.progress.pack(pady=(5, 0))
        self.progress.start(12)

    def _on_tab_changed(self, event=None):
        """Refreshes tab content when the user switches sections."""
        current_tab = self.notebook.select()
        self._update_footer_buttons()

        if current_tab != str(self.tab_stats):
            return

        if self.stats_loaded or self.analysis_running:
            return

        self.analysis_running = True
        self.current_analysis_id += 1
        analysis_id = self.current_analysis_id

        for child in self.tab_stats.winfo_children():
            child.destroy()

        self.populate_stats_tab_loading()

        self.analysis_thread = threading.Thread(
            target=self._run_analysis_worker,
            args=(analysis_id,),
            daemon=True
        )
        self.analysis_thread.start()

    def _run_analysis_worker(self, analysis_id):
        """Runs the inspector analysis job on a background thread."""
        processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
        ret_code, stderr = processor.analyze(self.file_path)

        if ret_code == 0:
            json_match = re.search(r'\{\s*"input_i".*?\}', stderr, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group(0))

                    overall_idx = stderr.find("Overall")
                    if overall_idx != -1:
                        overall_text = stderr[overall_idx:]

                        def extract_astat(key):
                            """Performs extract astat."""
                            pattern = re.escape(key) + r':\s*([^\n\r]+)'
                            m = re.search(pattern, overall_text)
                            return m.group(1).strip() if m else "N/A"

                        data['dc_offset'] = extract_astat("DC offset")
                        data['min_level'] = extract_astat("Min level")
                        data['max_level'] = extract_astat("Max level")
                        data['peak_db'] = extract_astat("Peak level dB")
                        data['rms_db'] = extract_astat("RMS level dB")
                        data['crest_factor_raw'] = extract_astat("Crest factor")
                        data['bit_depth_measured'] = extract_astat("Bit depth")

                        try:
                            peak_val = float(data['peak_db'])
                            rms_val = float(data['rms_db'])
                            crest_db = peak_val - rms_val
                            crest_lin = 10 ** (crest_db / 20)
                            data['crest_factor'] = f"{crest_lin:.2f} ({crest_db:.2f} dB)"
                        except Exception:
                            data['crest_factor'] = "N/A"

                    self.win.after(0, self._on_analysis_success, data, analysis_id)
                    return
                except Exception:
                    pass
        self.win.after(0, self._on_analysis_failed, analysis_id)

    def _on_analysis_success(self, data, analysis_id):
        """Stores analysis data returned by the worker."""
        if not self.win.winfo_exists(): return
        if analysis_id != self.current_analysis_id: return
        self.analysis_running = False
        self.stats_loaded = True
        self.stats_failed = False
        self.current_stats = data
        self._render_stats_success(data)

    def _on_analysis_failed(self, analysis_id):
        """Handles a failed analysis job."""
        if not self.win.winfo_exists(): return
        if analysis_id != self.current_analysis_id: return
        self.analysis_running = False
        self.stats_loaded = True
        self.stats_failed = True
        self.current_stats = None
        self._render_stats_failure()

    def copy_to_clipboard(self):
        """Copies the current inspector summary to the clipboard."""
        current_tab = self.notebook.select()
        text_to_copy = ""

        if current_tab == str(self.tab_general):
            ch_text = get_inspect_text("inspect_channel_stereo", "Stereo") if self.metadata["channels"] == 2 else (get_inspect_text("inspect_channel_mono", "Mono") if self.metadata["channels"] == 1 else f"{self.metadata['channels']}{get_inspect_text('inspect_channel_ch_suffix', ' Ch')}")
            res_bits = self.metadata.get("bits_per_sample")
            sample_fmt = self.metadata.get("sample_fmt", "")
            bits_str = get_inspect_text("inspect_bits", "bits")
            float_str = get_inspect_text("inspect_float_suffix", " (Float)")

            ext = os.path.splitext(self.file_path)[1].lower()
            if ext in (".mp3", ".m4a", ".ogg", ".aac"):
                res_text = get_inspect_text("inspect_na", "N/A")
            else:
                if res_bits:
                    res_text = f"{res_bits} {bits_str}"
                    if "flt" in sample_fmt or "dbl" in sample_fmt: res_text += float_str
                else:
                    if "s16" in sample_fmt: res_text = f"16 {bits_str}"
                    elif "s32" in sample_fmt: res_text = f"32 {bits_str}{float_str}" if "flt" in sample_fmt else f"32 {bits_str}"
                    elif "flt" in sample_fmt: res_text = f"32 {bits_str}{float_str}"
                    elif "dbl" in sample_fmt: res_text = f"64 {bits_str}{float_str}"
                    else: res_text = get_inspect_text("inspect_na", "N/A")

            br_val = self.metadata.get("bit_rate")
            br_text = f"{br_val // 1000} kbps" if br_val else get_inspect_text("inspect_na", "N/A")

            text_to_copy += f"--- {get_inspect_text('inspect_tab_general', 'General')} ---\n\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_filename', 'File Name:')} {self.metadata['filename']}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_container', 'Container:')} {self.metadata['container']}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_codec', 'Audio Codec:')} {self.metadata['codec']}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_bitrate', 'Bitrate:')} {br_text}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_size', 'Size on Disk:')} {utils.format_size(self.metadata['size_bytes'])}\n\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_samplerate', 'Sample Rate:')} {self.metadata['sample_rate']} Hz\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_channels', 'Channels:')} {ch_text}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_resolution', 'Resolution:')} {res_text}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_length', 'Duration:')} {utils.format_duration(self.metadata['duration'])}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_samples', 'Total Samples:')} {str(self.metadata.get('total_samples', 'N/A'))}\n"

        elif current_tab == str(self.tab_details):
            text_to_copy += f"--- {get_inspect_text('inspect_tab_details', 'Details')} ---\n\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_filename', 'File Name:')} {self.metadata['filename']}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_songname', 'Song Name:')} {self.title_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_artist', 'Artist:')} {self.artist_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_album', 'Album:')} {self.album_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_albumartist', 'Album Artist:')} {self.album_artist_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_composer', 'Composer:')} {self.composer_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_work', 'Work/Grouping:')} {self.work_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_genre', 'Genre:')} {self.genre_var.get()}\n"

            track_str = self.track_num_var.get()
            if self.track_total_var.get(): track_str += f" / {self.track_total_var.get()}"
            text_to_copy += f"{get_inspect_text('inspect_lbl_track_num', 'Track:')} {track_str}\n"

            disc_str = self.disc_num_var.get()
            if self.disc_total_var.get(): disc_str += f" / {self.disc_total_var.get()}"
            text_to_copy += f"{get_inspect_text('inspect_lbl_disc_num', 'Disc:')} {disc_str}\n"

            text_to_copy += f"{get_inspect_text('inspect_lbl_year', 'Year:')} {self.year_var.get()}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_bpm', 'BPM:')} {self.bpm_var.get()}\n"

            comp_val = get_inspect_text("inspect_yes", "Yes") if self.compilation_var.get() else get_inspect_text("inspect_no", "No")
            text_to_copy += f"{get_inspect_text('inspect_lbl_compilation_copy', 'Compilation:')} {comp_val}\n"

        elif current_tab == str(self.tab_stats):
            if not self.stats_loaded or not self.current_stats:
                messagebox.showwarning("Warning", get_inspect_text("inspect_copy_wait", "Please wait for the analysis to finish before copying."), parent=self.win)
                return

            data = self.current_stats
            text_to_copy += f"--- {get_inspect_text('inspect_tab_stats', 'Statistics')} ---\n\n"

            text_to_copy += f"[{get_inspect_text('inspect_group_loudness', 'Loudness Analysis')}]\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_integrated', 'Integrated Loudness:')} {data['input_i']} LUFS\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_truepeak', 'True Peak Level:')} {data['input_tp']} dBTP\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_lra', 'Loudness Range (LRA):')} {data['input_lra']} LU\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_threshold', 'Loudness Threshold:')} {data['input_thresh']} LUFS\n\n"

            text_to_copy += f"[{get_inspect_text('inspect_group_levels', 'Signal Levels & Peaks')}]\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_samplepeak', 'Sample Peak:')} {data.get('peak_db', 'N/A')} dBFS\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_minmax', 'Min / Max Level:')} {data.get('min_level', 'N/A')} / {data.get('max_level', 'N/A')}\n\n"

            text_to_copy += f"[{get_inspect_text('inspect_group_dynamics', 'Signal Dynamics & Power')}]\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_rmsaverage', 'Average RMS Power:')} {data.get('rms_db', 'N/A')} dB\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_crest', 'Crest Factor:')} {data.get('crest_factor', 'N/A')}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_dc', 'DC Offset:')} {data.get('dc_offset', 'N/A')}\n"
            text_to_copy += f"{get_inspect_text('inspect_lbl_bitdepth_measured', 'Measured Bit Depth:')} {data.get('bit_depth_measured', 'N/A')}\n"

        if text_to_copy:
            self.win.clipboard_clear()
            self.win.clipboard_append(text_to_copy)
            self.win.update()

            original_text = get_inspect_text("inspect_btn_copy", "Copy")
            self.btn_copy.config(text="✔ " + get_inspect_text("inspect_btn_copied", "Copied!"))
            self.win.after(2000, lambda: self.btn_copy.config(text=original_text))

    def save_data(self):
        """Validates and saves metadata and artwork changes."""
        current_tab = self.notebook.select()

        self.btn_save.config(state="disabled")
        self.btn_reload.config(state="disabled")

        if current_tab == str(self.tab_details):
            track_num = self.track_num_var.get().strip()
            track_total = self.track_total_var.get().strip()
            track_final = track_num
            if track_num and track_total:
                track_final = f"{track_num}/{track_total}"

            disc_num = self.disc_num_var.get().strip()
            disc_total = self.disc_total_var.get().strip()
            disc_final = disc_num
            if disc_num and disc_total:
                disc_final = f"{disc_num}/{disc_total}"

            tags_to_save = {
                "title": self.title_var.get().strip(),
                "artist": self.artist_var.get().strip(),
                "album": self.album_var.get().strip(),
                "album_artist": self.album_artist_var.get().strip(),
                "composer": self.composer_var.get().strip(),
                "work": self.work_var.get().strip(),
                "genre": self.genre_var.get().strip(),
                "track": track_final,
                "year": self.year_var.get().strip(),
                "disc": disc_final,
                "bpm": self.bpm_var.get().strip(),
                "compilation": "1" if self.compilation_var.get() else "0",
                "encoded_by": self.encoded_by_var.get().strip(),
                "url": self.url_var.get().strip(),
                "comment": self.comment_var.get().strip()
            }
            threading.Thread(target=self._save_metadata_worker, args=(tags_to_save,), daemon=True).start()

        elif current_tab == str(self.tab_artwork):
            if self.artwork_deleted_pending:
                threading.Thread(target=self._delete_artwork_worker, daemon=True).start()
            elif self.new_artwork_path:
                threading.Thread(target=self._save_artwork_worker, daemon=True).start()
            else:
                self.btn_save.config(state="normal")
                self.btn_reload.config(state="normal")
        else:
            self.btn_save.config(state="normal")
            self.btn_reload.config(state="normal")

    def _save_metadata_worker(self, tags):
        """Saves tag metadata on a background thread."""
        processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
        success, error_msg = processor.save_track_metadata(self.file_path, tags)

        if success:
            self.win.after(0, self._on_save_success)
        else:
            self.win.after(0, self._on_save_failed, error_msg)

    def _save_artwork_worker(self):
        """Saves artwork changes on a background thread."""
        if not self.new_artwork_path:
            self.win.after(0, self._on_save_success)
            return

        processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
        success, error_msg = processor.save_artwork_mp3(self.file_path, self.new_artwork_path)

        if success:
            self.new_artwork_path = None
            self.win.after(0, self._on_save_success)
        else:
            self.win.after(0, self._on_save_failed, error_msg)

    def _delete_artwork_worker(self):
        """Deletes embedded artwork on a background thread."""
        processor = FFMpegProcessor(self.ffmpeg_dir, lambda msg: None)
        success, error_msg = processor.remove_artwork_mp3(self.file_path)

        if success:
            self.artwork_deleted_pending = False
            self.win.after(0, self._on_save_success)
        else:
            self.win.after(0, self._on_save_failed, error_msg)

    def _on_save_success(self):
        """Handles a successful save operation."""
        self.btn_save.config(state="normal")
        self.btn_reload.config(state="normal")
        messagebox.showinfo(
            get_inspect_text("inspect_save_success_title", "Success"),
            get_inspect_text("inspect_save_success_msg", "Metadata saved successfully!"),
            parent=self.win
        )
        self.reload_data()

    def _on_save_failed(self, error_msg):
        """Handles a failed save operation."""
        self.btn_save.config(state="normal")
        self.btn_reload.config(state="normal")

        if error_msg == "ERR_ACCESS_DENIED":
            translated_details = get_inspect_text("inspect_error_access_denied", "Access Denied: File is in use.")
        else:
            translated_details = error_msg

        base_msg = get_inspect_text("inspect_save_failed_msg", "Failed to save metadata.")
        details_lbl = get_inspect_text("inspect_details_header", "Details:")
        full_error = f"{base_msg}\n\n{details_lbl}\n{translated_details}"

        messagebox.showerror(
            get_inspect_text("inspect_save_failed_title", "Save Error"),
            full_error,
            parent=self.win
        )