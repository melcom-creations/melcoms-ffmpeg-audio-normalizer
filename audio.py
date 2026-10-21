"""
audio.py
Contains all logic interfacing directly with FFmpeg processing and audio metadata parsing.
"""

import os
import subprocess
import json
import re
import tempfile
from typing import Callable, Optional
from mutagen.id3 import ID3, ID3NoHeaderError, TENC, WXXX, COMM
import constants
from analysis import parse_analysis, finite_number, normalization_mode
from normalization_results import NormalizationResult, valid_targets, valid_encoder_headroom

# --- Filter Builders ---
def _build_compressor_filter(compressor_settings):
    """Builds an FFmpeg compressor filter string from a settings mapping."""
    if not isinstance(compressor_settings, dict): return ""
    parameters = [f"{k}={v}" for k, v in compressor_settings.items() if v is not None]
    return "acompressor=" + ":".join(parameters) if parameters else ""

def _build_softclip_filter(softclip_settings):
    """Builds an FFmpeg soft clip filter string from a settings mapping."""
    if not isinstance(softclip_settings, dict): return ""
    parameters = [f"{k}={v}" for k, v in softclip_settings.items() if v is not None]
    return "asoftclip=" + ":".join(parameters) if parameters else ""

def _build_volume_filter(gain_value):
    """Builds an FFmpeg volume filter string for a gain value."""
    return f"volume={gain_value}" if gain_value is not None else ""

def build_mastering_filter_chain(mastering_preset_name):
    """Builds the full FFmpeg filter chain for a mastering preset."""
    preset = constants.MASTERING_PRESETS.get(mastering_preset_name)
    if not preset or not preset.get("enabled", False): return ""

    filter_parts = []
    for filter_key in ("pre_gain", "compressor", "softclip", "post_gain"):
        filter_value = preset.get(filter_key)
        if filter_value is None: continue
        if filter_key == "compressor": filter_parts.append(_build_compressor_filter(filter_value))
        elif filter_key == "softclip": filter_parts.append(_build_softclip_filter(filter_value))
        else: filter_parts.append(_build_volume_filter(filter_value))
    return ",".join([part for part in filter_parts if part])


