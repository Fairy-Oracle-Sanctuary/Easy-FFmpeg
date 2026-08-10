from PySide6.QtGui import QAction, QKeySequence
from PySide6.QtWidgets import QMenuBar

from ..common.text import Text


class MenuBar(QMenuBar):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.globalText = Text()

        # 文件菜单
        self.fileMenu = self.addMenu(self.globalText.FileMenu)
        self.openFileAct = QAction(
            self.globalText.OpenFile, shortcut="Ctrl+O", parent=self
        )
        self.settingsAct = QAction(
            self.globalText.Settings,
            shortcuts=QKeySequence.StandardKey.Preferences,
            parent=self,
        )
        self.closeWindowAct = QAction(
            self.globalText.CloseWindow, shortcut="Ctrl+W", parent=self
        )
        self.fileMenu.addActions([self.openFileAct, self.settingsAct])
        self.fileMenu.addSeparator()
        self.fileMenu.addAction(self.closeWindowAct)

        # 帮助菜单
        self.helpMenu = self.addMenu(self.globalText.HelpMenu)
        self.checkUpdateAct = QAction(self.globalText.CheckForUpdates, parent=self)
        self.githubAct = QAction(self.globalText.GitHubToolTip, parent=self)
        self.feedbackAct = QAction(self.globalText.Feedback, parent=self)
        self.ffmpegAct = QAction(self.globalText.FfmpegWebsite, parent=self)
        self.helpMenu.addActions(
            [self.checkUpdateAct, self.githubAct, self.feedbackAct]
        )
        self.helpMenu.addSeparator()
        self.helpMenu.addAction(self.ffmpegAct)
