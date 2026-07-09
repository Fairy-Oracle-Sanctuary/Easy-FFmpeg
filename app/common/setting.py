# coding: utf-8
import sys
from pathlib import Path

AUTHOR = "baby2016"
TEAM = "天机阁(Fairy-Oracle-Sanctuary)"
VERSION = "1.0.0"
YEAR = "2026"
UPDATE_TIME = "2026-6-30"
if sys.platform == "win32":
    COPYLEFT = "🄯 "
else:
    COPYLEFT = "©️ "

RELEASE_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases"
GITHUB_URL = "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg"

CONFIG_FOLDER = Path("AppData").absolute()

CONFIG_FILE = CONFIG_FOLDER / "config.json"
DB_PATH = CONFIG_FOLDER / "database.db"


if sys.platform == "win32":
    EXE_SUFFIX = ".exe"
else:
    EXE_SUFFIX = ""
