# melcom's FFmpeg Audio Normalizer 4.1.1

## Flickwerk Edition

Version 4.1.1 focuses on careful repairs, safer behavior, clearer settings, and the details that make daily use feel more reliable.

melcom's FFmpeg Audio Normalizer is a professional Windows application for batch audio normalization using FFmpeg's EBU R128 loudness workflow. It combines precise LUFS and True Peak targeting with format conversion, metadata editing, artwork management, audio analysis, and an integrated player.

## What's New in Version 4.1.1

* **GitHub Release Update Notifications:** Check for newer public releases directly from the application. Automatic checks are optional, remain silent when no update is available, and can include pre-releases when enabled.
* **Modernized Options Dialog:** A clearer layout groups appearance, FFmpeg, logging, and update settings while keeping all four supported languages in sync.
* **Safer Configuration Handling:** Invalid, incomplete, or unwritable configuration files no longer cause avoidable startup or save crashes.
* **Metadata and Stream Preservation:** Improved FFmpeg stream mapping and metadata handling protect album artwork and global metadata during normalization and artwork changes.
* **Localization Review:** English, German, Polish, and Swedish texts were reviewed for natural wording and consistent audio terminology.
* **Interface and Theme Refinements:** Dialog icons, light-theme surfaces, and selected theme colors were adjusted for a more consistent appearance.

