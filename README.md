# melcom's FFmpeg Audio Normalizer

A professional yet easy-to-use Windows GUI for batch-normalizing audio files with FFmpeg's EBU R128 loudness workflow.

Version 4.0.3 ("Läderlappen Edition 🦇") reflects the current GUI and preset workflow, including the Mastering Character selector, dynamic flat-style themes, batch-processing improvements, and the latest multi-track normalization fixes.

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-before-after.png"><img src="images/creations-ffmpeg-before-after.png?raw=true" alt="Waveform before and after normalization" width="800"></a>
</p>

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/creations-ffmpeg-start_2026-05-30_015717.png"><img src="images/creations-ffmpeg-start_2026-05-30_015717.png?raw=true" alt="Main application window of FFmpeg Audio Normalizer" width="800"></a>
</p>

## ✨ Features

* **Batch Processing** - Add multiple files or complete folders and process them sequentially.
* **Two Normalization Modes**
  * **Linear (2-Pass)** - High-precision EBU R128 normalization that preserves dynamics.
  * **Dynamic (1-Pass)** - Fast normalization for podcasts, speech, streaming, and radio-style workflows.
* **Mastering Character Selector** - Choose between `Transparent`, `Cohesive`, `Punchy`, and `Aggressive`.
* **Modern Flat UI & Dynamic Themes** - Includes Läderlappen, Midnight, Melcom, Modernlight, Aquamarine & Blue, and Light.
* **Multi-Language Support** - English, German, Polish, and Swedish.
* **Integrated Audio Player** - Preview tracks before processing.
* **Quality Preservation** - Preserves original sample rate and bit depth for WAV and FLAC.
* **Metadata Preservation** - Retains artist, album, title, and other metadata.
* **Multiple Output Formats** - WAV, MP3, FLAC, AAC, and OGG Vorbis.
* **Thread-Safe Logging Engine** - Rotating log files for improved stability during long batch jobs.
* **Safe Process Cancellation** - Proper FFmpeg process tree termination on Windows.
* **Improved Multi-Track Processing** - Stable progress handling during batch normalization.
* **Portable Application** - No installation and no registry modifications required.

## 📥 Download & Installation

Download the latest version from the GitHub Releases page and extract the archive.

Run:

`AudioNormalizer.exe`

No installation is required.

## 🚀 How to Use

1. Download the FFmpeg suite.
2. Open `File -> Options`.
3. Select the folder containing:
   - `ffmpeg.exe`
   - `ffplay.exe`
   - `ffprobe.exe`
4. Add files or folders.
5. Select LUFS, True Peak, Mastering Character, Normalization Mode, and Output Format.
6. Click **Start Normalization**.

Normalized files are saved next to the source files using the suffix:

`-Normalized`

## 🎛 Recommended Workflow

### Music

* Mode: `Linear (2-Pass)`
* Target: `-12 LUFS`
* True Peak: `-1 dBTP`
* Character: `Transparent` or `Cohesive`

### Electronic Music

* Mode: `Linear (2-Pass)`
* Target: `-14 LUFS`
* True Peak: `-1 dBTP`
* Character: `Aggressive`

### Streaming & Podcasts

* Mode: `Dynamic (1-Pass)`
* Target: `-14 LUFS`, `-16 LUFS`, or `-19 LUFS`
* True Peak: `-1 dBTP`

## 💬 Support & Feedback

GitHub Issues are intentionally disabled.

Contact:

http://melcom-creations.github.io/melcom-music/contact.html

## 📖 Detailed Help

Included help files:

* `help_de_DE.html`
* `help_en_US.html`
* `help_pl_PL.html`
* `help_sv_SE.html`

## 📜 Changelog

See:

`CHANGELOG.md`

## ⚖ License

Released under the MIT License.

See:

`LICENSE.txt`

---

Greetings from the shadows 🦇,<br>
melcom
