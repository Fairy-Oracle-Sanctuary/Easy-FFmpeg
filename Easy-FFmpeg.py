import os
import sys

from PySide6.QtCore import QFile, QLocale, Qt, QTranslator

from app.common.application import SingletonApplication
from app.common.config import Language, cfg
from app.common.logger import cleanOldLogs
from app.resource import resource_rc  # noqa
from app.view.main_window import MainWindow
from libs.qfluentwidgets_pro import FluentTranslator


def main():
    # 界面缩放
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    # 创建应用程序实例
    app = SingletonApplication(sys.argv, "Easy-FFmpeg")
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    if sys.platform == "darwin":
        from AppKit import NSApplication

        NSApplication.sharedApplication()

    # 启动时自动清理过期日志
    if cfg.get(cfg.autoCleanLogs):
        cleanOldLogs(cfg.get(cfg.logRetentionDays))

    # 安装翻译器
    language = cfg.get(cfg.language)
    locale = QLocale.system() if language == Language.AUTO else language.value
    translator = FluentTranslator(locale)
    galleryTranslator = QTranslator()
    if language != Language.AUTO or QFile.exists(f":/app/i18n/app.{locale.name()}.qm"):
        galleryTranslator.load(locale, "app", ".", ":/app/i18n")

    app.installTranslator(translator)
    app.installTranslator(galleryTranslator)

    # 创建并显示主窗口
    window = MainWindow()
    app.aboutToQuit.connect(window.onExit)
    window.show()

    # 运行应用程序
    return app.exec()


if __name__ == "__main__":
    print(sys.platform)
    sys.exit(main())

# Easy-FFmpeg

"""

---

## 中文简介

Easy-FFmpeg 是一款基于 FFmpeg 的跨平台多媒体处理工具，提供直观的图形界面，让用户无需记忆命令行参数即可完成各类音视频处理任务。

软件集成视频压制、音频提取、视频截图、GIF 制作、视频剪切、格式转换、视频拼接、硬字幕嵌入、音量归一化、速度调整等丰富功能于一体，并支持硬件加速编码（NVENC / QSV / AMF / VideoToolbox）、批量任务队列与多语言界面（75 种语言），帮助用户高效完成日常多媒体处理工作。

Easy-FFmpeg 尊重用户自由。用户可以自由运行、研究、修改和再分发本软件。

主要功能：

* 视频压制（软编 / 硬编，CRF / 码率控制，预设调优）
* 音频提取（MP3 / AAC / WAV / OPUS / VORBIS / FLAC）
* 视频截图与 GIF 制作
* 视频剪切与拼接（自动统一分辨率 / SAR）
* 音视频及图片格式转换
* 硬字幕嵌入（SRT / ASS / VTT 等）
* 音量归一化与速度调整
* 媒体信息查看（结构化展示）
* MS Store 徽标批量生成
* 批量任务队列与并发处理
* 硬件加速（NVIDIA / Intel / AMD / Apple）
* 75 种语言界面

项目地址：https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg

---

## English Description

Easy-FFmpeg is a cross-platform multimedia processing tool built on FFmpeg, providing an intuitive graphical interface that lets users handle various audio/video tasks without memorizing command-line parameters.

The software integrates video encoding, audio extraction, video screenshots, GIF creation, video cutting, format conversion, video concatenation, hard subtitle embedding, volume normalization, speed adjustment, and more. It supports hardware-accelerated encoding (NVENC / QSV / AMF / VideoToolbox), batch task queues, and a multilingual interface (75 languages), helping users efficiently accomplish everyday multimedia processing work.

Easy-FFmpeg respects user freedom. Users are free to run, study, modify, and redistribute this software.

Key Features:

* Video encoding (software / hardware, CRF / bitrate control, preset tuning)
* Audio extraction (MP3 / AAC / WAV / OPUS / VORBIS / FLAC)
* Video screenshots & GIF creation
* Video cutting & concatenation (auto-unify resolution / SAR)
* Audio, video, and image format conversion
* Hard subtitle embedding (SRT / ASS / VTT, etc.)
* Volume normalization & speed adjustment
* Media info viewer (structured display)
* MS Store logo batch generation
* Batch task queue with concurrent processing
* Hardware acceleration (NVIDIA / Intel / AMD / Apple)
* 75-language interface

Project page: https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg

---

🎬视频压制 • 🎵音频提取 • �截图GIF • ✂️剪切拼接 • 🔄格式转换 • 📝字幕嵌入 • ⚡硬件加速 • 🌍75种语言 • 🔓自由软件

🎬Video Encoding • 🎵Audio Extraction • 📸Screenshot & GIF • ✂️Cut & Merge • 🔄Format Conversion • 📝Subtitles • ⚡Hardware Acceleration • 🌍75 Languages • 🔓Free Software

---

Copyleft 🄯 2026 天机阁(Fairy-Oracle-Sanctuary)
Copyleft 🄯 2026 Fairy Oracle Sanctuary

---

本软件为自由软件。

软件源代码采用 GNU General Public License v3.0（GPL-3.0）许可协议发布；项目图标及相关美术资源采用 Creative Commons Attribution-ShareAlike 4.0 International（CC BY-SA 4.0）许可协议发布。

用户有权根据相应许可证条款自由运行、研究、修改和再分发本软件。

This software is free software.

The source code is licensed under the GNU General Public License v3.0 (GPL-3.0). Project icons and artwork are licensed under the Creative Commons Attribution-ShareAlike 4.0 International License (CC BY-SA 4.0).

Users are free to run, study, modify, and redistribute the software in accordance with the applicable license terms.

---

The application requires runFullTrust for file operations and executing external tools (FFmpeg) for media processing. This capability is used solely for core desktop application functions.

Our application is a desktop software installer that requires elevation during installation to write to Program Files directory. The installed application itself runs without elevation. This is standard practice for desktop software distribution on Windows.

"""