from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # 文件菜单
        self.fileMenu = self.addMenu("文件(&F)")
        self.openFileAct = QAction("打开文件", shortcut="Ctrl+O", parent=self)
        self.settingsAct = QAction(
            "设置", shortcuts=QKeySequence.StandardKey.Preferences, parent=self
        )
        self.closeWindowAct = QAction("关闭窗口", shortcut="Ctrl+W", parent=self)
        self.fileMenu.addActions([self.openFileAct, self.settingsAct])
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeWindowAct)

        # 帮助菜单
        self.helpMenu = self.addMenu("帮助(&H)")
        self.checkUpdateAct = QAction("检查更新", parent=self)
        self.githubAct = QAction("GitHub 仓库", parent=self)
        self.feedbackAct = QAction("问题反馈", parent=self)
        self.ffmpegAct = QAction("FFmpeg 官网", parent=self)
        self.helpMenu.addActions(
            [self.checkUpdateAct, self.githubAct, self.feedbackAct]
        )
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.ffmpegAct)
