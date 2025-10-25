# melcom's FFmpeg Audio Normalizer

A user-friendly GUI for Windows to batch-normalize audio files using the power of FFmpeg's EBU R128 loudness normalization filter.

Version 3 is a complete rewrite from the ground up, focusing on a powerful batch-processing workflow, an integrated audio player, and a modern, intuitive user interface.

![Main application window of FFmpeg Audio Normalizer v3](images/creations-ffmpeg-main.png?raw=true)

## ✨ Features

*   **Batch Processing:** Add multiple files or entire folders to the queue and process them all in one go.
*   **Integrated Audio Player:** Preview your tracks before processing with simple playlist controls (Play, Stop, Next, Previous).
*   **Loudness Normalization:** Normalize audio to a target loudness (LUFS) and True Peak (dBTP) based on the EBU R128 standard.
*   **Platform Presets:** Includes presets for popular platforms like YouTube, Spotify, Apple Music, and broadcast standards.
*   **Multiple Output Formats:** Save your normalized files in WAV, MP3, FLAC, AAC, or OGG format, with clear information about each format's specs.
*   **Live Input Validation:** Custom LUFS/TP fields provide immediate visual feedback to prevent errors.
*   **Multi-Language Support:** The user interface is available in English, German, and Polish.

<p align="center">
  <img src="images/creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="600">
</p>

## 📥 Download & Installation

You can download the latest version, which includes the `.exe` and all necessary files, from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

No installation is required. Simply unzip the archive and run `AudioNormalizer.exe`.

## 🚀 How to Use

#### 1. Prerequisite: Get the FFmpeg Suite
This program requires the complete FFmpeg suite to function correctly:
*   `ffmpeg.exe` (for normalization)
*   `ffplay.exe` (for the audio player)
*   `ffprobe.exe` (for reading track duration)

Download the latest FFmpeg package from a trusted source, for example: **[BtbN's FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)**. For Windows, look for a `.zip` file named something like `ffmpeg-master-latest-win64-gpl.zip`. Unzip it, and you will find the required `.exe` files inside the `bin` subfolder.

#### 2. Configure the Program
*   Start `AudioNormalizer.exe`.
*   Go to the menu `File` -> `Options`.
*   Under "FFmpeg Path", click the **Browse** button and select the folder where your `.exe` files are located (the `bin` folder from the previous step). This only needs to be done once.

#### 3. Process Your Files
*   Use the **"Add Files"** or **"Add Folder"** buttons to populate the file list.
*   (Optional) Select a file in the list and use the player controls to preview it.
*   On the right, choose your desired **LUFS** and **True Peak** presets.
*   Select your **Output Format**.
*   Click **"Start Normalization"** to process all files in the queue.

The normalized files will be saved in the same folder as the source files with a "-Normalized" suffix.

## 💬 Support & Feedback

Please note that the GitHub "Issues" feature has been disabled for this project. As a solo developer, I can provide the best support via direct contact.

If you find a bug, have a feature request, or need help, please use the **[contact form on my website](http://melcom-creations.github.io/melcom-music/contact.html)**.

## 📖 Detailed Help

For more detailed information, please refer to the help files included in the download package. Open `help_de_DE.html` (German), `help_en_US.html` (English), or `help_pl_PL.html` (Polish) in your web browser.

## License

This software is open-source and released under the MIT License. See the [LICENSE.txt](LICENSE.txt) file for details.

---

Cheers,<br>
melcom
