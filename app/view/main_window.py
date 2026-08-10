import sys

from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QSystemTrayIcon,
)

from app.common.event_bus import event_bus
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
    MessageBoxBase,
    ProgressBar,
    SubtitleLabel,
    TextBrowser,
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
    IS_MS_STORE_VERSION,
    MS_STORE_URL,
    VIDEO_CONTAINERS,
)
from ..common.utils import openUrl
from ..components.menu_bar import MenuBar
from ..components.system_tray_icon import SystemTrayIcon
from ..service.version_service import VersionCheckThread
from ..view.advance_interface import AdvanceInterface
from ..view.more_interface import MoreInterface


class UpdateDialog(MessageBoxBase):
    """更新对话框 - 显示更新日志并下载安装包（参考 Fairy-Kekkai-Workshop）

    - 商店版（IS_MS_STORE_VERSION=True）：仅提供"前往下载"按钮，跳转浏览器
    - 非商店版：内嵌进度条，首次点击开始下载，下载完成后转为"打开文件夹"
    """

    def __init__(self, version_service, version: str, notes: str, parent=None):
        super().__init__(parent)
        self.globalText = Text()
        self.versionService = version_service
        self.version = version
        self.notes = notes
        self.downloadThread = None
        self.filepath = ""
        self._downloading = False
        self._downloaded = False

        self.setup_ui()

    def setup_ui(self):
        self.titleLabel = SubtitleLabel(
            self.globalText.NewVersionAvailable.format(self.version), self
        )
        self.viewLayout.setSpacing(12)
        self.viewLayout.addWidget(self.titleLabel)

        # 更新日志（TextBrowser 渲染 Markdown）
        self.textBrowser = TextBrowser(self)
        self.textBrowser.setMarkdown(self.notes)
        self.textBrowser.setOpenExternalLinks(True)
        self.textBrowser.setMinimumWidth(420)
        self.textBrowser.setMaximumHeight(280)
        self.viewLayout.addWidget(self.textBrowser)

        # 进度条（仅非商店版下载时显示）
        self.progressBar = ProgressBar(self)
        self.progressBar.setVisible(False)
        self.viewLayout.addWidget(self.progressBar)

        # 商店版只能跳转浏览器，非商店版可直接下载安装包
        self.yesButton.setText(
            self.globalText.GoToDownload
            if IS_MS_STORE_VERSION
            else self.globalText.DownloadInstaller
        )
        self.cancelButton.setText(self.globalText.Close)
        self.widget.setMinimumWidth(480)
        self.widget.setMinimumHeight(350)

    def accept(self):
        """重写接受方法：商店版跳转浏览器；非商店版首次点击开始下载，再次点击打开文件夹"""
        if self._downloading:
            return  # 下载进行中，忽略点击

        if IS_MS_STORE_VERSION:
            QDesktopServices.openUrl(QUrl(MS_STORE_URL))
            super().accept()
            return

        if self._downloaded:
            # 已下载完成，打开文件夹并关闭
            VersionService.openFolder(self.filepath)
            super().accept()
            return

        # 非商店版：开始下载
        self._start_download()

    def _start_download(self):
        """开始下载安装包"""
        self._downloading = True
        self.yesButton.setEnabled(False)
        self.yesButton.setText(self.globalText.Downloading)
        self.cancelButton.setEnabled(False)
        self.progressBar.setVisible(True)
        self.progressBar.setValue(0)

        self.downloadThread, self.filepath = self.versionService.createDownloadThread()
        self.downloadThread.progress.connect(self._on_progress)
        self.downloadThread.succeeded.connect(self._on_finished)
        self.downloadThread.error.connect(self._on_error)
        # 连接 QThread 内置 finished 信号，在线程完全结束后安全清理
        self.downloadThread.finished.connect(self._on_thread_finished)
        self.downloadThread.start()

    def _on_progress(self, downloaded, total):
        if total > 0:
            self.progressBar.setValue(int(downloaded * 100 / total))

    def _on_finished(self, filepath):
        """下载成功（线程即将结束，但尚未完全退出）"""
        self.progressBar.setValue(100)
        self.yesButton.setText(self.globalText.OpenFolder)
        self.yesButton.setEnabled(True)
        self.cancelButton.setEnabled(True)
        self._downloading = False
        self._downloaded = True
        self.textBrowser.append(self.globalText.InstallerDownloadedTo.format(filepath))
        # 自动打开文件夹
        VersionService.openFolder(filepath)

    def _on_error(self, error_msg):
        """下载失败（线程即将结束，但尚未完全退出）"""
        self.progressBar.setVisible(False)
        self.yesButton.setEnabled(True)
        self.yesButton.setText(self.globalText.DownloadInstaller)
        self.cancelButton.setEnabled(True)
        self._downloading = False
        self.textBrowser.append(self.globalText.DownloadFailed.format(error_msg))

    def _on_thread_finished(self):
        """QThread 内置 finished 信号：线程已完全停止，可安全释放引用"""
        if self.downloadThread is not None:
            self.downloadThread.deleteLater()
            self.downloadThread = None

    def reject(self):
        """重写拒绝方法：下载进行中时不允许关闭"""
        if self._downloading:
            return
        super().reject()