# --- FFmpeg Processor ---
class FFMpegProcessor:

    """Provides FFmpeg- and ffprobe-based audio processing helpers."""
    def __init__(self, ffmpeg_path: str, update_callback: Callable, process_callback: Optional[Callable] = None,
                 cancel_callback=None, stage_callback=None):
        """Initializes the FFMpegProcessor."""
        self.ffmpeg_path = os.path.join(ffmpeg_path, constants.FFMPEG_EXECUTABLE_NAME)
        self.ffmpeg_dir = ffmpeg_path
        self.update_callback = update_callback
        self.process_callback = process_callback
        self.cancel_callback = cancel_callback or (lambda: False)
        self.stage_callback = stage_callback
        self.last_result = None

    def _clean_temp_paths_from_log(self, log_text: str, temp_path: str, real_path: str) -> str:
        """Replaces temporary paths in log output with the corresponding source paths."""
        if not log_text:
            return log_text
        log_text = log_text.replace(temp_path, real_path)
        log_text = log_text.replace(temp_path.replace('\\', '/'), real_path.replace('\\', '/'))
        log_text = log_text.replace(temp_path.replace('/', '\\'), real_path.replace('/', '\\'))
        return log_text

    def _interpret_ffmpeg_error(self, stderr_output: str) -> str:
        """Maps common FFmpeg stderr signatures to user-friendly diagnostics."""
        if not stderr_output:
            return "Error: FFmpeg process failed without any error output."

        signatures = {
            "Unknown encoder": "The selected audio encoder is not supported by your FFmpeg build. Please ensure you are using a full FFmpeg build containing the required codecs (e.g., libmp3lame, libvorbis).",
            "Invalid data found when processing input": "The source file appears to be corrupted or is not a valid audio format.",
            "Permission denied": "File access was denied. The file might be read-only, locked by another program (e.g., antivirus, cloud sync), or you lack the required folder permissions.",
            "No such file or directory": "The file or directory could not be found. Ensure the path is correct and accessible.",
            "Error initializing filter": "The FFmpeg audio filter could not be initialized. This is often caused by invalid LUFS/True Peak parameters or unsupported audio options.",
            "moov atom not found": "The file metadata is incomplete or broken. This typically happens with incomplete downloads or corrupted M4A/MP4 files.",
            "codec frame size is not set": "Audio codec parameters are missing or invalid. The source file might be corrupted."
        }

        for signature, diagnostic in signatures.items():
            if signature in stderr_output:
                return f"Error Diagnostic: {diagnostic}\n\n--- Original FFmpeg Error ---\n{stderr_output.strip()}"

        return stderr_output

    def _run_process(self, command):
        """Runs the prepared FFmpeg command and streams stderr to the UI callback."""
        process = None
        try:
            if self.cancel_callback():
                return -2, ""
            process = subprocess.Popen(
                command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                text=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW
            )

            if self.process_callback:
                self.process_callback(process)

            if self.cancel_callback():
                process.terminate()

            full_stderr = ""
            for line in iter(process.stderr.readline, ''):
                full_stderr += line
                self.update_callback(line)

            return_code = process.wait()

            if self.cancel_callback():
                return -2, full_stderr

            if return_code != 0:
                full_stderr = self._interpret_ffmpeg_error(full_stderr)

            return return_code, full_stderr
        except FileNotFoundError:
            return -1, "ffmpeg_not_found"
        except Exception as e:
            return -1, str(e)
        finally:
            if process is not None:
                if process.poll() is None:
                    process.terminate()
                    process.wait()
                if process.stderr is not None:
                    process.stderr.close()
            if self.process_callback:
                self.process_callback(None)

    def _get_audio_info(self, file_path):
        """Returns basic stream information for the selected audio file."""
        ffprobe_path = os.path.join(self.ffmpeg_dir, constants.FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path): return None
        try:
            cmd = [ffprobe_path, "-v", "error", "-select_streams", "a:0",
                   "-show_entries", "stream=sample_rate,sample_fmt,bits_per_raw_sample,channels,codec_name,bit_rate",
                   "-of", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
            data = json.loads(result.stdout)
            if "streams" in data and len(data["streams"]) > 0: return data["streams"][0]
        except Exception:
            pass
        return None

    def get_track_metadata(self, file_path):
        """Returns container and tag metadata for the selected audio file."""
        ffprobe_path = os.path.join(self.ffmpeg_dir, constants.FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path):
            return None
        try:
            cmd = [ffprobe_path, "-v", "error", "-show_format", "-show_streams", "-select_streams", "a:0", "-of", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
            data = json.loads(result.stdout)

            metadata = {}
            if "format" in data:
                f = data["format"]
                metadata["filename"] = os.path.basename(file_path)
                metadata["container"] = f.get("format_long_name", "Unknown Container")
                metadata["duration"] = float(f.get("duration", 0))
                metadata["size_bytes"] = int(f.get("size", 0))

                bit_rate_raw = f.get("bit_rate")
                if bit_rate_raw:
                    try:
                        metadata["bit_rate"] = int(bit_rate_raw)
                    except ValueError:
                        pass

                tags = f.get("tags", {})
                metadata["artist"] = tags.get("artist") or tags.get("ARTIST") or ""
                metadata["title"] = tags.get("title") or tags.get("TITLE") or ""
                metadata["album"] = tags.get("album") or tags.get("ALBUM") or ""
                metadata["album_artist"] = tags.get("album_artist") or tags.get("ALBUM_ARTIST") or tags.get("albumartist") or ""
                metadata["composer"] = tags.get("composer") or tags.get("COMPOSER") or ""
                metadata["work"] = tags.get("grouping") or tags.get("GROUPING") or tags.get("work") or tags.get("WORK") or ""
                metadata["genre"] = tags.get("genre") or tags.get("GENRE") or ""
                metadata["track"] = tags.get("track") or tags.get("TRACK") or ""
                metadata["year"] = tags.get("date") or tags.get("DATE") or tags.get("year") or tags.get("YEAR") or ""
                metadata["disc"] = tags.get("disc") or tags.get("DISC") or ""
                metadata["bpm"] = tags.get("tbpm") or tags.get("TBPM") or tags.get("bpm") or tags.get("BPM") or ""
                metadata["compilation"] = tags.get("compilation") or tags.get("COMPILATION") or ""
                metadata["comment"] = tags.get("comment") or tags.get("COMMENT") or ""

            if file_path.lower().endswith(".mp3"):
                try:
                    id3 = ID3(file_path)
                    metadata["encoded_by"] = str(id3.get("TENC",""))
                    wxxx = id3.getall("WXXX")
                    metadata["url"] = wxxx[0].url if wxxx else ""
                    comm = id3.getall("COMM")
                    metadata["comment"] = comm[0].text[0] if comm and comm[0].text else metadata.get("comment", "")
                except Exception:
                    pass

            if "streams" in data and len(data["streams"]) > 0:
                s = data["streams"][0]
                metadata["codec"] = s.get("codec_long_name", "Unknown Codec")
                metadata["sample_rate"] = int(s.get("sample_rate", 0))
                metadata["channels"] = int(s.get("channels", 0))
                metadata["sample_fmt"] = s.get("sample_fmt", "")
                metadata["bits_per_sample"] = int(s.get("bits_per_raw_sample", 0)) if s.get("bits_per_raw_sample") else None

                if not metadata.get("bit_rate") and s.get("bit_rate"):
                    try:
                        metadata["bit_rate"] = int(s.get("bit_rate"))
                    except ValueError:
                        pass

                if "duration" in metadata and metadata["sample_rate"]:
                    metadata["total_samples"] = int(metadata["duration"] * metadata["sample_rate"])

            return metadata
        except Exception:
            return None

    def save_track_metadata(self, file_path, tags):
        """Writes updated tag metadata back to the selected audio file."""
        if self._is_path_too_long(file_path):
            return False, "Error: Path too long (Windows MAX_PATH limit)."

        if not self._has_write_permissions(file_path):
            return False, "Error: Missing write permissions for the directory."

        try:
            temp_file = self._create_edit_temp(file_path, "metadata")
        except OSError as error:
            return False, str(error)

        ffmpeg_key_map = {
            "title": "title",
            "artist": "artist",
            "album": "album",
            "album_artist": "album_artist",
            "composer": "composer",
            "work": "grouping",
            "genre": "genre",
            "track": "track",
            "year": "date",
            "disc": "disc",
            "bpm": "tbpm",
            "compilation": "compilation",
            "comment": "comment"
        }

        command = [self.ffmpeg_path, "-hide_banner", "-nostdin", "-nostats", "-y", "-i", file_path, "-map", "0", "-map_metadata", "0", "-c", "copy"]

        is_mp3 = file_path.lower().endswith(".mp3")

        if is_mp3:
            command.extend(["-id3v2_version", "3", "-write_id3v1", "0"])
            command.extend(["-metadata", "comment=", "-metadata", "encoded_by=", "-metadata", "url="])

        for gui_key, val in tags.items():
            if gui_key in ("url", "encoded_by"):
                continue
            if is_mp3 and gui_key == "comment":
                continue

            ffmpeg_key = ffmpeg_key_map.get(gui_key)
            if ffmpeg_key:
                command.extend(["-metadata", f"{ffmpeg_key}={val}"])
                if gui_key == "bpm":
                    command.extend(["-metadata", f"bpm={val}"])

        command.append(temp_file)

        try:
            ret_code, stderr = self._run_process(command)
            stderr = self._clean_temp_paths_from_log(stderr, temp_file, file_path)
            if ret_code != 0 or self.cancel_callback():
                return False, stderr

            if is_mp3:
                try:
                    try:
                        id3 = ID3(temp_file)
                    except ID3NoHeaderError:
                        id3 = ID3()

                    id3.delall("COMM")
                    id3.delall("WXXX")
                    id3.delall("TENC")

                    txxx_keys = [k for k in id3.keys() if k.startswith("TXXX")]
                    for k in txxx_keys:
                        desc = getattr(id3[k], "desc", "").lower()
                        if desc in ("comment", "url", "encoded by"):
                            del id3[k]

                    encoded_by_val = tags.get("encoded_by", "")
                    if str(encoded_by_val).strip():
                        id3.add(TENC(encoding=3, text=[str(encoded_by_val)]))

                    url_val = tags.get("url", "")
                    if str(url_val).strip():
                        # An empty URL description does not need a UTF-16 byte-order mark.
                        id3.add(WXXX(encoding=0, desc="", url=str(url_val)))

                    comment_val = tags.get("comment", "")
                    if str(comment_val).strip():
                        id3.add(COMM(encoding=3, lang="eng", desc="", text=[str(comment_val)]))

                    id3.update_to_v23()
                    id3.save(temp_file, v2_version=3)
                except Exception as error:
                    return False, f"Failed to save MP3 tags: {error}"

            return self._commit_edit(temp_file, file_path)
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

    def extract_artwork(self, file_path, out_png_path, scale_size=None):
        """Extracts embedded artwork from the selected audio file."""
        ffprobe_path = os.path.join(self.ffmpeg_dir, constants.FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path):
            return False, None
        try:
            cmd = [ffprobe_path, "-v", "error", "-select_streams", "v:0",
                   "-show_entries", "stream=codec_name,width,height", "-of", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
            data = json.loads(result.stdout)

            if "streams" not in data or len(data["streams"]) == 0:
                return False, None

            s = data["streams"][0]
            codec = s.get("codec_name", "").upper()
            codec_display = "JPG" if codec == "MJPEG" else (codec if codec else "IMG")

            width = s.get("width", 0)
            height = s.get("height", 0)
            info_str = f"{codec_display} / {width} x {height}"

            filter_args = []
            if scale_size:
                filter_args = ["-vf", f"scale={scale_size}:{scale_size}:force_original_aspect_ratio=decrease"]

            cmd_extract = [self.ffmpeg_path, "-hide_banner", "-nostats", "-y", "-i", file_path, "-an"]
            cmd_extract.extend(filter_args)
            cmd_extract.extend(["-vcodec", "png", out_png_path])

            ret, stderr = self._run_process(cmd_extract)
            if ret == 0 and os.path.exists(out_png_path):
                return True, info_str
            return False, None
        except Exception:
            return False, None

    def save_artwork_mp3(self, file_path, artwork_image_path):
        """Save embedded artwork in supported MP3, FLAC, and M4A containers."""
        if self._is_path_too_long(file_path) or self._is_path_too_long(artwork_image_path):
            return False, "Error: Path is too long."

        if not self._has_write_permissions(file_path):
            return False, "Error: Missing write permissions."

        try:
            temp_file = self._create_edit_temp(file_path, "artwork")
        except OSError as error:
            return False, str(error)

        is_mp3 = file_path.lower().endswith(".mp3")

        command = [
            self.ffmpeg_path, "-hide_banner", "-nostdin", "-nostats", "-y",
            "-i", file_path,
            "-i", artwork_image_path,
            "-map", "0:a", "-map", "1:v",
            "-c:a", "copy", "-c:v", "copy",
            "-map_metadata", "0"
        ]

        if is_mp3:
            command.extend(["-id3v2_version", "3", "-write_id3v1", "0"])

        command.extend([
            "-metadata:s:v", "title=Album cover",
            "-metadata:s:v", "comment=Cover (front)",
            "-disposition:v", "attached_pic",
            temp_file
        ])

        return self._run_artwork_edit(command, temp_file, file_path)

    def remove_artwork_mp3(self, file_path):
        """Remove embedded artwork from supported audio containers."""
        if self._is_path_too_long(file_path):
            return False, "Error: Path is too long."

        if not self._has_write_permissions(file_path):
            return False, "Error: Missing write permissions."

        try:
            temp_file = self._create_edit_temp(file_path, "noartwork")
        except OSError as error:
            return False, str(error)

        is_mp3 = file_path.lower().endswith(".mp3")

        command = [
            self.ffmpeg_path, "-hide_banner", "-nostdin", "-nostats", "-y",
            "-i", file_path,
            "-map", "0:a",
            "-c:a", "copy",
            "-map_metadata", "0"
        ]

        if is_mp3:
            command.extend(["-id3v2_version", "3", "-write_id3v1", "0"])

        command.extend(["-vn", temp_file])

        return self._run_artwork_edit(command, temp_file, file_path)

    def _run_artwork_edit(self, command, temp_file, file_path):
        """Clean up the reserved output after every artwork-processing outcome."""
        try:
            ret_code, stderr = self._run_process(command)
            stderr = self._clean_temp_paths_from_log(stderr, temp_file, file_path)
            if ret_code != 0:
                return False, stderr
            if file_path.lower().endswith(".mp3"):
                restored, details = self._restore_mp3_metadata(file_path, temp_file, replace_artwork=True)
                if not restored:
                    return False, details
            return self._commit_edit(temp_file, file_path)
        finally:
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass

    def _restore_mp3_metadata(self, source, destination, replace_artwork=False):
        """Keep source ID3 frames that FFmpeg cannot round-trip through its tag map."""
        try:
            try:
                tags = ID3(source)
            except ID3NoHeaderError:
                return True, ""
            version = tags.version[1] if tags.version[1] in (3, 4) else 3
            if replace_artwork:
                rendered = ID3(destination)
                tags.delall("APIC")
                for picture in rendered.getall("APIC"):
                    tags.add(picture)
            if version == 3:
                tags.update_to_v23()
            tags.save(destination, v2_version=version)
            return True, ""
        except Exception as error:
            return False, f"Failed to preserve MP3 tags: {error}"

    def _create_edit_temp(self, file_path, operation):
        """Reserve a unique sibling file without touching similarly named files."""
        directory = os.path.dirname(os.path.abspath(file_path))
        stem, extension = os.path.splitext(os.path.basename(file_path))
        descriptor, path = tempfile.mkstemp(prefix=f"{stem[:48]}.{operation}.",
                                            suffix=constants.TEMP_FILE_EXTENSION + extension, dir=directory)
        os.close(descriptor)
        if self._is_path_too_long(path):
            os.remove(path)
            raise OSError("Error: Temp path exceeds Windows length limit (MAX_PATH).")
        return path

    def _commit_edit(self, temporary, original):
        """Replace the original only after every editing stage has succeeded."""
        if self.cancel_callback():
            return False, ""
        try:
            os.replace(temporary, original)
        except PermissionError:
            return False, "ERR_ACCESS_DENIED"
        except OSError as error:
            return False, f"Failed to replace original file: {error}"
        return True, ""

    def _is_path_too_long(self, *paths):
        """Checks whether a file path exceeds the Windows path limit."""
        if os.name == 'nt':
            for path in paths:
                if len(os.path.abspath(path)) >= 250:
                    return True
        return False

    def _has_write_permissions(self, target_path):
        """Checks whether the target directory is writable."""
        target_dir = os.path.dirname(os.path.abspath(target_path))
        if not target_dir: 
            target_dir = "."

        try:
            with tempfile.TemporaryFile(dir=target_dir) as probe:
                probe.write(b"test")
            return True
        except OSError:
            return False

    def analyze(self, file_path, lufs=-24, tp=-2, pre_filters=""):
        """Runs the configured FFmpeg analysis command for the selected file."""
        if self._is_path_too_long(file_path):
            return -1, "Error: Path too long (Windows MAX_PATH limit)."

        filters = [pre_filters, "astats", f"loudnorm=I={lufs}:TP={tp}:LRA=11:print_format=json"]
        command = [self.ffmpeg_path, "-hide_banner", "-nostdin", "-nostats", "-i", file_path,
                   "-map", "0:a:0", "-af", ",".join(part for part in filters if part), "-f", "null", "-"]
        return self._run_process(command)

    def normalize(self, input_file, output_file, lufs, tp, output_format_name, sr_index,
                  quality_index, mode="linear", mastering_preset=constants.DEFAULT_MASTERING_PRESET,
                  verify_output=False, encoder_headroom_db=0.0):
        """Normalize one file and optionally measure its encoded output."""
        result = NormalizationResult(input_file, output_file, lufs, tp, mode,
                                     mastering_preset, bool(verify_output))
        self.last_result = result
        temp_file = None

        def fail(code, details, key=""):
            result.processing_status = "cancelled" if self.cancel_callback() else "failed"
            result.error_code = key
            result.error_details = details
            return code, details

        def stage(name):
            if self.stage_callback:
                self.stage_callback(name, output_file if name == "verify" else input_file)

        if not valid_targets(lufs, tp):
            return fail(-1, "", "processing_invalid_targets")
        lufs, tp = float(lufs), float(tp)
        result.target_lufs, result.target_tp = lufs, tp
        if not valid_encoder_headroom(encoder_headroom_db):
            return fail(-1, "", "encoder_headroom_invalid")
        # Reserve codec headroom before encoding, independently of output verification.
        result.encoder_headroom_db = float(encoder_headroom_db) if output_format_name in ("MP3", "M4A", "OGG") else 0.0
        processing_tp = max(-9.0, tp - result.encoder_headroom_db)
        result.processing_tp = processing_tp
        quality_options = constants.FORMAT_QUALITY_OPTIONS.get(output_format_name, [])
        if (mode not in ("linear", "dynamic") or not quality_options
                or not isinstance(sr_index, int) or not 0 <= sr_index < len(constants.SAMPLE_RATES_LIST)
                or not isinstance(quality_index, int) or not 0 <= quality_index < len(quality_options)):
            return fail(-1, "", "processing_invalid_settings")
        if self.cancel_callback():
            return fail(-2, "")
        if self._is_path_too_long(input_file, output_file):
            return fail(-1, "", "processing_path_too_long")
        if not self._has_write_permissions(output_file):
            return fail(-1, "", "processing_write_denied")

        try:
            quality_str = quality_options[quality_index]
            result.output_format, result.output_quality = output_format_name, quality_str
            info = self._get_audio_info(input_file) or {}
            rate = str(info.get("sample_rate", 48000)) if sr_index == 0 else constants.SAMPLE_RATES_LIST[sr_index].split()[0]
            pre_filters = []
            if output_format_name in ("MP3", "M4A", "OGG"):
                pre_filters.append("aformat=channel_layouts=stereo")
            mastering_chain = build_mastering_filter_chain(mastering_preset or constants.DEFAULT_MASTERING_PRESET)
            if mastering_chain:
                pre_filters.append(mastering_chain)
            prefix = ",".join(pre_filters)

            if verify_output and (mode != "linear" or prefix):
                stage("analyze")
                code, log = self.analyze(input_file)
                if code != 0:
                    return fail(code, log)
                result.before = parse_analysis(log)

            target_lra = 11 if mode == "linear" else 7
            loudnorm = f"loudnorm=I={lufs}:TP={processing_tp}:LRA={target_lra}:linear=false:print_format=json"
            normalization_skipped = bool(result.before is not None and not result.before.measurable)
            if mode == "linear":
                stage("analyze")
                code, log = self.analyze(input_file, lufs, processing_tp, prefix)
                if code != 0:
                    return fail(code, log)
                measurement = parse_analysis(log)
                if not prefix:
                    result.before = measurement
                measured = measurement.raw
                normalization_skipped = not measurement.measurable
                keys = ("input_i", "input_tp", "input_lra", "input_thresh", "target_offset")
                if all(finite_number(measured.get(key)) is not None for key in keys):
                    loudnorm = (
                        f"loudnorm=I={lufs}:TP={processing_tp}:LRA=11:measured_I={measured['input_i']}:"
                        f"measured_TP={measured['input_tp']}:measured_LRA={measured['input_lra']}:"
                        f"measured_thresh={measured['input_thresh']}:offset={measured['target_offset']}:"
                        "linear=true:print_format=json"
                    )

            if normalization_skipped:
                loudnorm = "anull"
                result.processing_tp = None
            # Nonfinite filter output must not become full-scale integer samples.
            finite_output = "aeval='if(isnan(val(ch))+isinf(val(ch)),0,val(ch))':c=same"
            filters = pre_filters + [loudnorm, finite_output]
            codec_options = []
            if output_format_name == "WAV":
                codec = constants.WAV_CODEC_MAP.get(quality_str)
                if codec is None:
                    fmt, bits = info.get("sample_fmt", ""), str(info.get("bits_per_raw_sample", ""))
                    if "dbl" in fmt:
                        codec = "pcm_f64le"
                    elif "flt" in fmt:
                        codec = "pcm_f32le"
                    elif "s32" in fmt:
                        codec = "pcm_s24le" if bits == "24" else "pcm_s32le"
                    elif "u8" in fmt:
                        codec = "pcm_u8"
                    else:
                        codec = "pcm_s16le"
            elif output_format_name == "FLAC":
                codec = "flac"
                bits = "16" if quality_str.startswith("16") else "24"
                if quality_str == "Original / Default" and "s16" in info.get("sample_fmt", ""):
                    bits = "16"
                codec_options = ["-sample_fmt", "s16" if bits == "16" else "s32", "-bits_per_raw_sample", bits]
            else:
                codec, mapping = {
                    "MP3": ("libmp3lame", constants.MP3_ENCODER_MAP),
                    "M4A": ("aac", constants.M4A_ENCODER_MAP),
                    "OGG": ("libvorbis", constants.OGG_ENCODER_MAP),
                }[output_format_name]
                codec_options = list(mapping[quality_str])
                if output_format_name == "MP3":
                    codec_options.extend(["-abr", "0", "-compression_level:a", "0"])

            output_dir = os.path.dirname(os.path.abspath(output_file))
            stem, extension = os.path.splitext(os.path.basename(output_file))
            descriptor, temp_file = tempfile.mkstemp(prefix=stem[:48] + ".", suffix=".temp" + extension, dir=output_dir)
            os.close(descriptor)
            if self._is_path_too_long(temp_file):
                return fail(-1, "", "processing_path_too_long")

            command = [self.ffmpeg_path, "-hide_banner", "-nostdin", "-nostats", "-i", input_file,
                       "-map_metadata", "0", "-map", "0:a:0", "-af", ",".join(filters)]
            if output_format_name in ("MP3", "FLAC", "M4A"):
                command.extend(["-map", "0:v?", "-c:v", "copy"])
            else:
                command.append("-vn")
            if output_format_name == "MP3":
                command.extend(["-id3v2_version", "3", "-write_id3v1", "0"])
            command.extend(["-ar", rate, "-c:a", codec, *codec_options, "-y", temp_file])
            stage("normalize")
            code, log = self._run_process(command)
            log = self._clean_temp_paths_from_log(log, temp_file, output_file)
            if code != 0 or self.cancel_callback():
                return fail(-2 if self.cancel_callback() else code, log)
            if output_format_name == "MP3" and input_file.lower().endswith(".mp3"):
                restored, details = self._restore_mp3_metadata(input_file, temp_file)
                if not restored:
                    return fail(-1, details)
            if self.cancel_callback():
                return fail(-2, log)
            result.actual_mode = "not_applied" if normalization_skipped else normalization_mode(log)
            os.replace(temp_file, output_file)
            result.output_created = True
            result.processing_status = "created"

            if verify_output:
                result.verification_status = "pending"
                if self.cancel_callback():
                    result.verification_status = "cancelled"
                    return 0, log
                stage("verify")
                check_code, check_log = self.analyze(output_file)
                log += "\n" + check_log
                if self.cancel_callback():
                    result.verification_status = "cancelled"
                elif check_code != 0:
                    result.verification_status = "failed"
                    result.error_details = check_log
                else:
                    try:
                        result.after = parse_analysis(check_log)
                        result.evaluate()
                    except ValueError as error:
                        result.verification_status = "failed"
                        result.error_details = str(error)
            return 0, log
        except (OSError, ValueError, TypeError, KeyError) as error:
            if result.output_created:
                result.verification_status = "cancelled" if self.cancel_callback() else "failed"
                result.error_details = str(error)
                return 0, str(error)
            key = "processing_write_denied" if isinstance(error, PermissionError) else ""
            return fail(-1, str(error), key)
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except OSError:
                    pass
