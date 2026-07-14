"""
audio.py
Contains all logic interfacing directly with FFmpeg processing and audio metadata parsing.
"""

import os
import subprocess
import json
import re
from typing import Callable, Optional
from mutagen.id3 import ID3, TENC, WXXX, COMM
import constants

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
    def __init__(self, ffmpeg_path: str, update_callback: Callable, process_callback: Optional[Callable] = None):
        """Initializes the FFMpegProcessor."""
        self.ffmpeg_path = os.path.join(ffmpeg_path, constants.FFMPEG_EXECUTABLE_NAME)
        self.ffmpeg_dir = ffmpeg_path
        self.update_callback = update_callback
        self.process_callback = process_callback

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
        try:
            process = subprocess.Popen(
                command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                text=True, encoding='utf-8', errors='ignore', creationflags=subprocess.CREATE_NO_WINDOW
            )

            if self.process_callback:
                self.process_callback(process)

            full_stderr = ""
            for line in iter(process.stderr.readline, ''):
                full_stderr += line
                self.update_callback(line)

            return_code = process.wait()

            if return_code != 0:
                full_stderr = self._interpret_ffmpeg_error(full_stderr)

            return return_code, full_stderr
        except FileNotFoundError:
            return -1, "ffmpeg_not_found"
        except Exception as e:
            return -1, str(e)

    def _get_audio_info(self, file_path):
        """Returns basic stream information for the selected audio file."""
        ffprobe_path = os.path.join(self.ffmpeg_dir, constants.FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path): return None
        try:
            cmd = [ffprobe_path, "-v", "error", "-select_streams", "a:0",
                   "-show_entries", "stream=sample_rate,sample_fmt,bits_per_raw_sample",
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
                    metadata["comment"] = comm[0].text[0] if comm and comm[0].text else ""
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

        temp_file = os.path.splitext(file_path)[0] + ".metadata" + constants.TEMP_FILE_EXTENSION + os.path.splitext(file_path)[1]

        if self._is_path_too_long(temp_file):
            return False, "Error: Temp path exceeds Windows length limit (MAX_PATH)."

        if not self._has_write_permissions(file_path):
            return False, "Error: Missing write permissions for the directory."

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

        command = [self.ffmpeg_path, "-hide_banner", "-nostats", "-y", "-i", file_path, "-map", "0", "-map_metadata", "0", "-c", "copy"]

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

        ret_code, stderr = self._run_process(command)
        stderr = self._clean_temp_paths_from_log(stderr, temp_file, file_path)

        # Temp file cleanup runs in all cases
        try:
            if ret_code != 0:
                return False, stderr

            try:
                os.replace(temp_file, file_path)
            except OSError as e:
                if "[WinError 5]" in str(e):
                    return False, "ERR_ACCESS_DENIED"
                return False, f"Failed to replace original file: {str(e)}"

            if is_mp3:
                try:
                    try:
                        id3 = ID3(file_path)
                    except Exception:
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
                        id3.add(WXXX(encoding=3, desc="", url=str(url_val)))

                    comment_val = tags.get("comment", "")
                    if str(comment_val).strip():
                        id3.add(COMM(encoding=3, lang="eng", desc="", text=[str(comment_val)]))

                    id3.save(file_path, v2_version=3)
                except Exception:
                    pass

            return True, ""
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
        """Saves embedded artwork into an MP3 file."""
        if self._is_path_too_long(file_path) or self._is_path_too_long(artwork_image_path):
            return False, "Error: Path is too long."

        temp_file = os.path.splitext(file_path)[0] + ".artwork" + constants.TEMP_FILE_EXTENSION + os.path.splitext(file_path)[1]

        if self._is_path_too_long(temp_file):
            return False, "Error: Temp path is too long."

        if not self._has_write_permissions(file_path):
            return False, "Error: Missing write permissions."

        is_mp3 = file_path.lower().endswith(".mp3")

        command = [
            self.ffmpeg_path, "-hide_banner", "-nostats", "-y",
            "-i", file_path,
            "-i", artwork_image_path,
            "-map", "0:a", "-map", "1:v",
            "-c:a", "copy",
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

        ret_code, stderr = self._run_process(command)
        stderr = self._clean_temp_paths_from_log(stderr, temp_file, file_path)

        if ret_code == 0:
            try:
                os.replace(temp_file, file_path)
                return True, ""
            except OSError as e:
                if "[WinError 5]" in str(e):
                    return False, "ERR_ACCESS_DENIED"
                return False, f"Failed to overwrite file with new artwork: {str(e)}"
            finally:
                if os.path.exists(temp_file):
                    try: os.remove(temp_file)
                    except OSError: pass
        else:
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except OSError: pass
            return False, stderr

    def remove_artwork_mp3(self, file_path):
        """Removes embedded artwork from an MP3 file."""
        if self._is_path_too_long(file_path):
            return False, "Error: Path is too long."

        temp_file = os.path.splitext(file_path)[0] + ".noartwork" + constants.TEMP_FILE_EXTENSION + os.path.splitext(file_path)[1]

        if self._is_path_too_long(temp_file):
            return False, "Error: Temp path is too long."

        if not self._has_write_permissions(file_path):
            return False, "Error: Missing write permissions."

        is_mp3 = file_path.lower().endswith(".mp3")

        command = [
            self.ffmpeg_path, "-hide_banner", "-nostats", "-y",
            "-i", file_path,
            "-map", "0:a",
            "-c:a", "copy",
            "-map_metadata", "0"
        ]

        if is_mp3:
            command.extend(["-id3v2_version", "3", "-write_id3v1", "0"])

        command.extend(["-vn", temp_file])

        ret_code, stderr = self._run_process(command)
        stderr = self._clean_temp_paths_from_log(stderr, temp_file, file_path)

        if ret_code == 0:
            try:
                os.replace(temp_file, file_path)
                return True, ""
            except OSError as e:
                if "[WinError 5]" in str(e):
                    return False, "ERR_ACCESS_DENIED"
                return False, f"Failed to overwrite file without artwork: {str(e)}"
            finally:
                if os.path.exists(temp_file):
                    try: os.remove(temp_file)
                    except OSError: pass
        else:
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except OSError: pass
            return False, stderr

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

        dummy_file = os.path.join(target_dir, ".write_test.tmp")
        try:
            with open(dummy_file, 'w') as f:
                f.write("test")
            os.remove(dummy_file)
            return True
        except OSError:
            return False

    def analyze(self, file_path):
        """Runs the configured FFmpeg analysis command for the selected file."""
        if self._is_path_too_long(file_path):
            return -1, "Error: Path too long (Windows MAX_PATH limit)."

        command = [self.ffmpeg_path, "-hide_banner", "-nostats", "-i", file_path, "-af", "astats,loudnorm=print_format=json", "-f", "null", "-"]
        return self._run_process(command)

    def normalize(self, input_file, output_file, lufs, tp, output_format_name, sr_index, quality_index, mode="linear", mastering_preset=constants.DEFAULT_MASTERING_PRESET):
        """Runs the configured FFmpeg normalization command for the selected file."""
        temp_file = os.path.splitext(output_file)[0] + constants.TEMP_FILE_EXTENSION + os.path.splitext(output_file)[1]

        if self._is_path_too_long(input_file, output_file, temp_file):
            return -1, "Error: Target path exceeds Windows length limit (MAX_PATH)."

        if not self._has_write_permissions(output_file):
            return -1, "Error: Missing write permissions for the target directory."

        filter_chain = []
        mastering_chain = build_mastering_filter_chain(mastering_preset or constants.DEFAULT_MASTERING_PRESET)

        if mastering_chain: 
            filter_chain.append(mastering_chain)

        if mode == "linear":
            self.update_callback(f"--> Phase 1/2: Analyzing dynamics for {os.path.basename(input_file)}...\n")
            ret_code, stderr = self.analyze(input_file)
            if ret_code != 0: return ret_code, stderr

            try:
                json_match = re.search(r'\{\s*"input_i".*?\}', stderr, re.DOTALL)
                if not json_match:
                    return -1, "Error: Loudnorm analysis JSON block not found in FFmpeg output."

                m = json.loads(json_match.group(0))

                loudnorm_chain = (f"loudnorm=I={lufs}:TP={tp}:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
                                  f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:"
                                  f"linear=true:print_format=summary")
                self.update_callback(f"--> Analysis Result: Input {m['input_i']} LUFS, Peak {m['input_tp']} dBTP\n")
                self.update_callback(f"--> Phase 2/2: Applying {mastering_preset or constants.DEFAULT_MASTERING_PRESET} + 2-Pass Normalization...\n")
            except Exception as e:
                return -1, f"Error parsing analysis: {str(e)}"
        else:
            loudnorm_chain = f"loudnorm=I={lufs}:TP={tp}:print_format=summary"
            self.update_callback(f"--> Phase 1/1: Applying {mastering_preset or constants.DEFAULT_MASTERING_PRESET} + 1-Pass Normalization...\n")

        filter_chain.append(loudnorm_chain)

        quality_options = constants.FORMAT_QUALITY_OPTIONS.get(output_format_name, [])
        if 0 <= quality_index < len(quality_options):
            quality_str = quality_options[quality_index]
        else:
            quality_str = "Original / Default"

        if output_format_name == "FLAC" and quality_str != "Original / Default":
            raw_options = constants.FLAC_AF_MAP.get(quality_str, [])
            if len(raw_options) >= 2 and raw_options[0] == "-af":
                filter_chain.append(raw_options[1])

        af_filter_string = ",".join(filter_chain)

        cmd_rate = ["-ar", "48000"]
        if sr_index == 0:
            info = self._get_audio_info(input_file)
            if info and "sample_rate" in info:
                cmd_rate = ["-ar", str(info["sample_rate"])]
        else:
            sr_str = constants.SAMPLE_RATES_LIST[sr_index]
            sr_num = sr_str.split()[0]
            cmd_rate = ["-ar", sr_num]

        cmd_codec = []
        cmd_options = []
        cmd_channels = ["-ac", "2"]

        input_bitrate = None
        if quality_str == "Original / Default":
            meta = self.get_track_metadata(input_file)
            if meta and meta.get("bit_rate"):
                input_bitrate = meta.get("bit_rate")

        if output_format_name == "WAV":
            cmd_codec = ["-c:a", "pcm_s16le"]
            cmd_channels = []
            if quality_str == "Original / Default":
                info = self._get_audio_info(input_file)
                if info and "sample_fmt" in info:
                    fmt = info["sample_fmt"]
                    bits = info.get("bits_per_raw_sample", "N/A")
                    if "s16" in fmt: cmd_codec = ["-c:a", "pcm_s16le"]
                    elif "s32" in fmt and bits == "24": cmd_codec = ["-c:a", "pcm_s24le"]
                    elif "s32" in fmt: cmd_codec = ["-c:a", "pcm_s32le"]
                    elif "flt" in fmt or "dbl" in fmt: cmd_codec = ["-c:a", "pcm_f32le"]
            else:
                codec_name = constants.WAV_CODEC_MAP.get(quality_str)
                if codec_name:
                    cmd_codec = ["-c:a", codec_name]

        elif output_format_name == "FLAC":
            cmd_codec = ["-c:a", "flac"]
            cmd_channels = []

        elif output_format_name == "MP3":
            cmd_codec = ["-c:a", "libmp3lame"]
            if quality_str == "Original / Default":
                if input_bitrate:
                    cmd_options = ["-b:a", f"{input_bitrate // 1000}k"]
                else:
                    cmd_options = ["-b:a", "320k"]
            else:
                cmd_options = constants.MP3_ENCODER_MAP.get(quality_str, ["-b:a", "320k"])

        elif output_format_name == "M4A":
            cmd_codec = ["-c:a", "aac"]
            if quality_str == "Original / Default":
                if input_bitrate:
                    cmd_options = ["-b:a", f"{input_bitrate // 1000}k"]
                else:
                    cmd_options = ["-b:a", "256k"]
            else:
                cmd_options = constants.M4A_ENCODER_MAP.get(quality_str, ["-b:a", "256k"])

        elif output_format_name == "OGG":
            cmd_codec = ["-c:a", "libvorbis"]
            if quality_str == "Original / Default":
                if input_bitrate:
                    cmd_options = ["-b:a", f"{input_bitrate // 1000}k"]
                else:
                    cmd_options = ["-q:a", "10"]
            else:
                cmd_options = constants.OGG_ENCODER_MAP.get(quality_str, ["-q:a", "10"])

        command = [self.ffmpeg_path, "-hide_banner", "-nostats", "-i", input_file, "-map_metadata", "0", "-af", af_filter_string]
        if output_format_name == "MP3":
            command.extend(["-id3v2_version", "3", "-write_id3v1", "0"])

        if output_format_name not in ["MP3", "FLAC", "M4A"]:
            command.extend(["-map", "0:a"])
            command.append("-vn")
        else:
            command.extend(["-map", "0:a", "-map", "0:v?", "-c:v", "copy"])

        command.extend(cmd_rate)
        command.extend(cmd_channels)
        command.extend(cmd_codec)
        command.extend(cmd_options)
        command.extend(["-y", temp_file])

        try:
            return_code, stderr = self._run_process(command)
            stderr = self._clean_temp_paths_from_log(stderr, temp_file, output_file)

            if return_code == 0:
                try:
                    os.replace(temp_file, output_file)
                except OSError as e: 
                    if "[WinError 5]" in str(e):
                        return -1, "ERR_ACCESS_DENIED"
                    return -1, str(e)
            return return_code, stderr
        finally:
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except OSError: pass