# melcom's FFmpeg Audio Normalizer

Welcome to the **Kontrollraum Edition** - where raw audio signals meet absolute **Kontrolle**. If you are tired of wrestling with clunky command-line arguments, cryptic parameters, or clipping nightmares, you have just entered your new audio command center.

melcom's FFmpeg Audio Normalizer is a professional, high-fidelity Windows GUI designed to give you complete control over batch audio normalization workflows using FFmpeg's industry-standard EBU R128 loudness algorithm.

Version 4.0.6 introduces the new **Audio Properties Inspector** featuring a lossless metadata editor, album artwork manager, advanced signal statistics, and a bulletproof FFmpeg diagnostic engine.

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/melcoms_ffmpeg_audio_normalizer_-_image__4__juni_2026,_23_41_47-2560x2560.jpg"><img src="images/melcoms_ffmpeg_audio_normalizer_-_image__4__juni_2026,_23_41_47-2560x2560.jpg?raw=true" alt="melcom's FFmpeg Audio Normalizer Cover" width="600"></a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-before-after.png"><img src="images/creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="49%"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/02-creations-ffmpeg-screenshot_2026-06-05_115552.png"><img src="images/02-creations-ffmpeg-screenshot_2026-06-05_115552.png?raw=true" alt="Main application window of FFmpeg Audio Normalizer" width="49%"></a>
</p>

## ✨ Features

*   **Audio Properties Inspector:** View comprehensive file details, exact audio streams, and a newly integrated nominal **Bitrate** indicator at a glance. Bit depths for lossy formats are dynamically displayed as `N/A` for professional standard precision.
*   **Lossless Metadata & Artwork Editor:** Edit metadata tags (Artist, Album, Compilation, etc.) and manage album covers without re-encoding the audio stream.
*   **Advanced Loudness Statistics:** Analyze Integrated Loudness, True Peak, LRA, Crest Factor, RMS Power, and DC Offset using EBU R128 standards.
*   **Smart Diagnostics:** Translates cryptic FFmpeg console errors into clear, actionable advice, and proactively checks for folder write-permissions and Windows MAX_PATH limits.
*   **Batch Processing:** Add multiple files or entire folders to the queue and process them all in one go.
*   **Two Normalization Modes:**
    *   **Linear (2-Pass):** Professional mastering-grade normalization using FFmpeg's EBU R128 analysis workflow. This preserves dynamics while achieving accurate LUFS and True Peak targets.
    *   **Dynamic (1-Pass):** Faster one-pass normalization for podcasts, speech, streaming, and radio-style workflows.
*   **Mastering Character Selector:** Choose from `Transparent`, `Cohesive`, `Punchy`, and `Aggressive`, and read the matching help text directly below the selector.
*   **Multiple Dynamic Themes:** Switch on the fly between various flat-style dark and light themes, including *Läderlappen* (default dark), *Melcom*, *Midnight*, *Modernlight*, *Aquamarine & Blue* (classic tracker style), and classic *Light*.
*   **Quality Preservation:** Automatically keeps the original sample rate and bit depth for WAV and FLAC outputs, including high-resolution sources.
*   **Integrated Audio Player:** Preview tracks before processing with simple playlist controls, interactive click-to-seek timeline progress bar, and Windows-native playback pause (⏸) with zero CPU usage.
*   **Optional Treeview Columns:** Toggleable list columns (Duration, Format, Sample Rate) that scan and populate asynchronously in the background, keeping the main interface completely fluid.
*   **Common Platform Presets:** Includes presets for streaming, podcast, gaming/dynamic music, broadcast, and custom target values.
*   **Multiple Output Formats:** Save your files in WAV, MP3, FLAC, M4A, or OGG format, now featuring fully customizable Sample Rates (up to 192 kHz), linear/floating-point Bit Depths for lossless containers, and flexible Constant (CBR) or Variable (VBR) bitrate profiles for lossy targets.
*   **Interactive Real-Time Progress Spinner:** Features an integrated status-bar activity indicator (⏳ / ⌛) that animates dynamically during quiet background processes to prevent a "frozen" appearance during multi-track analysis.
*   **Automatic Cleanup:** Removes temporary `.temp` files when a process is cancelled or fails.
*   **Portable Application:** Runs without installation and does not modify the Windows registry.
*   **Multi-Language Support:** Available in English, German, Polish, and Swedish.

---

## 📸 Screenshots Gallery

*Click on any image to view it in full size (opens in a new tab to bypass GitHub loading errors).*

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/03-creations-ffmpeg-screenshot_2026-06-05_115929.png"><img src="images/03-creations-ffmpeg-screenshot_2026-06-05_115929.png?raw=true" width="32%" alt="General Tab"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/04-creations-ffmpeg-screenshot_2026-06-05_115938.png"><img src="images/04-creations-ffmpeg-screenshot_2026-06-05_115938.png?raw=true" width="32%" alt="Metadata Editor"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/05-creations-ffmpeg-screenshot_2026-06-05_115943.png"><img src="images/05-creations-ffmpeg-screenshot_2026-06-05_115943.png?raw=true" width="32%" alt="Artwork Manager"></a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/06-creations-ffmpeg-screenshot_2026-06-05_120000.png"><img src="images/06-creations-ffmpeg-screenshot_2026-06-05_120000.png?raw=true" width="32%" alt="Statistics"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/07-creations-ffmpeg-screenshot_2026-06-05_115750.png"><img src="images/07-creations-ffmpeg-screenshot_2026-06-05_115750.png?raw=true" width="32%" alt="Export Controls"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/08-creations-ffmpeg-screenshot_2026-06-05_115948.png"><img src="images/08-creations-ffmpeg-screenshot_2026-06-05_115948.png?raw=true" width="32%" alt="File Management"></a>
</p>

---

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
*   Pick the **Mastering Character** (`Transparent` is the default)
*   Choose the **Normalization Mode**
*   Select the desired **Output Format**
*   Click **"Start Normalization"**

The normalized files will be saved in the same directory as the source files with a `-Normalized` suffix.

---

## 🎛 Recommended Workflow

### For Music / Demoscene Releases

Recommended settings:

*   Mode: `Linear (2-Pass)`
*   Target Loudness: `-12 LUFS`
*   True Peak: `-1 dBTP`
*   Mastering Character: `Cohesive` or `Transparent`

This configuration preserves punch and dynamics while keeping the result coherent and polished.

### For More Aggressive Electronic Material

Recommended settings:

*   Mode: `Linear (2-Pass)`
*   Target Loudness: `-14 LUFS`
*   True Peak: `-1 dBTP`
*   Mastering Character: `Aggressive`

### For Streaming / Podcasts

Recommended settings:

*   Mode: `Dynamic (1-Pass)`
*   Target Loudness: `-14 LUFS` for general streaming or `-16 LUFS` / `-19 LUFS` for podcast workflows
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
*   `help_sv_SE.html`

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

Greetings from the shadows 🦇,<br>
melcom
