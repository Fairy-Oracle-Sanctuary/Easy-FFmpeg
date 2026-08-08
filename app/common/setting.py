import os
import sys
from pathlib import Path

AUTHOR = "baby2016"
TEAM = "天机阁(Fairy-Oracle-Sanctuary)"
VERSION = "0.5.0"
YEAR = "2026"
UPDATE_TIME = "2026-8-8"
if sys.platform == "win32":
    COPYLEFT = "🄯 "
else:
    COPYLEFT = "©️ "

RELEASE_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases"
GITHUB_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg"
FEEDBACK_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/issues"
OFFICIAL_WEBSITE = ""
FFMPEG_WEBSITE = "https://ffmpeg.org/"

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

if __name__ == "__main__":
    print(VIDEO_CONTAINERS | AUDIO_CONTAINERS)
