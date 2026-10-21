# melcom's FFmpeg Audio Normalizer 4.1.2

## Herbstklang Edition

The Herbstklang Edition adds output verification, clearer processing results, an adjustable workspace, and a new autumn theme.

melcom's FFmpeg Audio Normalizer is a professional Windows application for batch audio normalization using FFmpeg's EBU R128 loudness workflow. It combines precise LUFS and True Peak targeting with format conversion, metadata editing, artwork management, audio analysis, and an integrated player.

> **☕ Optional support**
>
> melcom's FFmpeg Audio Normalizer is free and will remain free. If you'd like to support my work, you're welcome to [☕ buy me a coffee through PayPal](https://paypal.me/melcom2630). Support is entirely optional and always appreciated.

## What's New in Version 4.1.2

* **Output Verification and Results:** Optionally measure encoded files and compare original measurements, targets, and output in the Results window. Results explain the actual processing mode and can be copied with visible confirmation.
* **Encoder Headroom:** Reserve 0 to 3 dB before MP3, M4A, or OGG encoding while keeping your selected output targets.
* **Adjustable Workspace:** Resize the file list, settings, and process log with draggable dividers. Window size and layout are saved automatically and can be reset.
* **Clearer Encoding Defaults:** MP3 and M4A start at 320 kbps CBR; OGG uses a 320 kbps ABR target. VBR quality presets remain explicit choices.
* **More Audio Statistics:** View and copy Peak-to-Loudness Ratio (PLR) alongside the existing loudness and signal measurements.
* **Remembered Folders:** Audio files and album artwork each remember their last directory across application restarts.
* **Metadata and Artwork Repairs:** Improved MP3 URL compatibility and preservation of comments and custom tags when changing artwork, plus fixes for M4A cover handling.
* **herbstklang Theme:** Warm brown backgrounds, amber accents, and cream-colored text, selected by default when no theme has been saved.

<p align="center">
  <a href="https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/00-ffmpeg_audio_normalizer_im_herbstglanz.jpg">
    <img src="images/00-ffmpeg_audio_normalizer_im_herbstglanz.jpg?raw=true" alt="Herbstklang Edition cover for melcom's FFmpeg Audio Normalizer 4.1.2" width="600">
  </a>
</p>

