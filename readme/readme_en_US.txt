**melcom's FFmpeg Audio Normalizer v3.0.0 (Halloween Edition)**

With this program, you can easily normalize the loudness of your audio files, individually or in batches, using FFmpeg.
The normalized files are automatically saved in the same folder as the original files.

**Quick Guide for You:**

1. **Install FFmpeg Suite:**
   - This program requires the free command-line tools `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe`.
   - Download the tools from a trustworthy website. For Windows users, we recommend the "essentials" or "full" build from https://github.com/BtbN/FFmpeg-Builds/releases. Look for a file like `ffmpeg-master-latest-win64-gpl.zip`.
   - Unzip the package and place the folder containing the `.exe` files on your computer.

2. **Start the Program and Set the FFmpeg Path:**
   - Start `AudioNormalizer.exe`.
   - In the program, go to "File" -> "Options".
   - Under "FFmpeg Path", specify the folder where `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` are located. This is essential for the program to function.

3. **Normalize Your Audio Files:**
   - In the main window, use the "Add Files" or "Add Folder" buttons to build a list of audio files you want to process.
   - Adjust the "LUFS Preset" and "Output Format" on the right to match your needs.
   - Click "Start Normalization".
   - The progress for the entire batch will be displayed, and the normalized files will be created automatically.

4. **Audio Preview:**
   - To preview a file, simply click on it in the list and press the "▶" (Play) button.
   - Use the "«" and "»" buttons to navigate through your file list like a playlist.

5. **Options (Settings):**
   - In the "File" -> "Options" menu, you can change the FFmpeg path, select the program language, and adjust log file settings.

**Important Notes for You:**

* **FFmpeg Suite Path:** Ensure the path to the folder containing `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` is correctly set in the options, otherwise the program will not work.
*   **`ffprobe.exe`:** This file is required for the time display in the audio player. If it's missing, playback will still work, but the duration will not be shown.
* **LUFS Presets:** The presets help you choose the right loudness for different platforms (e.g., YouTube, Spotify). You can also enter your own values.
* **Output Format:** The info box below the format selection gives you details about the technical specifications of the output file.

This software is Open-Source (MIT License). See `LICENSE.txt` for details.

Enjoy the program!

Sincerely,
melcom