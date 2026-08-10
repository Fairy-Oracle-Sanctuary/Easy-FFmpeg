<p align="center">
  <img src="app/resource/images/logo.png" alt="logo" width="200"/>
</p>

<h1 align="center">
  Easy FFmpeg
</h1>

<p align="center">
  <a href="https://easypeg.ora-san.org/">Official Website</a> · <a href="https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg">GitHub Repository</a> · <a href="https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases">Download Releases</a>
</p>

<p align="center">
  <i>A batch video processing tool based on FFmpeg, simple and easy to use</i>
</p>

<p align="center">
  Provides a visual task queue, advanced encoding parameters, and 12 common tools including audio extraction, video cutting, GIF creation, video concatenation, subtitle handling, loudness normalization, and speed adjustment. Built-in FFmpeg path auto-detection, right-click menu integration, and system tray.
</p>

<p align="center">
  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/LICENSE-GPL%20v3-green" alt="LICENSE"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Python-3.9+-yellow" alt="Python 3.9+"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Version-1.0.0-purple" alt="Version 1.0.0"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-orange" alt="Platform Windows | macOS | Linux"/>
  </a>

  <a style="text-decoration:none">
    <img src="https://img.shields.io/badge/UI-PySide6%20%2B%20QFluentWidgets_Pro-cyan" alt="UI PySide6 + QFluentWidgets_Pro"/>
  </a>
</p>

<p align="center">
 <a href="README.md">English</a> | <a href="README.zh.md">简体中文</a>
</p>

<p align="center">
  <a href="#features">Features</a> •
  <a href="#quick-start">Quick Start</a> •
  <a href="#usage">Usage</a> •
  <a href="#configuration">Configuration</a> •
  <a href="#faq">FAQ</a>
</p>

---

## Features

### 🎬 Task Queue & Batch Processing
- Visual task cards showing real-time progress, speed, bitrate, and estimated size
- Persistent task storage (SQLite); only completed tasks are saved, running tasks stay in memory
- Batch add, retry, cancel, delete (optionally delete output files alongside the task)
- Retry tasks with either "current settings" or "original task parameters"
- Two-Pass encoding support with automatic stage label switching
- Failed-task badge warnings with one-click jump from the home info card
- Drop files into the path input box to add them; supports recursive folder scanning
- Windows Explorer right-click menu to send media files directly

### 🎛️ Advanced Encoding Parameters
- Encoder selection (software encoding / hardware acceleration: CUDA, VideoToolbox, QSV, etc.)
- Quality control (CRF / target bitrate) and encoding speed (preset)
- Resolution (custom width/height / common presets) and frame rate
- Audio encoder, audio bitrate, remove audio track
- Image quality and encoding parameters
- Advanced settings: start time, duration, deinterlace, rotation, tune
- Parameter blocks can be toggled on; unchecked blocks are not added to the FFmpeg command
- Custom FFmpeg command templates supported (`{{input_file}}` / `{{output_file}}` placeholders)

### 🧰 More Tools (12)
- **Audio Extract**: extract audio tracks from video, convert to MP3/AAC/WAV/Opus/Vorbis/FLAC
- **Video Snapshot**: capture a single frame at a given time point
- **GIF Make**: turn a video clip into a GIF animation
- **Video Cut**: trim a video by time range
- **Media Convert**: container and codec conversion
- **Image Convert**: image format conversion and quality compression
- **Video Concat**: merge multiple videos, automatically unifying resolution and SAR with `scale2ref` + `setsar`
- **Media Info**: async probe of codec / bitrate / duration details, shown in a structured format
- **MS Store Logo**: generate 5 logos for Microsoft Store listing (720×1080, 1080×1080, 300×300, 150×150, 71×71), preserving aspect ratio and centering with transparent padding
- **Subtitle**: extract subtitles / burn-in hard subtitles / embed soft subtitles / format conversion (SRT/ASS/VTT)
- **Loudnorm**: loudness and dynamic range normalization based on the EBU R128 standard
- **Speed**: audio+video / video-only / audio-only speed change, `atempo` chain supports 0.25×–8×+

### 🖼️ Interface & Interaction
- Modern Fluent design (PySide6 + QFluentWidgets)
- Windows 11 Mica effect
- Title bar quick theme switching (dark / light), automatically persisted
- System tray integration, minimize to tray on close
- InfoBadge on the update button showing the version number when a new version is detected
- Built-in update check: non-store version can download the installer locally; store version opens the browser
- Multi-language support (FluentTranslator-based i18n framework)
- Automatic log cleanup (configurable retention days)

---

## System Requirements

- **Operating System**: Windows 10/11 (recommended), macOS, Linux
- **Python**: 3.9+ (for running from source)
- **FFmpeg**: must be installed separately; the app can auto-detect the path or you can specify it manually
- **Hardware**: GPU with hardware acceleration support (optional, for encoding acceleration)

---

## Quick Start

### 1. Clone the repository

```bash
git clone --recursive https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg.git
cd Easy-FFmpeg
```

### 2. Create a virtual environment (uv recommended)

```bash
uv venv
# Windows
.venv\Scripts\activate
# Unix/macOS
source .venv/bin/activate
```

### 3. Install dependencies

```bash
# Common dependencies
uv pip install -r requirements.txt

# Windows extra dependencies (pywin32)
uv pip install -r requirements-win.txt

# macOS extra dependencies (PyObjC)
uv pip install -r requirements-mac.txt
```

### 4. Prepare FFmpeg

