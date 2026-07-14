"""
player.py
Handles the audio playback engine via FFplay, including process suspension for pausing.
"""

import os
import subprocess
import threading
import re
import ctypes
from typing import Optional

import constants
import i18n

get_text = i18n.get_text

# --- Playback Controller ---
class AudioPlayer:
    """Manages FFplay-based playback control for the selected audio file."""
    def __init__(self, ffmpeg_path, gui_queue):
        """Initializes the AudioPlayer."""
        self.ffmpeg_path = ffmpeg_path
        self.gui_queue = gui_queue

        self.is_playing = False
        self.is_paused = False
        self.current_playback_process: Optional[subprocess.Popen] = None
        self.total_duration_sec = 0
        self.playback_generation = 0
        self.current_playback_id = 0
        self.ffprobe_checked = False

    def update_ffmpeg_path(self, new_path):
        """Updates the ffmpeg path if it was changed in the options."""
        self.ffmpeg_path = new_path

    def _set_playback_suspended(self, suspend: bool):
        """Uses Windows native API to freeze/unfreeze the ffplay subprocess."""
        process = self.current_playback_process
        if process is None or process.poll() is not None:
            return False
        handle_value = getattr(process, "_handle", None)
        if handle_value is None:
            return False
        try:
            ntdll = ctypes.WinDLL("ntdll.dll")
            handle = int(handle_value)
            if suspend:
                status = ntdll.NtSuspendProcess(handle)
                return status == 0
            else:
                status = ntdll.NtResumeProcess(handle)
                return status == 0
        except Exception:
            return False

    def toggle_pause(self):
        """Toggles the pause state and returns the new paused status, or None if failed."""
        if not self.is_playing: 
            return None

        if not self.is_paused:
            if self._set_playback_suspended(True):
                self.is_paused = True
                return True
        else:
            if self._set_playback_suspended(False):
                self.is_paused = False
                return False
        return None

    def stop(self):
        """Terminates playback completely."""
        if self.is_paused:
            self._set_playback_suspended(False)
            self.is_paused = False

        self.is_playing = False
        if self.current_playback_process and self.current_playback_process.poll() is None:
            try:
                self.current_playback_process.terminate()
            except Exception:
                pass

    def play(self, filepath: str, start_time_sec: float = 0.0):
        """Starts playback of a file in a separate background thread."""
        self.stop()
        self.playback_generation += 1
        playback_id = self.playback_generation
        self.current_playback_id = playback_id

        thread = threading.Thread(target=self._playback_worker, args=(filepath, start_time_sec, playback_id))
        thread.daemon = True
        self.is_playing = True
        thread.start()

    def _playback_worker(self, filepath: str, start_time_sec: float, playback_id: int):
        """Loads metadata and launches FFplay on a background thread."""
        self.gui_queue.put(("toggle_playback_controls", False))

        if not self.is_playing or playback_id != self.current_playback_id:
            return

        ffprobe_path = os.path.join(self.ffmpeg_path, constants.FFPROBE_EXECUTABLE_NAME)
        if not os.path.exists(ffprobe_path):
            if not self.ffprobe_checked:
                self.gui_queue.put(("error", (get_text("error_ffprobe_not_found_title"), get_text("error_ffprobe_not_found_message"))))
                self.ffprobe_checked = True
            self.total_duration_sec = 0
        else:
            try:
                cmd = [ffprobe_path, "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", filepath]
                result = subprocess.run(cmd, capture_output=True, encoding="utf-8", errors="ignore", creationflags=subprocess.CREATE_NO_WINDOW)
                self.total_duration_sec = float(result.stdout.strip())
            except Exception as e:
                self.gui_queue.put(("info", f"\n[FFprobe Analysis Error]: {str(e)}\n"))
                self.total_duration_sec = 0

        if not self.is_playing or playback_id != self.current_playback_id:
            return

        self.gui_queue.put(("update_time", (start_time_sec, self.total_duration_sec)))

        ffplay_path = os.path.join(self.ffmpeg_path, constants.FFPLAY_EXECUTABLE_NAME)
        if not os.path.exists(ffplay_path):
             self.gui_queue.put(("error", (get_text("play_error_ffplay_not_found_title"), get_text("play_error_ffplay_not_found_message"))))
             self.gui_queue.put(("playback_finished", playback_id))
             return

        if not self.is_playing or playback_id != self.current_playback_id:
            return

        try:
            cmd = [ffplay_path, "-nodisp", "-autoexit", "-loglevel", "info"]
            if start_time_sec > 0:
                cmd.extend(["-ss", str(start_time_sec)])
            cmd.append(filepath)

            process = subprocess.Popen(
                cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE,
                text=True, creationflags=subprocess.CREATE_NO_WINDOW,
                encoding='utf-8', errors='ignore'
            )
            self.current_playback_process = process
            stderr = process.stderr
            if stderr is None:
                raise RuntimeError("FFplay stderr pipe is unavailable.")

            buffer = ""
            while self.is_playing and playback_id == self.current_playback_id:
                char = stderr.read(1)
                if not char:
                    break
                if char in ('\r', '\n'):
                    match = re.search(r'^\s*([0-9]+\.[0-9]+)', buffer)
                    if match:
                        current_time_sec = float(match.group(1))
                        self.gui_queue.put(("update_time", (current_time_sec, self.total_duration_sec)))
                    buffer = ""
                else:
                    buffer += char

            process.wait()
        except FileNotFoundError:
            self.gui_queue.put(("error", ("Playback Error", "ffplay.exe could not be executed.")))
        except Exception as e:
            self.gui_queue.put(("info", f"\n[Playback Worker Error]: {str(e)}\n"))
        finally:
            self.gui_queue.put(("playback_finished", playback_id))
