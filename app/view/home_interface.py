# coding:utf-8
# from ..common.signal_bus import signalBus
# from ..common.icon import Logo

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from libs.qfluentwidgets_pro import DropSingleFileWidget, ScrollArea

from ..common.text import Text


class HomeInterface(ScrollArea):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.globalText = Text()
        self.view = QWidget(self)
        self.mainLayout = QVBoxLayout(self.view)

        # Drop
        self.Drop = DropSingleFileWidget()
        # self.Drop.setMinimumHeight(120)
        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("homeInterface")

        # initialize style sheet
        self.enableTransparentBackground()

        # initialize layout
        self.__initLayout()

        self._connectSignalToSlot()

    def __initLayout(self):
        # add setting card group to layout
        self.mainLayout.setContentsMargins(36, 36, 36, 36)
        self.mainLayout.addWidget(self.Drop)

    def _connectSignalToSlot(self):
        self.Drop.selectionChange.connect(self.test)
        self.Drop.draggedChange.connect(self.test)

    def test(self, files):
        print(files)
