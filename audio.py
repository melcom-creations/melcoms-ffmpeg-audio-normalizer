# -*- coding: utf-8 -*-
"""
audio.py
Contains all logic interfacing directly with FFmpeg processing and audio metadata parsing.
"""

import os
import subprocess
import json
import re
from typing import Callable, Optional
import constants

def _build_compressor_filter(compressor_settings):
    """Generates the acompressor FFmpeg filter string based on preset dictionary values."""
    if not isinstance(compressor_settings, dict): return ""
    parameters = [f"{k}={v}" for k, v in compressor_settings.items() if v is not None]
    return "acompressor=" + ":".join(parameters) if parameters else ""

def _build_softclip_filter(softclip_settings):
    """Generates the asoftclip FFmpeg filter string based on preset dictionary values."""
    if not isinstance(softclip_settings, dict): return ""
    parameters = [f"{k}={v}" for k, v in softclip_settings.items() if v is not None]
    return "asoftclip=" + ":".join(parameters) if parameters else ""

def _build_volume_filter(gain_value):
    """Generates a volume modification filter string."""
    return f"volume={gain_value}" if gain_value is not None else ""

def build_mastering_filter_chain(mastering_preset_name):
    """Assembles the complete audio filter chain string for the selected mastering character."""
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


class FFMpegProcessor:
    """Wrapper class for executing FFmpeg operations, handling both analysis and normalization passes."""
    
    def __init__(self, ffmpeg_path: str, update_callback: Callable, process_callback: Optional[Callable] = None):
        self.ffmpeg_path = os.path.join(ffmpeg_path, constants.FFMPEG_EXECUTABLE_NAME)
        self.ffmpeg_dir = ffmpeg_path
        self.update_callback = update_callback
        self.process_callback = process_callback

    def _run_process(self, command):
        """Executes a subprocess command, captures stderr in real-time, and delegates termination control."""
        try:
            process = subprocess.Popen(
                command, stderr=subprocess.PIPE, stdout=subprocess.DEVNULL,
                text=True, encoding='utf-8', creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if self.process_callback:
                self.process_callback(process)
            
            full_stderr = ""
            for line in iter(process.stderr.readline, ''):
                full_stderr += line
                self.update_callback(line)
            
            return_code = process.wait()
            return return_code, full_stderr
        except FileNotFoundError:
            return -1, "ffmpeg_not_found"
        except Exception as e:
            return -1, str(e)

    def _get_audio_info(self, file_path):
        """Extracts sample rate, format, and bit depth via ffprobe to preserve original source quality."""
        ffprobe_path = os.path.join(self.ffmpeg_dir, constants.FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path): return None
        try:
            cmd = [ffprobe_path, "-v", "error", "-select_streams", "a:0",
                   "-show_entries", "stream=sample_rate,sample_fmt,bits_per_raw_sample",
                   "-of", "json", file_path]
            result = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
            data = json.loads(result.stdout)
            if "streams" in data and len(data["streams"]) > 0: return data["streams"][0]
        except Exception:
            pass
        return None

    def analyze(self, file_path):
        """Performs the first pass EBU R128 analysis."""
        command = [self.ffmpeg_path, "-i", file_path, "-af", "loudnorm=print_format=json", "-f", "null", "-"]
        return self._run_process(command)

    def normalize(self, input_file, output_file, lufs, tp, codec, options, mode="linear", output_format_name="", mastering_preset=constants.DEFAULT_MASTERING_PRESET):
        """Builds the FFmpeg command and executes the final audio rendering pass."""
        temp_file = os.path.splitext(output_file)[0] + constants.TEMP_FILE_EXTENSION + os.path.splitext(output_file)[1]
        filter_chain = []
        mastering_chain = build_mastering_filter_chain(mastering_preset or constants.DEFAULT_MASTERING_PRESET)
        
        if mastering_chain: 
            filter_chain.append(mastering_chain)

        if mode == "linear":
            self.update_callback(f"--> Phase 1/2: Analyzing dynamics for {os.path.basename(input_file)}...\n")
            ret_code, stderr = self.analyze(input_file)
            if ret_code != 0: return ret_code, stderr

            try:
                json_match = re.search(r'\{.*\}', stderr, re.DOTALL)
                if not json_match: return -1, "Error: Could not parse loudnorm analysis data."
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
        af_filter_string = ",".join(filter_chain)

        cmd_rate = ["-ar", "48000"]
        cmd_channels = ["-ac", "2"]
        cmd_codec = ["-c:a", codec]
        
        if output_format_name in ["WAV", "FLAC"]:
            info = self._get_audio_info(input_file)
            if info:
                if "sample_rate" in info: cmd_rate = ["-ar", str(info["sample_rate"])]
                cmd_channels = []
                if output_format_name == "WAV" and "sample_fmt" in info:
                    fmt = info["sample_fmt"]
                    bits = info.get("bits_per_raw_sample", "N/A")
                    if "s16" in fmt: cmd_codec = ["-c:a", "pcm_s16le"]
                    elif "s32" in fmt and bits == "24": cmd_codec = ["-c:a", "pcm_s24le"]
                    elif "s32" in fmt: cmd_codec = ["-c:a", "pcm_s32le"]
                    elif "flt" in fmt or "dbl" in fmt: cmd_codec = ["-c:a", "pcm_f32le"]
                    else: cmd_codec = ["-c:a", "pcm_s16le"]

        command = [self.ffmpeg_path, "-i", input_file, "-map_metadata", "0", "-af", af_filter_string]
        if output_format_name == "MP3": command.extend(["-id3v2_version", "3"])
        
        command.extend(cmd_rate); command.extend(cmd_channels); command.extend(cmd_codec)
        if options: command.extend(options)
        command.extend(["-y", temp_file])
        
        try:
            return_code, stderr = self._run_process(command)
            if return_code == 0:
                try:
                    if os.path.exists(output_file): os.remove(output_file)
                    os.rename(temp_file, output_file)
                except OSError as e: return -1, str(e)
            return return_code, stderr
        finally:
            if os.path.exists(temp_file):
                try: os.remove(temp_file)
                except OSError: pass