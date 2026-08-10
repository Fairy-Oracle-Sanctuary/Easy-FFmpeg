import shutil
import subprocess

from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QFileDialog, QWidget

from libs.qfluentwidgets_pro import (
    ComboBoxSettingCard,
    Dialog,
    ExpandLayout,
    InfoBadge,
    InfoBadgePosition,
    PrimaryPushSettingCard,
    PushSettingCard,
    ScrollArea,
    Signal,
    SwitchSettingCard,
    TitleLabel,
    setFont,
    setTheme,
    setThemeColor,
)
from libs.qfluentwidgets_pro import FluentIcon as FIF
from libs.qfluentwidgets_pro import SettingCardGroup as CardGroup
from libs.qfluentwidgets_pro.qframelesswindow.utils import getSystemAccentColor

from ..common.config import cfg, get_default_exe_path, isWin11
from ..common.event_bus import event_bus
from ..common.icon import Logo
from ..common.setting import COPYLEFT, TEAM, VERSION, YEAR
from ..common.text import Text
from ..components.config_card import DetectionCard


class ExeDetectThread(QThread):
    """通过执行 version 命令检测可执行文件是否可用（macOS app bundle 内的文件无法用 exists 判断）"""

    detected = Signal(str, bool)  # exe_path, success

    def __init__(self, exe_path: str, version_flag: str = "-version"):
        super().__init__()
        self.exe_path = exe_path
        self.version_flag = version_flag

    def run(self):
        try:
            result = subprocess.run(
                [self.exe_path, self.version_flag],
                capture_output=True,
                timeout=10,
                check=False,
                creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
            )
            print(result.stdout.decode("utf-8"))
            print(result.stderr.decode("utf-8"))
            self.detected.emit(self.exe_path, result.returncode == 0)
        except (FileNotFoundError, subprocess.TimeoutExpired, TimeoutError, OSError):
            self.detected.emit(self.exe_path, False)


class SettingCardGroup(CardGroup):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        setFont(self.titleLabel, 14, QFont.Weight.DemiBold)


