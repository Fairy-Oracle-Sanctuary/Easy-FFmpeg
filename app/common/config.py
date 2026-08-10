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

from .setting import CONFIG_FILE, EXE_SUFFIX, IS_MS_STORE_VERSION


def isWin11():
    return sys.platform == "win32" and sys.getwindowsversion().build >= 22000


class Language(Enum):
    """Language enumeration（与 libs/qfluentwidgets_pro 支持的语言对齐）"""

    CHINESE_SIMPLIFIED = QLocale("zh_CN")
    CHINESE_TRADITIONAL = QLocale("zh_TW")
    ENGLISH = QLocale("en_US")
    JAPANESE = QLocale("ja_JP")
    KOREAN = QLocale("ko_KR")
    FRENCH = QLocale("fr_FR")
    GERMAN = QLocale("de_DE")
    SPANISH = QLocale("es_ES")
    PORTUGUESE = QLocale("pt_BR")
    RUSSIAN = QLocale("ru_RU")
    ITALIAN = QLocale("it_IT")
    DUTCH = QLocale("nl_NL")
    POLISH = QLocale("pl_PL")
    TURKISH = QLocale("tr_TR")
    VIETNAMESE = QLocale("vi_VN")
    THAI = QLocale("th_TH")
    INDONESIAN = QLocale("id_ID")
    HINDI = QLocale("hi_IN")
    ARABIC = QLocale("ar_EG")
    AFRIKAANS = QLocale("af_ZA")
    AMHARIC = QLocale("am_ET")
    AZERBAIJANI = QLocale("az_AZ")
    BELARUSIAN = QLocale("be_BY")
    BULGARIAN = QLocale("bg_BG")
    BENGALI = QLocale("bn_BD")
    BOSNIAN = QLocale("bs_BA")
    CATALAN = QLocale("ca_ES")
    CZECH = QLocale("cs_CZ")
    WELSH = QLocale("cy_GB")
    DANISH = QLocale("da_DK")
    GREEK = QLocale("el_GR")
    ESTONIAN = QLocale("et_EE")
    BASQUE = QLocale("eu_ES")
    PERSIAN = QLocale("fa_IR")
    FINNISH = QLocale("fi_FI")
    IRISH = QLocale("ga_IE")
    GALICIAN = QLocale("gl_ES")
    GUJARATI = QLocale("gu_IN")
    HEBREW = QLocale("he_IL")
    CROATIAN = QLocale("hr_HR")
    HUNGARIAN = QLocale("hu_HU")
    ARMENIAN = QLocale("hy_AM")
    ICELANDIC = QLocale("is_IS")
    GEORGIAN = QLocale("ka_GE")
    KAZAKH = QLocale("kk_KZ")
    KHMER = QLocale("km_KH")
    KANNADA = QLocale("kn_IN")
    LITHUANIAN = QLocale("lt_LT")
    LATVIAN = QLocale("lv_LV")
    MACEDONIAN = QLocale("mk_MK")
    MALAYALAM = QLocale("ml_IN")
    MONGOLIAN = QLocale("mn_MN")
    MARATHI = QLocale("mr_IN")
    MALAY = QLocale("ms_MY")
    BURMESE = QLocale("my_MM")
    NORWEGIAN_BOKMAL = QLocale("nb_NO")
    NEPALI = QLocale("ne_NP")
    NORWEGIAN_NYNORSK = QLocale("nn_NO")
    PUNJABI = QLocale("pa_IN")
    PORTUGUESE_EUROPEAN = QLocale("pt_PT")
    ROMANIAN = QLocale("ro_RO")
    SINHALA = QLocale("si_LK")
    SLOVAK = QLocale("sk_SK")
    SLOVENIAN = QLocale("sl_SI")
    ALBANIAN = QLocale("sq_AL")
    SERBIAN = QLocale("sr_RS")
    SWEDISH = QLocale("sv_SE")
    SWAHILI = QLocale("sw_KE")
    TAMIL = QLocale("ta_IN")
    TELUGU = QLocale("te_IN")
    TAJIK = QLocale("tg_TJ")
    TAGALOG = QLocale("fil_PH")
    UKRAINIAN = QLocale("uk_UA")
    URDU = QLocale("ur_PK")
    UZBEK = QLocale("uz_UZ")
    CHINESE_HONGKONG = QLocale("zh_HK")
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
        if IS_MS_STORE_VERSION and getattr(sys, "frozen", False) or "__compiled__" in globals():
            # MSIX 打包后：CWD 为 C:\Windows\system32，需基于 sys.executable 定位
            return str(Path(sys.executable).parent / "tools" / f"{exe_name}{EXE_SUFFIX}")
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
        Language.AUTO,
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

    # 日志
    # 启动时自动清理过期日志
    autoCleanLogs = ConfigItem(
        "Log", "AutoCleanLogs", True, BoolValidator(), restart=False
    )
    # 日志保留天数，超过该天数的 .log 文件将在启动时自动清理
    logRetentionDays = OptionsConfigItem(
        "Log",
        "RetentionDays",
        30,
        OptionsValidator([7, 14, 30, 90]),
        restart=False,
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

    # 自定义图片压制参数
    ffmpegCustomImageArgs = ConfigItem(
        "FFmpeg",
        "CustomImageArgs",
        "ffmpeg -i {{input_file}} -q:v 5 {{output_file}} -y",
        restart=False,
    )

    # 启用的参数块（过滤器选择状态），存储为逗号分隔的标识符
    ffmpegEnabledBlocks = ConfigItem(
        "FFmpeg",
        "EnabledBlocks",
        [
            "encoder",
            "quality",
            "preset",
            "resolution",
            "frame_rate",
            "audio",
            "image",
            "extra",
        ],
        serializer=StringListSerializer(),
        restart=False,
    )

    # 并发数量，同时压制多个视频时的最大并行数
    ffmpegConcurrentEncodes = RangeConfigItem(
        "FFmpeg", "ConcurrentEncodes", 2, RangeValidator(1, 3), restart=False
    )

    # 任务重试时是否使用当前高级设置重建参数
    # 开启：重试按当前配置重新构建 args
    # 关闭：使用添加任务时固化的参数
    retryUseCurrentSettings = ConfigItem(
        "FFmpeg", "RetryUseCurrentSettings", True, BoolValidator(), restart=False
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
    # 硬件编码器平台（macOS 固定为 Apple，其他系统为 NVIDIA/Intel/AMD）
    _is_macos = sys.platform == "darwin"
    ffmpegHardWareVideoCodecPlatform = OptionsConfigItem(
        "FFmpeg",
        "HardWareVideoCodecPlatform",
        "Apple" if _is_macos else "NVIDIA",
        OptionsValidator(["Apple"] if _is_macos else ["NVIDIA", "Intel", "AMD"]),
        restart=False,
    )
    # 硬件编码器（macOS 使用 VideoToolbox，其他系统使用 NVENC/QSV/AMF）
    ffmpegHardWareVideoCodec = OptionsConfigItem(
        "FFmpeg",
        "HardWareVideoCodec",
        "h264_videotoolbox" if _is_macos else "h264_nvenc",
        OptionsValidator(
            ["h264_videotoolbox", "hevc_videotoolbox", "av1_videotoolbox"]
            if _is_macos
            else [
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
        "libmp3lame",
        OptionsValidator(["libmp3lame", "aac", "libopus", "copy"]),
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

    # 图片质量（-q:v，数值越小质量越高，仅对 jpeg/webp 等有损格式生效）
    ffmpegImageQuality = OptionsConfigItem(
        "FFmpeg",
        "ImageQuality",
        "5",
        OptionsValidator(["2", "5", "10", "15"]),
        restart=False,
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

    # 工具页：音频提取格式（按格式标识持久化，与 _FORMATS 顺序解耦）
    toolAudioExtractFormat = OptionsConfigItem(
        "Tool",
        "AudioExtractFormat",
        "MP3",
        OptionsValidator(["MP3", "AAC", "WAV", "OPUS", "VORBIS", "FLAC"]),
        restart=False,
    )
    # 工具页：音频提取码率（留空=默认，仅对有损格式生效）
    toolAudioExtractBitrate = ConfigItem(
        "Tool", "AudioExtractBitrate", "", restart=False
    )

    # 工具页：视频截图（时间点留空=截首帧）
    toolVideoSnapshotTime = ConfigItem("Tool", "VideoSnapshotTime", "", restart=False)
    toolVideoSnapshotFormat = OptionsConfigItem(
        "Tool",
        "VideoSnapshotFormat",
        "PNG",
        OptionsValidator(["PNG", "JPG", "WEBP"]),
        restart=False,
    )

    # 工具页：GIF 制作
    toolGifMakeStart = ConfigItem("Tool", "GifMakeStart", "", restart=False)
    toolGifMakeDuration = ConfigItem("Tool", "GifMakeDuration", "", restart=False)
    toolGifMakeWidth = OptionsConfigItem(
        "Tool",
        "GifMakeWidth",
        "480",
        OptionsValidator(["480", "640", "320", "origin"]),
        restart=False,
    )
    toolGifMakeFps = OptionsConfigItem(
        "Tool",
        "GifMakeFps",
        15,
        OptionsValidator([10, 15, 20, 24]),
        restart=False,
    )

    # 工具页：视频剪切
    toolVideoCutStart = ConfigItem("Tool", "VideoCutStart", "", restart=False)
    toolVideoCutDuration = ConfigItem("Tool", "VideoCutDuration", "", restart=False)
    toolVideoCutMode = OptionsConfigItem(
        "Tool",
        "VideoCutMode",
        "copy",
        OptionsValidator(["copy", "accurate"]),
        restart=False,
    )

    # 工具页：音视频格式转换
    toolMediaConvertPreset = OptionsConfigItem(
        "Tool",
        "MediaConvertPreset",
        "MP4_H264",
        OptionsValidator(["MP4_H264", "MP4_H265", "MKV_H264", "WEBM_VP9", "MOV_H264"]),
        restart=False,
    )

    # 工具页：图片格式转换
    toolImageConvertFormat = OptionsConfigItem(
        "Tool",
        "ImageConvertFormat",
        "JPG",
        OptionsValidator(["JPG", "PNG", "WEBP", "BMP"]),
        restart=False,
    )
    toolImageConvertQuality = ConfigItem(
        "Tool", "ImageConvertQuality", "", restart=False
    )

    # 工具页：视频拼接
    toolVideoConcatMode = OptionsConfigItem(
        "Tool",
        "VideoConcatMode",
        "av",
        OptionsValidator(["av", "video"]),
        restart=False,
    )

    # 工具页：字幕处理
    toolSubtitleMode = OptionsConfigItem(
        "Tool",
        "SubtitleMode",
        "extract",
        OptionsValidator(["extract", "burn", "embed", "convert"]),
        restart=False,
    )
    toolSubtitleConvertFormat = OptionsConfigItem(
        "Tool",
        "SubtitleConvertFormat",
        "SRT",
        OptionsValidator(["SRT", "ASS", "VTT"]),
        restart=False,
    )

    # 工具页：音量归一化
    toolLoudnormMode = OptionsConfigItem(
        "Tool",
        "LoudnormMode",
        "loudnorm",
        OptionsValidator(["loudnorm", "dynaudnorm"]),
        restart=False,
    )
    toolLoudnormTarget = ConfigItem("Tool", "LoudnormTarget", "-16", restart=False)

    # 工具页：速度调整
    toolSpeedFactor = ConfigItem("Tool", "SpeedFactor", "2.0", restart=False)
    toolSpeedMode = OptionsConfigItem(
        "Tool",
        "SpeedMode",
        "av",
        OptionsValidator(["av", "video", "audio"]),
        restart=False,
    )


cfg = Config()
cfg.themeMode.value = Theme.AUTO
qconfig.load(str(CONFIG_FILE.absolute()), cfg)

# MSIX 环境下旧配置可能指向不存在的路径，启动时自动修正
if IS_MS_STORE_VERSION and not Path(cfg.get(cfg.ffmpegPath)).exists():
    cfg.set(cfg.ffmpegPath, get_default_exe_path("ffmpeg"))
