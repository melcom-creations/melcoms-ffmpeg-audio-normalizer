**melcom's FFmpeg Audio Normalizer v3.1.0 (Feierabend Edition)**

With this program, you can professionally normalize the loudness of your audio files, individually or in batches, using FFmpeg. The normalized files are automatically saved in the same folder as the original source files.

**Quick Guide for You:**

1. **Install FFmpeg Suite:**
   - This program requires the free command-line tools `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe`.
   - Download the tools from a trustworthy website. We recommend the builds from https://github.com/BtbN/FFmpeg-Builds/releases (e.g., `ffmpeg-master-latest-win64-gpl.zip`).
   - Unzip the package and ensure the path to the `bin` folder is correctly set in the program's Options.

2. **Start the Program and Set Up:**
   - Start `AudioNormalizer.exe`.
   - Go to "File" -> "Options" and specify the folder containing your FFmpeg executables.

3. **Normalize Your Audio Files (New in v3.1):**
   - Add files or entire folders to the processing list.
   - Select your LUFS and True Peak presets on the right.
   - **Choose the Mode:** 
     - *Linear (2 Passes):* Recommended for music. Preserves full dynamic range.
     - *Dynamic (1 Pass):* Recommended for voice/radio. Adjusts volume on the fly.
   - Select your output format and click "Start Normalization."

4. **Audio Preview:**
   - Use the integrated player below the list to preview tracks and navigate through your playlist.

**Important Highlights & Notes for You:**

*   **Highest Quality:** When outputting as WAV or FLAC, the program automatically preserves the original sample rate (e.g., 96 kHz) and bit depth (e.g., 24-bit) of the source file. No unnecessary downsampling occurs.
*   **Metadata:** Your tags (Artist, Title, Album, etc.) are preserved and transferred to the new file. MP3s use the ID3v2.3 standard for best compatibility with Windows and external players.
*   **Linear Mode:** The new 2-pass mode (Linear) provides mastering-level precision by analyzing the file first and then leveling it perfectly without squashing the dynamics.
*   **Automatic Cleanup:** The program automatically deletes temporary work files (`.temp`), even if a process is cancelled or an error occurs.
*   **FFmpeg Path:** The program cannot function without the correct path to `ffmpeg.exe`, `ffplay.exe`, and `ffprobe.exe` in the Options.

This software is Open-Source (MIT License). See `LICENSE.txt` for details.

Enjoy the Feierabend Edition!

Sincerely,
melcom