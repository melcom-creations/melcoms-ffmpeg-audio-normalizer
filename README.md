# melcom's FFmpeg Audio Normalizer

A professional yet easy-to-use Windows GUI for batch-normalizing audio files with FFmpeg's EBU R128 loudness workflow.

Version 4.0.3 ("Läderlappen Edition 🦇") reflects the current GUI and preset workflow, including the Mastering Character selector, dynamic flat-style themes, Swedish localization, modular architecture improvements, and enhanced multi-track normalization stability.

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-before-after.png"><img src="images/creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="800"></a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-start_2026-05-29_211653.png"><img src="images/creations-ffmpeg-start_2026-05-29_211653.png?raw=true" alt="Main application window of FFmpeg Audio Normalizer" width="800"></a>
</p>

## ✨ Features

*   **Batch Processing:** Add multiple files or entire folders to the queue and process them all in one go.
*   **Two Normalization Modes:**
    *   **Linear (2-Pass):** Professional mastering-grade normalization using FFmpeg's EBU R128 analysis workflow. This preserves dynamics while achieving accurate LUFS and True Peak targets.
    *   **Dynamic (1-Pass):** Faster one-pass normalization for podcasts, speech, streaming, and radio-style workflows.
*   **Mastering Character Selector:** Choose from `Transparent`, `Cohesive`, `Punchy`, and `Aggressive`, and read the matching help text directly below the selector.
*   **Multiple Dynamic Themes:** Switch on the fly between various flat-style dark and light themes, including *Läderlappen* (default dark), *Melcom*, *Midnight*, *Modernlight*, *Aquamarine & Blue* (Classic Tracker Style), and classic *Light*.
*   **Dynamic Preset Processing:** The selected preset defines the mastering filter chain, so the processing path stays clear and easy to extend.
*   **Modern Modular Architecture:** Refactored into dedicated modules for GUI, audio processing, themes, localization, configuration, and logging.
*   **Thread-Safe Logging Engine:** Dedicated rotating log system for improved stability during long batch jobs.
*   **Swedish Localization:** Full Swedish language support in addition to English, German, and Polish.
*   **Quality Preservation:** Automatically keeps the original sample rate and bit depth for WAV and FLAC outputs, including high-resolution sources.
*   **Metadata & Tags:** Preserves artist, title, album, and other tags and carries them into the normalized files.
*   **Integrated Audio Player:** Preview tracks before processing with simple playlist controls.
*   **Common Platform Presets:** Includes presets for streaming, podcast, gaming/dynamic music, broadcast, and custom target values.
*   **Multiple Output Formats:** Save your files in WAV, MP3, FLAC, AAC, or OGG format.
*   **Automatic Cleanup:** Removes temporary `.temp` files when a process is cancelled or fails.
*   **Portable Application:** Runs without installation and does not modify the Windows registry.
*   **Multi-Language Support:** Available in English, German, Polish, and Swedish.

---

## 📸 Screenshots Gallery

*Click on any image to view it in full size (opens in a new tab to bypass GitHub loading errors).*

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-lufs_2026-05-29_211451.png"><img src="images/creations-ffmpeg-lufs_2026-05-29_211451.png?raw=true" width="32%" alt="LUFS Preset Selection"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-tp_2026-05-29_211457.png"><img src="images/creations-ffmpeg-tp_2026-05-29_211457.png?raw=true" width="32%" alt="True Peak Preset Selection"></a>
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-mastering_2026-05-29_211501.png"><img src="images/creations-ffmpeg-mastering_2026-05-29_211501.png?raw=true" width="32%" alt="Mastering Character Selection"></a>
</p>

---
