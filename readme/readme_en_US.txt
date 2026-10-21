melcom's FFmpeg Audio Normalizer v4.1.2 - Herbstklang Edition

Output Verification and Results
-------------------------------

PLR (Peak-to-Loudness Ratio)
PLR is the difference between the maximum true peak and integrated loudness of the same file. It is shown in LU and complements LRA and crest factor. It is derived from the existing analysis without another measurement pass. Missing or nonfinite measurements are shown as N/A; PLR alone does not rate sound quality.

Window Layout
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
- Press the "Play" button

Use the "Previous" and "Next" buttons to navigate through your playlist.


5. Options and Settings

Under:
File -> Options

you can:

- change the FFmpeg path
- switch the program language
- switch the App theme
- configure log file settings
- enable or disable automatic update checks
- optionally include pre-release updates

The update checker only displays a notification and a link to the matching GitHub release. It never downloads or installs updates automatically. A manual check is available under Info -> Check for Updates.


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

LICENSE

for additional details.


Enjoy melcom's FFmpeg Audio Normalizer!

Sincerely
melcom
