from PySide6.QtWidgets import QSystemTrayIcon

from libs.qfluentwidgets_pro import Action, SystemTrayMenu

from ..common.event_bus import event_bus
from ..common.text import Text


class SystemTrayIcon(QSystemTrayIcon):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setIcon(parent.windowIcon())
        self.globalText = Text()

        self.menu = SystemTrayMenu(parent=parent)
        self.menu.addActions(
            [
                Action(
                    self.globalText.ToggleWindow,
                    triggered=lambda: event_bus.appMessageSig.emit("switch"),
                ),
                Action(
                    self.globalText.Quit,
                    triggered=lambda: event_bus.forceQuitSig.emit(),
                ),
            ]
        )
        self.setContextMenu(self.menu)
