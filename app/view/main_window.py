import sys

from PySide6.QtCore import QUrl
from PySide6.QtGui import QDesktopServices, QIcon
from PySide6.QtWidgets import QApplication

from app.common.event_bus import event_bus
from app.common.setting import RELEASE_URL
from app.common.text import Text
from app.components.infobar import NotificationService
from app.service.version_service import VersionService
from app.view.home_interface import HomeInterface
from app.view.setting_interface import SettingInterface  # noqa
from libs.qfluentwidgets_pro import FluentIcon as FIF
from libs.qfluentwidgets_pro import (
    InfoBarPosition,
    MessageBox,
    TopFluentWindow,
    TopNavigationItemPosition,
)


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

        # 可以自定义配置（可选）
        self.notification_service.set_default_duration(3000)
        self.notification_service.set_position(InfoBarPosition.BOTTOM_RIGHT)
        event_bus.notification_service = self.notification_service

        self._initNavigation()

        self._connectSignalToSlot()

    def _initWindow(self):
        w, h = 680, 577
        self.resize(w, h if sys.platform == "win32" else h + 19)
        self.setMinimumWidth(w)
        self.setMinimumHeight(450)
        self.setWindowIcon(QIcon(":/app/images/logo.png"))
        self.setWindowTitle("Easy FFmpeg")

        desktop = QApplication.primaryScreen().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

    def _initNavigation(self):
        self.homeInterface = HomeInterface(self)
        self.settingInterface = SettingInterface(self)

        self.addSubInterface(
            self.homeInterface,
            FIF.HOME,
            "主页",
            TopNavigationItemPosition.LEFT,
            expanded=True,
        )
        self.addSubInterface(
            self.settingInterface,
            FIF.SETTING,
            "设置",
            TopNavigationItemPosition.RIGHT,
        )

    def _connectSignalToSlot(self):
        """连接信号到槽"""
        event_bus.checkUpdateSig.connect(self.checkUpdate)

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

    def checkUpdate(self):
        if self.versionManager.hasNewVersion():
            self.showMessageBox(
                self.globalText.NewVersionDetected,
                self.globalText.NewVersion
                + f" {self.versionManager.lastestVersion} "
                + self.globalText.ADYWTDI,
                True,
                lambda: QDesktopServices.openUrl(QUrl(RELEASE_URL)),
            )
        else:
            self.showMessageBox(
                self.globalText.NoNewVersion,
                self.globalText.FKWIUTD,
            )
