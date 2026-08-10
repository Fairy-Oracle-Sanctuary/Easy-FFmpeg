import random
import shlex
import sys
from pathlib import Path

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

from ..common.config import cfg
from ..common.event_bus import event_bus
from ..common.icon import Logo
from ..common.task_status import TaskStatus
from ..common.text import Text
from ..common.utils import DeleteFileWorker, classifyMediaPaths
from ..components.empty_status_widget import EmptyStatusWidget
from ..components.task_card import DeleteTaskDialog, FFmpegTaskCard
from ..service.ffmpeg_service import FFmpegTask, FFmpegWorker


class TaskInterface(ScrollArea):
    """任务界面"""

    _idle_statuses = (
        TaskStatus.Waiting,
        TaskStatus.Succeeded,
        TaskStatus.Failed,
        TaskStatus.Cancelled,
    )

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
        self.subTaskPool = QThreadPool()
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
        self.lastSelectedemptyStatusIcon = random.randint(
            0, len(self.emptyStatusIcons) - 1
        )
        self.emptyStatusWidget = EmptyStatusWidget(
            self.emptyStatusIcons[self.lastSelectedemptyStatusIcon],
            self.globalText.NoTasks,
            self,
        )

        self._initWidget()
        self._connectSignalToSlot()

    def _initWidget(self):
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setObjectName("taskInterface")
        self.enableTransparentBackground()
        self.setAcceptDrops(True)
        self.viewport().setAcceptDrops(True)

        self.emptyStatusWidget.setMinimumWidth(200)
        self._updateEmptyStatus(False)

        self.segmentedWidget.addItem(
            self.allTab, self.globalText.All, lambda: self._filterTasks("all")
        )
        self.segmentedWidget.addItem(
            self.processingTab,
            self.globalText.Pressing,
            lambda: self._filterTasks(TaskStatus.Processing),
        )
        self.segmentedWidget.addItem(
            self.completedTab,
            self.globalText.Success,
            lambda: self._filterTasks(TaskStatus.Succeeded),
        )
        self.segmentedWidget.addItem(
            self.failedTab,
            self.globalText.Failed,
            lambda: self._filterTasks(TaskStatus.Failed),
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
        event_bus.addToolTaskSig.connect(self._add_tool_task)
        event_bus.updateTaskStatusSig.connect(self._update_task_status)
        event_bus.finishTaskSig.connect(self._handle_task_finished)
        event_bus.deleteTaskSig.connect(self._handle_task_deleted)
        event_bus.cancelTaskSig.connect(self._handle_cancel_task)
        event_bus.retryTaskSig.connect(self._handle_retry_task)
        event_bus.taskStageChangedSig.connect(self._handle_stage_changed)
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
            self.lastSelectedemptyStatusIcon = (
                self.lastSelectedemptyStatusIcon + 1
            ) % len(self.emptyStatusIcons)
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
            self.subTaskPool.start(DeleteFileWorker(str(output_path)))
        # 异步删除日志文件（如果存在）
        if card.task.logPath:
            self.subTaskPool.start(DeleteFileWorker(card.task.logPath))
        card.hide()
        card.deleteLater()
        # 被删卡片如果是选中状态，手动更新计数
        if card.isChecked():
            self.selectionCount = max(0, self.selectionCount - 1)
            if self.selectionCount == 0:
                self.setSelectionMode(False)
        self._updateEmptyStatus(not self.cards)
        event_bus.taskCountChanged.emit(len(self.cards))
        self._check_failed_tasks()

    def _is_idle_card(self, card):
        """是否可删除/可重试（非进行中的任务）"""
        return card.status in self._idle_statuses

    def _removeSelectedTasks(self):
        w = DeleteTaskDialog(self.window(), deleteOnClose=False)
        w.contentLabel.setText(self.globalText.DeleteSelectedConfirm)
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

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        if not event.mimeData().hasUrls():
            event.ignore()
            return

        paths = [
            url.toLocalFile() for url in event.mimeData().urls() if url.isLocalFile()
        ]
        video_set, audio_set, image_set = classifyMediaPaths(
            paths, cfg.get(cfg.homeRecursive)
        )

        if video_set or audio_set or image_set:
            event_bus.addTaskSig.emit(video_set, audio_set, image_set)

        event.acceptProposedAction()

    @staticmethod
    def _get_output_name(file_path, is_audio: bool = False) -> str:
        """根据输入路径生成输出文件名

        视频文件沿用原扩展名；音频文件按音频编码器选择匹配的容器扩展名
        （aac→.m4a, libmp3lame→.mp3, libopus→.opus），copy 沿用原扩展名。
        避免如 aac 编码输出 .mp3 容器导致的格式不匹配。
        """
        if is_audio:
            codec = cfg.get(cfg.ffmpegAudioCodec)
            ext_map = {"aac": ".m4a", "libmp3lame": ".mp3", "libopus": ".opus"}
            ext = ext_map.get(codec, file_path.suffix)
            return f"{file_path.stem}_pressed{ext}"
        return file_path.name.replace(file_path.suffix, f"_pressed{file_path.suffix}")

    def _build_custom_args(self, template: str, file_path) -> list:
        """从自定义参数模板构建 ffmpeg args 列表

        先用 shlex 解析模板结构，再替换占位符 token，
        避免 Windows 路径中的反斜杠被当作转义字符。
        """
        output_name = self._get_output_name(file_path)
        output_path = str(file_path.parent / output_name)
        input_path = str(file_path)

        tokens = shlex.split(template)
        # 去掉开头的 ffmpeg 可执行文件名（实际路径由 FFmpegWorker 注入）
        if tokens and Path(tokens[0]).name.lower().startswith("ffmpeg"):
            tokens = tokens[1:]

        # 替换占位符（在已 split 的 token 上替换，路径不会被二次解析）
        return [
            token.replace("{{input_file}}", input_path).replace(
                "{{output_file}}", output_path
            )
            for token in tokens
        ]

    def _build_default_args(
        self,
        file_path,
        is_audio: bool = False,
        is_image: bool = False,
        pass_mode: int = 0,
        passlogfile: str = "",
    ) -> list:
        """根据高级设置构建默认 ffmpeg args 列表

        Parameters
        ----------
        file_path : Path
            输入文件路径
        is_audio : bool
            是否为纯音频文件（跳过视频相关参数块）
        is_image : bool
            是否为图片文件（仅质量压缩，跳过视频/音频参数块）
        pass_mode : int
            0=单 pass, 1=two-pass 第一遍（仅分析），2=two-pass 第二遍（编码）
        passlogfile : str
            two-pass passlog 文件前缀，pass 1/2 必须一致，完成后用于清理
        """
        output_name = self._get_output_name(file_path, is_audio)
        output_path = str(file_path.parent / output_name)
        input_path = str(file_path)
        enabled = cfg.get(cfg.ffmpegEnabledBlocks)

        args = []

        if is_image:
            # 图片：仅质量压缩，输出沿用原格式（不转换格式、不缩放）
            args += ["-i", input_path]
            if "image" in enabled:
                ext = file_path.suffix.lower()
                if ext in {".jpg", ".jpeg", ".webp"}:
                    # 有损格式：-q:v 调质量（数值越小质量越高）
                    args += ["-q:v", cfg.get(cfg.ffmpegImageQuality)]
                elif ext == ".png":
                    # 无损格式：调压缩级别（不损失质量，仅减小体积）
                    args += ["-compression_level", "6"]
                # 其他格式（bmp/tiff 等）无质量参数，直接重编码
            args += [output_path, "-y"]
            return args

        # 进阶：裁剪（放 -i 前作为输入选项，seek 更快）
        if "extra" in enabled:
            start = str(cfg.get(cfg.ffmpegStartTime)).strip()
            if start:
                args += ["-ss", start]
            duration = str(cfg.get(cfg.ffmpegDuration)).strip()
            if duration:
                args += ["-t", duration]

        args += ["-i", input_path]

        # 视频参数（纯音频文件跳过）
        if not is_audio:
            is_soft_x264 = not cfg.get(cfg.ffmpegUseHardWareVideoCodec) and cfg.get(
                cfg.ffmpegSoftWareVideoCodec
            ) in ("libx264", "libx265")

            # 编码器
            if "encoder" in enabled:
                if cfg.get(cfg.ffmpegUseHardWareVideoCodec):
                    args += ["-c:v", cfg.get(cfg.ffmpegHardWareVideoCodec)]
                else:
                    args += ["-c:v", cfg.get(cfg.ffmpegSoftWareVideoCodec)]

            # 质量控制
            if "quality" in enabled:
                if cfg.get(cfg.ffmpegQualityMode) == "CRF":
                    args += ["-crf", str(cfg.get(cfg.ffmpegCrf))]
                else:
                    args += ["-b:v", f"{cfg.get(cfg.ffmpegVideoBitrate)}k"]
                    # two-pass：pass1/pass2 共享 -b:v，分别附加 -pass 标志
                    if pass_mode == 1:
                        args += ["-pass", "1", "-passlogfile", passlogfile]
                    elif pass_mode == 2:
                        args += ["-pass", "2", "-passlogfile", passlogfile]

            # 编码速度预设（仅 libx264/libx265 软件编码生效）
            if "preset" in enabled and is_soft_x264:
                args += ["-preset", cfg.get(cfg.ffmpegPreset)]

            # 进阶：tune 调优（仅 libx264/libx265 软件编码生效）
            if "extra" in enabled and is_soft_x264:
                tune = cfg.get(cfg.ffmpegTune)
                if tune != "none":
                    args += ["-tune", tune]

            # 滤镜链（分辨率 / 反交错 / 旋转合并为一个 -vf）
            filters = []
            if "resolution" in enabled:
                res = cfg.get(cfg.ffmpegResolution)
                if res == "1080p":
                    filters.append("scale=-2:1080")
                elif res == "720p":
                    filters.append("scale=-2:720")
                elif res == "480p":
                    filters.append("scale=-2:480")
                elif res == "custom":
                    filters.append(f"scale={cfg.get(cfg.ffmpegCustomWidth)}:-2")

            if "extra" in enabled:
                if cfg.get(cfg.ffmpegDeinterlace):
                    filters.append("yadif")
                rotation = cfg.get(cfg.ffmpegRotation)
                if rotation == "90":
                    filters.append("transpose=1")
                elif rotation == "180":
                    filters.append("transpose=1,transpose=1")
                elif rotation == "270":
                    filters.append("transpose=2")

            if filters:
                args += ["-vf", ",".join(filters)]

            # 帧率
            if "frame_rate" in enabled:
                fps = cfg.get(cfg.ffmpegFrameRate)
                if fps != "origin":
                    args += ["-r", str(fps)]

        # 音频（pass 1 跳过音频，-an 在输出块统一加）
        if pass_mode != 1 and "audio" in enabled:
            if cfg.get(cfg.ffmpegRemoveAudio) and not is_audio:
                # 删除音轨仅对视频文件有意义（音频文件删了音轨=空输出）
                args += ["-an"]
            else:
                audio_codec = cfg.get(cfg.ffmpegAudioCodec)
                args += ["-c:a", audio_codec]
                if audio_codec != "copy":
                    args += ["-b:a", cfg.get(cfg.ffmpegAudioBitrate)]

        # 输出
        if pass_mode == 1:
            # pass 1 输出到空设备，-an 跳过音频，-f mp4 指定容器
            # （输出到 NUL/dev/null 需显式格式，否则 ffmpeg 无法推断容器）
            null_output = "NUL" if sys.platform == "win32" else "/dev/null"
            args += ["-an", "-f", "mp4", null_output]
        else:
            args += [output_path, "-y"]
        return args

    def _is_two_pass_enabled(self, is_audio: bool) -> bool:
        """判断是否启用 two-pass 二次编码

        启用条件全部满足：
        - 非纯音频文件（two-pass 是视频编码概念）
        - 质量模式为 Bitrate（CRF 模式下 two-pass 无意义）
        - 用户开启了二次编码开关
        - 使用软件编码（硬件编码器 two-pass 机制不同，暂不支持）
        - quality 参数块已启用（-b:v 在该块内）
        """
        if is_audio:
            return False
        if cfg.get(cfg.ffmpegQualityMode) != "Bitrate":
            return False
        if not cfg.get(cfg.ffmpegTwoPass):
            return False
        if cfg.get(cfg.ffmpegUseHardWareVideoCodec):
            return False
        if "quality" not in cfg.get(cfg.ffmpegEnabledBlocks):
            return False
        return True

    def addTask(self, video_paths: set, audio_paths: set, image_paths: set = None):
        """添加任务"""
        if image_paths is None:
            image_paths = set()
        added = 0
        total = len(video_paths) + len(audio_paths) + len(image_paths)

        if cfg.get(cfg.ffmpegIsUseCustomArgs):
            # 自定义参数模式：使用用户填写的命令行模板
            video_template = cfg.get(cfg.ffmpegCustomVideoArgs)
            audio_template = cfg.get(cfg.ffmpegCustomAudioArgs)
            image_template = cfg.get(cfg.ffmpegCustomImageArgs)
            for file_path, template, is_audio, is_image in [
                *((p, video_template, False, False) for p in video_paths),
                *((p, audio_template, True, False) for p in audio_paths),
                *((p, image_template, False, True) for p in image_paths),
            ]:
                args = self._build_custom_args(template, file_path)
                if self._add_single_task(
                    file_path,
                    args,
                    is_custom_args=True,
                    custom_template=template,
                    is_audio=is_audio,
                    is_image=is_image,
                ):
                    added += 1
        else:
            # 默认参数模式：根据高级设置配置项拼装参数
            for file_path in video_paths:
                if self._is_two_pass_enabled(is_audio=False):
                    # two-pass：生成 pass1（分析）+ pass2（编码）两套参数
                    # passlogfile 用输出目录 + 随机前缀，避免并发任务 passlog 冲突
                    passlogfile = str(
                        file_path.parent
                        / f"_easy_ffmpeg_pass_{random.randint(100000, 999999)}"
                    )
                    args_pass1 = self._build_default_args(
                        file_path, is_audio=False, pass_mode=1, passlogfile=passlogfile
                    )
                    args_pass2 = self._build_default_args(
                        file_path, is_audio=False, pass_mode=2, passlogfile=passlogfile
                    )
                    if self._add_single_task(
                        file_path,
                        args_pass2,
                        two_pass=True,
                        args_pass1=args_pass1,
                        passlogfile=passlogfile,
                        is_audio=False,
                    ):
                        added += 1
                else:
                    args = self._build_default_args(file_path, is_audio=False)
                    if self._add_single_task(file_path, args, is_audio=False):
                        added += 1
            for file_path in audio_paths:
                args = self._build_default_args(file_path, is_audio=True)
                if self._add_single_task(file_path, args, is_audio=True):
                    added += 1
            for file_path in image_paths:
                args = self._build_default_args(file_path, is_image=True)
                if self._add_single_task(file_path, args, is_image=True):
                    added += 1

        event_bus.notification_service.show_success(
            self.globalText.Success,
            self.globalText.TasksAdded.format(added, total - added),
        )
        event_bus.taskCountChanged.emit(len(self.cards))
        # 切到"全部"tab 并刷新空状态
        self.segmentedWidget.setCurrentItem(self.allTab)
        self._filterTasks("all")

    def _add_single_task(
        self,
        file_path,
        args: list,
        two_pass: bool = False,
        args_pass1: list = None,
        passlogfile: str = "",
        is_custom_args: bool = False,
        custom_template: str = "",
        is_audio: bool = False,
        is_image: bool = False,
        is_tool_task: bool = False,
        output_name: str = "",
        save_folder: str = "",
        allow_duplicate: bool = False,
    ) -> bool:
        """添加单个任务，返回是否成功添加（非重复）

        output_name/save_folder 为空时按输入路径推导；工具任务(功能页)会
        显式传入，覆盖默认推导结果。allow_duplicate=True 时跳过输入路径
        去重（用于同一输入生成多个不同输出的批量任务）。
        """
        input_path = str(file_path)
        if not allow_duplicate:
            if input_path in self._input_paths:
                return False
            self._input_paths.add(input_path)

        output_name = output_name or self._get_output_name(file_path, is_audio)
        task = FFmpegTask(
            args=args,
            fileName=file_path.name,
            videoPath=input_path,
            saveFolder=save_folder or file_path.parent,
            outputName=output_name,
            two_pass=two_pass,
            args_pass1=args_pass1,
            passlogfile=passlogfile,
            is_custom_args=is_custom_args,
            custom_template=custom_template,
            is_audio=is_audio,
            is_image=is_image,
            is_tool_task=is_tool_task,
        )
        card = FFmpegTaskCard(task, self.taskListContainer)
        card.checkedChanged.connect(self._onCardCheckedChanged)

        if self.isSelectionMode:
            card.setSelectionMode(True)

        self.taskListLayout.insertWidget(0, card, 0, Qt.AlignmentFlag.AlignTop)
        self.cards.insert(0, card)
        self.cardMap[task.task_id] = card
        self.threadMap[task.task_id] = FFmpegWorker(task, self.globalText)
        self.taskPool.start(self.threadMap[task.task_id])
        return True

    def _add_tool_task(self, info):
        """接收功能页提交的工具任务，加入主任务队列

        工具任务 args 固定(含完整输出路径)，重试时不重建参数。
        复用 _add_single_task 的卡片创建与线程池启动逻辑。
        """
        file_path = Path(info.input_path)
        added = self._add_single_task(
            file_path,
            info.args,
            is_custom_args=True,
            is_tool_task=True,
            output_name=info.output_name,
            save_folder=info.save_folder,
            allow_duplicate=info.allow_duplicate,
        )
        if added:
            event_bus.notification_service.show_success(
                self.globalText.Success,
                self.globalText.TaskAddedName.format(file_path.name),
            )
        else:
            event_bus.notification_service.show_warning(
                self.globalText.Notice, self.globalText.FileInQueue
            )
        event_bus.taskCountChanged.emit(len(self.cards))
        self.segmentedWidget.setCurrentItem(self.allTab)
        self._filterTasks("all")

    def _update_task_status(
        self, task_id, progress, status, size, time, bitrate, speed
    ):
        """更新任务状态"""
        card = self.cardMap.get(task_id)
        if card:
            card.updateTask(progress, status, size, time, bitrate, speed)
            self._check_failed_tasks()
        else:
            print(f"找不到任务：{task_id}")

    def _handle_stage_changed(self, task_id, stage_text: str):
        """two-pass 阶段切换：更新卡片阶段文案"""
        card = self.cardMap.get(task_id)
        if card:
            card.updateStage(stage_text)

    def _handle_task_finished(self, task_id, success: bool, logPath: str):
        """任务完成"""
        card = self.cardMap.get(task_id)
        if card and card.status not in (TaskStatus.Cancelled, TaskStatus.Cancelling):
            card.updateTask(
                status=TaskStatus.Succeeded if success else TaskStatus.Failed,
                progress=100 if success else 0,
            )
            if success:
                self.subTaskPool.start(DeleteFileWorker(logPath))
                event_bus.notification_service.show_success(
                    self.globalText.Success,
                    self.globalText.TaskFinished.format(card.task.fileName),
                )
                event_bus.trayMessageSig.emit(
                    "Easy-FFmpeg",
                    self.globalText.TaskFinished.format(card.task.fileName),
                    "info",
                )
            else:
                event_bus.notification_service.show_error(
                    self.globalText.Failed,
                    self.globalText.TaskFailedName.format(card.task.fileName),
                )
                event_bus.trayMessageSig.emit(
                    "Easy-FFmpeg",
                    self.globalText.TaskFailedName.format(card.task.fileName),
                    "warning",
                )
            self._check_failed_tasks()

    def _handle_cancel_task(self, task_id):
        """取消任务"""
        card = self.cardMap.get(task_id)
        if not card or card.status in (TaskStatus.Cancelled, TaskStatus.Cancelling):
            return
        card.updateTask(status=TaskStatus.Cancelling)
        card.updateStage("")  # 清除 two-pass 阶段文案
        thread = self.threadMap.pop(task_id, None)
        if thread and hasattr(thread, "cancel"):
            # 调用 worker.cancel() 标记取消并 kill 当前阶段进程，
            # 双阶段下防止 pass 1 结束后自动启动 pass 2，且 _finish 不 emit 完成信号
            thread.cancel()
        if card:
            card.updateTask(status=TaskStatus.Cancelled)

    def _handle_retry_task(self, task_id):
        """重试任务"""
        card = self.cardMap.get(task_id)
        if not card:
            return
        task = card.task
        card.updateStage("")  # 清除上次的 two-pass 阶段文案
        # 若开启"重试用当前设置"，按当前高级设置重建参数（含重新判断 two-pass）
        if cfg.get(cfg.retryUseCurrentSettings):
            self._rebuild_task_args(task)
        card.updateTask(status=TaskStatus.Waiting, progress=0)
        thread = FFmpegWorker(task, self.globalText)
        self.threadMap[task_id] = thread
        self.taskPool.start(thread)
        self._check_failed_tasks()

    def _rebuild_task_args(self, task):
        """用当前高级设置重建任务参数（重试时调用）

        根据任务原始模式重建：
        - 自定义模式：用当前对应模板（视频/音频/图片）重建 args
        - 默认模式：用当前配置块重建，图片仅质量压缩，视频重新判断 two-pass
        重建后 task 的 args/args_pass1/two_pass/passlogfile 全部刷新。
        """
        if task.is_tool_task:
            # 工具任务（功能页自定义命令）args 固定，重试时原样复用
            return
        file_path = Path(task.videoPath)
        if task.is_custom_args:
            if task.is_image:
                template = cfg.get(cfg.ffmpegCustomImageArgs)
            elif task.is_audio:
                template = cfg.get(cfg.ffmpegCustomAudioArgs)
            else:
                template = cfg.get(cfg.ffmpegCustomVideoArgs)
            task.args = self._build_custom_args(template, file_path)
            task.custom_template = template
            task.two_pass = False
            task.args_pass1 = []
            task.passlogfile = ""
        elif task.is_image:
            # 图片默认模式：仅质量压缩，无 two-pass
            task.args = self._build_default_args(file_path, is_image=True)
            task.two_pass = False
            task.args_pass1 = []
            task.passlogfile = ""
        else:
            if self._is_two_pass_enabled(task.is_audio):
                passlogfile = str(
                    file_path.parent
                    / f"_easy_ffmpeg_pass_{random.randint(100000, 999999)}"
                )
                task.args_pass1 = self._build_default_args(
                    file_path, task.is_audio, pass_mode=1, passlogfile=passlogfile
                )
                task.args = self._build_default_args(
                    file_path, task.is_audio, pass_mode=2, passlogfile=passlogfile
                )
                task.two_pass = True
                task.passlogfile = passlogfile
            else:
                task.args = self._build_default_args(file_path, task.is_audio)
                task.two_pass = False
                task.args_pass1 = []
                task.passlogfile = ""

        # 默认模式：输出文件名可能因配置变化而改变，同步更新 outputName
        # 使其与 args 内的输出路径保持一致
        if not task.is_custom_args:
            task.outputName = self._get_output_name(file_path, task.is_audio)

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
        self.globalText = Text()
        self.redownloadAction = Action(FluentIcon.UPDATE, self.globalText.Retry, self)
        self.deleteAction = Action(FluentIcon.DELETE, self.globalText.Delete, self)
        self.selectAllAction = Action(
            FluentIcon.SELECT, self.globalText.SelectAll, self
        )
        self.cancelAction = Action(
            FluentIcon.CLEAR_SELECTION, self.globalText.Cancel, self
        )

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
