# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.1.0] - 2026-06-11 
### Kontrollraum Edition 🖥

### Added
- **Totally Professional Graphic Equalizer™**: Added a highly sophisticated equalizer to the player. It doesn't analyze anything, doesn't modify anything, and has absolutely no influence on the audio. But it looks cool and can be clicked. Sometimes that's enough. 🙈
- **Full Modular Codebase Overhaul**: Refactored the monolithic GUI script by extracting specialized subsystems into decoupled modules:
  - `player.py`: Isolates the entire background audio engine (FFplay subprocess, thread handling, and process suspension).
  - `dialogs.py`: Separates the standalone popup sub-windows (`AboutDialog`, `OptionsDialog`).
  - `utils.py`: Houses globally shared formatting and window centering utilities.
- **Dynamic Live-Sync Inspector**: Redesigned `AudioInspectorDialog` to be modeless (non-modal) by removing `grab_set()`. The Properties window now remains open and dynamically synchronizes to show the newly selected file's metadata, cover art, and real-time statistics in the background on selection changes.
- **Flexible Queue Operations During Playback**: Unlocked the queue controls (**Add Files**, **Add Folder**, **Remove Selected**) to remain fully active during playback. Implemented intelligent playback stopping and index recalibration if the currently playing track or preceding files are removed from the list.
- **Windows Explorer Context Menu Integration**: Added native context menu options to instantly **Open file location** (launching Windows Explorer and automatically highlighting the selected track) and show the native Windows **Properties** sheet using ShellExecuteExW (`SEE_MASK_INVOKEIDLIST`).
- **Ergonomic Context Menu Layout**: Redesigned and prioritized the treeview right-click menu structure to prioritize user attention, separating actions cleanly with logical separators.
- **Process Log Context Menu**: Integrated a responsive right-click context menu (Copy / Select All) into the Process Log, fully paired with standard system hotkeys.
- **F1 Menu Shortcut Labeling**: Aligned main help menu item label with standard Windows shortcuts (e.g., `Help (F1)`).
- **High-Precision Export Format Customization**: Added full support for selecting custom output **Sample Rates** (Original up to 192000 Hz) and **Bit Depths / Bitrates** (floating-point formats for WAV, bit depths for FLAC, CBR and VBR profiles for MP3, and specific bitrates for M4A/OGG) next to the main output format selector.
- **Real-Time Dynamic Spec Reconstruction**: Configured the Specs info label to rebuild itself in real-time on every format, sample rate, or quality change, displaying the exact selected parameters dynamically.
- **Dynamic Subprocess Quality Query**: Built a lookup system in the encoder stage to automatically parse the input file's nominal bitrate when "Original / Default" is selected for lossy formats (MP3, M4A, OGG), applying the exact matching bitrate to the output stream.
- **Nominal Bitrate Display**: Enhanced the FFMpegProcessor and the Audio Properties General tab to fetch, map, and display the nominal file bitrate (e.g., `128 kbps` or `320 kbps`) and include it in clipboard copies.
- **Academically Precise Lossy Bit Depths**: Configured the Inspector to display `N/A` for the resolution/bit depth of lossy files (MP3, OGG, M4A, AAC) instead of the misleading internal decoding planar float format (`32 bits (Float)`).
- **Visual Progress Activity Spinner**: Integrated a toggling hourglass animation (`⏳` / `⌛`) in the bottom status bar that pulses dynamically during background tasks (analysis and normalization passes) to give instant visual feedback during quiet processing phases.
- **Proactive FFmpeg Path Validation**: Implemented strict path checks on queue additions (via files, folders, or drag & drop) to proactively block file loading and prevent "N/A" metadata treeview states if FFmpeg is missing.
- **Help Menu Integration & F1 Shortcut**: Implemented a global `F1` shortcut and a dedicated "Help" menu entry under Info to automatically locate and launch the appropriate localized HTML help file from the `/help/` or root directory.
- **Fully Translated Subprocess Warnings**: Integrated missing translation keys for FFplay and FFprobe missing-executable popups, cleanly resolving raw bracket string indicators with localized user instructions.
- **Interactive Player Progress Bar & Seek**: Configured the player progress bar to support interactive mouse-click seek operations. Clicking calculates the target second and restarts the playback stream from that timestamp using FFplay's `-ss` argument.
- **System-Native Playback Pause**: Added a thread-safe playback pause/resume control next to the transport buttons, utilizing Windows ntdll `NtSuspendProcess` and `NtResumeProcess` via `ctypes` to pause the active FFplay subprocess with zero CPU usage.
- **Instant Time Update Parsing**: Overhauled stderr parsing in the playback background worker to read char-by-char, instantly resolving `\r` carriage returns from FFplay to eliminate the buffering delay and provide instant timeline tracking from second 0.
- **Multi-Thread Playback Guard**: Introduced a playback generation identifier (`playback_id`) to cleanly track and separate active subprocess threads, preventing delayed exit callbacks from overlapping or halting new playback sessions.
- **Completely Localized Inspector Strings**: Fully decoupled all remaining hardcoded labels, unit names, fallbacks, and the interactive genre list from `inspector.py`, routing them dynamically through the i18n JSON translation modules.
- **Optional Treeview Columns & Background Scanner**: Added optional columns to the Treeview (Duration, Format, Sample Rate) that load asynchronously in a lightweight background thread on file insertion, preventing GUI freezes. Includes a native checkbutton column visibility toggle in context menus.
- **M4A Container Integration**: Replaced legacy ADTS AAC (`.aac`) export format with the industry-standard MPEG-4 M4A (`.m4a`) container, unlocking full, standardized tagging (Song Name, Artist, Album, Genre, Year, Track, Comment, etc.) and embedded cover art capabilities for AAC audio exports.
- **Precision Format-Aware Tag Constraints**: Implemented strict, standard-compliant metadata restrictions in the Inspector Details tab. Custom tags are dynamically enabled or disabled (e.g., restricting WAV metadata to RIFF INFO standards and ADTS `.aac` to completely read-only), preventing file header corruption and ensuring broad player compatibility.
- **Lossless FLAC & M4A Artwork Support**: Enabled complete cover art management (viewing, changing, lossless removal, and exporting) for FLAC (`.flac`) and M4A (`.m4a`) files, keeping their processing fully asynchronous.
- **Universal Comment Mapping**: Enhanced the metadata writer to natively map comments via FFmpeg for WAV, FLAC, M4A, and OGG containers.
- **Drag & Drop File Queue Support**: Added native drag & drop support for the main file queue.
  - **Single File Support**: Audio files can now be dragged directly from Windows Explorer into the file list.
  - **Multi-File Support**: Multiple selected audio files can be dropped simultaneously.
  - **Folder Support**: Entire folders can be dragged into the queue and are scanned recursively for supported audio formats.
  - **Multi-Folder Support**: Multiple folders can be dropped at once and are processed recursively.
  - **Duplicate Protection**: Files already present in the queue are automatically ignored, preventing accidental duplicate entries.
  - **General Tab**: Displays detailed file container, sample format, and estimated total sample count properties.
  - **Details Tab**: Added an interactive metadata tag editor supporting Song Name, Artist, Album, Album Artist, Composer, Grouping, Genre, Track, Year, Disc, BPM, and Compilation flags.
  - **Artwork Tab**: Added a brand-new tab for album covers. Allows users to view the embedded cover, check its resolution and codec (e.g., JPG / 1024 x 1024), export the image, change it, or delete it entirely via a dedicated "✕" button. Cover modification and deletion operations are performed losslessly and are supported for MP3, FLAC, and M4A files.
  - **Statistics Tab**: Uses FFmpeg's `astats` and `loudnorm` filters to display EBU R128 loudness metrics (Integrated Loudness, LRA, Threshold) alongside detailed signal analysis values such as True Peak, Sample Peak, Min/Max Levels, RMS Power, DC Offset, Measured Bit Depth, and Crest Factor.
  - **Asynchronous Loading**: Added background analysis with visual progress feedback for both statistics calculation and artwork extraction, keeping the Inspector responsive.
  - **Lossless Metadata Writer**: Implemented safe, lossless metadata and artwork saving using FFmpeg stream copy (`-c copy`), avoiding any audio quality degradation or re-encoding.
  - **Smart Clipboard Copy Tool**: Added an intuitive, localized "Copy" button to the properties dialog footer. It dynamically formats and exports the contents of the currently active tab to the system clipboard, featuring temporary visual button feedback ("✔ Copied!").
  - **Dynamic Crest Factor**: Implemented automatic real-time calculation of linear Crest Factor and Decibel peak-to-RMS ratios in the Statistics tab.
  - **Thread-Safe Analysis Guard**: Integrated unique analysis transaction IDs to prevent GUI race conditions and overlapping thread errors if the "Reload" button is clicked rapidly.