[![melcom's FFmpeg Audio Normalizer Cover](images/melcoms_ffmpeg_audio_normalizer_-_image_14._juli_2026,_08_52_09-2560x2560.jpg?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/melcoms_ffmpeg_audio_normalizer_-_image_14._juli_2026,_08_52_09-2560x2560.jpg)

| Normalization comparison | Main application window |
| --- | --- |
| [![Waveform before and after normalization](images/01-creations-ffmpeg-before-after.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/01-creations-ffmpeg-before-after.png) | [![Main application window of FFmpeg Audio Normalizer](images/02-creations-ffmpeg-screenshot_2026-07-14_080543.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/02-creations-ffmpeg-screenshot_2026-07-14_080543.png) |

## Core Features

* **Dynamic Live-Sync Inspector:** A completely redesigned, modeless Audio Properties window. It stays open and dynamically synchronizes to show the selected file's metadata, cover art, and real-time statistics as you navigate your queue.
* **Lossless Metadata & Artwork Editor:** Manage album covers and edit metadata tags (Artist, Album, Compilation, etc.) for MP3, FLAC, and M4A files *without* touching or re-encoding the original audio stream.
* **Two Normalization Modes:**
  * **Linear (2-Pass):** Professional mastering-grade normalization using FFmpeg's EBU R128 analysis workflow. Preserves dynamics while hitting exact LUFS and True Peak targets.
  * **Dynamic (1-Pass):** Faster one-pass normalization for podcasts, speech, streaming, and radio-style workflows.
* **Advanced Loudness Statistics:** Analyze Integrated Loudness, True Peak, LRA, Crest Factor, RMS Level, and DC Offset using strict EBU R128 standards.
* **Nerd-Level Output Precision:** Total control over your exports. Select custom Sample Rates (up to 192kHz), floating-point bit depths for lossless containers, and exact CBR/VBR profiles for lossy targets.
* **Drag & Drop Workflow:** Drag single files, multiple selected tracks, or entire nested folders directly from Windows Explorer into the processing queue. Complete with automatic duplicate protection.
* **Modder-Friendly JSON Theming Engine:** Fully externalized UI styling. Drop a custom `.json` color palette into the `/themes/` folder, and the app dynamically loads it - even calculating the background's perceived luminance to automatically adjust text contrast.
* **Modern Options Dialog:** Configure appearance, FFmpeg, logging, and update behavior in a clean, localized settings window.
* **Update Notifications:** Check GitHub Releases manually or enable a silent startup check, with optional pre-release support.
* **FFmpeg Diagnostic Engine:** Cryptic FFmpeg console errors are intercepted and translated into human-readable advice. The app proactively checks for Windows MAX_PATH limits, missing encoders, and folder write permissions before FFmpeg even starts.
* **Integrated Audio Player & Equalizer:** Preview tracks natively before processing. Features an interactive click-to-seek timeline, a pulsing graphic equalizer, and Windows-native playback pausing with zero CPU usage.
* **Mastering Character Selector:** Choose from `Transparent`, `Cohesive`, `Punchy`, and `Aggressive` presets to give your material the exact processing color it needs.
* **Quality Preservation by Default:** Automatically retains the original sample rate and bit depth for WAV and FLAC outputs. Your high-res source files are respected.
* **Portable & Clean:** Runs entirely without installation, does not modify your Windows registry, and features automatic cleanup of temporary files.
* **Multi-Language Support:** Fully localized in English, German, Polish, and Swedish via a dynamic language pack system.

---

## Screenshots Gallery

*Click on any image to view it in full size (opens in a new tab).*

| Audio Properties | Metadata Editor | Artwork Manager |
| --- | --- | --- |
| [![Audio Properties](images/03-creations-ffmpeg-screenshot_2026-07-14_080600.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/03-creations-ffmpeg-screenshot_2026-07-14_080600.png) | [![Metadata Editor](images/04-creations-ffmpeg-screenshot_2026-07-14_080648.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/04-creations-ffmpeg-screenshot_2026-07-14_080648.png) | [![Artwork Manager](images/05-creations-ffmpeg-screenshot_2026-07-14_080657.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/05-creations-ffmpeg-screenshot_2026-07-14_080657.png) |
| **Audio Properties** | **Export Controls** | **Audio Properties** |
| [![Audio Properties](images/06-creations-ffmpeg-screenshot_2026-07-14_080711.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/06-creations-ffmpeg-screenshot_2026-07-14_080711.png) | [![Export Controls](images/07-creations-ffmpeg-screenshot_2026-07-14_081701.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/07-creations-ffmpeg-screenshot_2026-07-14_081701.png) | [![Audio Properties](images/08-creations-ffmpeg-screenshot_2026-07-14_084122.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/08-creations-ffmpeg-screenshot_2026-07-14_084122.png) |

---

## Download & Installation

You can download Version 4.1.1 and future public releases from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

No installation is required. Simply unzip the archive and run `AudioNormalizer.exe`.

The application is fully portable and does not modify the Windows registry.

### Update Notifications

The application can check GitHub Releases for a newer public version when it starts. Automatic checks can be enabled or disabled under **File - Options**. Pre-release updates can be included with a separate option and are excluded by default.

Automatic checks stay silent when the installed version is current or GitHub cannot be reached. A manual check under **Info - Check for Updates...** always displays the result. The application only provides a notification and a link to the matching GitHub release; it never downloads or installs updates automatically.

## How to Use

### 1. Prerequisite: Get the FFmpeg Suite

This program requires the complete FFmpeg suite to function:

* `ffmpeg.exe` - normalization, mastering, and analysis
* `ffplay.exe` - integrated audio player
* `ffprobe.exe` - duration, bitrate, and audio quality detection

Download the latest FFmpeg package from:

**[BtbN's FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)**

For Windows, look for a `.zip` file named similar to:

`ffmpeg-master-latest-win64-gpl.zip`

The required `.exe` files are located inside the `bin` subfolder.

### 2. Configure the Program

* Start `AudioNormalizer.exe`
* Open `File -> Options`
* Under "FFmpeg Path", select the folder containing the FFmpeg executables

### 3. Process Your Files

* Use **"Add Files"**, **"Add Folder"**, or simply **Drag & Drop** your tracks into the queue.
* Select your desired **LUFS** and **True Peak** presets.
* Pick the **Mastering Character** (`Transparent` is the default).
* Choose the **Normalization Mode**.
* Select the desired **Output Format**.
* Click **"Start Normalization"**.

The normalized files will be saved in the same directory as the source files with a `-Normalized` suffix.

---

## Recommended Workflow

### For Music / Demoscene Releases

Recommended settings:

* Mode: `Linear (2-Pass)`
* Target Loudness: `-12 LUFS`
* True Peak: `-1 dBTP`
* Mastering Character: `Cohesive` or `Transparent`

This configuration preserves punch and dynamics while keeping the result coherent and polished.

### For More Aggressive Electronic Material

Recommended settings:

* Mode: `Linear (2-Pass)`
* Target Loudness: `-14 LUFS`
* True Peak: `-1 dBTP`
* Mastering Character: `Aggressive`

### For Streaming / Podcasts

Recommended settings:

* Mode: `Dynamic (1-Pass)`
* Target Loudness: `-14 LUFS` for general streaming or `-16 LUFS` / `-19 LUFS` for podcast workflows
* True Peak: `-1 dBTP`

---

## Support & Feedback

This project is developed and maintained by a single person.

Please note that I live with a chronic illness that can sometimes significantly limit my available time, energy, and ability to work on the project. Because of this, there may be periods where I am unable to respond quickly to bug reports, feature requests, or support inquiries.

To keep the project manageable during such times, GitHub Issues are intentionally not used as the primary support channel.

If you encounter a bug, have a feature request, or would simply like to get in touch, you are very welcome to send me a message through my contact page:

[melcom creations contact page](http://melcom-creations.github.io/melcom-music/contact.html)

Thank you for your understanding, patience, and support.

---

## Detailed Help

For more detailed information, please refer to the included help files:

* `help_de_DE.html`
* `help_en_US.html`
* `help_pl_PL.html`
* `help_sv_SE.html`

---

## Changelog

For a detailed history of all changes, please see:

[CHANGELOG.md](CHANGELOG.md)

---

## License

This software is open-source and released under the MIT License.

See:

[LICENSE](LICENSE)

for details.

---

Greetings from the Flickwerkstatt,

melcom
