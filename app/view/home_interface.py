# from ..common.signal_bus import signalBus
# from ..common.icon import Logo

from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QVBoxLayout, QWidget

from libs.qfluentwidgets_pro import DropAnyWidget, ScrollArea

from ..common.config import cfg
from ..common.event_bus import event_bus
from ..common.setting import AUDIO_CONTAINERS, VIDEO_CONTAINERS
from ..common.text import Text


class HomeInterface(ScrollArea):
    """Home interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.globalText = Text()
        self.view = QWidget(self)
        self.mainLayout = QVBoxLayout(self.view)
        self.media_containers = VIDEO_CONTAINERS | AUDIO_CONTAINERS

        # Drop
        self.Drop = DropAnyWidget()
        drop_extensions = "*" + ";*".join(self.media_containers)
        self.Drop.setFileExtensions(
            extensions=drop_extensions, name=self.globalText.MediaFiles
        )
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
        self.Drop.selectionChange.connect(self.extractPaths)
        self.Drop.draggedChange.connect(self.extractPaths)

    def extractPaths(self, paths, recursive=None):
        """
        遍历用户选择的文件和文件夹
        """
        # print(paths)
        recursive = cfg.get(cfg.homeRecursive)
        video_set = set()
        audio_set = set()

        for path_str in paths:
            path = Path(path_str)

            if not path.exists():
                continue

            if path.is_file() and path.suffix.lower() in VIDEO_CONTAINERS:
                video_set.add(path)
            elif path.is_file() and path.suffix.lower() in AUDIO_CONTAINERS:
                audio_set.add(path)
            elif path.is_dir():
                # 遍历文件夹
                if recursive:
                    # 递归遍历所有子文件夹
                    for item in path.rglob("*"):
                        if item.is_file() and item.suffix.lower() in VIDEO_CONTAINERS:
                            video_set.add(item)
                        elif item.is_file() and item.suffix.lower() in AUDIO_CONTAINERS:
                            audio_set.add(item)
                else:
                    # 只遍历当前文件夹下的文件
                    for item in path.iterdir():
                        if item.is_file() and item.suffix.lower() in VIDEO_CONTAINERS:
                            video_set.add(item)
                        elif item.is_file() and item.suffix.lower() in AUDIO_CONTAINERS:
                            audio_set.add(item)

        # print(video_set)
        # print(audio_set)
        # 发送信号
        event_bus.addTaskSig.emit(video_set, audio_set)