- **Information Icon Button ("ℹ")**: Added a compact Info button next to the file management buttons ("Add Files", "Add Folder", "Remove Selected") in the main window.
  - **Reactive Selection Binding**: Configured the `"ℹ"` button to automatically sync with the Treeview list selection. It remains safely locked (`disabled`) when no tracks are chosen or during active audio processing, and unlocks instantly once a track is selected.
  - **Dynamic Help Status Bar Tooltips**: Bound hover events on the active `"ℹ"` button to the status bar, smoothly displaying a localized tooltip on mouseover and restoring the default status text on mouseout.
- **Unicode-Safe Player Processes**: Replaced legacy system locale pipe decoders in `gui.py` and `audio.py` with UTF-8 decoding and malformed byte handlers (`errors="ignore"`), improving compatibility with paths containing non-ASCII characters.
- **FFmpeg Diagnostic Engine**: Implemented a new error translation layer. Cryptic FFmpeg errors (e.g., missing encoders, corrupted files, or locked directories) are now intercepted and translated into clear, actionable diagnostic messages in the UI.
- **Pre-Flight Write Check**: The application now proactively checks for write permissions in the destination folder before starting the FFmpeg process, cleanly catching read-only USB drives or restricted network shares.
- **MAX_PATH Safety Check**: Added proactive checks for the Windows 260-character path limit. Files exceeding this limit are now skipped with a clear warning message instead of causing application or FFmpeg failures.
- **Dynamic Language Pack System**: Replaced the previously static language registration mechanism with a fully dynamic folder-based architecture. All valid language files located in the `/lang/` directory are now detected automatically and become instantly available in the application settings.
- **Modder-Friendly Localization Workflow**: Users, translators, and community contributors can now create and distribute custom language packs (e.g. `fr_FR`, `es_ES`, `it_IT`, `nl_NL`, `pt_BR`, or any other locale) without modifying Python source code. Invalid or corrupted language files are automatically ignored to maintain maximum application stability.
- **External JSON-based Theming Engine**: Transitioned the entire UI styling system to a modder-friendly external architecture. All color palettes are now stored as individual `.json` files within a dedicated `/themes/` directory.
- **Dynamic Theme Folder Scanning**: Implemented an automated startup routine that scans the `/themes/` folder, dynamically populating the "App Theme" selector with any valid theme found on disk.
- **Automatic Theme Template Generation**: Configured the engine to automatically populate the `/themes/` directory with standard templates (Light, Läderlappen, Melcom, etc.) if the folder is empty, providing an immediate starting point for custom modifications.
- **Smart Luminance Detection**: Built a mathematical "Perceived Luminance" calculator that analyzes the background color of any external theme. The system now automatically determines if a modded theme is "Light" or "Dark" to apply the correct contrast settings for menus and listboxes.
- **Self-Healing Configuration Logic**: Integrated a fail-safe check during application startup. If a previously selected theme folder or file is missing or renamed, the app automatically recalibrates to the internal `Light` default and updates the `options.ini` to prevent UI inconsistencies.

