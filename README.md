# melcom's FFmpeg Audio Normalizer

A professional yet user-friendly GUI for Windows to batch-normalize audio files using the power of FFmpeg's EBU R128 loudness normalization filter.

Version 3.1.0 ("Feierabend Edition") introduces professional Two-Pass Linear normalization, making it a powerful tool for music mastering and archival.

![Main application window of FFmpeg Audio Normalizer v3](images/creations-ffmpeg-main.png?raw=true)

## ✨ Features

*   **Batch Processing:** Add multiple files or entire folders to the queue and process them all in one go.
*   **Two Normalization Modes:**
    *   **Linear (2-Pass):** Professional mode that preserves full dynamic range. Recommended for music and mastering.
    *   **Dynamic (1-Pass):** Adjusts volume on the fly. Ideal for podcasts, voice, and radio-style streams.
*   **Quality Preservation:** Automatically maintains the **original sample rate** and **bit depth** for WAV and FLAC outputs (supporting high-res audio up to 96kHz/24-bit and beyond).
*   **Metadata & Tags:** All ID3 tags and metadata (Artist, Title, Album, etc.) are preserved and transferred to the normalized files.
*   **Integrated Audio Player:** Preview your tracks before processing with simple playlist controls (Play, Stop, Next, Previous).
*   **Platform Presets:** Includes presets for popular platforms like YouTube, Spotify, Apple Music, and broadcast standards (EBU R128).
*   **Multiple Output Formats:** Save your files in WAV, MP3, FLAC, AAC, or OGG format.
*   **Automatic Cleanup:** Automatically removes temporary work files (`.temp`) if a process is cancelled or an error occurs.
*   **Multi-Language Support:** Available in English, German, and Polish.

<p align="center">
  <img src="images/creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="600">
</p>

## 📥 Download & Installation

You can download the latest version from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

No installation is required. Simply unzip the archive and run `AudioNormalizer.exe`.

## 🚀 How to Use

#### 1. Prerequisite: Get the FFmpeg Suite
This program requires the complete FFmpeg suite to function:
*   `ffmpeg.exe` (for normalization and analysis)
*   `ffplay.exe` (for the audio player)
*   `ffprobe.exe` (for time display and audio quality detection)

Download the latest FFmpeg package from: **[BtbN's FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)**. For Windows, look for a `.zip` file named something like `ffmpeg-master-latest-win64-gpl.zip`. The required `.exe` files are inside the `bin` subfolder.

#### 2. Configure the Program
*   Start `AudioNormalizer.exe`.
*   Go to the menu `File` -> `Options`.
*   Under "FFmpeg Path", select the folder where your FFmpeg `.exe` files are located.

#### 3. Process Your Files
*   Use **"Add Files"** or **"Add Folder"** to populate the list.
*   Select your desired **LUFS** and **True Peak** presets.
*   Choose the **Normalization Mode** (Linear is highly recommended for music to preserve dynamics).
*   Select your **Output Format** and click **"Start Normalization"**.

The normalized files will be saved in the same folder as the source files with a "-Normalized" suffix.

## 💬 Support & Feedback

Please note that the GitHub "Issues" feature has been disabled for this project.

If you find a bug, have a feature request, or need help, please use the **[contact form on my website](http://melcom-creations.github.io/melcom-music/contact.html)**.

## 📖 Detailed Help

For more detailed information, please refer to the help files included in the package: `help_de_DE.html` (German), `help_en_US.html` (English), or `help_pl_PL.html` (Polish).

## 📜 Changelog

For a detailed history of all changes, please see the [CHANGELOG.md](CHANGELOG.md) file.

## License

This software is open-source and released under the MIT License. See the [License.txt](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/blob/main/License.txt) file for details.

---

Cheers,<br>
melcom