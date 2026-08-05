import shutil
import sys
from enum import Enum
from pathlib import Path

from PySide6.QtCore import QLocale

from libs.qfluentwidgets_pro import (
    BoolValidator,
    ConfigItem,
    ConfigSerializer,
    OptionsConfigItem,
    OptionsValidator,
    QConfig,
    RangeConfigItem,
    RangeValidator,
    Theme,
    qconfig,
)

from .setting import CONFIG_FILE, EXE_SUFFIX


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


class Language(Enum):
    """Language enumeration"""

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """Language serializer"""

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class StringListSerializer(ConfigSerializer):
    """逗号分隔字符串 ↔ list 的序列化器"""

    def serialize(self, items: list) -> str:
        if isinstance(items, list):
            return ",".join(items)
        return str(items)

    def deserialize(self, value) -> list:
        if isinstance(value, list):
            return value
        if isinstance(value, str):
            return value.split(",") if value else []
        return []


def get_default_exe_path(exe_name: str) -> str:
    """获取可执行文件的默认路径，根据操作系统返回不同路径"""
    # Windows: 使用 tools 目录
    if sys.platform == "win32":
        return str(Path(f"tools/{exe_name}{EXE_SUFFIX}").absolute())

    # macOS: 优先使用打包后的app目录下的tools目录
    if sys.platform == "darwin":
        # 检测是否在app bundle中运行
        if ".app" in sys.executable:
            # 在app bundle中，tools目录在Contents/MacOS下
            bundle_path = Path(sys.executable)
            resources_dir = bundle_path.parent.parent / "MacOS"
            return str((resources_dir / "tools" / exe_name).absolute())
        else:
            # 开发环境，使用本地tools目录
            return str(Path(f"tools/{exe_name}").absolute())

    # Linux: 优先使用系统包管理器安装的路径
    if sys.platform == "linux":
        # 优先检查标准系统路径，避免被 IDE 等第三方工具的 PATH 干扰
        system_paths = [
            f"/usr/bin/{exe_name}",
            f"/usr/local/bin/{exe_name}",
        ]
        for path in system_paths:
            if Path(path).exists():
                return path
        # 兜底: 从 PATH 中查找
        which_path = shutil.which(exe_name)
        if which_path:
            return which_path

    # 回退到使用 tools 目录
    return str(Path(f"tools/{exe_name}").absolute())