### Changed
- **Visual Droplist Focus Clearing (Bug Fix)**: Solved persistent blue text selection highlights in readonly Comboboxes by routing events to immediately drop widget focus and execute delayed selection clears.
- **FFmpeg Execution Stutter / Lag Fix**: Replaced the performance-heavy byte-by-byte stream reader with a fast line-by-line `readline()` loop for FFmpeg subprocesses, instantly eliminating CPU-overhead lag and GUI freezes during batch processing.
- **Auto-Reset for Output Parameters**: Added a UX safety reset that automatically falls back both Sample Rate and Quality dropdowns to `Original / Default` whenever the main container format is changed.
- **Improved File Queue Workflow**: Added familiar Windows keyboard shortcuts for faster queue management.
  - **Ctrl+A**: Instantly selects all files currently loaded in the queue.
  - **Ctrl+D**: Clears the current file selection without removing any files.
  - **Delete Key**: Continues to remove all selected files, enabling fast queue cleanup when combined with Ctrl+A.
- **Comprehensive Localization Polish**: Thoroughly reviewed and refined English, German, Polish, and Swedish language files. Fixed typos, improved grammar, and adapted audio terminology to match professional industry standards across all supported languages (e.g. standardizing terms like 'Compilation', 'Punch', and 'Klangfärbung').
- **Enhanced Resolution Recognition**: Improved sample format parsing to automatically map Float WAV and uncompressed bit depth properties, resolving several legacy "N/A" metadata results (e.g., correctly resolving `32 bits (Float)`).
- **Polished Tab Aesthetics**: Structured custom stylesheet maps in `theme.py` to automatically adapt Notebook tabs, borders, and selected active accent colors to every handcrafted theme.
- **Cleaner Process Logs**: Added the `-hide_banner` flag to all internal FFmpeg calls. This removes the FFmpeg version and library build header from the UI log, making process output significantly cleaner and easier to read.
- **Streamlined Release Layout**: Simplified the structure of the distributed ZIP package. The executable, language files, documentation, and customization resources are now located directly in the root directory of the release package instead of an additional dist subfolder, making the extracted release easier to navigate and use.
- **Streamlined `theme.py` Architecture**: Completely refactored the theming module by removing hundreds of lines of static color data, replacing them with a lean, passive loader that relies on the external JSON ecosystem.
- **Internal Safety Fallback**: Retained a hardcoded "Light" palette within the source code as a high-security fallback to ensure application stability even in cases of complete directory deletion or file-system permission errors.

