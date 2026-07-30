from PySide6.QtCore import QEvent, QSize, Qt, QThreadPool
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGraphicsDropShadowEffect,
    QVBoxLayout,
    QWidget,
)

from libs.qfluentwidgets_pro import (
    Action,
    CommandBarView,
    FluentIcon,
    ScrollArea,
    SegmentedWidget,
    isDarkTheme,
)
from pathlib import Path
import random

from ..common.event_bus import event_bus
from ..common.text import Text
from ..common.utils import DeleteFileWorker
from ..components.task_card import DeleteTaskDialog, FFmpegTaskCard
from ..service.ffmpeg_service import FFmpegTask, FFmpegWorker
from ..components.empty_status_widget import EmptyStatusWidget
from ..common.icon import Logo
from ..common.task_status import TaskStatus

class TaskInterface(ScrollArea):
    """任务界面"""
    _idle_statuses = (TaskStatus.Waiting, TaskStatus.Succeeded, TaskStatus.Failed, TaskStatus.Cancelled)

    def __init__(
        self,
        parent=None,
    ):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.segmentedWidget = SegmentedWidget(self)
        self.allTab = QWidget()
        self.processingTab = QWidget()
        self.completedTab = QWidget()
        self.failedTab = QWidget()
        self.globalText = Text()
        self.taskListContainer = QWidget(self)
        self.taskListLayout = QVBoxLayout(self.taskListContainer)

        self.taskPool = QThreadPool()
        self.taskPool.setMaxThreadCount(2)
        self.cards = []
        self.cardMap = {}
        self.threadMap = {}
        self.selectionCount = 0
        self.isSelectionMode = False
        self._hadFailedTasks = False
        self._input_paths = set()

        self.commandView = TaskCommandBarView(self.window())
        self.commandView.hide()

        self.emptyStatusIcons = [
            Logo.FACE01,
            Logo.FACE02,
            Logo.FACE03,
            Logo.FACE04,
            Logo.FACE05,
            Logo.FACE06,
            Logo.FACE07,
            Logo.FACE08,
            Logo.FACE09,
            Logo.FACE10,
        ]
        self.lastSelectedemptyStatusIcon = random.randint(0, len(self.emptyStatusIcons) - 1)
        self.emptyStatusWidget = EmptyStatusWidget(
            self.emptyStatusIcons[self.lastSelectedemptyStatusIcon], "目前没有任务", self
        )

        self._initWidget()
        self._connectSignalToSlot()

    def _initWidget(self):
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setObjectName("taskInterface")
        self.enableTransparentBackground()

        self.emptyStatusWidget.setMinimumWidth(200)
        self._updateEmptyStatus(False)

        self.segmentedWidget.addItem(self.allTab, self.globalText.All, lambda: self._filterTasks("all"))
        self.segmentedWidget.addItem(
            self.processingTab,
            "压制中",
            lambda: self._filterTasks(TaskStatus.Processing),
        )
        self.segmentedWidget.addItem(
            self.completedTab,
            "成功",
            lambda: self._filterTasks(TaskStatus.Succeeded)
        )
        self.segmentedWidget.addItem(
            self.failedTab,
            "失败",
            lambda: self._filterTasks(TaskStatus.Failed)
        )

        self.segmentedWidget.setCurrentItem(self.allTab)
        self.segmentedWidget.setMaximumHeight(30)

        # 创建任务列表容器
        self.taskListLayout.setAlignment(Qt.AlignTop)

        # 设置布局
        self.vBoxLayout.addWidget(self.segmentedWidget)
        self.vBoxLayout.addWidget(self.taskListContainer)


    def _connectSignalToSlot(self):
        event_bus.addTaskSig.connect(self.addTask)
        event_bus.updateTaskStatusSig.connect(self._update_task_status)
        event_bus.finishTaskSig.connect(self._handle_task_finished)
        event_bus.deleteTaskSig.connect(self._handle_task_deleted)
        event_bus.cancelTaskSig.connect(self._handle_cancel_task)
        event_bus.retryTaskSig.connect(self._handle_retry_task)
        self.emptyStatusWidget.clicked.connect(self._updateEmptyStatus)
        self.commandView.redownloadAction.triggered.connect(self._restartSelectedTasks)
        self.commandView.deleteAction.triggered.connect(self._removeSelectedTasks)
        self.commandView.selectAllAction.triggered.connect(self.selectAll)
        self.commandView.cancelAction.triggered.connect(
            lambda: self.setSelectionMode(False)
        )

    def _filterTasks(self, status):
        """根据任务状态过滤任务"""
        hasCard = False
        for card in self.cards.copy():
            if card.status == status or status == "all":
                card.setVisible(True)
                hasCard = True
            else:
                card.setVisible(False)

        self._updateEmptyStatus(not hasCard)

    def _updateEmptyStatus(self, show: bool = True):
        """更新空状态显示"""
        self.emptyStatusWidget.setVisible(show)
        if show:
            self.lastSelectedemptyStatusIcon = (self.lastSelectedemptyStatusIcon  + 1) % len(self.emptyStatusIcons)
            icon = self.emptyStatusIcons[self.lastSelectedemptyStatusIcon]
            self.emptyStatusWidget.setIcon(icon)
        
    def selectAll(self):
        for card in self.cards.copy():
            card.setChecked(True)

    def _removeCard(self, card, deleteFile=False):
        """从布局和列表中移除卡片"""
        task_id = card.task.task_id
        # 断开信号，防止 deleteLater 时触发 checkedChanged
        card.checkedChanged.disconnect(self._onCardCheckedChanged)
        self.taskListLayout.removeWidget(card)
        self.cards.remove(card)
        self.cardMap.pop(task_id, None)
        self._input_paths.discard(card.task.videoPath)
        # 按需异步删除输出文件
        if deleteFile:
            output_path = Path(card.task.saveFolder) / card.task.outputName
            self.taskPool.start(DeleteFileWorker(str(output_path)))
        card.hide()
        card.deleteLater()
        self._updateEmptyStatus(not self.cards)
        event_bus.taskCountChanged.emit(len(self.cards))
        self._check_failed_tasks()

    _idle_statuses = (TaskStatus.Waiting, TaskStatus.Succeeded, TaskStatus.Failed, TaskStatus.Cancelled)

    def _is_idle_card(self, card):
        """是否可删除/可重试（非进行中的任务）"""
        return card.status in self._idle_statuses

    def _removeSelectedTasks(self):
        w = DeleteTaskDialog(self.window(), deleteOnClose=False)
        w.contentLabel.setText("确定删除选中的任务吗？")
        w.deleteFileCheckBox.setChecked(False)

        if w.exec():
            deleteFile = w.deleteFileCheckBox.isChecked()
            for card in self.cards.copy():
                if card.isChecked() and self._is_idle_card(card):
                    self._removeCard(card, deleteFile)

        w.deleteLater()
        self.setSelectionMode(False)

    def _restartSelectedTasks(self):
        for card in self.cards.copy():
            if card.isChecked() and self._is_idle_card(card):
                event_bus.retryTaskSig.emit(card.task.task_id)

    def _onCardCheckedChanged(self, checked: bool):
        if checked:
            self.selectionCount += 1
            self.setSelectionMode(True)
        else:
            self.selectionCount = max(0, self.selectionCount - 1)
            if self.selectionCount == 0:
                self.setSelectionMode(False)

    def setSelectionMode(self, enter: bool):
        if self.isSelectionMode == enter:
            return

        self.isSelectionMode = enter

        for card in self.cards:
            card.setSelectionMode(enter)

        if enter:
            self.commandView.setVisible(True)
            self.commandView.raise_()
        else:
            self.commandView.setVisible(False)
            self.selectionCount = 0

    def showEvent(self, event: QEvent):
        """切换到本页面时检测任务"""
        super().showEvent(event)
        self._refreshEmptyStatus()
        self._filterTasks("all")
        # self.segmentedWidget.setCurrentItem(self.allTab)

    def _refreshEmptyStatus(self):
        """根据当前筛选条件刷新空状态"""
        current = self.segmentedWidget.currentItem()
        if current == self.allTab:
            status = "all"
        elif current == self.processingTab:
            status = TaskStatus.Processing
        elif current == self.completedTab:
            status = TaskStatus.Succeeded
        else:
            status = TaskStatus.Failed
        self._filterTasks(status)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        x = self.window().width() // 2 - self.commandView.width() // 2
        y = self.window().height() - self.commandView.sizeHint().height() - 20
        self.commandView.move(x, y)

        self.emptyStatusWidget.adjustSize()
        w, h = self.emptyStatusWidget.width(), self.emptyStatusWidget.height()
        y = self.height() // 2 - h // 2
        self.emptyStatusWidget.move(int(self.width() / 2 - w / 2), y)

    def addTask(self, video_paths: set, audio_paths: set):
        """添加任务"""
        added = 0
        # 视频: libx264，音频: libmp3lame
        for file_path, extra_args in [
            *((p, ["-c:v", "libx264", "-preset", "ultrafast"]) for p in video_paths),
            *((p, ["-c:a", "libmp3lame"]) for p in audio_paths),
        ]:
            if self._add_single_task(file_path, extra_args):
                added += 1

        event_bus.notification_service.show_success(
            "成功",
            "已添加 {} 个任务，过滤 {} 个重复任务".format(
                added, len(video_paths) + len(audio_paths) - added
            ),
        )
        event_bus.taskCountChanged.emit(len(self.cards))

    def _add_single_task(self, file_path, extra_args: list) -> bool:
        """添加单个任务，返回是否成功添加（非重复）"""
        input_path = str(file_path)
        if input_path in self._input_paths:
            return False
        self._input_paths.add(input_path)

        name = file_path.name
        output_name = name.replace(file_path.suffix, f"_pressed{file_path.suffix}")
        output_path = file_path.parent / output_name
        task = FFmpegTask(
            args=["-i", input_path, *extra_args, str(output_path), "-y"],
            fileName=name,
            videoPath=input_path,
            saveFolder=file_path.parent,
            outputName=output_name,
        )
        card = FFmpegTaskCard(task, self.taskListContainer)
        card.checkedChanged.connect(self._onCardCheckedChanged)

        if self.isSelectionMode:
            card.setSelectionMode(True)

        self.taskListLayout.insertWidget(0, card, 0, Qt.AlignmentFlag.AlignTop)
        self.cards.insert(0, card)
        self.cardMap[task.task_id] = card
        self.threadMap[task.task_id] = FFmpegWorker(task)
        self.taskPool.start(self.threadMap[task.task_id])
        return True
        
    def _update_task_status(self, task_id, progress, status, size, time, bitrate, speed):
        """更新任务状态"""
        card = self.cardMap.get(task_id)
        if card:
            card.updateTask(progress, status, size, time, bitrate, speed)
            self._check_failed_tasks()
        else:
            print(f"找不到任务：{task_id}")
            
    def _handle_task_finished(self, task_id, success: bool):
        """任务完成"""
        card = self.cardMap.get(task_id)
        if card and card.status not in (TaskStatus.Cancelled, TaskStatus.Cancelling):
            card.updateTask(status=TaskStatus.Succeeded if success else TaskStatus.Failed,
                            progress=100 if success else 0)
            self._check_failed_tasks()

    def _handle_cancel_task(self, task_id):
        """取消任务"""
        card = self.cardMap.get(task_id)
        if not card or card.status in (TaskStatus.Cancelled, TaskStatus.Cancelling):
            return
        card.updateTask(status=TaskStatus.Cancelling)
        thread = self.threadMap.pop(task_id, None)
        if thread and hasattr(thread, "process"):
            thread.process.kill()
        # 更新为已取消（kill 后 _handle_finished 也会触发，但会被上面的检查跳过）
        if card:
            card.updateTask(status=TaskStatus.Cancelled)

    def _handle_retry_task(self, task_id):
        """重试任务"""
        card = self.cardMap.get(task_id)
        if not card:
            return
        task = card.task
        card.updateTask(status=TaskStatus.Waiting, progress=0)
        thread = FFmpegWorker(task)
        self.threadMap[task_id] = thread
        self.taskPool.start(thread)
        self._check_failed_tasks()

    def _check_failed_tasks(self):
        """检查是否存在失败任务，状态变化时 emit"""
        hasFailed = any(card.status == TaskStatus.Failed for card in self.cards)
        if hasFailed != self._hadFailedTasks:
            self._hadFailedTasks = hasFailed
            event_bus.hasFailedTasks.emit(hasFailed)

    def _handle_task_deleted(self, task_id, deleteFile):
        """移除对应卡片"""
        for card in self.cards.copy():
            if hasattr(card, "task") and card.task.task_id == task_id:
                self._removeCard(card, deleteFile)
                break


class TaskCommandBarView(CommandBarView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.redownloadAction = Action(FluentIcon.UPDATE, "重试", self)
        self.deleteAction = Action(FluentIcon.DELETE, "删除", self)
        self.selectAllAction = Action(FluentIcon.SELECT, "全选", self)
        self.cancelAction = Action(FluentIcon.CLEAR_SELECTION, "取消", self)

        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(18, 18))
        self.addActions([self.redownloadAction, self.deleteAction])
        self.addSeparator()
        self.addActions([self.selectAllAction, self.cancelAction])
        self.resizeToSuitableWidth()
        self.setShadowEffect()

    def setShadowEffect(self, blurRadius=35, offset=(0, 8)):
        """add shadow to dialog"""
        color = QColor(0, 0, 0, 80 if isDarkTheme() else 30)
        self.shadowEffect = QGraphicsDropShadowEffect(self)
        self.shadowEffect.setBlurRadius(blurRadius)
        self.shadowEffect.setOffset(*offset)
        self.shadowEffect.setColor(color)
        self.setGraphicsEffect(None)
        self.setGraphicsEffect(self.shadowEffect)