Ensure `ffmpeg` is accessible in the system PATH, or manually specify the FFmpeg executable path in the app's "Settings" page. The app auto-detects it on startup.

### 5. Run the application

```bash
python Easy-FFmpeg.py
```

> General users can download the installer for their platform directly from [Releases](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases) without setting up a Python environment.

---

## Usage

### Home
- **Info Card**: shows version, update time, log usage; provides shortcuts to the FFmpeg website, GitHub, clear logs, and reset settings
- **Update Button**: shows a version-number badge when a new version is detected; click to check for updates

### Task Page
- Drop or right-click-send media files to add tasks
- Task cards support start / cancel / retry / delete (delete can optionally remove the output file too)
- The top badge shows the task count and turns red when there are failed tasks

### Advance Page
- Toggle the parameter blocks you need; configure encoder, quality, resolution, audio, etc. as needed
- Enable "custom parameters" to write FFmpeg command templates directly

### More Page
- Pick a tool from the entry grid, fill in the parameters on the function page, then execute
- Tool tasks reuse the main task queue, with unified progress and status display

### Settings Page
- Configure personalization (theme, theme color, interface scaling, language), FFmpeg path, default encoding parameters, log cleanup, etc.
- Some settings take effect only after restarting the app

### Theme Switching
Click the theme switch button to the left of the minimize button in the title bar to quickly switch between dark / light mode; the setting is saved automatically.

---

## Configuration

Main configuration items can be modified in the "Settings" page. The config file is stored in the user directory (Windows: `%APPDATA%\EasyFFmpeg\config.json`).

### Personalization
- App theme (dark / light / follow system)
- Theme color
- Interface scaling
- Mica effect (Windows 11)
- Language

### FFmpeg
- FFmpeg executable path (auto-detected)
- Custom video / audio / image parameter templates
- Enabled parameter blocks
- Concurrent encode count
- Whether retry tasks use current settings
- Software encoder / hardware acceleration toggle and encoder selection
- Quality mode (CRF / bitrate), CRF, video bitrate, Two-Pass
- Encoding speed, resolution, custom width/height, frame rate
- Audio encoder, audio bitrate, remove audio track
- Image quality, tune, start time, duration, deinterlace, rotation

### Main Window
- Exit directly on close (instead of minimizing to tray)
- Check for updates on startup

### Home
- Recursively scan subfolders when adding files

### Log
- Automatically clean up expired logs
- Log retention days

---

## FAQ

### Q: It says FFmpeg cannot be found
A: Make sure `ffmpeg` is installed and available in the system PATH, or manually specify the full path to `ffmpeg.exe` (Windows) / `ffmpeg` (macOS/Linux) in "Settings → FFmpeg". The app supports auto-detection.

### Q: Video concatenation fails with "Input link parameters do not match"
A: When input videos have mismatched resolution or SAR, the app already unifies them automatically with the `scale2ref` + `setsar` filters. If it still fails, check whether the input files are corrupted, or unify the parameters first with "Media Convert".

### Q: Burning-in hard subtitles fails (path contains spaces / drive letters)
A: The app escapes `\`, `:`, and `'` in subtitle paths and wraps the path in single quotes. If it still fails, try to avoid special characters in the path, or check whether the subtitle format is supported by the `subtitles` filter.

### Q: MS Store logo only generated one task
A: This feature already supports generating 5 tasks of different sizes from the same input (`allow_duplicate`). If it still misbehaves, confirm the input is an image file.

### Q: Update check is unresponsive or download fails
A: The non-store version downloads the installer via GitHub Release; make sure your network can reach GitHub. The store version opens the Release page in the browser.

### Q: macOS says the developer cannot be verified on first open
A: The app is unsigned. On first open, right-click → Open, or run `xattr -dr com.apple.quarantine /Applications/Easy-FFmpeg.app` in the terminal.

---

## Tech Stack

- **UI Framework**: PySide6 + QFluentWidgets (Fluent design)
- **Video Processing**: FFmpeg
- **Task Storage**: SQLite
- **Config Storage**: JSON
- **Packaging**: Nuitka
- **Installer**: Inno Setup (Windows)
- **Package Manager**: uv (recommended)

---

## Contributing

1. Fork this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under [GPL v3](LICENSE).

---

## Acknowledgments

- UI components based on [PyQt-Fluent-Widgets](https://github.com/zhiyiYo/PyQt-Fluent-Widgets)
- Video processing based on [FFmpeg](https://ffmpeg.org/)

---

<a href="https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/graphs/contributors"> <img src="https://contrib.rocks/image?repo=Fairy-Oracle-Sanctuary/Easy-FFmpeg" /> </a>

## Star History

<a href="https://www.star-history.com/?repos=Fairy-Oracle-Sanctuary%2FEasy-FFmpeg&type=date&legend=top-left">
 <picture>
   <source media="(prefers-color-scheme: dark)" srcset="https://api.star-history.com/chart?repos=Fairy-Oracle-Sanctuary/Easy-FFmpeg&type=date&theme=dark&legend=top-left" />
   <source media="(prefers-color-scheme: light)" srcset="https://api.star-history.com/chart?repos=Fairy-Oracle-Sanctuary/Easy-FFmpeg&type=date&legend=top-left" />
   <img alt="Star History Chart" src="https://api.star-history.com/chart?repos=Fairy-Oracle-Sanctuary/Easy-FFmpeg&type=date&legend=top-left" />
 </picture>
</a>