### Fixed
- **Normalization Tag Loss & Container Corruption**: Resolved a critical issue where normalizing files with cover art into non-artwork formats (WAV, OGG, raw AAC) caused FFmpeg to map the cover as a broken video stream, leading to container corruption and lost metadata. Automated video-stream stripping (`-vn`) is now applied to these targets.
- **Cover Art Re-encoding Failures**: Resolved an issue where normalizing MP3, FLAC, or M4A files containing artwork caused FFmpeg to fail with codec parameters errors due to attempting to re-encode the cover picture into an H.264 video stream. Implemented strict lossless video stream copying (`-c:v copy`) for these formats.
- **Dynamic Status Bar State Management**: Reworked the entire status bar update logic to accurately reflect the current application state at all times. Playback, analysis, normalization, file selection, startup, cancellation, completion, and error states now update dynamically through the localization system instead of relying on stale or static status messages.
- **Bulletproof JSON Parsing**: Completely rewrote the parsing logic for FFmpeg's `loudnorm` analysis. It now uses highly specific, non-greedy regex matching and strict key validation. This makes the tool resilient against malformed FFmpeg output, unexpected warnings, and metadata containing embedded braces.
- **Improved Exception Handling**: Added specific `JSONDecodeError` handling to provide exact text block dumps if parsing ever fails, significantly improving debuggability for future edge cases.
- **Modeless Inspector Theme Synchronization**: Resolved a legacy issue where the Audio Properties window (Inspector) failed to inherit new color values during a live theme switch. The Inspector now fully supports real-time, zero-latency design updates without requiring a window reload.

---

## [4.0.3] - 2026-05-30
### Läderlappen Edition 🦇

### Added
- **Modern Flat UI & Theming Engine**
  - Introduced a complete visual overhaul with a sleek, flat-style design, replacing legacy 3D frames with modern, clean geometries.
  - Added true dynamic theme support allowing users to switch themes on the fly without restarting.
  - Included multiple new handcrafted themes: "Midnight", "Modernlight", "Melcom", "Aquamarine & Blue" (Classic Tracker Style), and the namesake "Läderlappen" dark mode.
- **Swedish Localization**
  - Added full Swedish (`sv_SE`) language support, properly honoring the "Läderlappen" edition name.
