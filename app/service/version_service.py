import json
import os
import platform
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

from PySide6.QtCore import QThread, QVersionNumber, Signal

from ..common.setting import VERSION


class DownloadThread(QThread):
    """安装包下载线程（使用标准库 urllib，避免引入 requests 依赖）"""

    progress = Signal(int, int)  # downloaded, total
    succeeded = Signal(str)  # filepath
    error = Signal(str)

    def __init__(self, url, filepath, parent=None):
        super().__init__(parent)
        self.url = url
        self.filepath = filepath
        self._cancel = False

    def cancel(self):
        """请求取消下载"""
        self._cancel = True

    def run(self):
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
            request = urllib.request.Request(self.url, headers=headers)
            # urlopen 默认跟随 301/302/303 重定向，GitHub Release 下载会跳转到 CDN
            with urllib.request.urlopen(request, timeout=30) as response:
                total = int(response.headers.get("Content-Length", 0))
                downloaded = 0
                with open(self.filepath, "wb") as f:
                    while True:
                        if self._cancel:
                            break
                        chunk = response.read(65536)
                        if not chunk:
                            break
                        f.write(chunk)
                        downloaded += len(chunk)
                        self.progress.emit(downloaded, total)

            if self._cancel:
                # 清理未完成的文件
                try:
                    os.remove(self.filepath)
                except OSError:
                    pass
                return

            self.succeeded.emit(self.filepath)
        except Exception as e:
            self.error.emit(str(e))


class VersionService:
    """Version service"""

    GITHUB_API = "https://api.github.com/repos/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/latest"
    RELEASE_BASE = (
        "https://github.com/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/download"
    )

    def __init__(self):
        self.currentVersion = VERSION
        self.lastestVersion = VERSION
        self.releaseNotes = ""
        self.versionPattern = re.compile(r"v(\d+)\.(\d+)\.(\d+)")
        self._releaseInfo = None

    def _fetchReleaseInfo(self):
        """获取并缓存 GitHub release 信息"""
        if self._releaseInfo is not None:
            return self._releaseInfo

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        try:
            request = urllib.request.Request(self.GITHUB_API, headers=headers)
            with urllib.request.urlopen(request, timeout=5) as response:
                self._releaseInfo = json.loads(response.read().decode("utf-8"))
        except Exception as e:
            print(f"Error fetching release info: {e}")
        return self._releaseInfo

    def getLatestVersion(self):
        """get latest version"""
        info = self._fetchReleaseInfo()
        if not info:
            return VERSION

        version = info.get("tag_name", "")
        match = self.versionPattern.search(version)
        if not match:
            return VERSION

        self.lastestVersion = version[1:]
        self.releaseNotes = info.get("body", "")
        return self.lastestVersion

    def hasNewVersion(self) -> bool:
        """check whether there is a new version"""
        version = QVersionNumber.fromString(self.getLatestVersion())
        currentVersion = QVersionNumber.fromString(self.currentVersion)
        return version > currentVersion

    def getDefaultDownloadUrl(self):
        """根据平台和架构构建默认安装包下载 URL"""
        version = self.lastestVersion
        base = f"{self.RELEASE_BASE}/v{version}"
        if sys.platform == "win32":
            return f"{base}/Easy-FFmpeg-v{version}-Windows-x86_64-Setup.exe"
        if sys.platform == "darwin":
            return f"{base}/Easy-FFmpeg-v{version}-macOS-x86_64.dmg"
        # Linux：按架构选择 deb 包
        machine = platform.machine().lower()
        if machine in ("aarch64", "arm64"):
            return f"{base}/Easy-FFmpeg-v{version}-Linux-aarch64.deb"
        return f"{base}/Easy-FFmpeg-v{version}-Linux-x86_64.deb"

    def getDownloadDir(self):
        """获取下载目录"""
        if sys.platform == "win32":
            downloads = Path.home() / "Downloads"
            if downloads.exists():
                return downloads / "EasyFFmpeg"
        return Path(tempfile.gettempdir()) / "EasyFFmpeg"

    def createDownloadThread(self, url=None):
        """创建下载线程

        Returns:
            (DownloadThread, filepath)
        """
        if url is None:
            url = self.getDefaultDownloadUrl()

        download_dir = self.getDownloadDir()
        download_dir.mkdir(parents=True, exist_ok=True)

        filename = url.split("/")[-1] or "Easy-FFmpeg-Setup.exe"
        filepath = str(download_dir / filename)

        thread = DownloadThread(url, filepath)
        return thread, filepath

    @staticmethod
    def openFolder(filepath):
        """在文件管理器中打开文件所在目录"""
        try:
            if sys.platform == "win32":
                subprocess.Popen(f'explorer /select,"{filepath}"')
            elif sys.platform == "darwin":
                subprocess.Popen(["open", "-R", filepath])
            else:
                subprocess.Popen(["xdg-open", str(Path(filepath).parent)])
        except Exception as e:
            print(f"Error opening folder: {e}")


class VersionCheckThread(QThread):
    """后台检查版本更新，避免阻塞 UI"""

    finished = Signal(bool, str, str)  # hasNewVersion, latestVersion, releaseNotes

    def __init__(self, versionService: VersionService, parent=None):
        super().__init__(parent)
        self.versionService = versionService

    def run(self):
        hasNew = self.versionService.hasNewVersion()
        self.finished.emit(
            hasNew, self.versionService.lastestVersion, self.versionService.releaseNotes
        )
