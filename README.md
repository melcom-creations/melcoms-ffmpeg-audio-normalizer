# melcom's FFmpeg Audio Normalizer

A professional yet user-friendly GUI for Windows to batch-normalize audio files using the power of FFmpeg's EBU R128 loudness normalization filter.

Version 3.2.0-dev09 ("Nachtschicht Edition") expands the professional Two-Pass Linear normalization engine with improved mastering behavior, scene-oriented character processing, and refined loudness handling for music production and archival workflows.

![Main application window of FFmpeg Audio Normalizer v3](images/creations-ffmpeg-main.png?raw=true)

## ✨ Features

*   **Batch Processing:** Add multiple files or entire folders to the queue and process them all in one go.
*   **Two Normalization Modes:**
    *   **Linear (2-Pass):** Professional mastering-grade normalization using FFmpeg's EBU R128 analysis workflow. Preserves dynamics while achieving highly accurate LUFS and True Peak targets.
    *   **Dynamic (1-Pass):** Faster real-time normalization mode ideal for podcasts, speech, streaming, and broadcast-style workflows.
*   **Scene Mastering Engine:** Includes optional mastering character chains such as "Scene Punch" and "Scene Glue Light" for more cohesive, tracker-inspired sound shaping before normalization.
*   **Quality Preservation:** Automatically maintains the original sample rate and bit depth for WAV and FLAC outputs (supporting high-resolution audio up to 96kHz/24-bit and beyond).
*   **Metadata & Tags:** All ID3 tags and metadata (Artist, Title, Album, etc.) are preserved and transferred to the normalized files.
*   **Integrated Audio Player:** Preview your tracks before processing with simple playlist controls (Play, Stop, Next, Previous).
*   **Platform Presets:** Includes presets for popular platforms like YouTube, Spotify, Apple Music, EBU R128 broadcast standards, and scene-oriented mastering workflows.
*   **Multiple Output Formats:** Save your files in WAV, MP3, FLAC, AAC, or OGG format.
*   **Automatic Cleanup:** Automatically removes temporary work files (`.temp`) if a process is cancelled or an error occurs.
*   **Portable Application:** The application is fully portable and does not modify the Windows registry.
*   **Multi-Language Support:** Available in English, German, and Polish.

<p align="center">
  <img src="images/creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="600">
</p>

## 📥 Download & Installation

You can download the latest stable or development builds from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

No installation is required. Simply unzip the archive and run `AudioNormalizer.exe`.

The application is fully portable and does not modify the Windows registry.

## 🚀 How to Use

#### 1. Prerequisite: Get the FFmpeg Suite

This program requires the complete FFmpeg suite to function:

*   `ffmpeg.exe` - normalization, mastering, and analysis
*   `ffplay.exe` - integrated audio player
*   `ffprobe.exe` - duration, bitrate, and audio quality detection

Download the latest FFmpeg package from:

**[BtbN's FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)**

For Windows, look for a `.zip` file named similar to:

`ffmpeg-master-latest-win64-gpl.zip`

The required `.exe` files are located inside the `bin` subfolder.

#### 2. Configure the Program

*   Start `AudioNormalizer.exe`
*   Open `File -> Options`
*   Under "FFmpeg Path", select the folder containing the FFmpeg executables

#### 3. Process Your Files

*   Use **"Add Files"** or **"Add Folder"** to populate the queue
*   Select your desired **LUFS** and **True Peak** presets
*   Choose the **Normalization Mode**
*   Select the desired **Output Format**
*   Click **"Start Normalization"**

The normalized files will be saved in the same directory as the source files with a `-Normalized` suffix.

---

## 🎛 Recommended Workflow

### For Music / Scene Releases

Recommended settings:

*   Mode: `Linear (2-Pass)`
*   Target Loudness: `-12 LUFS`
*   True Peak: `-1 dBTP`
*   Mastering Preset: `Scene Glue Light`

This configuration preserves punch and dynamics while providing a cohesive and scene-friendly master.

### For Streaming / Podcasts

Recommended settings:

*   Mode: `Dynamic (1-Pass)`
*   Target Loudness: `-14 LUFS`
*   True Peak: `-1 dBTP`

---

## 💬 Support & Feedback

Please note that GitHub Issues are intentionally disabled to keep development and support centralized.

If you find a bug, have a feature request, or need help, please use the contact form on my website:

**http://melcom-creations.github.io/melcom-music/contact.html**

---

## 📖 Detailed Help

For more detailed information, please refer to the included help files:

*   `help_de_DE.html`
*   `help_en_US.html`
*   `help_pl_PL.html`

---

## 📜 Changelog

For a detailed history of all changes, please see:

`CHANGELOG.md`

---

## ⚖ License

This software is open-source and released under the MIT License.

See:

`LICENSE.txt`

for details.

---

Greetings from the nightshift,<br>
melcom