- **Thread-Safe Log Engine**
  - Implemented a new, dedicated `AppLogger` with automatic disk rotation (`RotatingFileHandler`). This replaces the legacy RAM-heavy log method, making long batch processes much safer and more efficient.

### Changed
- **Modular Architecture Overhaul (Under the Hood)**
  - Completely refactored the monolithic script into a modern, decoupled multi-file structure (`main.py`, `gui.py`, `core.py`, `theme.py`, `audio.py`, `i18n.py`, `constants.py`). This drastically improves maximum stability, future maintainability, and resource management.
- **Refined Workspace Layout**
  - Optimized the Options menu by placing the "Language" and "App Theme" dropdowns side-by-side, reducing vertical height.
  - Rebalanced the main window layout. Adjusted vertical spacing for the file list and process log to keep the progress bar permanently visible without requiring manual window resizing.
  - Styled the "Start Normalization" button with a prominent Accent color to improve the visual workflow hierarchy.
- **State Management & GUI Queue**
  - Fully encapsulated background execution states. Improved threading communication to prevent UI freezes and eliminate background log spam during idle states.

### Fixed
- **Orphaned Subprocess & Zombie Prevention**
  - Overhauled task cancellation. The app now cleanly targets and forcefully terminates active FFmpeg process trees on Windows, preventing audio file lockouts and background memory leaks.
- **Dynamic Theme Switching Glitches**
  - Built a custom Combobox Cache-Clearing Engine to fix persistent visual bugs where dropdown menus would render with inverted colors after switching themes. 
  - Fixed an issue where switching from Dark to Light theme would leave residual dark backgrounds on checkbuttons.
- **Window Management Stability**
  - Implemented a single-instance tracking system for all dialogs (Options, About). This prevents application crashes and race conditions if a user clicks menu items too rapidly.
- **Translation Mappings**
  - Fixed a missing key mapping issue where raw translation keys (e.g., `[mastering_character_preset_transparent]`) were shown in the Mastering Character dropdown instead of the actual localized text.

### Fixed
- **Progress Bar Rendering Bug**
  - Fixed an issue where the progress bar would not display or would flicker when normalizing multiple tracks sequentially.
  - Ensured proper initialization and reset of the progress bar for each normalization task.
  - Background thread handling improved to prevent old queue messages from affecting new normalization runs.
- **Multi-Track Normalization Stability**
  - Selecting a new track mid-process no longer causes the progress bar to flicker.
  - Cancelled one track now safely terminates the FFmpeg process without impacting subsequent tracks.

---

## [3.2.0] - 2026-05-24
### Nachtschicht Edition

### Added
- **Mastering Character Selector**
    - Added a dedicated combo box for mastering character selection.
    - The help text below the selector updates dynamically for the selected preset.
- **Professional Mastering Character Presets**
    - Added internal mastering presets for different electronic music workflows.
    - The UI now shows these presets using the current professional labels in each supported language: `Transparent`, `Cohesive`, `Punchy`, and `Aggressive`.
    - The internal preset key remains `Clean`; the visible default is `Transparent`.
- **Expanded Loudness Presets**
    - Added clearer LUFS presets for streaming, podcast, gaming/dynamic music, and broadcast workflows.
    - Added separate podcast presets for stereo (`-16 LUFS`) and mono/speech (`-19 LUFS`).
- **Expanded True Peak Presets**
    - Added clearer True Peak labels for streaming-safe, lossy-codec-safe, hot/CD-style, and risky no-limit workflows.

### Changed
- **Transparent is now the default displayed preset**
    - The internal preset key remains `Clean`, but the default UI label is now `Transparent` and applies no extra character processing.
- **Dynamic preset generation**
    - The filter chain is now built from the preset definitions instead of hardcoded branches in the normalization workflow.
- **Improved Progress Display**
    - Single-file processing now uses an animated progress indicator so the user can clearly see that the application is working.
    - Multi-file batch processing keeps the existing determinate file-by-file progress behavior.
- **User Interface Layout**
    - Slightly increased the main window width.
    - Increased LUFS and True Peak preset dropdown widths to better fit the expanded preset names.
    - Improved layout compatibility for longer preset names in English, German, and Polish.
- **Localization**
    - Updated English, German, and Polish LUFS, True Peak, and mastering-character labels.
