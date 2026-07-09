# coding:utf-8
# from ..common.signal_bus import signalBus
# from ..common.icon import Logo
import shutil
import subprocess
import sys
from pathlib import Path

from datetime import datetime

from PySide6.QtCore import Qt, QThread, QUrl
from PySide6.QtGui import QDesktopServices, QFont
from PySide6.QtWidgets import QFileDialog, QWidget

from libs.qfluentwidgets_pro import (
    ComboBoxSettingCard,
    Dialog,
    ExpandLayout,
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

from ..common.config import cfg, get_default_exe_path
from ..common.event_bus import event_bus
from ..common.setting import COPYLEFT, TEAM, VERSION, YEAR
from ..common.text import Text
from ..components.config_card import DetectionCard
from ..service.ffmpeg_scanner import FFmpegScanResult, FFmpegScanThread


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

        # 个性化
        self.personalGroup = SettingCardGroup(
            self.globalText.Personalization, self.scrollWidget
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
            texts=["简体中文", "English", self.globalText.FollowSystem],
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
        self.exeGroup = SettingCardGroup(self.globalText.Download, self.scrollWidget)
        self.ffmpegPathCard = PushSettingCard(
            self.globalText.SelectFile,
            ":/app/images/logo/FFmpeg.svg",
            "FFmpeg",
            cfg.get(cfg.ffmpegPath),
            self.exeGroup,
        )
        self.detectionCard = DetectionCard(
            FIF.SEARCH, self.globalText.DetectPrograms, self.globalText.FFmpegScanTooltip
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
        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 90, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)
        self.setObjectName("settingInterface")

        # initialize style sheet
        setFont(self.settingLabel, 23, QFont.Weight.DemiBold)
        self.enableTransparentBackground()

        # initialize layout
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 40)

        self.personalGroup.addSettingCard(self.themeCard)
        self.personalGroup.addSettingCard(self.zoomCard)
        self.personalGroup.addSettingCard(self.languageCard)
        self.personalGroup.addSettingCard(self.accentColorCard)
        self.personalGroup.addSettingCard(self.closeDirectlyCard)

        self.exeGroup.addSettingCard(self.ffmpegPathCard)
        self.exeGroup.addSettingCard(self.detectionCard)

        self.aboutGroup.addSettingCard(self.aboutCard)

        # add setting card group to layout
        self.expandLayout.setSpacing(26)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
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
        if sys.platform == "win32":
            filter_str = "ffmpeg.exe (*.exe)"
        else:
            filter_str = "ffmpeg (*)"
        path, _ = QFileDialog.getOpenFileName(
            self, self.globalText.SelectFfmpegFile, filter=filter_str
        )

        if not path or cfg.get(cfg.ffmpegPath) == path:
            return

        cfg.set(cfg.ffmpegPath, path)
        self.ffmpegPathCard.setContent(path)

    def _detectExe(self, exe_name, url, cfg_item, path_card, version_flag="-version"):
        exe_path_str = get_default_exe_path(exe_name)
        exe_path = Path(exe_path_str)

        if sys.platform == "darwin":
            # macOS: app bundle 内的文件无法用 exists判断，通过 version 命令检测
            exe_path_str = str(exe_path)
            if not hasattr(self, "_pending_detects"):
                self._pending_detects = {}
                self._detect_threads = []
            self._pending_detects[exe_path_str] = {
                "name": exe_name,
                "url": url,
                "cfg_item": cfg_item,
                "path_card": path_card,
            }
            thread = ExeDetectThread(exe_path_str, version_flag)
            thread.detected.connect(self._onExeDetected)
            self._detect_threads.append(thread)
            thread.start()
        else:
            # Windows / Linux: 使用 exists + which 回退
            if not exe_path.exists() and sys.platform == "win32":
                exe_path_str = shutil.which(exe_name)
                if exe_path_str:
                    exe_path = Path(exe_path_str)
                else:
                    exe_path = None

            if exe_path is not None:
                cfg.set(cfg_item, str(exe_path))
                event_bus.notification_service.show_success(
                    self.globalText.DetectionSuccessful,
                    self.globalText.PathSetTo.format(exe_name, str(exe_path)),
                )
                path_card.setContent(str(exe_path))
            else:
                dialog = Dialog(
                    self.globalText.DetectionFailed,
                    self.globalText.NotFoundDownloadIt.format(exe_name),
                    self,
                )
                dialog.yesButton.setText(self.globalText.GoToDownload)
                dialog.cancelButton.setText(self.globalText.Cancel)
                if dialog.exec():
                    QDesktopServices.openUrl(QUrl(url))

    def _onExeDetected(self, exe_path: str, success: bool):
        """macOS ExeDetectThread 检测完成回调"""
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
        else:
            dialog = Dialog(
                self.globalText.DetectionFailed,
                self.globalText.NotFoundDownloadIt.format(info["name"]),
                self,
            )
            dialog.yesButton.setText(self.globalText.GoToDownload)
            dialog.cancelButton.setText(self.globalText.Cancel)
            if dialog.exec():
                QDesktopServices.openUrl(QUrl(info["url"]))

        # 所有检测完成后恢复按钮
        if not getattr(self, "_pending_detects", {}):
            self.detectionCard.openButton.setEnabled(True)
            self.detectionCard.openButton.setText(self.globalText.Detect)

    def _onDectectionCardClicked(self):
        self.detectionCard.openButton.setEnabled(False)
        self.detectionCard.openButton.setText(self.globalText.Detecting)

        # 断开旧线程连接（如有）
        if hasattr(self, "_ffmpeg_scan_thread") and self._ffmpeg_scan_thread:
            try:
                self._ffmpeg_scan_thread.progress.disconnect()
                self._ffmpeg_scan_thread.finished.disconnect()
            except (TypeError, RuntimeError):
                pass
            try:
                self._ffmpeg_scan_thread.quit()
                self._ffmpeg_scan_thread.wait(1000)
            except RuntimeError:
                pass
            self._ffmpeg_scan_thread = None

        # 启动全面扫描线程
        self._ffmpeg_scan_thread = FFmpegScanThread(parent=self)
        self._ffmpeg_scan_thread.progress.connect(self._onFFmpegScanProgress)
        self._ffmpeg_scan_thread.finished.connect(self._onFFmpegScanFinished)
        self._ffmpeg_scan_thread.finished.connect(self._ffmpeg_scan_thread.deleteLater)
        self._ffmpeg_scan_thread.start()

    def _onFFmpegScanProgress(self, message: str):
        """扫描进度更新"""
        self.detectionCard.openButton.setText(message)

    def _onFFmpegScanFinished(self, result: FFmpegScanResult):
        """扫描完成回调"""
        self.detectionCard.openButton.setEnabled(True)
        self.detectionCard.openButton.setText(self.globalText.Detect)

        if not result.available:
            # 未找到 FFmpeg
            dialog = Dialog(
                self.globalText.DetectionFailed,
                self.globalText.NotFoundDownloadIt.format("ffmpeg"),
                self,
            )
            dialog.yesButton.setText(self.globalText.GoToDownload)
            dialog.cancelButton.setText(self.globalText.Cancel)
            if dialog.exec():
                QDesktopServices.openUrl(QUrl("https://ffmpeg.org/download.html"))
            return

        # 保存扫描结果到配置
        cfg.set(cfg.ffmpegPath, result.ffmpeg_path)
        cfg.set(cfg.ffmpegVersion, result.version)
        cfg.set(cfg.ffmpegHasNvenc, result.has_nvenc)
        cfg.set(cfg.ffmpegHasQsv, result.has_qsv)
        cfg.set(cfg.ffmpegHasVideotoolbox, result.has_videotoolbox)
        cfg.set(cfg.ffmpegHasAmf, result.has_amf)
        cfg.set(cfg.ffmpegHwaccels, ", ".join(result.hwaccels))
        cfg.set(cfg.ffmpegEncoders, ", ".join(sorted(result.encoders)))
        cfg.set(
            cfg.ffmpegLastScanTime,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        )

        # 更新 UI
        self.ffmpegPathCard.setContent(result.ffmpeg_path)

        # 构建成功通知消息
        hwaccel_parts = []
        if result.has_nvenc:
            hwaccel_parts.append("NVIDIA NVENC")
        if result.has_qsv:
            hwaccel_parts.append("Intel QSV")
        if result.has_videotoolbox:
            hwaccel_parts.append("VideoToolbox")
        if result.has_amf:
            hwaccel_parts.append("AMD AMF")

        version_msg = self.globalText.FFmpegVersionDetected.format(result.version)
        if hwaccel_parts:
            hwaccel_msg = self.globalText.FFmpegHwaccelDetected.format(
                ", ".join(hwaccel_parts)
            )
            msg = f"{version_msg}\n{hwaccel_msg}"
        else:
            msg = f"{version_msg}\n{self.globalText.FFmpegNoHwaccel}"

        event_bus.notification_service.show_success(
            self.globalText.FFmpegScanDone,
            msg,
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
        cfg.themeChanged.connect(setTheme)
        cfg.accentColor.valueChanged.connect(self._onAccentColorChanged)

        self.ffmpegPathCard.clicked.connect(self._onFFmpegPathCardClicked)
        self.detectionCard.openButton.clicked.connect(self._onDectectionCardClicked)

        # 检查更新
        self.aboutCard.clicked.connect(event_bus.checkUpdateSig)
