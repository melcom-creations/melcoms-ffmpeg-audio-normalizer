**melcom's FFmpeg Audio Normalizer v2.2.1 (GUI Edition)**

With this program, you can easily normalize the loudness of your audio files using FFmpeg.
The normalized file is automatically saved in the same folder as the original file.

**Quick Guide for You:**

1. **Install FFmpeg:**
   - For this program, you need the free program `ffmpeg.exe`.
   - Download `ffmpeg.exe` from a trustworthy website, for example from https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest.
   - Place the folder containing `ffmpeg.exe` on your computer.

2. **Start the program and specify the FFmpeg path:**
   - Start `AudioNormalizer.exe`.
   - In the program, go to "File" -> "Options".
   - Under "FFmpeg Path", specify the folder where `ffmpeg.exe` is located. This is important so that the program can use FFmpeg.

3. **Normalize an audio file:**
   - In the main window, click "Browse" and select the audio file you want to normalize.
   - Under "LUFS Preset", select a preset for the loudness (e.g., "YouTube" or "Spotify") or enter your own values.
   - Under "Output Format", select the desired format for the normalized file (e.g., WAV, MP3).
   - Click "Start Normalization".
   - The progress will be displayed, and the normalized file will be created automatically.

4. **Options (Settings):**
   - In the "File" -> "Options" menu, you can change the path to FFmpeg, select the program language, and adjust log file settings.

5. **Detailed Help:**
   - For more detailed information, open the help files in the `help` folder.
   - Open `help_de_DE.html` (for German), `help_en_US.html` (for English), or `help_pl_PL.html` (for Polish) with your web browser.

**Important Notes for You:**

* **FFmpeg Path:** Make sure that the path to FFmpeg is correctly specified in the options, otherwise the program will not work.
* **LUFS Presets:** The presets help you choose the right loudness for different platforms (e.g., YouTube, Spotify). However, you can also enter your own values.
* **Output Format:** Choose the desired audio format for the normalized file. WAV is lossless and recommended for the highest quality.

This software is Open-Source (MIT License). See `LICENSE.txt` for details.

Enjoy the program!

Sincerely,
melcom
