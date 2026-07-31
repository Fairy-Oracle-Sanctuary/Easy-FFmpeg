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

    # exe
    ffmpegPath = ConfigItem("FFmpeg", "FFmpegPath", get_default_exe_path("ffmpeg"))

    # home
    homeRecursive = ConfigItem(
        "Home", "Recursive", False, BoolValidator(), restart=False
    )


cfg = Config()
cfg.themeMode.value = Theme.LIGHT
qconfig.load(str(CONFIG_FILE.absolute()), cfg)
