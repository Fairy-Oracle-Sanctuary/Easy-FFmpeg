import json
import re
import urllib.request

from PySide6.QtCore import QVersionNumber

from ..common.setting import VERSION


class VersionService:
    """Version service"""

    def __init__(self):
        self.currentVersion = VERSION
        self.lastestVersion = VERSION
        self.versionPattern = re.compile(r"v(\d+)\.(\d+)\.(\d+)")

    def getLatestVersion(self):
        """get latest version"""
        url = "https://api.github.com/repos/Fairy-Oracle-Sanctuary/Easy-FFmpeg/releases/latest"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Edg/112.0.1722.64"
        }

        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=5) as response:
                data = json.loads(response.read().decode("utf-8"))

            # parse version
            version = data["tag_name"]  # type:str
            match = self.versionPattern.search(version)
            if not match:
                return VERSION

            self.lastestVersion = version[1:]
            return self.lastestVersion
        except Exception as e:
            print(f"Error getting latest version: {e}")

    def hasNewVersion(self) -> bool:
        """check whether there is a new version"""
        version = QVersionNumber.fromString(self.getLatestVersion())
        currentVersion = QVersionNumber.fromString(self.currentVersion)
        return version > currentVersion