- **Documentation alignment**
    - README and built-in help files were updated to reflect the current UI, defaults, and preset set.

### Notes
- The two-pass linear loudnorm workflow remains the main normalization path.
- No automatic post-render loudness correction pass is applied.
- No additional final limiter is added beyond the selected processing chain.
- The workflow favors musicality and preserved dynamics over forcing loudness targets at any cost.

---

## [3.1.0] - 2026-02-20
### "Feierabend Edition"

### Added
- **New Normalization Mode: Two-Pass (Linear)**
    - Introduced a professional Two-Pass normalization mode that preserves the original dynamics (LRA) of the audio while reaching the target LUFS.
    - Uses a first pass for analysis and a second pass for high-precision linear gain adjustment.
- **Metadata Preservation**
    - The tool now preserves global metadata tags (Artist, Album, Title, etc.) from the source file and maps them to the output file across all formats.
- **Automatic Temporary File Cleanup**
    - Implemented a robust cleanup system that ensures `.temp` files are automatically deleted from the workspace, regardless of whether a process succeeds, fails, or is cancelled by the user.

### Changed
- **Dynamic Quality Preservation for WAV and FLAC**
    - WAV and FLAC outputs no longer force a fixed sample rate (48 kHz) or bit depth (32-bit).
    - The tool now uses `ffprobe` to detect the source's properties and preserves the original sample rate and bit depth (e.g., keeping 24-bit/96kHz files intact).
- **Enhanced MP3 Compatibility**
    - MP3 encoding now forces ID3v2.3 tags, ensuring much better compatibility with Windows Explorer and older hardware players.
- **Code Refactoring and Documentation**
    - Completely overhauled the internal comments for better readability and future maintainability.
    - Cleaned up legacy code blocks and refined the FFmpeg command generation logic.

### Fixed
- **About Dialog Bug:** Fixed a variable reference error in the "About" window that could cause issues when closing the dialog.
- **Process Robustness:** Improved the error handling during the Two-Pass analysis phase to prevent crashes on malformed audio files.

---

## [3.0.1] - 2025-11-03

### Fixed
- **Improved Application Path Handling for Robustness**
    - Fixed a critical issue where language files and other resources (e.g., options.ini, logs) would fail to load when the application was launched from the Windows Start Menu search.
    - The program now correctly determines its own location, ensuring that all necessary files are found regardless of how or from where it is started.
    - This enhances stability and provides a consistent user experience across all versions of Windows.

---

## [3.0.0] - 2025-10-24

### Added
- **Batch Processing**
    - Process Multiple Files: The tool is no longer limited to a single file. You can now add a list of audio files to be processed in sequence.
    - Add Entire Folders: A new "Add Folder" button allows you to recursively scan a directory and add all supported audio files.
    - Redesigned File Management: A modern file list now displays all files queued for processing.
- **Integrated Audio Player & Playlist**
    - Audio Preview for Batches: To help verify that the correct files are loaded, a mini-player has been integrated below the file list.
    - Full Playback Controls: Includes Play, Stop, Next («), and Previous (»).
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

---

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

---

## [2.2.1] - 2025-08-29

### Changed
- **Improved AAC Output Encoding:**
    - AAC encoding now utilizes a Constant Bit Rate (CBR) of 512k. Previously, AAC output had no explicit bitrate specified, relying on FFmpeg's defaults.
- **Improved OGG Vorbis Output Encoding:**
    - OGG Vorbis encoding now uses a target bitrate of 500k (managed mode). This replaces the previous quality-scale setting (`-qscale:a 10`), providing more explicit control over the output file size and quality.
- Updated Build Date: The application's build date has been updated to 2025-08-29.

---

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

---

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

---

## [2.0.5]

### Fixed
- Bug Fixes and Stability Improvements.

---

## [2.0.1]

### Added
- **New Output Format Option: OGG Vorbis**
    - OGG Vorbis can now be selected as an output format.
- **New Option: "Single Log Entry per Process"**
    - A checkbox was added in Options to control log behavior, enabled by default.

### Changed
- **Default FFmpeg Path in Options Dialog**
    - Shows the program path on first start and loads any saved path on subsequent starts.

---

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

---

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