| Normalization comparison | Main application window |
| --- | --- |
| [![Waveform before and after normalization](images/01-creations-ffmpeg-before-after.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/01-creations-ffmpeg-before-after.png) | [![Main application window with the herbstklang theme](images/02-screenshot_2026-10-21_193722.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/02-screenshot_2026-10-21_193722.png) |

## Core Features

* **Dynamic Live-Sync Inspector:** A completely redesigned, modeless Audio Properties window. It stays open and dynamically synchronizes to show the selected file's metadata, cover art, and real-time statistics as you navigate your queue.
* **Lossless Metadata & Artwork Editor:** Manage album covers and edit metadata tags (Artist, Album, Compilation, etc.) for MP3, FLAC, and M4A files *without* touching or re-encoding the original audio stream.
* **Two Normalization Modes:**
  * **Linear (2-Pass):** Requests linear gain based on a measurement pass. Results show whether FFmpeg used linear or dynamic processing for the selected targets.
  * **Dynamic (1-Pass):** Faster one-pass normalization for podcasts, speech, streaming, and radio-style workflows.
* **Advanced Loudness Statistics:** Analyze Integrated Loudness, True Peak, LRA, Crest Factor, RMS Level, and DC Offset. The Inspector also shows Peak-to-Loudness Ratio (PLR) in LU and includes it in copied statistics. PLR is derived from the existing true-peak and integrated-loudness measurements without another analysis pass; it complements the dynamics measurements and does not rate sound quality.
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

*Click on any image to view it in full size.*

| Audio Properties | Metadata Editor | Artwork Manager |
| --- | --- | --- |
| [![Audio Properties](images/03-screenshot_2026-10-21_193747.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/03-screenshot_2026-10-21_193747.png) | [![Metadata Editor](images/04-screenshot_2026-10-21_193805.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/04-screenshot_2026-10-21_193805.png) | [![Artwork Manager](images/05-screenshot_2026-10-21_193903.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/05-screenshot_2026-10-21_193903.png) |
| **Loudness & Signal Statistics** | **Export Controls** | **Normalization Results** |
| [![Loudness and signal statistics](images/06-screenshot_2026-10-21_193951.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/06-screenshot_2026-10-21_193951.png) | [![Output format selection](images/07-screenshot_2026-10-21_194016.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/07-screenshot_2026-10-21_194016.png) | [![Normalization results comparing original measurements, targets, and measured output](images/08-Screenshot%202026-10-21%20221814.png?raw=true)](https://raw.githubusercontent.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/main/images/08-Screenshot%202026-10-21%20221814.png) |

---

## Download & Installation

Official public release archives are available from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

No installation is required. Simply unzip the archive and run `AudioNormalizer.exe`.

The application is fully portable and does not modify the Windows registry.

### Update Notifications

The application can check GitHub Releases for a newer public version when it starts. Automatic checks can be enabled or disabled under **File - Options**. Pre-release updates can be included with a separate option and are excluded by default.

Automatic checks stay silent when the installed version is current or GitHub cannot be reached. A manual check under **Info - Check for Updates...** always displays the result. The application only provides a notification and a link to the matching GitHub release; it never downloads or installs updates automatically.

## Running from Source

On Windows, install 64-bit Python 3 with Tcl/Tk support. From the repository's main folder, install the Python dependencies and start the application:

```powershell
python -m pip install -r requirements.txt
python -B main.py
```

The FFmpeg executables are installed separately and configured under **File - Options**, as described below.

### Building the Windows Executable

Install the build dependencies and create the executable without UPX compression:

```powershell
python -m pip install -r requirements-build.txt
python -m PyInstaller --clean --noconfirm --onefile --windowed --noupx --name AudioNormalizer --icon favicon/melcom.ico main.py
```

The executable is created as `dist/AudioNormalizer.exe`. Copy the external resource folders and documentation next to it:

```powershell
Copy-Item -Path custom, favicon, help, images, lang, readme, themes -Destination dist -Recurse -Force
Copy-Item -Path README.md, CHANGELOG.md, LICENSE, melcoms_ffmpeg_audio_normalizer.diz -Destination dist -Force
```

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

## Processing and Workspace Details

Drag the horizontal divider above the process log to change its height. Drag the vertical divider between the files and settings to change their widths. Settings can be scrolled when there is less space. Processing controls remain visible below the work areas.

Window size, divider positions, and maximized state are saved automatically in the Layout section of options.ini and restored at the next start. File - Reset Window Layout restores the built-in layout. Layout is independent of audio profiles and is preserved when changing output format, language, or theme.

MP3 and M4A now default explicitly to 320 kbps CBR, independently of the source bitrate. MP3 uses LAME algorithm quality 0. VBR is enabled only by choosing a VBR quality preset; M4A offers q2 and q1. OGG/Vorbis defaults to 320 kbps ABR, which is an average-rate target, not strict CBR. Its VBR quality presets remain explicit alternatives. Older lossy profiles with Original / Default load the new format default; the old Vorbis option labeled 320 kbps (CBR) maps to 320 kbps (ABR). Profiles store the explicit quality selection. Format guidance below Specs explains encoder headroom; the text wraps with the panel. Results and clipboard export include the encoding selection.

"Encoder headroom (dB)" reserves 0 to 3 dB before MP3, M4A, or OGG encoding to allow for peaks introduced during lossy encoding. It lowers the internal true-peak limit by the specified value, down to FFmpeg's minimum of -9 dBTP. The selected loudness and final true-peak targets remain unchanged. A value of 0 disables the additional margin. The setting is available under Output Format and is stored in profiles. Older profiles default to 0. WAV and FLAC ignore this setting. Results and clipboard export show the requested and applied margin. Output verification measures the encoded file against the selected targets without changing it.

Enable "Verify output files" before starting normalization to measure the finished encoded files. This option is off by default and adds analysis time. File - Options saves the default; profiles can store the selection. Older profiles load with verification disabled.

After processing, open "Results..." to compare original, target, and measured output. Results belong to the most recent normalization batch and stay in memory until another normalization batch starts or the application closes. Copy the selected result for your records.

File creation and verification have separate outcomes. A failed or canceled verification does not discard a successfully created file. Loudness is checked within +/- 0.2 LU; true peak may exceed the selected limit by at most 0.1 dB for a passing check. LRA is displayed as information without a target test. These are application tolerances, not a certification.

Measures first and requests a fixed gain. FFmpeg can switch to dynamic processing if true-peak or loudness-range limits prevent linear processing. The mastering preset processes the audio before normalization and can change dynamics even when FFmpeg reports Linear. When analysis cannot establish loudness, the two-pass loudness adjustment is skipped and verification cannot pass. Silence and very short files are examples.

Pass counts refer to normalization. Output verification adds a measurement of the encoded file; mastering may also require a separate original-file measurement.

Valid targets are -70 to -5 LUFS and -9 to 0 dBTP. Original / Default preserves supported WAV bit depths, including 64-bit float. Standard lossy encoder settings are used when the source bitrate is incompatible with the output codec. Conflicting output paths are rejected before processing.

## Recommended Workflow

### For Music / Demoscene Releases

Recommended settings:

* Mode: `Linear (2-Pass)`
* Target Loudness: `-12 LUFS`
* True Peak: `-1 dBTP`
* Mastering Character: `Cohesive` or `Transparent`

This configuration requests linear normalization. Cohesive adds compression and soft peak shaping before normalization; Transparent adds no mastering filters. FFmpeg may use dynamic normalization if linear gain is not possible.

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

* [de_DE](help/help_de_de.html)
* [en_US](help/help_en_us.html)
* [pl_PL](help/help_pl_pl.html)
* [sv_SE](help/help_sv_se.html)

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

Best regards,

melcom
