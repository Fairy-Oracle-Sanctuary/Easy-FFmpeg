from PySide6.QtWidgets import QApplication, QSystemTrayIcon

from libs.qfluentwidgets_pro import Action, SystemTrayMenu

from ..common.event_bus import event_bus


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(parent.windowIcon())

        self.menu = SystemTrayMenu(parent=parent)
        self.menu.addActions(
            [
                Action(
                    "显示/隐藏窗口",
                    triggered=lambda: event_bus.appMessageSig.emit("switch"),
                ),
                Action("退出", triggered=lambda: event_bus.forceQuitSig.emit()),
            ]
        )
        self.setContextMenu(self.menu)
