melcom's FFmpeg Audio Normalizer v4.1.0

Open-source audio normalization using FFmpeg with LUFS and True Peak support.

With this application, you can easily normalize the loudness of your audio files - individually or in batches - using FFmpeg. The processed files are automatically saved in the same folder as the original files.


========================================
QUICK START
========================================

1. Install the FFmpeg Suite

This application requires the following free command-line tools:

- ffmpeg.exe
- ffplay.exe
- ffprobe.exe

Recommended download source:
https://github.com/BtbN/FFmpeg-Builds/releases

For Windows users, the "essentials" or "full" builds are recommended.
Look for a file similar to:

ffmpeg-master-latest-win64-gpl.zip

Extract the archive to any location on your computer.


2. Start the Program and Configure the FFmpeg Path

- Launch AudioNormalizer.exe
- Open: File -> Options
- Select the folder containing ffmpeg.exe, ffplay.exe, and ffprobe.exe

Important:
The application will not function correctly without a valid FFmpeg path.


3. Normalize Your Audio Files

- Use "Add Files" or "Add Folder"
- Choose your preferred LUFS preset
- Select the desired output format
- Click "Start Normalization"

The batch processing progress is displayed live.
Normalized files are created automatically.


4. Audio Preview

- Select a file from the list
- Press the "▶" button

Use the "«" and "»" buttons to navigate through your playlist.


5. Options and Settings

Under:
File -> Options

you can:

- change the FFmpeg path
- switch the program language
- switch the App theme
- configure log file settings


========================================
MASTERING CHARACTER PRESETS
========================================

Transparent
Applies loudness normalization only without additional sound shaping.

Cohesive
Adds gentle broadband compression with a subtle softclip contour for a smoother overall mix.

Punchy
Increases presence and impact through stronger compression.

Aggressive
The strongest option for dense and edgy material.


========================================
IMPORTANT NOTES
========================================

FFmpeg Path
Make sure the path to ffmpeg.exe, ffplay.exe, and ffprobe.exe is configured correctly.

ffprobe.exe
This file is used for the time display in the audio player.
Playback will still work without it, but without duration information.

LUFS Presets
The presets help you choose suitable loudness targets for different platforms.
Custom values can also be entered manually.

Output Format
The info box below the format selection displays technical details about the currently selected output format.


========================================
LICENSE
========================================

This software is Open-Source and released under the MIT License.
See:

LICENSE.txt

for additional details.


Enjoy melcom's FFmpeg Audio Normalizer!

Sincerely
melcom
