# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [3.0.1] - 2025-11-03

### Fixed
- **Improved Application Path Handling for Robustness**
    - Fixed a critical issue where language files and other resources (e.g., options.ini, logs) would fail to load when the application was launched from the Windows Start Menu search.
    - The program now correctly determines its own location, ensuring that all necessary files are found regardless of how or from where it is started.
    - This enhances stability and provides a consistent user experience across all versions of Windows.

## [3.0.0] - 2025-10-24

### Added
- **Batch Processing**
    - Process Multiple Files: The tool is no longer limited to a single file. You can now add a list of audio files to be processed in sequence.
    - Add Entire Folders: A new "Add Folder" button allows you to recursively scan a directory and add all supported audio files.
    - Redesigned File Management: A modern file list now displays all files queued for processing.
- **Integrated Audio Player & Playlist**
    - Audio Preview for Batches: To help verify that the correct files are loaded, a mini-player has been integrated below the file list.
    - Full Playback Controls: Includes Play, Stop, Next («), and Previous (») buttons for easy navigation.
    - Playlist Functionality: The Next and Previous buttons allow you to cycle through the entire list of loaded files.
    - Real-Time Time Display: A live time display shows the current playback position and the total duration of the track.
    - Note: The time display requires `ffprobe.exe` to be in the same directory as `ffmpeg.exe`.
- **Output Format Information**
    - Dynamic Info Box: When selecting an output format, a descriptive panel appears, showing technical specifications (bitrate, sample rate) and a brief description of the format's intended use.
- **Modernized File List**
    - The simple file list has been upgraded to a modern Treeview, providing a cleaner look and a foundation for future features like displaying track metadata.
- **Live Input Validation**
    - The custom input fields for LUFS and True Peak now provide immediate visual feedback. Invalid entries (e.g., non-numeric values or values out of range) will instantly cause the field to be highlighted in red, preventing errors before a process is started.

### Changed
- **Completely Redesigned User Interface (UI)**
    - New Two-Column Layout: Files are now managed on the left, while all normalization and output settings are neatly grouped on the right.
    - Batch Progress Bar: A progress bar at the bottom of the window shows the overall progress of the batch job.
    - Live Status Bar: A status bar provides real-time information on the current file being processed or the total number of files loaded.
- **Improved Workflow: Overwrite Confirmation**
    - Pre-Process Check: The application now checks for existing output files *before* starting the normalization process.
    - Per-File Confirmation: You will be asked for each file whether you want to overwrite it, allowing you to skip specific files without interrupting the entire batch.
- **Complete Code Refactoring for Stability and Future Extensibility**
    - Modern Object-Oriented Structure: The entire codebase has been rewritten into classes for better organization and maintainability.
    - Improved Threading Model: A queue-based system now handles communication between the processing thread and the UI, preventing the application from freezing and ensuring stability.
    - Modular Code: Logic for configuration, FFmpeg processing, and the GUI are now separated, making future updates and new features much easier to implement.
- **Return to a Unified Retro Look & Feel**
    - Custom-Styled Windows: The "Options" and "About" windows have been rebuilt as custom windows to perfectly match the application's unique retro design, ensuring a consistent visual experience.
    - Automatic Window Centering: All windows (main, options, about) now automatically open in the center of the screen.
- **Consistent FFmpeg Parameters**
    - Output parameters have been aligned to ensure maximum, predictable output quality, consistent with the philosophy of previous versions.

### Fixed
- Fixed an issue where disabled dropdown menus (Comboboxes) would turn bright white during processing. They now blend seamlessly into the background as intended.
- Fixed an issue where closing the application via the "X" button would not terminate a running audio preview. All child processes are now properly closed.

## [2.2.2] - 2025-10-03

### Added
- **Audio Preview with Play/Stop Functionality**
    - Play & Stop Buttons Added: New "Play" and "Stop" buttons have been added to the file selection area.
    - Instant File Preview: Allows users to quickly listen to the selected audio file directly within the application before starting normalization or analysis.
    - Improved Workflow: Helps to verify that the correct file is loaded, saving time and preventing errors.

### Changed
- **Real-Time Process Information and Scrollbar**
    - Live FFmpeg Output: The "Process Information" window now streams the output from FFmpeg in real-time, providing detailed feedback as the process runs.
    - Enhanced User Feedback: Users can now see exactly what the tool is doing at every step, instead of waiting for a final summary.
    - Scrollbar Implemented: A vertical scrollbar has been added to the information window, allowing users to scroll through long logs.
- Updated "Check for Updates" Link: The URL for checking for updates in the "Info" menu has been updated to the new project website.
- GUI Layout Adjustments: The default window width has been slightly increased to better accommodate the new preview buttons.