class MainWindow(TopFluentWindow):
    def __init__(self):
        super().__init__()
        self.globalText = Text()

        # 初始化窗口
        self._initWindow()

        # 初始化版本服务
        self.versionManager = VersionService()
        self._versionThread = None

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
        self.moreInterface = MoreInterface(self)
        self.settingInterface = SettingInterface(self)

        self.addSubInterface(
            self.homeInterface,
            FIF.HOME,
            self.globalText.Home,
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.taskItem = self.addSubInterface(
            self.taskInterface,
            FIF.MEDIA,
            self.globalText.Task,
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.addSubInterface(
            self.advanceInterface,
            FIF.BOOK_SHELF,
            self.globalText.Advance,
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.addSubInterface(
            self.moreInterface,
            FIF.MORE,
            self.globalText.More,
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            self.globalText.Settings,
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
        event_bus.forceQuitSig.connect(self.forceQuit)
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
        self.themeButton.clicked.connect(lambda: toggleTheme(save=True))
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
            lambda hasNew, ver, notes: self._onVersionChecked(
                hasNew, ver, notes, silent
            )
        )
        self._versionThread.start()

    def _onVersionChecked(self, hasNewVersion, latestVersion, releaseNotes, silent):
        event_bus.checkUpdateStateChanged.emit(False)
        event_bus.newVersionDetected.emit(latestVersion if hasNewVersion else "")
        if hasNewVersion:
            notes = self._parseReleaseNotes(releaseNotes)
            dialog = UpdateDialog(self.versionManager, latestVersion, notes, self)
            dialog.exec()
        elif not silent:
            self.showMessageBox(
                self.globalText.NoNewVersion,
                self.globalText.FKWIUTD,
            )

    def _parseReleaseNotes(self, notes: str) -> str:
        """截掉下载及之后的内容，只保留新增/改进/修复"""
        if not notes:
            return self.globalText.NoReleaseNotes
        idx = notes.find("## 下载")
        if idx != -1:
            notes = notes[:idx].strip()
        return notes

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

        filters = (
            self.globalText.MediaFiles
            + " (*"
            + " *".join(VIDEO_CONTAINERS | AUDIO_CONTAINERS)
            + ")"
        )
        paths, _ = QFileDialog.getOpenFileNames(
            self, self.globalText.OpenFile, "", filters
        )
        if not paths:
            return
        self._handleFileArgs(paths)

    def _handleFileArgs(self, paths: list):
        """处理右键菜单传入的文件路径"""
        from pathlib import Path

        from ..common.utils import classifyMediaPaths

        file_paths = [Path(p) for p in paths if p]
        video, audio, image = classifyMediaPaths(file_paths, cfg.get(cfg.homeRecursive))
        if video or audio or image:
            event_bus.addTaskSig.emit(video, audio, image)
            self.switchTo(self.taskInterface)
            self.show()
            self.raise_()

    def onError(self, message: str):
        """系统错误消息"""
        QApplication.clipboard().setText(message)
        self.showMessageBox(
            self.globalText.UnhandledException,
            self.globalText.UnhandledExceptionDesc,
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
        if getattr(self, "_really_quit", False) or cfg.get(cfg.closeDirectly):
            event.accept()
            self.onExit()
        else:
            event.ignore()
            self.hide()
            self.systemTrayIcon.showMessage(
                "Easy-FFmpeg",
                self.globalText.MinimizedToTray,
                QIcon(":/app/images/logo.png"),
            )

    def onExit(self):
        """exit main window"""
        self.systemTrayIcon.hide()

    def forceQuit(self):
        """真正退出程序（供托盘菜单、重置重启等调用）"""
        self._really_quit = True
        if (
            getattr(self, "_versionThread", None) is not None
            and self._versionThread.isRunning()
        ):
            self._versionThread.terminate()
        QApplication.instance().exit(0)
