from enum import Enum
from pathlib import Path

from PySide6.QtCore import QFileInfo, Qt, Signal
from PySide6.QtGui import QColor, QFont, QPainter, QPen
from PySide6.QtWidgets import QFileIconProvider, QHBoxLayout, QVBoxLayout
import time

from libs.qfluentwidgets_pro import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    CheckBox,
    FluentIcon,
    IconWidget,
    ImageLabel,
    MessageBoxBase,
    ProgressBar,
    SubtitleLabel,
    ToolButton,
    ToolTipFilter,
    isDarkTheme,
    setFont,
    themeColor,
)

from ..common.event_bus import event_bus
from ..common.utils import showInFolder
from ..service.ffmpeg_service import FFmpegTask


from ..common.task_status import TaskStatus



class TaskCardBase(CardWidget):
    """Task card base class"""

    deleted = Signal()
    checkedChanged = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.checkBox = CheckBox()
        self.checkBox.setFixedSize(23, 23)
        self.setSelectionMode(False)

        self.checkBox.stateChanged.connect(self._onCheckedChanged)

    def setSelectionMode(self, enter: bool):
        self.isSelectionMode = enter
        self.checkBox.setVisible(enter)
        if not enter:
            self.checkBox.setChecked(False)

        self.update()

    def isChecked(self):
        return self.checkBox.isChecked()

    def setChecked(self, checked):
        if checked == self.isChecked():
            return

        self.checkBox.setChecked(checked)
        self.update()

    def removeTask(self, deleteFile=False):
        raise NotImplementedError

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        if self.isSelectionMode:
            self.setChecked(not self.isChecked())
        else:
            self.setSelectionMode(True)
            self.setChecked(True)

    def _onDeleteButtonClicked(self):
        w = DeleteTaskDialog(self.window(), deleteOnClose=False)
        w.deleteFileCheckBox.setChecked(False)

        if w.exec():
            self.removeTask(w.deleteFileCheckBox.isChecked())

        w.deleteLater()

    def _onCheckedChanged(self):
        self.setChecked(self.checkBox.isChecked())
        self.checkedChanged.emit(self.checkBox.isChecked())
        self.update()

    def paintEvent(self, e):
        if not (self.isSelectionMode and self.isChecked()):
            return super().paintEvent(e)

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        r = self.borderRadius
        painter.setPen(QPen(themeColor(), 2))
        painter.setBrush(
            QColor(255, 255, 255, 15) if isDarkTheme() else QColor(0, 0, 0, 8)
        )
        painter.drawRoundedRect(self.rect().adjusted(2, 2, -2, -2), r, r)