class SettingInterface(ScrollArea):
    """Setting interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.globalText = Text()
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        # setting label
        self.settingLabel = TitleLabel(self.globalText.Settings, self)

        # 软件
        self.softwareGroup = SettingCardGroup(
            self.globalText.Software, self.scrollWidget
        )
        self.homeRecursiveCard = SwitchSettingCard(
            FIF.FOLDER,
            self.globalText.HomeRecursive,
            self.globalText.HomeRecursiveDesc,
            cfg.homeRecursive,
            self.softwareGroup,
        )
        self.retryUseCurrentSettingsCard = SwitchSettingCard(
            FIF.SYNC,
            self.globalText.RetryUseCurrentSettings,
            self.globalText.RetryUseCurrentSettingsDesc,
            cfg.retryUseCurrentSettings,
            self.softwareGroup,
        )
        self.autoCleanLogsCard = SwitchSettingCard(
            FIF.BROOM,
            self.globalText.AutoCleanLogs,
            self.globalText.AutoCleanLogsDesc,
            cfg.autoCleanLogs,
            self.softwareGroup,
        )
        self.logRetentionCard = ComboBoxSettingCard(
            cfg.logRetentionDays,
            FIF.HISTORY,
            self.globalText.LogRetentionDays,
            self.globalText.LogRetentionDaysDesc,
            [
                self.globalText.NDays.format(7),
                self.globalText.NDays.format(14),
                self.globalText.NDays.format(30),
                self.globalText.NDays.format(90),
            ],
            self.softwareGroup,
        )

        # 个性化
        self.personalGroup = SettingCardGroup(
            self.globalText.Personalization, self.scrollWidget
        )
        self.micaCard = SwitchSettingCard(
            FIF.TRANSPARENT,
            self.globalText.MicaEffect,
            self.globalText.MicaEffectDesc,
            cfg.micaEnabled,
            self.personalGroup,
        )
        self.themeCard = ComboBoxSettingCard(
            cfg.themeMode,
            FIF.BRUSH,
            self.globalText.ApplicationTheme,
            self.globalText.AAA,
            texts=[
                self.globalText.Light,
                self.globalText.Dark,
                self.globalText.FollowSystem,
            ],
            parent=self.personalGroup,
        )
        self.accentColorCard = ComboBoxSettingCard(
            cfg.accentColor,
            FIF.PALETTE,
            self.globalText.ThemeColor,
            self.globalText.AdjustThemeColor,
            texts=[self.globalText.SeafoamGreen, self.globalText.FollowSystem],
            parent=self.personalGroup,
        )
        self.zoomCard = ComboBoxSettingCard(
            cfg.dpiScale,
            FIF.ZOOM,
            self.globalText.InterfaceScaling,
            self.globalText.ACAFS,
            texts=[
                "100%",
                "125%",
                "150%",
                "175%",
                "200%",
                self.globalText.FollowSystem,
            ],
            parent=self.personalGroup,
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FIF.LANGUAGE,
            self.globalText.Language,
            self.globalText.SetInterfaceLanguage,
            texts=[
                "简体中文",
                "繁體中文",
                "English",
                "日本語",
                "한국어",
                "Français",
                "Deutsch",
                "Español",
                "Português",
                "Русский",
                "Italiano",
                "Nederlands",
                "Polski",
                "Türkçe",
                "Tiếng Việt",
                "ไทย",
                "Bahasa Indonesia",
                "हिन्दी",
                "العربية",
                "Afrikaans",
                "አማርኛ",
                "Azərbaycanca",
                "Беларуская",
                "Български",
                "বাংলা",
                "Bosanski",
                "Català",
                "Čeština",
                "Cymraeg",
                "Dansk",
                "Ελληνικά",
                "Eesti",
                "Euskara",
                "فارسی",
                "Suomi",
                "Gaeilge",
                "Galego",
                "ગુજરાતી",
                "עברית",
                "Hrvatski",
                "Magyar",
                "Հայերեն",
                "Íslenska",
                "ქართული",
                "Қазақша",
                "ខ្មែរ",
                "ಕನ್ನಡ",
                "Lietuvių",
                "Latviešu",
                "Македонски",
                "മലയാളം",
                "Монгол",
                "मराठी",
                "Bahasa Melayu",
                "မြန်မာ",
                "Norsk bokmål",
                "नेपाली",
                "Norsk nynorsk",
                "ਪੰਜਾਬੀ",
                "Português (Portugal)",
                "Română",
                "සිංහල",
                "Slovenčina",
                "Slovenščina",
                "Shqip",
                "Српски",
                "Svenska",
                "Kiswahili",
                "தமிழ்",
                "తెలుగు",
                "Тоҷикӣ",
                "Tagalog",
                "Українська",
                "اردو",
                "Oʻzbekcha",
                "繁體中文（香港）",
                self.globalText.FollowSystem,
            ],
            parent=self.personalGroup,
        )
        self.closeDirectlyCard = SwitchSettingCard(
            FIF.CLOSE,
            self.globalText.CloseDirectly,
            self.globalText.EODDC,
            configItem=cfg.closeDirectly,
            parent=self.personalGroup,
        )

        # exe
        self.exeGroup = SettingCardGroup(self.globalText.Rely, self.scrollWidget)
        self.ffmpegPathCard = PushSettingCard(
            self.globalText.SelectFile,
            Logo.FFMPEG,
            "FFmpeg",
            cfg.get(cfg.ffmpegPath),
            self.exeGroup,
        )
        self.detectionCard = DetectionCard(
            FIF.SEARCH, self.globalText.DetectPrograms, self.globalText.ADAUPP
        )

        # 关于
        self.aboutGroup = SettingCardGroup(self.globalText.About, self.scrollWidget)
        self.aboutCard = PrimaryPushSettingCard(
            self.globalText.CheckForUpdates,
            ":/app/images/logo.png",
            self.globalText.About,
            COPYLEFT
            + self.globalText.Copyleft
            + f" {YEAR}, {TEAM}. "
            + self.globalText.CurrentVersion
            + " v"
            + VERSION,
            self.aboutGroup,
        )
        self.updateOnStartUpCard = SwitchSettingCard(
            FIF.UPDATE,
            self.globalText.CheckUpdateAtStartUp,
            self.globalText.CheckUpdateAtStartUpDesc,
            configItem=cfg.checkUpdateAtStartUp,
            parent=self.aboutGroup,
        )
        self._initWidget()

    def _initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 90, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        # initialize style sheet
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.enableTransparentBackground()

        self.micaCard.setEnabled(isWin11())

        # initialize layout
        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.settingLabel.move(36, 40)

        self.softwareGroup.addSettingCard(self.homeRecursiveCard)
        self.softwareGroup.addSettingCard(self.retryUseCurrentSettingsCard)
        self.softwareGroup.addSettingCard(self.autoCleanLogsCard)
        self.softwareGroup.addSettingCard(self.logRetentionCard)

        self.personalGroup.addSettingCard(self.micaCard)
        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)
        self.personalGroup.addSettingCard(self.accentColorCard)
        self.personalGroup.addSettingCard(self.closeDirectlyCard)

        self.exeGroup.addSettingCard(self.ffmpegPathCard)
        self.exeGroup.addSettingCard(self.detectionCard)

        self.aboutGroup.addSettingCard(self.updateOnStartUpCard)

        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(26)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.softwareGroup)
        self.expandLayout.addWidget(self.personalGroup)
        self.expandLayout.addWidget(self.exeGroup)
        self.expandLayout.addWidget(self.aboutGroup)

        # adjust icon size
        # for card in self.findChildren(SettingCard):
        #     card.setIconSize(18, 18)

    def _showRestartTooltip(self):
        """show restart tooltip"""
        event_bus.notification_service.show_success(
            self.globalText.UpdateSuccessful, self.globalText.STEAR
        )

    def _onFFmpegPathCardClicked(self):
        path, _ = QFileDialog.getOpenFileName(self, self.globalText.SelectFfmpegFile)

        if not path or cfg.get(cfg.ffmpegPath) == path:
            return

        cfg.set(cfg.ffmpegPath, path)
        self.ffmpegPathCard.setContent(path)

    def _detectExe(self, exe_name, url, cfg_item, path_card, version_flag="-version"):
        """检测可执行文件：先 version 命令验证默认路径，失败再全局查找"""
        if not hasattr(self, "_pending_detects"):
            self._pending_detects = {}
            self._detect_threads = []

        exe_path_str = get_default_exe_path(exe_name)
        self._pending_detects[exe_path_str] = {
            "name": exe_name,
            "url": url,
            "cfg_item": cfg_item,
            "path_card": path_card,
            "tried_global": False,
        }
        self._startDetect(exe_path_str, version_flag)

    def _startDetect(self, exe_path_str, version_flag="-version"):
        thread = ExeDetectThread(exe_path_str, version_flag)
        thread.detected.connect(self._onExeDetected)
        self._detect_threads.append(thread)
        thread.start()

    def _onExeDetected(self, exe_path: str, success: bool):
        """ExeDetectThread 检测完成回调"""
        info = getattr(self, "_pending_detects", {}).pop(exe_path, None)
        if info is None:
            return

        if success:
            cfg.set(info["cfg_item"], exe_path)
            event_bus.notification_service.show_success(
                self.globalText.DetectionSuccessful,
                self.globalText.PathSetTo.format(info["name"], exe_path),
            )
            info["path_card"].setContent(exe_path)
        elif not info.get("tried_global"):
            # 默认路径检测失败，尝试全局查找
            found = shutil.which(info["name"])
            if found:
                info["tried_global"] = True
                self._pending_detects[found] = info
                self._startDetect(found)
                return
            self._showDownloadDialog(info)
        else:
            self._showDownloadDialog(info)

        # 所有检测完成后恢复按钮
        if not getattr(self, "_pending_detects", {}):
            self.detectionCard.openButton.setEnabled(True)
            self.detectionCard.openButton.setText(self.globalText.Detect)

    def _showDownloadDialog(self, info):
        dialog = Dialog(
            self.globalText.DetectionFailed,
            self.globalText.NotFoundDownloadIt.format(info["name"]),
            self,
        )
        dialog.yesButton.setText(self.globalText.GoToDownload)
        dialog.cancelButton.setText(self.globalText.Cancel)
        if dialog.exec():
            QDesktopServices.openUrl(QUrl(info["url"]))

    def _onDectectionCardClicked(self):
        self.detectionCard.openButton.setEnabled(False)
        self.detectionCard.openButton.setText(self.globalText.Detecting)

        # ffmpeg
        self._detectExe(
            "ffmpeg",
            "https://ffmpeg.org/download.html",
            cfg.ffmpegPath,
            self.ffmpegPathCard,
        )

    def _onAccentColorChanged(self):
        color = cfg.get(cfg.accentColor)
        if color != "Auto":
            setThemeColor(color, save=False)
        else:
            sysColor = getSystemAccentColor()
            if sysColor.isValid():
                setThemeColor(sysColor, save=False)
            else:
                setThemeColor(color, save=False)

    def _connectSignalToSlot(self):
        """绑定信号"""
        cfg.appRestartSig.connect(self._showRestartTooltip)

        # 个性化
        self.micaCard.checkedChanged.connect(event_bus.micaEnableChanged)
        cfg.themeChanged.connect(setTheme)
        cfg.accentColor.valueChanged.connect(self._onAccentColorChanged)

        self.ffmpegPathCard.clicked.connect(self._onFFmpegPathCardClicked)
        self.detectionCard.openButton.clicked.connect(self._onDectectionCardClicked)

        # 检查更新
        self.aboutCard.clicked.connect(event_bus.checkUpdateSig)
        event_bus.checkUpdateStateChanged.connect(
            lambda busy: (
                self.aboutCard.button.setEnabled(not busy),
                self.aboutCard.button.setText(
                    self.globalText.Checking
                    if busy
                    else self.globalText.CheckForUpdates
                ),
            )
        )
        # 新版本检测到时在检查更新按钮上显示版本号徽标
        self.aboutBadge = InfoBadge.error(
            "",
            parent=self.aboutCard,
            target=self.aboutCard.button,
            position=InfoBadgePosition.TOP_LEFT,
        )
        self.aboutBadge.hide()
        event_bus.newVersionDetected.connect(self._onNewVersionDetected)

        # 日志自动清理：关闭时禁用保留天数选项
        self.autoCleanLogsCard.checkedChanged.connect(
            lambda checked: self.logRetentionCard.setEnabled(checked)
        )
        self.logRetentionCard.setEnabled(cfg.get(cfg.autoCleanLogs))

    def _onNewVersionDetected(self, version: str):
        """新版本检测到时在检查更新按钮上显示版本号徽标"""
        if version:
            self.aboutBadge.setText(version)
            self.aboutBadge.setFixedSize(self.aboutBadge.sizeHint())
            if self.aboutBadge.manager:
                self.aboutBadge.move(self.aboutBadge.manager.position())
            self.aboutBadge.show()
        else:
            self.aboutBadge.hide()
