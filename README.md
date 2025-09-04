# melcom's FFmpeg Audio Normalizer

A user-friendly GUI tool to easily normalize the loudness of your audio files using FFmpeg. The normalized file is automatically saved in the same folder as the original file.

![Screenshot of the main interface](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/blob/main/images/Screenshot%202025-01-22%20175408_.png?raw=true)
![Screenshot of the options dialog](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/blob/main/images/Screenshot%202025-02-28%20074549.png?raw=true)

## Features

*   **Loudness Normalization:** Normalize audio to target loudness (LUFS) and True Peak (dBTP).
*   **Platform Presets:** Includes presets for popular platforms like YouTube, Spotify, Apple Music, and more.
*   **Audio Analysis:** Analyze audio files to check their current loudness levels before processing.
*   **Multiple Output Formats:** Save your normalized files in WAV, MP3, FLAC, AAC, or OGG format.
*   **Multi-Language Support:** The user interface is available in English, German, and Polish.

## Download & Installation

You can download the latest version, which includes the `.exe` and all necessary files, from the **[Releases Page](https://github.com/melcom-creations/melcoms-ffmpeg-audio-normalizer/releases/latest)**.

## How to Use

For a visual guide, check out the official video tutorial on how to install and use the program:

[![How to Install & Use Video Tutorial](https://img.youtube.com/vi/8nzvCOJsASw/hqdefault.jpg)](https://youtu.be/8nzvCOJsASw)

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
*   Adjust the **LUFS** and **True Peak** presets as needed. The default settings are a great starting point for general use.
*   Select your desired `Output Format`.
*   Click `Start Normalization`.

## Support & Feedback

Please note that the GitHub "Issues" feature has been disabled for this project. As a solo developer, I can provide the best support via direct email.

If you find a bug, have a feature request, or need help, please send a constructive email to:
**[melcom@gmx.net](mailto:melcom@gmx.net)**

## Detailed Help

For more detailed information, please refer to the help files included in the download package. Open `help_de_DE.html` (German), `help_en_US.html` (English), or `help_pl_PL.html` (Polish) in your web browser.

## License

This software is open-source and released under the MIT License. See the [LICENSE.txt](License.txt) file for details.

---

Sincerely,
melcom