class FFmpegTaskCard(TaskCardBase):
    """FFmpeg Task card"""

    def __init__(self, task: FFmpegTask, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()
        self.infoLayout = QHBoxLayout()

        self.task = task
        self.task_id = task.task_id
        self.status = TaskStatus.Waiting
        self.statusText = ["等待中", "初始化中", "压制中", "失败", "成功", "正在取消", "已取消"]
        self.imageLabel = ImageLabel()
        self.fileNameLabel = BodyLabel(task.fileName)
        self.progressBar = ProgressBar()

        self.statusIcon = IconWidget(FluentIcon.TAG)
        self.statusLabel = CaptionLabel(self.statusText[self.status.value])

        # size=256KiB  time=00:00:32.23  bitrate=  65.1kbits/s  speed=61.9x  elapsed=0:00:00.52
        self.sizeIcon = IconWidget(FluentIcon.BOOK_SHELF)
        self.sizeLabel = CaptionLabel("0MB")
        self.timeIcon = IconWidget(FluentIcon.STOP_WATCH)
        self.timeLabel = CaptionLabel("0.0s")
        self.bitrateIcon = IconWidget(FluentIcon.IOT)
        self.bitrateLabel = CaptionLabel("0kbits/s")
        self.speedIcon = IconWidget(FluentIcon.SPEED_HIGH)
        self.speedLabel = CaptionLabel("0x")
        self.finishTimeIcon = IconWidget(FluentIcon.CALENDAR)
        self.finishTimeLabel = CaptionLabel("2016-02-16 20:16:20")

        self.openFolderButton = ToolButton(FluentIcon.FOLDER)
        self.deleteButton = ToolButton(FluentIcon.DELETE)

        self._initWidget()

    def _initWidget(self):
        self.imageLabel.setImage(
            QFileIconProvider().icon(QFileInfo(self.task.videoPath)).pixmap(32, 32)
        )
        self.statusIcon.setFixedSize(16, 16)
        self.sizeIcon.setFixedSize(16, 16)
        self.timeIcon.setFixedSize(16, 16)
        self.bitrateIcon.setFixedSize(16, 16)
        self.speedIcon.setFixedSize(16, 16)
        self.finishTimeIcon.setFixedSize(16, 16)

        self.openFolderButton.setToolTip("在文件夹中显示")
        self.openFolderButton.setToolTipDuration(3000)
        self.openFolderButton.installEventFilter(ToolTipFilter(self.openFolderButton))
        self.cancelButton = ToolButton(FluentIcon.CLOSE)
        self.cancelButton.setToolTip("取消任务")
        self.cancelButton.setToolTipDuration(3000)
        self.cancelButton.installEventFilter(ToolTipFilter(self.cancelButton))
        self.retryButton = ToolButton(FluentIcon.SYNC)
        self.retryButton.setToolTip("重试任务")
        self.retryButton.setToolTipDuration(3000)
        self.retryButton.installEventFilter(ToolTipFilter(self.retryButton))
        self.deleteButton.setToolTip("移除任务")
        self.deleteButton.setToolTipDuration(3000)
        self.deleteButton.installEventFilter(ToolTipFilter(self.deleteButton))

        setFont(self.fileNameLabel, 18, QFont.Weight.Bold)
        self.fileNameLabel.setWordWrap(True)

        self._initLayout()
        self._connectSignalToSlot()
        self._updateStatus()

    def _initLayout(self):
        self.hBoxLayout.setContentsMargins(20, 11, 20, 11)
        self.hBoxLayout.addWidget(self.checkBox)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addWidget(self.imageLabel)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addLayout(self.vBoxLayout)
        self.hBoxLayout.addSpacing(20)
        self.hBoxLayout.addWidget(self.openFolderButton)
        self.hBoxLayout.addWidget(self.cancelButton)
        self.hBoxLayout.addWidget(self.retryButton)
        self.hBoxLayout.addWidget(self.deleteButton)

        self.vBoxLayout.setSpacing(5)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addWidget(self.fileNameLabel)
        self.vBoxLayout.addLayout(self.infoLayout)
        self.vBoxLayout.addWidget(self.progressBar)

        self.infoLayout.setContentsMargins(0, 0, 0, 0)
        self.infoLayout.setSpacing(3)
        self.infoLayout.addWidget(self.statusIcon)
        self.infoLayout.addWidget(self.statusLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.sizeIcon)
        self.infoLayout.addWidget(self.sizeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.timeIcon)
        self.infoLayout.addWidget(self.timeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.bitrateIcon)
        self.infoLayout.addWidget(self.bitrateLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.speedIcon)
        self.infoLayout.addWidget(self.speedLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addSpacing(5)
        self.infoLayout.addWidget(self.finishTimeIcon)
        self.infoLayout.addWidget(self.finishTimeLabel, 0, Qt.AlignmentFlag.AlignLeft)
        self.infoLayout.addStretch(1)

    def _connectSignalToSlot(self):
        self.openFolderButton.clicked.connect(self._onOpenButtonClicked)
        self.cancelButton.clicked.connect(self._onCancelButtonClicked)
        self.retryButton.clicked.connect(self._onRetryButtonClicked)
        self.deleteButton.clicked.connect(self._onDeleteButtonClicked)

    def _updateStatus(self, status: TaskStatus = TaskStatus.Waiting):
        self.status = status
        self.statusLabel.setText(self.statusText[self.status.value])
        if status == TaskStatus.Waiting:
            self.openFolderButton.setVisible(False)
            self.cancelButton.setVisible(False)
            self.retryButton.setVisible(False)
            self.deleteButton.setVisible(True)
            self._updateInfoVisible(False)
        elif status == TaskStatus.Pending or status == TaskStatus.Processing:
            self.openFolderButton.setVisible(False)
            self.cancelButton.setVisible(True)
            self.retryButton.setVisible(False)
            self.deleteButton.setVisible(False)
            self._updateInfoVisible(True)
        elif status == TaskStatus.Cancelling:
            self.openFolderButton.setVisible(False)
            self.cancelButton.setVisible(True)
            self.cancelButton.setEnabled(False)
            self.retryButton.setVisible(False)
            self.deleteButton.setVisible(False)
            self._updateInfoVisible(False)
        elif status == TaskStatus.Cancelled:
            self.openFolderButton.setVisible(False)
            self.cancelButton.setVisible(False)
            self.cancelButton.setEnabled(True)
            self.retryButton.setVisible(True)
            self.deleteButton.setVisible(True)
            self._updateInfoVisible(False)
        elif status == TaskStatus.Failed:
            self.openFolderButton.setVisible(False)
            self.cancelButton.setVisible(False)
            self.retryButton.setVisible(True)
            self.deleteButton.setVisible(True)
            self._updateInfoVisible(False)
        elif status == TaskStatus.Succeeded:
            self.openFolderButton.setVisible(True)
            self.cancelButton.setVisible(False)
            self.retryButton.setVisible(False)
            self.deleteButton.setVisible(True)
            self._updateInfoVisible(False)

    def _updateInfo(self, size, time, bitrate, speed):
        self.sizeLabel.setText(str(size))
        self.timeLabel.setText(str(time)+"s")
        self.bitrateLabel.setText(str(bitrate))
        self.speedLabel.setText(str(speed)+"x")

    def _updateInfoVisible(self, visible: bool):
        self.sizeIcon.setVisible(visible)
        self.sizeLabel.setVisible(visible)
        self.timeIcon.setVisible(visible)
        self.timeLabel.setVisible(visible)
        self.bitrateIcon.setVisible(visible)
        self.bitrateLabel.setVisible(visible)
        self.speedIcon.setVisible(visible)
        self.speedLabel.setVisible(visible)
        self.finishTimeIcon.setVisible(not visible)
        self.finishTimeLabel.setVisible(not visible)
        if not visible:
            t = time.gmtime()
            self.finishTimeLabel.setText(time.strftime("%Y-%m-%d %H:%M:%S", t))


    def updateTask(self, progress=0, status=TaskStatus.Waiting, size="0KiB", time=0.0, bitrate="0kbits/s", speed=0.0):
        self.progressBar.setValue(progress)
        self._updateStatus(status)
        self._updateInfo(size, time, bitrate, speed)

    def removeTask(self, deleteFile=False):
        event_bus.deleteTaskSig.emit(self.task.task_id, deleteFile)

    def _onOpenButtonClicked(self):
        path = Path(self.task.saveFolder) / self.task.outputName  
        showInFolder(path)
    
    def _onCancelButtonClicked(self):
        event_bus.cancelTaskSig.emit(self.task.task_id)
    
    def _onRetryButtonClicked(self):
        event_bus.retryTaskSig.emit(self.task.task_id)
    
    # def removeTask(self, deleteFile=False):
    #     if not self.task.isRunning():
    #         return

    # downloadTaskService.removeDownloadingTask(self.task, deleteFile)
    # self.deleted.emit(self.task)

    # def setInfo(self, info: VODDownloadProgressInfo):
    #     """update progress info"""
    #     self.speedLabel.setText(info.speed)
    #     self.remainTimeLabel.setText(info.remainTime)
    #     self.sizeLabel.setText(f"{info.currentSize}/{info.totalSize}")

    #     self.progressBar.setRange(0, info.totalChunks)
    #     self.progressBar.setValue(info.currentChunk)


class DeleteTaskDialog(MessageBoxBase):
    def __init__(self, parent=None, showCheckBox=True, deleteOnClose=True):
        super().__init__(parent)
        self.titleLabel = SubtitleLabel("删除任务", self)
        self.contentLabel = BodyLabel(
            "确认删除任务吗？", self
        )
        self.deleteFileCheckBox = CheckBox("删除文件", self)

        self.deleteFileCheckBox.setVisible(showCheckBox)

        if deleteOnClose:
            self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose, True)

        self._initWidgets()

    def _initWidgets(self):
        self.deleteFileCheckBox.setChecked(True)
        self.widget.setMinimumWidth(330)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.titleLabel)
        layout.addSpacing(12)
        layout.addWidget(self.contentLabel)
        layout.addSpacing(10)
        layout.addWidget(self.deleteFileCheckBox)
        self.viewLayout.addLayout(layout)
