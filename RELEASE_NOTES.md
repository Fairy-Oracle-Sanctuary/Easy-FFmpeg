## 新增功能 / New Features
- 视频压制：支持软编（libx264/libx265/VP9/AV1）与硬编（NVENC/QSV/AMF/VideoToolbox），CRF 与码率双模式
  Video encoding: software (libx264/libx265/VP9/AV1) & hardware (NVENC/QSV/AMF/VideoToolbox), CRF and bitrate modes
- 音频提取：MP3 / AAC / WAV / OPUS / VORBIS / FLAC 六种格式
  Audio extraction: MP3 / AAC / WAV / OPUS / VORBIS / FLAC
- 视频截图与 GIF 制作：支持自定义时间点与输出格式
  Video screenshots & GIF creation with custom timestamps and output formats
- 视频剪切与拼接：concat 滤镜自动统一分辨率与 SAR
  Video cutting & concatenation with auto resolution/SAR unification
- 音视频及图片格式转换：智能容器选择，支持自定义 FFmpeg 命令
  Audio/video/image format conversion with smart container selection and custom FFmpeg commands
- 硬字幕嵌入：支持 SRT / ASS / VTT 等格式，跨平台路径转义
  Hard subtitle embedding: SRT / ASS / VTT, cross-platform path escaping
- 音量归一化与速度调整
  Volume normalization & speed adjustment
- 媒体信息查看：将 ffmpeg 输出解析为结构化中文展示
  Media info viewer: parses ffmpeg output into structured display
- MS Store 徽标批量生成：720×1080 / 1080×1080 / 300×300 / 150×150 / 71×71 五种尺寸
  MS Store logo batch generation: 720×1080 / 1080×1080 / 300×300 / 150×150 / 71×71
- 批量任务队列：支持并发压制、重试、取消、删除、查看日志
  Batch task queue: concurrent processing, retry, cancel, delete, view logs
- 国际化：支持 75 种语言界面
  Internationalization: 75-language interface
- 检查更新：自动检测新版本并展示更新日志
  Update checker: auto-detect new versions and display release notes
- 拖放文件支持：直接拖入文件即可填充路径
  Drag-and-drop file support
- 跨平台支持：Windows / macOS / Linux
  Cross-platform: Windows / macOS / Linux

## 改进 / Improvements
- 官方网站上线
  Official website launched

## 修复 / Fixes
- None

## 下载 / Download

| 平台 / Platform | 架构 / Arch | 安装包 / Installer |
| --- | --- | --- |
| Windows | x86_64 | [Easy-FFmpeg-v1.0.0-Windows-x86_64-Setup.exe](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download/v1.0.0/Easy-FFmpeg-v1.0.0-Windows-x86_64-Setup.exe) |
| Windows | MS Store | [Microsoft Store](https://apps.microsoft.com/detail/9MWJTGD5K71V) |
| macOS | x86_64 (Intel / Rosetta 2) | [Easy-FFmpeg-v1.0.0-macOS-x86_64.dmg](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download/v1.0.0/Easy-FFmpeg-v1.0.0-macOS-x86_64.dmg) |
| Linux | x86_64 | [Easy-FFmpeg-v1.0.0-Linux-x86_64.deb](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download/v1.0.0/Easy-FFmpeg-v1.0.0-Linux-x86_64.deb) · [Easy-FFmpeg-v1.0.0-Linux-x86_64.rpm](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download/v1.0.0/Easy-FFmpeg-v1.0.0-Linux-x86_64.rpm) |
| Linux | aarch64 | [Easy-FFmpeg-v1.0.0-Linux-aarch64.deb](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download/v1.0.0/Easy-FFmpeg-v1.0.0-Linux-aarch64.deb) · [Easy-FFmpeg-v1.0.0-Linux-aarch64.rpm](https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download/v1.0.0/Easy-FFmpeg-v1.0.0-Linux-aarch64.rpm) |

## 使用说明 / Usage

- **Windows**：运行安装包，按向导完成安装。也可通过 Microsoft Store 安装。
  Run the installer and follow the setup wizard. Alternatively, install via Microsoft Store.
- **macOS**：挂载 DMG，将 `Easy-FFmpeg.app` 拖入 Applications。应用未签名，首次打开请右键 → 打开（或终端执行 `xattr -dr com.apple.quarantine /Applications/Easy-FFmpeg.app`）。
  Mount the DMG and drag `Easy-FFmpeg.app` to Applications. The app is unsigned; on first launch, right-click → Open (or run `xattr -dr com.apple.quarantine /Applications/Easy-FFmpeg.app` in Terminal).
- **Linux**：使用系统包管理器安装对应的 deb/rpm 包（会自动安装 ffmpeg 依赖），或直接运行解压后的 `Easy-FFmpeg` 可执行文件。
  Install the appropriate deb/rpm package via your system package manager (ffmpeg dependency installed automatically), or run the extracted `Easy-FFmpeg` executable directly.
