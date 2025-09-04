# melcom's FFmpeg Audio Normalizer

A user-friendly GUI tool to easily normalize the loudness of your audio files using FFmpeg. The normalized file is automatically saved in the same folder as the original file.

<!-- Hier könntest du später einen Screenshot deines Programms einfügen! -->
<!-- ![Screenshot of Audio Normalizer](...) -->

## Features

*   **Loudness Normalization:** Normalize audio to target loudness (LUFS) and True Peak (dBTP).
*   **Platform Presets:** Includes presets for popular platforms like YouTube, Spotify, Apple Music, and more.
*   **Audio Analysis:** Analyze audio files to check their current loudness levels before processing.
*   **Multiple Output Formats:** Save your normalized files in WAV, MP3, FLAC, AAC, or OGG format.
*   **Multi-Language Support:** The user interface is available in English, German, and Polish.

## Download & Installation

You can download the latest version, which includes the `.exe` and all necessary files, from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

## How to Use

#### 1. Prerequisite: Get FFmpeg
This program requires **`ffmpeg.exe`** to function.
*   Download the latest FFmpeg package from a trusted source, for example: **[BtbN's FFmpeg Builds](https://github.com/BtbN/FFmpeg-Builds/releases/tag/latest)**.
*   For Windows, look for the `.zip` file in the assets list, typically named something like `ffmpeg-master-latest-win64-gpl.zip`.
*   Unzip the package. The `ffmpeg.exe` file you need is located inside the `bin` subfolder.

#### 2. Configure the Program
*   Start `AudioNormalizer.exe`.
*   Go to the menu `File` -> `Options`.
*   Under "FFmpeg Path", click the browse button and select the folder where your `ffmpeg.exe` is located (the `bin` folder from the previous step). This only needs to be done once.

#### 3. Normalize an Audio File
*   In the main window, click `Browse` and select the audio file you want to process.
*   Choose a `LUFS Preset` or enter a custom value.
*   Select your desired `Output Format`.
*   Click `Start Normalization`.

## Detailed Help

For more detailed information, please refer to the help files included in the download package. Open `help_de_DE.html` (German), `help_en_US.html` (English), or `help_pl_PL.html` (Polish) in your web browser.

## License

This software is open-source and released under the MIT License. See the [LICENSE](LICENSE) file for details.

---

Sincerely,
melcom
