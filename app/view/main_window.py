import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QApplication, QFileDialog, QSystemTrayIcon

from app.common.event_bus import event_bus
from app.common.setting import RELEASE_URL
from app.common.text import Text
from app.components.infobar import NotificationService
from app.service.version_service import VersionService
from app.view.home_interface import HomeInterface
from app.view.setting_interface import SettingInterface
from app.view.task_interface import TaskInterface
from libs.qfluentwidgets_pro import FluentIcon as FIF
from libs.qfluentwidgets_pro import (
    InfoBadge,
    InfoBadgePosition,
    InfoBarPosition,
    InfoLevel,
    MessageBox,
    Theme,
    TopFluentWindow,
    TopNavigationItemPosition,
    TransparentToolButton,
    isDarkTheme,
    qconfig,
    toggleTheme,
)

from ..common.config import cfg
from ..common.setting import (
    AUDIO_CONTAINERS,
    FEEDBACK_URL,
    FFMPEG_WEBSITE,
    GITHUB_URL,
    VIDEO_CONTAINERS,
)
from ..common.utils import openUrl
from ..components.menu_bar import MenuBar
from ..components.system_tray_icon import SystemTrayIcon
from ..service.version_service import VersionCheckThread
from ..view.advance_interface import AdvanceInterface


class MainWindow(TopFluentWindow):
    def __init__(self):
        super().__init__()
        self.globalText = Text()

        # 初始化窗口
        self._initWindow()

        # 初始化版本服务
        self.versionManager = VersionService()

        # 初始化通知服务
        self.notification_service = NotificationService(self)

        # 初始化系统托盘
        self.systemTrayIcon = SystemTrayIcon(self)

        # 可以自定义配置
        self.notification_service.set_default_duration(3000)
        self.notification_service.set_position(InfoBarPosition.BOTTOM_RIGHT)
        event_bus.notification_service = self.notification_service

        self._initNavigation()

        self._connectSignalToSlot()

        self._initMenuBar()

        self._initThemeButton()

        self.onInitFinished()

    def _initWindow(self):
        w, h = 680, 577
        self.resize(w, h if sys.platform == "win32" else h + 19)
        self.setMinimumWidth(w)
        self.setMinimumHeight(450)
        self.setWindowIcon(QIcon(":/app/images/logo.png"))
        self.setWindowTitle("Easy FFmpeg")

        self.setMicaEffectEnabled(cfg.get(cfg.micaEnabled))

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _initNavigation(self):
        self.homeInterface = HomeInterface(self)
        self.taskInterface = TaskInterface(self)
        self.advanceInterface = AdvanceInterface(self)
        self.settingInterface = SettingInterface(self)

        self.addSubInterface(
            self.homeInterface,
            FIF.HOME,
            "主页",
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.taskItem = self.addSubInterface(
            self.taskInterface,
            FIF.MEDIA,
            "任务",
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.addSubInterface(
            self.advanceInterface,
            FIF.BOOK_SHELF,
            "高级",
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            "设置",
            TopNavigationItemPosition.RIGHT,
            expanded=False,
        )

        self.taskBadge = InfoBadge.attension(
            "0",
            parent=self.navigationInterface,
            target=self.taskItem,
            position=InfoBadgePosition.TOP_NAVIGATION_ITEM,
        )
        self.taskBadge.setFixedSize(0, 0)
        self.taskBadge.setText("")

    def _connectSignalToSlot(self):
        """连接信号到槽"""
        event_bus.micaEnableChanged.connect(self.setMicaEffectEnabled)
        event_bus.checkUpdateSig.connect(self.checkUpdate)
        event_bus.taskCountChanged.connect(self._updateTaskBadge)
        event_bus.hasFailedTasks.connect(self._updateBadgeLevel)
        event_bus.appMessageSig.connect(self.onMessage)
        event_bus.appErrorSig.connect(self.onError)
        event_bus.trayMessageSig.connect(self._onTrayMessage)
        self.systemTrayIcon.messageClicked.connect(self.onSystemTrayMessageClicked)
        self.systemTrayIcon.activated.connect(self.onSystemTrayActivated)
        qconfig.themeChanged.connect(self._updateThemeButtonIcon)

    def _initMenuBar(self):
        """初始化 macOS 原生菜单栏"""
        if sys.platform != "darwin":
            return

        self.menuBar = MenuBar(self)
        self.menuBar.openFileAct.triggered.connect(self.openFile)
        self.menuBar.closeWindowAct.triggered.connect(self.close)
        self.menuBar.settingsAct.triggered.connect(
            lambda: self.switchTo(self.settingInterface)
        )
        self.menuBar.checkUpdateAct.triggered.connect(
            lambda: self.checkUpdate(silent=False)
        )
        self.menuBar.githubAct.triggered.connect(lambda: openUrl(GITHUB_URL))
        self.menuBar.feedbackAct.triggered.connect(lambda: openUrl(FEEDBACK_URL))
        self.menuBar.ffmpegAct.triggered.connect(lambda: openUrl(FFMPEG_WEBSITE))

    def _initThemeButton(self):
        """在标题栏最小化按钮左侧添加主题切换按钮"""
        if sys.platform == "darwin":
            return

        self.themeButton = TransparentToolButton(self.titleBar)
        # 与最小化按钮尺寸保持一致
        self.themeButton.setFixedSize(self.titleBar.minBtn.size())
        self.themeButton.clicked.connect(lambda: toggleTheme())
        self._updateThemeButtonIcon()
        # 插入到最小化按钮左侧（buttonLayout: minBtn, maxBtn, closeBtn）
        self.titleBar.buttonLayout.insertWidget(
            0, self.themeButton, 0, Qt.AlignmentFlag.AlignTop
        )

    def _updateThemeButtonIcon(self, theme: Theme = None):
        """根据当前主题更新按钮图标"""
        if sys.platform == "darwin":
            return

        # 深色模式显示太阳（切到浅色），浅色模式显示月亮（切到深色）
        self.themeButton.setIcon(FIF.BRIGHTNESS if isDarkTheme() else FIF.QUIET_HOURS)

    def onInitFinished(self):
        """初始化完成"""
        self.systemTrayIcon.show()
        if cfg.get(cfg.checkUpdateAtStartUp):
            self.checkUpdate(silent=True)
        # 处理右键菜单启动时传入的文件
        if len(sys.argv) > 1:
            self._handleFileArgs(sys.argv[1:])

    def _updateBadgeLevel(self, hasFailed: bool):
        """有失败任务时角标变橙色警告"""
        self.taskBadge.setLevel(InfoLevel.ERROR if hasFailed else InfoLevel.ATTENTION)

    def _updateTaskBadge(self, count: int):
        """更新任务数量角标"""
        if count > 0:
            self.taskBadge.setText(str(count))
            self.taskBadge.setFixedSize(self.taskBadge.sizeHint())
        else:
            self.taskBadge.setText("")
            self.taskBadge.setFixedSize(0, 0)
        # 尺寸变化后重新定位，修复首次显示时 y 轴偏移
        if self.taskBadge.manager:
            self.taskBadge.move(self.taskBadge.manager.position())

    def showMessageBox(
        self, title: str, content: str, showYesButton=False, yesSlot=None
    ):
        """show message box"""
        w = MessageBox(title, content, self)
        w.yesButton.setText(self.globalText.OK)
        w.cancelButton.setText(self.globalText.Close)
        if not showYesButton:
            w.cancelButton.setText(self.globalText.Close)
            w.yesButton.hide()
            w.buttonLayout.insertStretch(0, 1)

        if w.exec() and yesSlot is not None:
            yesSlot()

    def checkUpdate(self, silent=False):
        """检查更新，silent=True 时只在有新版本时提示"""
        event_bus.checkUpdateStateChanged.emit(True)
        self._versionThread = VersionCheckThread(self.versionManager, self)
        self._versionThread.finished.connect(
            lambda hasNew, ver: self._onVersionChecked(hasNew, ver, silent)
        )
        self._versionThread.start()

    def _onVersionChecked(self, hasNewVersion, latestVersion, silent):
        event_bus.checkUpdateStateChanged.emit(False)
        if hasNewVersion:
            self.showMessageBox(
                self.globalText.NewVersionDetected,
                self.globalText.NewVersion
                + f" {latestVersion} "
                + self.globalText.ADYWTDI,
                True,
                lambda: QDesktopServices.openUrl(QUrl(RELEASE_URL)),
            )
        elif not silent:
            self.showMessageBox(
                self.globalText.NoNewVersion,
                self.globalText.FKWIUTD,
            )

    def onMessage(self, message: str):
        """系统消息"""
        if message == "show":
            if self.windowState() & Qt.WindowMinimized:
                self.showNormal()
            else:
                self.show()
                self.raise_()
        elif message == "hide":
            self.hide()
        elif message == "switch":
            if self.isMinimized() or not self.isVisible():
                self.showNormal() if self.isMinimized() else self.show()
                self.raise_()
                self.activateWindow()
            else:
                self.hide()
        elif message:
            # 右键菜单传入的文件路径（换行分隔）
            self._handleFileArgs(message.split("\n"))

    def openFile(self):
        """打开文件对话框，选择媒体文件添加到任务"""

        filters = "媒体文件 (*" + " *".join(VIDEO_CONTAINERS | AUDIO_CONTAINERS) + ")"
        paths, _ = QFileDialog.getOpenFileNames(self, "打开文件", "", filters)
        if not paths:
            return
        self._handleFileArgs(paths)

    def _handleFileArgs(self, paths: list):
        """处理右键菜单传入的文件路径"""
        from pathlib import Path

        from ..common.utils import classifyMediaPaths

        file_paths = [Path(p) for p in paths if p]
        video, audio = classifyMediaPaths(file_paths, cfg.get(cfg.homeRecursive))
        if video or audio:
            event_bus.addTaskSig.emit(video, audio)
            self.switchTo(self.taskInterface)
            self.show()
            self.raise_()

    def onError(self, message: str):
        """系统错误消息"""
        QApplication.clipboard().setText(message)
        self.showMessageBox(
            "发生未处理异常",
            "报错信息已写入系统粘贴板和日志文件，是否立即反馈？",
            True,
            lambda: openUrl(FEEDBACK_URL),
        )

    def _onTrayMessage(self, title: str, message: str, msg_type: str):
        """显示系统托盘消息"""
        icon = (
            QSystemTrayIcon.MessageIcon.Warning
            if msg_type == "warning"
            else QSystemTrayIcon.MessageIcon.Information
        )
        self.systemTrayIcon.showMessage(title, message, icon)

    def onSystemTrayMessageClicked(self):
        """系统托盘消息点击"""
        self.onMessage("show")

    def onSystemTrayActivated(self, reason: QSystemTrayIcon.ActivationReason):
        """系统托盘点击事件"""
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.onMessage("show")

    def closeEvent(self, event):
        if cfg.get(cfg.closeDirectly):
            event.accept()
            self.onExit()
        else:
            event.ignore()
            self.hide()
            self.systemTrayIcon.showMessage(
                "Easy-FFmpeg",
                "程序已最小化到系统托盘",
                QIcon(":/app/images/logo.png"),
            )

    def onExit(self):
        """exit main window"""
        self.systemTrayIcon.hide()
