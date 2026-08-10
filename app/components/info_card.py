import os
import sys

from PySide6.QtCore import QProcess, QSize, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QApplication, QHBoxLayout, QVBoxLayout

from libs.qfluentwidgets_pro import (
    BodyLabel,
    FluentIcon,
    HyperlinkLabel,
    ImageLabel,
    InfoBadge,
    LuminaPushButton,
    MessageBox,
    PrimaryPushButton,
    SimpleCardWidget,
    TitleLabel,
    TransparentToolButton,
    VerticalSeparator,
    setFont,
)

from ..common.event_bus import event_bus
from ..common.icon import Logo
from ..common.logger import LOG_FOLDER
from ..common.setting import (
    CONFIG_FILE,
    FFMPEG_WEBSITE,
    GITHUB_URL,
    OFFICIAL_WEBSITE,
    UPDATE_TIME,
    VERSION,
)
from ..common.text import Text
from ..common.utils import safeRemoveFile
from .statistic_widget import StatisticsWidget


class EasyFFmpegInfoCard(SimpleCardWidget):
    """Easy FFmpeg information card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.globalText = Text()
        self.setBorderRadius(8)
        self.iconLabel = ImageLabel(
            QIcon(":/app/images/logo.png").pixmap(120, 120), self
        )

        self.nameLabel = TitleLabel("Easy FFmpeg", self)
        self.updateButton = PrimaryPushButton(self.globalText.Update, self)
        self.companyLabel = HyperlinkLabel(
            QUrl("https://space.bilibili.com/499929312"),
            "Baby2016",
            self,
        )

        self.versionWidget = StatisticsWidget(
            self.globalText.Version, "v" + VERSION, self
        )
        self.updateTimeWidget = StatisticsWidget(
            self.globalText.UpdateTime, UPDATE_TIME, self
        )
        self.logSizeWidget = StatisticsWidget(
            self.globalText.LogUsage, self._formatLogSize(self._getLogSize()), self
        )

        self.descriptionLabel = BodyLabel(self.globalText.AppDescription, self)

        self.ffmpegButton = LuminaPushButton(Logo.FFMPEG, "FFmpeg")
        self.testButton = PrimaryPushButton(self.globalText.Test)

        self.clearffmpegButton = TransparentToolButton(FluentIcon.DELETE, self)
        self.clearffmpegButton.setToolTip(self.globalText.ClearLogsToolTip)
        self.resetButton = TransparentToolButton(FluentIcon.SYNC, self)
        self.resetButton.setToolTip(self.globalText.ResetSettingsToolTip)
        self.websiteButton = TransparentToolButton(FluentIcon.GLOBE, self)
        self.websiteButton.setToolTip(self.globalText.WebsiteToolTip)
        self.githubButton = TransparentToolButton(FluentIcon.GITHUB, self)
        self.githubButton.setToolTip(self.globalText.GitHubToolTip)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.topLayout = QHBoxLayout()
        self.statisticsLayout = QHBoxLayout()
        self.buttonLayout = QHBoxLayout()

        self.__initWidgets()
        self.__connectSignalToSlot()

    def __initWidgets(self):
        self.iconLabel.setBorderRadius(8, 8, 8, 8)
        self.iconLabel.scaledToWidth(120)

        self.updateButton.setFixedWidth(160)

        self.descriptionLabel.setWordWrap(True)
        # self.githubButton.clicked.connect(lambda: openUrl(DEPLOY_URL))

        # self.tagButton.setCheckable(False)
        # setFont(self.tagButton, 12)
        # self.tagButton.setFixedSize(80, 32)

        self.websiteButton.setFixedSize(32, 32)
        self.websiteButton.setIconSize(QSize(14, 14))
        self.githubButton.setFixedSize(32, 32)
        self.githubButton.setIconSize(QSize(14, 14))

        self.clearffmpegButton.setFixedSize(32, 32)
        self.clearffmpegButton.setIconSize(QSize(14, 14))
        self.resetButton.setFixedSize(32, 32)
        self.resetButton.setIconSize(QSize(14, 14))

        setFont(self.ffmpegButton, 12)
        self.ffmpegButton.setFixedHeight(32)

        self.nameLabel.setObjectName("nameLabel")
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.initLayout()

    def initLayout(self):
        self.hBoxLayout.setSpacing(30)
        self.hBoxLayout.setContentsMargins(34, 24, 24, 24)
        self.hBoxLayout.addWidget(self.iconLabel)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)

        # name label and install button
        self.vBoxLayout.addLayout(self.topLayout)
        self.topLayout.setContentsMargins(0, 0, 0, 0)
        self.topLayout.addWidget(self.nameLabel)
        self.topLayout.addWidget(self.updateButton, 0, Qt.AlignRight)

        # company label
        self.vBoxLayout.addSpacing(3)
        self.vBoxLayout.addWidget(self.companyLabel)

        # statistics widgets
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addLayout(self.statisticsLayout)
        self.statisticsLayout.setContentsMargins(0, 0, 0, 0)
        self.statisticsLayout.setSpacing(10)
        self.statisticsLayout.addWidget(self.versionWidget)
        self.statisticsLayout.addWidget(VerticalSeparator())
        self.statisticsLayout.addWidget(self.updateTimeWidget)
        self.statisticsLayout.addWidget(VerticalSeparator())
        self.statisticsLayout.addWidget(self.logSizeWidget)
        self.statisticsLayout.setAlignment(Qt.AlignLeft)

        # description label
        self.vBoxLayout.addSpacing(20)
        self.vBoxLayout.addWidget(self.descriptionLabel)

        # button
        self.vBoxLayout.addSpacing(12)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.buttonLayout)
        self.buttonLayout.addWidget(self.ffmpegButton, 0, Qt.AlignLeft)
        # self.buttonLayout.addWidget(self.testButton, 0, Qt.AlignLeft)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.clearffmpegButton, 0, Qt.AlignRight)
        self.buttonLayout.addWidget(self.resetButton, 0, Qt.AlignRight)
        self.buttonLayout.addWidget(self.githubButton, 0, Qt.AlignRight)
        self.buttonLayout.addWidget(self.websiteButton, 0, Qt.AlignRight)

    def __connectSignalToSlot(self):
        self.ffmpegButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(FFMPEG_WEBSITE))
        )
        self.updateButton.clicked.connect(lambda: event_bus.checkUpdateSig.emit())
        self.clearffmpegButton.clicked.connect(self.__onClearLogClicked)
        self.resetButton.clicked.connect(self.__onResetClicked)
        self.githubButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(GITHUB_URL))
        )
        self.websiteButton.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(OFFICIAL_WEBSITE))
        )
        event_bus.checkUpdateStateChanged.connect(
            lambda busy: (
                self.updateButton.setEnabled(not busy),
                self.updateButton.setText(
                    self.globalText.Checking if busy else self.globalText.Update
                ),
            )
        )
        # 新版本检测到时在更新按钮上显示版本号徽标
        self.updateBadge = InfoBadge.error("", parent=self, target=self.updateButton)
        self.updateBadge.hide()
        event_bus.newVersionDetected.connect(self._onNewVersionDetected)
        # 任务失败或应用出错时会写入日志，刷新日志占用大小
        event_bus.finishTaskSig.connect(
            lambda _id, ok, _log: self._refreshLogSize() if not ok else None
        )
        event_bus.appErrorSig.connect(lambda _msg: self._refreshLogSize())

    def _onNewVersionDetected(self, version: str):
        """新版本检测到时在更新按钮上显示版本号徽标"""
        if version:
            self.updateBadge.setText(version)
            self.updateBadge.setFixedSize(self.updateBadge.sizeHint())
            if self.updateBadge.manager:
                self.updateBadge.move(self.updateBadge.manager.position())
            self.updateBadge.show()
        else:
            self.updateBadge.hide()

    def _getLogSize(self) -> int:
        """计算 LOG_FOLDER 下所有 .log 文件的总大小（字节）"""
        if not LOG_FOLDER.exists():
            return 0
        return sum(f.stat().st_size for f in LOG_FOLDER.rglob("*.log") if f.is_file())

    def _formatLogSize(self, size: int) -> str:
        """将字节数格式化为人类可读的字符串（B/KB/MB/GB/TB）"""
        if size < 1024:
            return f"{size} B"
        for unit in ["KB", "MB", "GB", "TB"]:
            size /= 1024
            if size < 1024:
                return f"{size:.1f} {unit}"
        return f"{size:.1f} TB"

    def _refreshLogSize(self):
        """重新计算并刷新日志占用大小显示"""
        self.logSizeWidget.valueLabel.setText(self._formatLogSize(self._getLogSize()))

    def __onClearLogClicked(self):
        """清空所有日志文件"""
        size_str = self._formatLogSize(self._getLogSize())
        w = MessageBox(
            self.globalText.ClearLogs,
            self.globalText.ClearLogsConfirm.format(size_str),
            self.window(),
        )
        if not w.exec():
            return

        from ..common.application import SingletonApplication
        from ..common.logger import Logger, closeLogger

        # 只关闭 application logger 释放句柄，其他被占用的直接跳过
        closeLogger("application")

        cleared = 0
        failed = 0
        for log_file in LOG_FOLDER.rglob("*.log"):
            if safeRemoveFile(str(log_file)):
                cleared += 1
            else:
                failed += 1

        # 重建 application logger，恢复正常写入
        SingletonApplication.logger = Logger("application")

        # 刷新日志占用大小显示
        self._refreshLogSize()

        msg = self.globalText.LogsCleared.format(cleared)
        if failed:
            msg += self.globalText.LogsSkipped.format(failed)
        event_bus.notification_service.show_success(self.globalText.Done, msg)

    def __onResetClicked(self):
        """重置所有设置并重启"""
        w = MessageBox(
            self.globalText.ResetSettings,
            self.globalText.ResetSettingsConfirm,
            self.window(),
        )
        if not w.exec():
            return

        # 删除配置文件，让下次启动使用默认值
        safeRemoveFile(str(CONFIG_FILE))

        self.__restartApplication()

    def __restartApplication(self):
        """重启应用程序（兼容源码运行和 Nuitka 打包）"""
        main_window = self.window()

        # 标记主窗口真正退出，避免最小化到托盘
        if main_window is not None:
            main_window._really_quit = True
            # 立即隐藏托盘图标
            if hasattr(main_window, "systemTrayIcon"):
                try:
                    main_window.systemTrayIcon.hide()
                except Exception:
                    pass

            # 等待版本检查线程结束，避免 QThread 销毁时仍在运行导致崩溃
            if (
                hasattr(main_window, "_versionThread")
                and main_window._versionThread is not None
            ):
                thread = main_window._versionThread
                if thread.isRunning():
                    thread.terminate()

        # 在应用真正退出后再启动新实例，避免单例共享内存 / 本地套接字冲突
        # （Nuitka 打包后尤其需要这个时序）
        QApplication.instance().aboutToQuit.connect(self.__spawnNewInstance)
        QApplication.instance().exit(0)

    def __spawnNewInstance(self):
        """启动新的应用实例"""
        if getattr(sys, "frozen", False) or "__compiled__" in globals():
            program = os.path.abspath(sys.argv[0])
            args = sys.argv[1:]
        else:
            # 源码运行
            program = sys.executable
            args = [os.path.abspath(sys.argv[0])] + sys.argv[1:]
        QProcess.startDetached(program, args)
