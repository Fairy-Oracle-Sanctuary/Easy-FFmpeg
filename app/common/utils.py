import os
import re
import sys
from json import loads
from pathlib import Path

from PySide6.QtCore import QDir, QFile, QFileInfo, QProcess, QRunnable, QUrl
from PySide6.QtGui import QDesktopServices


def adjustFileName(name: str):
    """adjust file name

    Returns
    -------
    name: str
        file name after adjusting
    """
    name = re.sub(r'[\\/:*?"<>|\r\n\s]+', "_", name.strip()).strip()
    return name.rstrip(".")


def readFile(filePath: str):
    """load json data from file"""
    file = QFile(filePath)
    file.open(QFile.OpenModeFlag.ReadOnly)
    data = str(file.readAll(), encoding="utf-8")
    file.close()
    return data


def loadJsonData(filePath):
    """load json data from file"""
    return loads(readFile(filePath))


def safeRemoveFile(filePath) -> bool:
    """安全删除文件（跨平台），仅在文件存在时删除"""
    path = Path(filePath)
    if not path.is_file():
        return False
    try:
        os.remove(str(path))
        return True
    except OSError:
        return False


def classifyMediaPaths(paths, recursive=False):
    """将路径列表分类为视频集合、音频集合和图片集合

    Parameters
    ----------
    paths : list[str]
        文件/文件夹路径列表
    recursive : bool
        是否递归遍历文件夹

    Returns
    -------
    tuple[set[Path], set[Path], set[Path]]
        (视频文件集合, 音频文件集合, 图片文件集合)
    """
    from .setting import AUDIO_CONTAINERS, IMAGE_CONTAINERS, VIDEO_CONTAINERS

    video_set = set()
    audio_set = set()
    image_set = set()

    for path_str in paths:
        path = Path(path_str)
        if not path.exists():
            continue
        if path.is_file():
            suffix = path.suffix.lower()
            if suffix in VIDEO_CONTAINERS:
                video_set.add(path)
            elif suffix in AUDIO_CONTAINERS:
                audio_set.add(path)
            elif suffix in IMAGE_CONTAINERS:
                image_set.add(path)
        elif path.is_dir():
            iterator = path.rglob("*") if recursive else path.iterdir()
            for item in iterator:
                if not item.is_file():
                    continue
                suffix = item.suffix.lower()
                if suffix in VIDEO_CONTAINERS:
                    video_set.add(item)
                elif suffix in AUDIO_CONTAINERS:
                    audio_set.add(item)
                elif suffix in IMAGE_CONTAINERS:
                    image_set.add(item)

    return video_set, audio_set, image_set


class DeleteFileWorker(QRunnable):
    """异步删除文件"""

    def __init__(self, filePath):
        super().__init__()
        self.filePath = filePath

    def run(self):
        safeRemoveFile(self.filePath)


def openUrl(url):
    if not url.startswith("http"):
        if not os.path.exists(url):
            return False

        QDesktopServices.openUrl(QUrl.fromLocalFile(url))
    else:
        QDesktopServices.openUrl(QUrl(url))

    return True


def showInFolder(path):
    """show file in file explorer"""
    if not os.path.exists(path):
        return False

    if isinstance(path, Path):
        path = str(path.absolute())

    if not path or path.lower().startswith("http"):
        return False

    info = QFileInfo(path)  # type:QFileInfo
    if sys.platform == "win32":
        args = [QDir.toNativeSeparators(path)]
        if not info.isDir():
            args.insert(0, "/select,")

        QProcess.startDetached("explorer", args)
    elif sys.platform == "darwin":
        args = [
            "-e",
            'tell application "Finder"',
            "-e",
            "activate",
            "-e",
            f'select POSIX file "{path}"',
            "-e",
            "end tell",
            "-e",
            "return",
        ]
        QProcess.execute("/usr/bin/osascript", args)
    else:
        url = QUrl.fromLocalFile(path if info.isDir() else info.path())
        QDesktopServices.openUrl(url)

    return True


def runProcess(executable, args=None, timeout=5000, cwd=None) -> str:
    process = QProcess()

    if cwd:
        process.setWorkingDirectory(str(cwd))

    process.start(str(executable).replace("\\", "/"), args or [])
    process.waitForFinished(timeout)
    return process.readAllStandardOutput().toStdString()


def runDetachedProcess(executable, args=None, cwd=None):
    process = QProcess()

    if cwd:
        process.setWorkingDirectory(str(cwd))

    process.startDetached(str(executable).replace("\\", "/"), args or [])


def getSystemProxy():
    """get system proxy"""
    if sys.platform == "win32":
        try:
            import winreg

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Internet Settings",
            ) as key:
                enabled, _ = winreg.QueryValueEx(key, "ProxyEnable")

                if enabled:
                    return "http://" + winreg.QueryValueEx(key, "ProxyServer")
        except:
            pass
    elif sys.platform == "darwin":
        s = os.popen("scutil --proxy").read()
        info = dict(re.findall(r"(?m)^\s+([A-Z]\w+)\s+:\s+(\S+)", s))

        if info.get("HTTPEnable") == "1":
            return f"http://{info['HTTPProxy']}:{info['HTTPPort']}"
        elif info.get("ProxyAutoConfigEnable") == "1":
            return info["ProxyAutoConfigURLString"]

    return os.environ.get("http_proxy")