## [2.2.1] - 2025-08-29

### Changed
- **Improved AAC Output Encoding:**
    - AAC encoding now utilizes a Constant Bit Rate (CBR) of 512k. Previously, AAC output had no explicit bitrate specified, relying on FFmpeg's defaults.
- **Improved OGG Vorbis Output Encoding:**
    - OGG Vorbis encoding now uses a target bitrate of 500k (managed mode). This replaces the previous quality-scale setting (`-qscale:a 10`), providing more explicit control over the output file size and quality.
- Updated Build Date: The application's build date has been updated to 2025-08-29.

## [2.2.0] - 2025-08-29

### Added
- **"Check for Updates" Menu Item**
    - "Updates" Menu Item Added: A "Check for Updates" entry has been added to the "Info" menu.
    - Easy Access to Update Information: Clicking this menu item opens the program's website in the default web browser.

### Changed
- **New Default LUFS Value: -14 LUFS**
    - The default target loudness for normalization has been changed from -10 LUFS to -14 LUFS.
    - Presets Updated: The "Default" preset in the LUFS preset selection now reflects the -14 LUFS target.
- **Improved GUI Styling for Options Dialog**
    - The Options dialog window now features the same visual style and color scheme as the main application window.

## [2.1.0]

### Added
- **Language Selection in Program**
    - Users can now select the program language (German, English, Polish) directly in the Options dialog.
    - The selected language is saved in the program settings.
- **Use of Temporary Files During Normalization**
    - The normalization process now creates temporary files for increased data security.
- **Cancel Normalization Process**
    - A "Cancel" button has been implemented in the GUI to terminate the FFmpeg process.

### Changed
- **Improved Input Validation and Error Handling for Custom LUFS/TP Values**
    - Comprehensive validation of user-defined target LUFS and True Peak values within FFmpeg-compliant ranges.
    - Clearer error messages to guide the user.
- **Limitation of Maximum Log File Size**
    - The maximum size for the log file has been limited to 10 MB.
- **Code Structure Improvements**
    - **Reduction of Global Variables:** Encapsulated configuration settings in a `Config` class.
    - **Centralization of GUI Update Logic:** Consolidated repeated code into a central helper function.
- **User Interface Improvements**
    - Unified `parent` parameters for all MessageBox calls for consistent modal dialogs.
    - Shortened label text for "Target Loudness Value".
    - Removed the "wait" mouse cursor.

### Fixed
- Incorrect error message "Unexpected Error!" on cancel has been fixed.

## [2.0.5]

### Fixed
- Bug Fixes and Stability Improvements.

## [2.0.1]

### Added
- **New Output Format Option: OGG Vorbis**
    - OGG Vorbis can now be selected as an output format.
- **New Option: "Single Log Entry per Process"**
    - A checkbox was added in Options to control log behavior, enabled by default.

### Changed
- **Default FFmpeg Path in Options Dialog**
    - Shows the program path on first start and loads any saved path on subsequent starts.

## [2.0.0]

### Added
- **Completely New Program Base & GUI (Python & Tkinter)**
- **Audio File Analysis**
    - Allows analysis of LUFS, True Peak, and LRA before normalizing.
- **Extended Normalization Options**
    - Adjustable True Peak target value and presets.
    - Output format selection (WAV, MP3, FLAC, AAC).
- **Extended Log File Functionality**
    - Separate `analysis.log` for analysis logs.
- **"About..." Menu Item**
- **Automatic FFmpeg Check on startup**
- **"Continuous Mode"** to keep the tool open after process completion.

### Changed
- **Improved User Interface & User Guidance**
    - Modern progress bar.
    - Detailed process information window.
    - Message boxes for results and completion.
- Version number is now displayed in the window title.
- Improved error handling with more detailed messages.

## [1.0.0 - 1.4.0]

*This section summarizes the development steps from the initial version to 1.4, which were integrated into Version 2.0.*

### Added
- **GUI Version** (v1.4)
- **Multilingual Support** (German/English) (v1.4)
- **Automatic FFmpeg Check** (v1.4)
- **Continuous Mode** (v1.4)
- **Logging Function** (Log File with timestamps and size limits) (v1.3)
- **Prompt to Overwrite Existing Output Files** (v1.2)
- **Progress Display During Normalization** (v1.1)
- **Initial Version (Batch File)** with basic normalization functionalities (v1.0)

### Changed
- **Restructuring of Log File** (newest entries at the top) (v1.4)
- **Improved User Interface** (clearer prompts/inputs) (v1.4)
- **Log File View After Process Completion** (v1.4)