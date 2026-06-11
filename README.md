# melcom's FFmpeg Audio Normalizer

Welcome to the **Kontrollraum Edition** – where raw audio signals meet absolute **Kontrolle**. If you are tired of wrestling with clunky command-line arguments, cryptic parameters, or clipping nightmares, you have just entered your new audio command center.

melcom's FFmpeg Audio Normalizer is a professional, high-fidelity Windows GUI designed to give you complete control over batch audio normalization workflows using FFmpeg's industry-standard EBU R128 loudness algorithm. 

With Version 4.1.0, the project has evolved from a simple batch processor into a comprehensive audio workstation. If you're from the demoscene, you know how it is: no half-measures.

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/melcoms_ffmpeg_audio_normalizer_-_image_8._juni_2026,_07_56_24-2560x2560.jpg"><img src="images/melcoms_ffmpeg_audio_normalizer_-_image_8._juni_2026,_07_56_24-2560x2560.jpg?raw=true" alt="melcom's FFmpeg Audio Normalizer Cover" width="600"></a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/01-creations-ffmpeg-before-after.png"><img src="images/01-creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="49%"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/02-creations-ffmpeg-screenshot_2026-06-08_130528.png"><img src="images/02-creations-ffmpeg-screenshot_2026-06-08_130528.png?raw=true" alt="Main application window of FFmpeg Audio Normalizer" width="49%"></a>
</p>

## ✨ Core Features

*   **Dynamic Live-Sync Inspector:** A completely redesigned, modeless Audio Properties window. It stays open and dynamically synchronizes to show the selected file's metadata, cover art, and real-time statistics as you navigate your queue.
*   **Lossless Metadata & Artwork Editor:** Manage album covers and edit metadata tags (Artist, Album, Compilation, etc.) for MP3, FLAC, and M4A files *without* touching or re-encoding the original audio stream.
*   **Two Normalization Modes:**
    *   **Linear (2-Pass):** Professional mastering-grade normalization using FFmpeg's EBU R128 analysis workflow. Preserves dynamics while hitting exact LUFS and True Peak targets.
    *   **Dynamic (1-Pass):** Faster one-pass normalization for podcasts, speech, streaming, and radio-style workflows.
*   **Advanced Loudness Statistics:** Analyze Integrated Loudness, True Peak, LRA, Crest Factor, RMS Power, and DC Offset using strict EBU R128 standards.
*   **Nerd-Level Output Precision:** Total control over your exports. Select custom Sample Rates (up to 192kHz), floating-point bit depths for lossless containers, and exact CBR/VBR profiles for lossy targets.
*   **Drag & Drop Workflow:** Drag single files, multiple selected tracks, or entire nested folders directly from Windows Explorer into the processing queue. Complete with automatic duplicate protection.
*   **Modder-Friendly JSON Theming Engine:** Fully externalized UI styling. Drop a custom `.json` color palette into the `/themes/` folder, and the app dynamically loads it—even calculating the background's perceived luminance to automatically adjust text contrast.
*   **FFmpeg Diagnostic Engine:** Cryptic FFmpeg console errors are intercepted and translated into human-readable advice. The app proactively checks for Windows MAX_PATH limits, missing encoders, and folder write permissions before FFmpeg even starts.
*   **Integrated Audio Player & Equalizer:** Preview tracks natively before processing. Features an interactive click-to-seek timeline, a pulsing graphic equalizer, and Windows-native playback pausing (⏸) with zero CPU usage.
*   **Mastering Character Selector:** Choose from `Transparent`, `Cohesive`, `Punchy`, and `Aggressive` presets to give your material the exact processing color it needs.
*   **Quality Preservation by Default:** Automatically retains the original sample rate and bit depth for WAV and FLAC outputs. Your high-res source files are respected.
*   **Portable & Clean:** Runs entirely without installation, does not modify your Windows registry, and features automatic cleanup of temporary files.
*   **Multi-Language Support:** Fully localized in English, German, Polish, and Swedish via a dynamic language pack system.

---

## 📸 Screenshots Gallery

*Click on any image to view it in full size (opens in a new tab).*

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/03-creations-ffmpeg-screenshot_2026-06-08_130633.png"><img src="images/03-creations-ffmpeg-screenshot_2026-06-08_130633.png?raw=true" width="32%" alt="General Tab"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/04-creations-ffmpeg-screenshot_2026-06-08_130759.png"><img src="images/04-creations-ffmpeg-screenshot_2026-06-08_130759.png?raw=true" width="32%" alt="Metadata Editor"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/05-creations-ffmpeg-screenshot_2026-06-08_130830.png"><img src="images/05-creations-ffmpeg-screenshot_2026-06-08_130830.png?raw=true" width="32%" alt="Artwork Manager"></a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/06-creations-ffmpeg-screenshot_2026-06-08_130903.png"><img src="images/06-creations-ffmpeg-screenshot_2026-06-08_130903.png?raw=true" width="32%" alt="Statistics"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/07-creations-ffmpeg-screenshot_2026-06-08_130935.png"><img src="images/07-creations-ffmpeg-screenshot_2026-06-08_130935.png?raw=true" width="32%" alt="Export Controls"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/08-creations-ffmpeg-screenshot_2026-06-08_131001.png"><img src="images/08-creations-ffmpeg-screenshot_2026-06-08_131001.png?raw=true" width="32%" alt="File Management"></a>
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

*   Use **"Add Files"**, **"Add Folder"**, or simply **Drag & Drop** your tracks into the queue.
*   Select your desired **LUFS** and **True Peak** presets.
*   Pick the **Mastering Character** (`Transparent` is the default).
*   Choose the **Normalization Mode**.
*   Select the desired **Output Format**.
*   Click **"Start Normalization"**.

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

This project is developed and maintained by a single person.

Please note that I live with a chronic illness that can sometimes significantly limit my available time, energy, and ability to work on the project. Because of this, there may be periods where I am unable to respond quickly to bug reports, feature requests, or support inquiries.

To keep the project manageable during such times, GitHub Issues are intentionally not used as the primary support channel.

If you encounter a bug, have a feature request, or would simply like to get in touch, you are very welcome to send me a message through my contact page:

http://melcom-creations.github.io/melcom-music/contact.html

Thank you for your understanding, patience, and support.

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

Greetings from the Kontrollraum 🖥️,<br>
melcom