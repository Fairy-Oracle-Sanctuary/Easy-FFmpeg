import os
import sys
from pathlib import Path

AUTHOR = "baby2016"
TEAM = "天机阁(Fairy-Oracle-Sanctuary)"
VERSION = "1.0.0"
YEAR = "2026"
UPDATE_TIME = "2026-8-15"
if sys.platform == "win32":
    COPYLEFT = "🄯 "
else:
    COPYLEFT = "©️ "

RELEASE_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases"
GITHUB_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg"
FEEDBACK_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/issues"
OFFICIAL_WEBSITE = ""
FFMPEG_WEBSITE = "https://ffmpeg.org/"

# 是否为微软商店版本（商店版不允许内置下载安装包功能，只能跳转浏览器）
IS_MS_STORE_VERSION = False
MS_STORE_URL = ""

# 统一放用户目录，避免权限问题和路径漂移
if sys.platform == "win32":
    CONFIG_FOLDER = Path(os.environ.get("APPDATA", str(Path.home()))) / "EasyFFmpeg"
elif sys.platform == "darwin":
    CONFIG_FOLDER = Path.home() / "Library" / "Application Support" / "EasyFFmpeg"
else:
    CONFIG_FOLDER = Path.home() / ".config" / "EasyFFmpeg"

CONFIG_FILE = CONFIG_FOLDER / "config.json"
DB_PATH = CONFIG_FOLDER / "database.db"


if sys.platform == "win32":
    EXE_SUFFIX = ".exe"
else:
    EXE_SUFFIX = ""

VIDEO_CONTAINERS = {
    # 主流格式
    ".mp4",
    ".mkv",
    ".avi",
    ".mov",
    ".wmv",
    ".flv",
    ".webm",
    ".m4v",
    ".mpg",
    ".mpeg",
    ".m2ts",
    ".mts",
    ".ts",
    ".vob",
    # 高清/蓝光
    ".m2v",
    ".3gp",
    ".3g2",
    # 其他常见
    ".ogv",
    ".rm",
    ".rmvb",
    ".asf",
    ".divx",
    ".xvid",
    ".f4v",
    ".swf",
    ".mjpeg",
    ".mjpg",
    # Apple生态
    ".dv",
    # 专业/广播级
    ".mxf",
    ".gxf",
}

AUDIO_CONTAINERS = {
    # 无损/高保真
    ".wav",
    ".aiff",
    ".flac",
    ".alac",
    ".dsd",
    ".dff",
    ".dsf",
    # 有损压缩
    ".mp3",
    ".aac",
    ".ogg",
    ".m4a",
    ".wma",
    ".opus",
    ".ac3",
    ".eac3",
    ".dts",
    ".truehd",
    # 其他
    ".amr",
    ".awb",
    ".ra",
    ".ram",
    ".voc",
    ".caf",
    ".ape",
    ".wv",
    ".tak",
    ".tta",
    # 低码率/语音
    ".gsm",
    ".dct",
    ".snd",
}

IMAGE_CONTAINERS = {
    # 主流格式
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    # 现代/高效格式（依赖 ffmpeg 编译支持）
    ".heic",
    ".heif",
    ".avif",
    # 其他常见
    ".ico",
    ".tga",
    ".psd",
    ".ppm",
    ".pgm",
    ".pbm",
    ".pnm",
    ".pcx",
}

SUBTITLE_CONTAINERS = {
    ".srt",
    ".ass",
    ".ssa",
    ".vtt",
    ".sub",
    ".sup",
    ".lrc",
}


def buildFileFilter(name: str, containers: set) -> str:
    """构建 QFileDialog 文件过滤器字符串

    Parameters
    ----------
    name : str
        过滤器显示名，如 "视频文件"
    containers : set
        容器扩展名集合（元素带前导点，如 ".mp4"），如 VIDEO_CONTAINERS
    """
    exts = " ".join(f"*{e}" for e in sorted(containers))
    return f"{name} ({exts})"


if __name__ == "__main__":
    print(VIDEO_CONTAINERS | AUDIO_CONTAINERS | IMAGE_CONTAINERS)