class Config(QConfig):
    """Config of application"""

    # main window
    micaEnabled = ConfigItem("MainWindow", "MicaEnabled", isWin11(), BoolValidator())
    dpiScale = OptionsConfigItem(
        "MainWindow",
        "DpiScale",
        "Auto",
        OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]),
        restart=True,
    )
    language = OptionsConfigItem(
        "MainWindow",
        "Language",
        Language.CHINESE_SIMPLIFIED,
        OptionsValidator(Language),
        LanguageSerializer(),
        restart=True,
    )
    accentColor = OptionsConfigItem(
        "MainWindow", "AccentColor", "#009faa", OptionsValidator(["#009faa", "Auto"])
    )
    closeDirectly = ConfigItem(
        "MainWindow", "CloseDirectly", False, BoolValidator(), restart=False
    )
    checkUpdateAtStartUp = ConfigItem(
        "MainWindow", "CheckUpdateAtStartUp", True, BoolValidator(), restart=False
    )

    # exe
    ffmpegPath = ConfigItem("FFmpeg", "FFmpegPath", get_default_exe_path("ffmpeg"))

    # home
    homeRecursive = ConfigItem(
        "Home", "Recursive", False, BoolValidator(), restart=False
    )

    # ffmpeg
    # 是否使用完全自定义的参数
    ffmpegIsUseCustomArgs = ConfigItem(
        "FFmpeg", "IsUseCustomArgs", True, BoolValidator(), restart=False
    )

    # 自定义视频压制参数
    ffmpegCustomVideoArgs = ConfigItem(
        "FFmpeg",
        "CustomVideoArgs",
        "ffmpeg -i {{input_file}} -c:v libx264 -preset medium {{output_file}} -y",
        restart=False,
    )

    # 自定义音频压制参数
    ffmpegCustomAudioArgs = ConfigItem(
        "FFmpeg",
        "CustomAudioArgs",
        "ffmpeg -i {{input_file}} -c:a libmp3lame {{output_file}} -y",
        restart=False,
    )

    # 启用的参数块（过滤器选择状态），存储为逗号分隔的标识符
    ffmpegEnabledBlocks = ConfigItem(
        "FFmpeg",
        "EnabledBlocks",
        ["encoder", "quality", "preset", "resolution", "frame_rate", "audio", "extra"],
        serializer=StringListSerializer(),
        restart=False,
    )

    # 并发数量，同时压制多个视频时的最大并行数
    ffmpegConcurrentEncodes = RangeConfigItem(
        "FFmpeg", "ConcurrentEncodes", 2, RangeValidator(1, 3), restart=False
    )

    # 软件编码器
    ffmpegSoftWareVideoCodec = OptionsConfigItem(
        "FFmpeg",
        "SoftWareVideoCodec",
        "libx264",
        OptionsValidator(["libx264", "libx265", "libvpx-vp9", "libaom-av1"]),
        restart=False,
    )

    # 是否使用硬件编码器
    ffmpegUseHardWareVideoCodec = ConfigItem(
        "FFmpeg", "UseHardWareVideoCodec", False, BoolValidator(), restart=False
    )
    # 硬件编码器平台
    ffmpegHardWareVideoCodecPlatform = OptionsConfigItem(
        "FFmpeg",
        "HardWareVideoCodecPlatform",
        "NVIDIA",
        OptionsValidator(["NVIDIA", "Intel", "AMD"]),
        restart=False,
    )
    # 硬件编码器
    ffmpegHardWareVideoCodec = OptionsConfigItem(
        "FFmpeg",
        "HardWareVideoCodec",
        "h264_nvenc",
        OptionsValidator(
            [
                "h264_nvenc",
                "hevc_nvenc",
                "av1_nvenc",
                "h264_qsv",
                "hevc_qsv",
                "av1_qsv",
                "h264_amf",
                "hevc_amf",
                "av1_amf",
            ]
        ),
        restart=False,
    )

    # 质量控制模式：CRF 恒定质量 / Bitrate 目标码率（二选一）
    ffmpegQualityMode = OptionsConfigItem(
        "FFmpeg",
        "QualityMode",
        "CRF",
        OptionsValidator(["CRF", "Bitrate"]),
        restart=False,
    )
    # CRF 质量参数 (0-51, 0为无损，18-28为常用范围)
    ffmpegCrf = ConfigItem("FFmpeg", "Crf", "24", restart=False)
    # 视频目标码率 (kbps)，仅在质量模式为 Bitrate 时生效
    ffmpegVideoBitrate = ConfigItem("FFmpeg", "VideoBitrate", "2000", restart=False)
    # 二次编码，码率控制更精准但耗时翻倍，仅 Bitrate 模式有意义
    ffmpegTwoPass = ConfigItem(
        "FFmpeg", "TwoPass", False, BoolValidator(), restart=False
    )

    # 编码速度预设
    ffmpegPreset = OptionsConfigItem(
        "FFmpeg",
        "Preset",
        "medium",
        OptionsValidator(
            [
                "ultrafast",
                "superfast",
                "veryfast",
                "faster",
                "fast",
                "medium",
                "slow",
                "slower",
                "veryslow",
            ]
        ),
        restart=False,
    )

    # 分辨率：origin 保持原分辨率 / 1080p / 720p / 480p / custom 自定义
    ffmpegResolution = OptionsConfigItem(
        "FFmpeg",
        "Resolution",
        "origin",
        OptionsValidator(["origin", "1080p", "720p", "480p", "custom"]),
        restart=False,
    )
    # 自定义分辨率宽度（高度按比例自动计算，需为偶数）
    ffmpegCustomWidth = ConfigItem("FFmpeg", "CustomWidth", "1920", restart=False)

    # 帧率：origin 保持原帧率 / 24 / 30 / 60
    ffmpegFrameRate = OptionsConfigItem(
        "FFmpeg",
        "FrameRate",
        "origin",
        OptionsValidator(["origin", 24, 30, 60]),
        restart=False,
    )

    # 音频编码器：aac / libmp3lame / libopus / copy（不重编码）
    ffmpegAudioCodec = OptionsConfigItem(
        "FFmpeg",
        "AudioCodec",
        "aac",
        OptionsValidator(["aac", "libmp3lame", "libopus", "copy"]),
        restart=False,
    )
    # 音频码率
    ffmpegAudioBitrate = OptionsConfigItem(
        "FFmpeg",
        "AudioBitrate",
        "128k",
        OptionsValidator(["128k", "192k", "320k"]),
        restart=False,
    )
    # 删除音轨
    ffmpegRemoveAudio = ConfigItem(
        "FFmpeg", "RemoveAudio", False, BoolValidator(), restart=False
    )

    # 进阶：tune 调优（仅 libx264/libx265 生效）
    ffmpegTune = OptionsConfigItem(
        "FFmpeg",
        "Tune",
        "none",
        OptionsValidator(["none", "film", "animation", "grain", "fastdecode"]),
        restart=False,
    )
    # 裁剪起始时间 (秒)，留空表示从头开始
    ffmpegStartTime = ConfigItem("FFmpeg", "StartTime", "", restart=False)
    # 裁剪持续时间 (秒)，留空表示到结尾
    ffmpegDuration = ConfigItem("FFmpeg", "Duration", "", restart=False)
    # 反交错
    ffmpegDeinterlace = ConfigItem(
        "FFmpeg", "Deinterlace", False, BoolValidator(), restart=False
    )
    # 旋转角度
    ffmpegRotation = OptionsConfigItem(
        "FFmpeg",
        "Rotation",
        "none",
        OptionsValidator(["none", "90", "180", "270"]),
        restart=False,
    )


cfg = Config()
cfg.themeMode.value = Theme.LIGHT
qconfig.load(str(CONFIG_FILE.absolute()), cfg)
