import re
import sys
from pathlib import Path

from PySide6.QtCore import QEvent, QProcess, Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFileDialog,
    QGridLayout,
    QHBoxLayout,
    QSizePolicy,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from libs.qfluentwidgets_pro import (
    BodyLabel,
    CaptionLabel,
    CardWidget,
    ComboBox,
    IconWidget,
    LineEdit,
    PlainTextEdit,
    PrimaryPushButton,
    PushButton,
    ScrollArea,
    StrongBodyLabel,
    SubtitleLabel,
    TransparentToolButton,
)
from libs.qfluentwidgets_pro import (
    FluentIcon as FIF,
)

from ..common.config import cfg
from ..common.event_bus import ToolTaskInfo, event_bus
from ..common.setting import (
    AUDIO_CONTAINERS,
    IMAGE_CONTAINERS,
    SUBTITLE_CONTAINERS,
    VIDEO_CONTAINERS,
    buildFileFilter,
)
from ..common.text import Text


class FunctionCard(CardWidget):
    """功能入口卡片：图标 + 标题 + 描述，点击发出 clicked 信号（继承自 CardWidget）"""

    def __init__(self, icon, title: str, description: str, name: str = "", parent=None):
        super().__init__(parent=parent)
        self.name = name  # 功能标识，供整页切换区分

        self.iconWidget = IconWidget(icon, self)
        self.iconWidget.setFixedSize(32, 32)

        self.titleLabel = StrongBodyLabel(title, self)
        self.descLabel = CaptionLabel(description, self)
        self.descLabel.setWordWrap(True)
        self.descLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.__initLayout()

    def __initLayout(self):
        # 宽度可伸缩（随视口/列宽自适应），高度固定
        # 避免 fixed 宽度撑开 ScrollArea 导致 right margin 失效
        self.setMinimumSize(180, 140)
        self.setMaximumHeight(140)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 20, 16, 16)
        layout.setSpacing(6)

        layout.addWidget(self.iconWidget, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.titleLabel, 0, Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.descLabel)


class FunctionPage(QWidget):
    """功能页基类：返回按钮 + 标题 + 文件选择区 + 参数区(子类填充) + 执行按钮

    子类需：
    - 在 _initParams() 中向 self.paramLayout 填充参数控件
    - 重写 _buildArgs() 返回 ffmpeg args 列表(走主任务队列)
    - 或重写 _onExecute() 自定义执行逻辑(如媒体信息查看直接展示)
    """

    backRequested = Signal()  # 请求返回入口页

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        # 子类可在调用 super().__init__ 前创建 globalText 以构造标题，此处复用
        if not hasattr(self, "globalText"):
            self.globalText = Text()
        self._title = title

        self.backButton = TransparentToolButton(FIF.RETURN, self)
        self.titleLabel = SubtitleLabel(self._title, self)
        self.filePathEdit = LineEdit(self)
        self.filePathEdit.setPlaceholderText(self.globalText.SelectInputFileHint)
        self.selectButton = PushButton(self.globalText.SelectFile, self)
        self.executeButton = PrimaryPushButton(
            FIF.PLAY_SOLID, self.globalText.Execute, self
        )
        # 默认禁用，选择文件后才启用（见 _onFilePathChanged）
        self.executeButton.setEnabled(False)

        self.paramLayout = QVBoxLayout()

        self.__initWidget()
        self._initParams()

    def __initWidget(self):
        self.__initLayout()
        self._connectSignalToSlot()

    def __initLayout(self):
        mainLayout = QVBoxLayout(self)
        mainLayout.setContentsMargins(36, 20, 36, 20)
        mainLayout.setSpacing(16)

        # 顶部栏：返回按钮 + 标题
        topBar = QHBoxLayout()
        topBar.setSpacing(12)
        topBar.addWidget(self.backButton)
        topBar.addWidget(self.titleLabel)
        topBar.addStretch(1)
        mainLayout.addLayout(topBar)

        # 文件选择区
        fileBar = QHBoxLayout()
        fileBar.setSpacing(12)
        fileBar.addWidget(self.filePathEdit, 1)
        fileBar.addWidget(self.selectButton)
        mainLayout.addLayout(fileBar)

        # 参数区（子类填充）
        self.paramLayout.setSpacing(12)
        mainLayout.addLayout(self.paramLayout)

        # 执行按钮：紧跟参数区右对齐，避免孤悬页面底部
        bottomBar = QHBoxLayout()
        bottomBar.addStretch(1)
        bottomBar.addWidget(self.executeButton)
        mainLayout.addLayout(bottomBar)

        mainLayout.addStretch(1)

    def _connectSignalToSlot(self):
        self.backButton.clicked.connect(self.backRequested)
        self.selectButton.clicked.connect(self._onSelectFile)
        self.executeButton.clicked.connect(self._onExecute)
        self.filePathEdit.textChanged.connect(self._onFilePathChanged)
        # 启用文件拖拽到路径输入框
        self.filePathEdit.setAcceptDrops(True)
        self.filePathEdit.installEventFilter(self)

    def _initParams(self):
        """子类重写：向 self.paramLayout 添加参数控件"""

    def _onFilePathChanged(self, text: str):
        """文件路径变化时切换执行按钮启用状态"""
        self.executeButton.setEnabled(bool(text.strip()))

    # 子类覆盖：输入文件容器集合（空=不过滤）与过滤器显示名（Text 属性名）
    _inputContainers: set = set()
    _inputFilterName: str = "Files"

    def _buildInputFilter(self) -> str:
        """由 _inputContainers 生成文件对话框过滤器"""
        name = getattr(self.globalText, self._inputFilterName)
        if self._inputContainers:
            return (
                f"{buildFileFilter(name, self._inputContainers)};;"
                f"{self.globalText.AllFiles} (*)"
            )
        return f"{self.globalText.AllFiles} (*)"

    def _isAcceptable(self, paths: list) -> list:
        """按 _inputContainers 过滤路径，空集合表示不过滤"""
        if not self._inputContainers:
            return paths
        return [p for p in paths if Path(p).suffix.lower() in self._inputContainers]

    def _onSelectFile(self):
        """选择输入文件（子类可覆盖 _inputContainers 指定文件类型）"""
        path, _ = QFileDialog.getOpenFileName(
            self, self.globalText.SelectFile, "", self._buildInputFilter()
        )
        if path:
            self.filePathEdit.setText(path)

    def eventFilter(self, obj, event):
        """拦截路径输入框的拖拽事件，按 _inputContainers 过滤后填充"""
        if obj is self.filePathEdit:
            if event.type() == QEvent.Type.DragEnter:
                if event.mimeData().hasUrls():
                    paths = [
                        u.toLocalFile()
                        for u in event.mimeData().urls()
                        if u.toLocalFile()
                    ]
                    if self._isAcceptable(paths):
                        event.acceptProposedAction()
                        return True
            elif event.type() == QEvent.Type.Drop:
                paths = [
                    u.toLocalFile() for u in event.mimeData().urls() if u.toLocalFile()
                ]
                paths = self._isAcceptable(paths)
                if paths:
                    self._onFilesDropped(paths)
                    event.acceptProposedAction()
                    return True
        return super().eventFilter(obj, event)

    def _onFilesDropped(self, paths: list):
        """拖拽文件落入：默认取第一个填入路径框，子类可重写以处理多文件"""
        self.filePathEdit.setText(paths[0])

    def _buildArgs(self):
        """子类重写：返回 ffmpeg args 列表，返回 None 表示不走任务队列"""
        return

    def _onExecute(self):
        """执行：默认构建 args 并通过 event_bus 提交到主任务队列

        约定子类 _buildArgs 返回的 args 末尾元素为输出文件路径。
        """
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return
        args = self._buildArgs()
        if not args:
            return
        output_path = Path(args[-1])
        info = ToolTaskInfo(
            input_path=input_path,
            args=args,
            output_name=output_path.name,
            save_folder=str(output_path.parent),
            title=self._title,
        )
        event_bus.addToolTaskSig.emit(info)


class _PlaceholderPage(FunctionPage):
    """占位功能页：功能未实现时展示提示"""

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.FeatureInDevelopment, parent)
        hint = BodyLabel(self.globalText.FeatureInDevelopmentHint, self)
        hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.paramLayout.addWidget(hint)
        # 占位页不需要文件选择和执行按钮
        self.filePathEdit.hide()
        self.selectButton.hide()
        self.executeButton.hide()


class AudioExtractPage(FunctionPage):
    """音频提取：从视频提取音轨并转为指定音频格式（MP3/AAC/WAV/Opus/Vorbis/FLAC）"""

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.AudioExtract, parent)

    def _initParams(self):
        # (格式标识, 显示名, 编码器, 输出扩展名, 是否有损)
        # 标识用于持久化配置，显示名带说明给用户看
        self._FORMATS = [
            ("MP3", "MP3", "libmp3lame", ".mp3", True),
            ("AAC", "AAC", "aac", ".m4a", True),
            ("WAV", self.globalText.FmtWav, "pcm_s16le", ".wav", False),
            ("OPUS", "Opus", "libopus", ".opus", True),
            ("VORBIS", "Vorbis", "libvorbis", ".ogg", True),
            ("FLAC", self.globalText.FmtFlac, "flac", ".flac", False),
        ]
        self.formatCombo = ComboBox(self)
        for _, display, _, _, _ in self._FORMATS:
            self.formatCombo.addItem(display)
        # 从配置恢复格式选择（按标识匹配，与顺序解耦）
        self.formatCombo.setCurrentIndex(
            self._formatIndex(cfg.get(cfg.toolAudioExtractFormat))
        )

        formatRow = QHBoxLayout()
        formatRow.addWidget(BodyLabel(self.globalText.AudioFormat, self))
        formatRow.addWidget(self.formatCombo, 1)
        self.paramLayout.addLayout(formatRow)

        self.bitrateEdit = LineEdit(self)
        self.bitrateEdit.setPlaceholderText(self.globalText.AudioBitrateHint)
        self.bitrateEdit.setText(cfg.get(cfg.toolAudioExtractBitrate))
        bitrateRow = QHBoxLayout()
        bitrateRow.addWidget(BodyLabel(self.globalText.AudioBitrate, self))
        bitrateRow.addWidget(self.bitrateEdit, 1)
        self.paramLayout.addLayout(bitrateRow)

        # 设置变化即持久化
        self.formatCombo.currentIndexChanged.connect(self._onFormatChanged)
        self.bitrateEdit.editingFinished.connect(self._onBitrateChanged)

    def _formatIndex(self, fmtId: str) -> int:
        """格式标识 → _FORMATS 索引，未匹配返回 0"""
        for i, (fid, *_rest) in enumerate(self._FORMATS):
            if fid == fmtId:
                return i
        return 0

    def _onFormatChanged(self, index: int):
        cfg.set(cfg.toolAudioExtractFormat, self._FORMATS[index][0], save=True)

    def _onBitrateChanged(self):
        cfg.set(cfg.toolAudioExtractBitrate, self.bitrateEdit.text().strip(), save=True)

    # 输入：视频文件
    _inputContainers = VIDEO_CONTAINERS
    _inputFilterName = "VideoFiles"

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        idx = self.formatCombo.currentIndex()
        _, _, codec, ext, lossy = self._FORMATS[idx]
        output_path = str(
            Path(input_path).with_name(f"{Path(input_path).stem}_audio{ext}")
        )
        args = ["-i", input_path, "-vn", "-c:a", codec]
        if lossy:
            bitrate = self.bitrateEdit.text().strip()
            if bitrate:
                args += ["-b:a", bitrate]
        args += ["-y", output_path]
        return args


class VideoSnapshotPage(FunctionPage):
    """视频截图：按时间点截取一帧画面"""

    _inputContainers = VIDEO_CONTAINERS
    _inputFilterName = "VideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.VideoSnapshot, parent)

    def _initParams(self):
        # (格式标识, 显示名, 扩展名, 是否有损)
        self._FORMATS = [
            ("PNG", self.globalText.FmtPng, "png", False),
            ("JPG", "JPG", "jpg", True),
            ("WEBP", "WebP", "webp", True),
        ]
        self.timeEdit = LineEdit(self)
        self.timeEdit.setPlaceholderText(self.globalText.TimePointHint)
        self.timeEdit.setText(cfg.get(cfg.toolVideoSnapshotTime))
        timeRow = QHBoxLayout()
        timeRow.addWidget(BodyLabel(self.globalText.TimePoint, self))
        timeRow.addWidget(self.timeEdit, 1)
        self.paramLayout.addLayout(timeRow)

        self.formatCombo = ComboBox(self)
        for _, display, _, _ in self._FORMATS:
            self.formatCombo.addItem(display)
        self.formatCombo.setCurrentIndex(
            self._formatIndex(cfg.get(cfg.toolVideoSnapshotFormat))
        )
        formatRow = QHBoxLayout()
        formatRow.addWidget(BodyLabel(self.globalText.ImageFormat, self))
        formatRow.addWidget(self.formatCombo, 1)
        self.paramLayout.addLayout(formatRow)

        self.timeEdit.editingFinished.connect(self._onTimeChanged)
        self.formatCombo.currentIndexChanged.connect(self._onFormatChanged)

    def _formatIndex(self, fmtId: str) -> int:
        for i, (fid, *_rest) in enumerate(self._FORMATS):
            if fid == fmtId:
                return i
        return 0

    def _onTimeChanged(self):
        cfg.set(cfg.toolVideoSnapshotTime, self.timeEdit.text().strip(), save=True)

    def _onFormatChanged(self, index: int):
        cfg.set(cfg.toolVideoSnapshotFormat, self._FORMATS[index][0], save=True)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        time = self.timeEdit.text().strip()
        _, _, ext, lossy = self._FORMATS[self.formatCombo.currentIndex()]
        output_path = str(
            Path(input_path).with_name(f"{Path(input_path).stem}_snapshot.{ext}")
        )
        args = []
        if time:
            args += ["-ss", time]
        args += ["-i", input_path, "-frames:v", "1"]
        if lossy:
            args += ["-q:v", "2"]
        args += ["-y", output_path]
        return args


class GifMakePage(FunctionPage):
    """GIF 制作：视频片段转为 GIF 动图"""

    _FPS = [10, 15, 20, 24]
    _inputContainers = VIDEO_CONTAINERS
    _inputFilterName = "VideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.GifMake, parent)

    def _initParams(self):
        # (标识, 显示名)
        self._WIDTHS = [
            ("480", "480px"),
            ("640", "640px"),
            ("320", "320px"),
            ("origin", self.globalText.OriginResolution),
        ]
        self.startEdit = LineEdit(self)
        self.startEdit.setPlaceholderText(self.globalText.StartTimeHint)
        self.startEdit.setText(cfg.get(cfg.toolGifMakeStart))
        startRow = QHBoxLayout()
        startRow.addWidget(BodyLabel(self.globalText.StartTime, self))
        startRow.addWidget(self.startEdit, 1)
        self.paramLayout.addLayout(startRow)

        self.durationEdit = LineEdit(self)
        self.durationEdit.setPlaceholderText(self.globalText.DurationHint)
        self.durationEdit.setText(cfg.get(cfg.toolGifMakeDuration))
        durationRow = QHBoxLayout()
        durationRow.addWidget(BodyLabel(self.globalText.Duration, self))
        durationRow.addWidget(self.durationEdit, 1)
        self.paramLayout.addLayout(durationRow)

        self.widthCombo = ComboBox(self)
        for _, label in self._WIDTHS:
            self.widthCombo.addItem(label)
        self.widthCombo.setCurrentIndex(self._widthIndex(cfg.get(cfg.toolGifMakeWidth)))
        widthRow = QHBoxLayout()
        widthRow.addWidget(BodyLabel(self.globalText.Width, self))
        widthRow.addWidget(self.widthCombo, 1)
        self.paramLayout.addLayout(widthRow)

        self.fpsCombo = ComboBox(self)
        for fps in self._FPS:
            self.fpsCombo.addItem(str(fps))
        self.fpsCombo.setCurrentIndex(self._fpsIndex(cfg.get(cfg.toolGifMakeFps)))
        fpsRow = QHBoxLayout()
        fpsRow.addWidget(BodyLabel(self.globalText.FrameRate, self))
        fpsRow.addWidget(self.fpsCombo, 1)
        self.paramLayout.addLayout(fpsRow)

        self.startEdit.editingFinished.connect(self._onStartChanged)
        self.durationEdit.editingFinished.connect(self._onDurationChanged)
        self.widthCombo.currentIndexChanged.connect(self._onWidthChanged)
        self.fpsCombo.currentIndexChanged.connect(self._onFpsChanged)

    def _widthIndex(self, wid: str) -> int:
        for i, (w, *_rest) in enumerate(self._WIDTHS):
            if w == wid:
                return i
        return 0

    def _fpsIndex(self, fps) -> int:
        for i, f in enumerate(self._FPS):
            if f == fps:
                return i
        return 1  # 默认 15

    def _onStartChanged(self):
        cfg.set(cfg.toolGifMakeStart, self.startEdit.text().strip(), save=True)

    def _onDurationChanged(self):
        cfg.set(cfg.toolGifMakeDuration, self.durationEdit.text().strip(), save=True)

    def _onWidthChanged(self, index: int):
        cfg.set(cfg.toolGifMakeWidth, self._WIDTHS[index][0], save=True)

    def _onFpsChanged(self, index: int):
        cfg.set(cfg.toolGifMakeFps, self._FPS[index], save=True)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        start = self.startEdit.text().strip()
        duration = self.durationEdit.text().strip()
        wid = self._WIDTHS[self.widthCombo.currentIndex()][0]
        fps = self._FPS[self.fpsCombo.currentIndex()]
        output_path = str(Path(input_path).with_name(f"{Path(input_path).stem}.gif"))
        # 滤镜：fps 抽帧 + scale 缩放（-1 保持比例）
        vf = f"fps={fps}"
        if wid != "origin":
            vf += f",scale={wid}:-1:flags=lanczos"
        args = []
        if start:
            args += ["-ss", start]
        if duration:
            args += ["-t", duration]
        args += ["-i", input_path, "-vf", vf, "-y", output_path]
        return args


class VideoCutPage(FunctionPage):
    """视频剪切：按时间段裁剪视频"""

    _inputContainers = VIDEO_CONTAINERS
    _inputFilterName = "VideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.VideoCut, parent)

    def _initParams(self):
        # (模式标识, 显示名)
        self._MODES = [
            ("copy", self.globalText.ModeFastCopy),
            ("accurate", self.globalText.ModeAccurateCut),
        ]
        self.startEdit = LineEdit(self)
        self.startEdit.setPlaceholderText(self.globalText.CutStartHint)
        self.startEdit.setText(cfg.get(cfg.toolVideoCutStart))
        startRow = QHBoxLayout()
        startRow.addWidget(BodyLabel(self.globalText.StartTime, self))
        startRow.addWidget(self.startEdit, 1)
        self.paramLayout.addLayout(startRow)

        self.durationEdit = LineEdit(self)
        self.durationEdit.setPlaceholderText(self.globalText.CutDurationHint)
        self.durationEdit.setText(cfg.get(cfg.toolVideoCutDuration))
        durationRow = QHBoxLayout()
        durationRow.addWidget(BodyLabel(self.globalText.Duration, self))
        durationRow.addWidget(self.durationEdit, 1)
        self.paramLayout.addLayout(durationRow)

        self.modeCombo = ComboBox(self)
        for _, label in self._MODES:
            self.modeCombo.addItem(label)
        self.modeCombo.setCurrentIndex(self._modeIndex(cfg.get(cfg.toolVideoCutMode)))
        modeRow = QHBoxLayout()
        modeRow.addWidget(BodyLabel(self.globalText.CutMode, self))
        modeRow.addWidget(self.modeCombo, 1)
        self.paramLayout.addLayout(modeRow)

        self.startEdit.editingFinished.connect(self._onStartChanged)
        self.durationEdit.editingFinished.connect(self._onDurationChanged)
        self.modeCombo.currentIndexChanged.connect(self._onModeChanged)

    def _modeIndex(self, modeId: str) -> int:
        for i, (mid, *_rest) in enumerate(self._MODES):
            if mid == modeId:
                return i
        return 0

    def _onStartChanged(self):
        cfg.set(cfg.toolVideoCutStart, self.startEdit.text().strip(), save=True)

    def _onDurationChanged(self):
        cfg.set(cfg.toolVideoCutDuration, self.durationEdit.text().strip(), save=True)

    def _onModeChanged(self, index: int):
        cfg.set(cfg.toolVideoCutMode, self._MODES[index][0], save=True)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        start = self.startEdit.text().strip()
        duration = self.durationEdit.text().strip()
        if not start and not duration:
            return None
        mode = self._MODES[self.modeCombo.currentIndex()][0]
        ext = Path(input_path).suffix
        output_path = str(
            Path(input_path).with_name(f"{Path(input_path).stem}_cut{ext}")
        )
        args = []
        if start:
            args += ["-ss", start]
        if duration:
            args += ["-t", duration]
        args += ["-i", input_path]
        if mode == "copy":
            args += ["-c", "copy"]
        args += ["-y", output_path]
        return args


class MediaConvertPage(FunctionPage):
    """音视频格式转换：容器与编码转换"""

    # (标识, 显示名, 视频编码, 音频编码, 扩展名)
    _PRESETS = [
        ("MP4_H264", "MP4 (H.264 + AAC)", "libx264", "aac", ".mp4"),
        ("MP4_H265", "MP4 (H.265 + AAC)", "libx265", "aac", ".mp4"),
        ("MKV_H264", "MKV (H.264 + AAC)", "libx264", "aac", ".mkv"),
        ("WEBM_VP9", "WebM (VP9 + Opus)", "libvpx-vp9", "libopus", ".webm"),
        ("MOV_H264", "MOV (H.264 + AAC)", "libx264", "aac", ".mov"),
    ]
    _inputContainers = VIDEO_CONTAINERS | AUDIO_CONTAINERS
    _inputFilterName = "AudioVideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.MediaConvert, parent)

    def _initParams(self):
        self.presetCombo = ComboBox(self)
        for _, display, _, _, _ in self._PRESETS:
            self.presetCombo.addItem(display)
        self.presetCombo.setCurrentIndex(
            self._presetIndex(cfg.get(cfg.toolMediaConvertPreset))
        )
        presetRow = QHBoxLayout()
        presetRow.addWidget(BodyLabel(self.globalText.OutputFormat, self))
        presetRow.addWidget(self.presetCombo, 1)
        self.paramLayout.addLayout(presetRow)

        self.presetCombo.currentIndexChanged.connect(self._onPresetChanged)

    @classmethod
    def _presetIndex(cls, presetId: str) -> int:
        for i, (pid, *_rest) in enumerate(cls._PRESETS):
            if pid == presetId:
                return i
        return 0

    def _onPresetChanged(self, index: int):
        cfg.set(cfg.toolMediaConvertPreset, self._PRESETS[index][0], save=True)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        _, _, vcodec, acodec, ext = self._PRESETS[self.presetCombo.currentIndex()]
        output_path = str(
            Path(input_path).with_name(f"{Path(input_path).stem}_converted{ext}")
        )
        args = ["-i", input_path, "-c:v", vcodec, "-c:a", acodec, "-y", output_path]
        return args


class ImageConvertPage(FunctionPage):
    """图片格式转换：图片格式互转与质量压缩"""

    _inputContainers = IMAGE_CONTAINERS
    _inputFilterName = "ImageFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.ImageConvert, parent)

    def _initParams(self):
        # (格式标识, 显示名, 扩展名, 是否有损)
        self._FORMATS = [
            ("JPG", "JPG", "jpg", True),
            ("PNG", self.globalText.FmtPng, "png", False),
            ("WEBP", "WebP", "webp", True),
            ("BMP", self.globalText.FmtBmp, "bmp", False),
        ]
        self.formatCombo = ComboBox(self)
        for _, display, _, _ in self._FORMATS:
            self.formatCombo.addItem(display)
        self.formatCombo.setCurrentIndex(
            self._formatIndex(cfg.get(cfg.toolImageConvertFormat))
        )
        formatRow = QHBoxLayout()
        formatRow.addWidget(BodyLabel(self.globalText.OutputFormat, self))
        formatRow.addWidget(self.formatCombo, 1)
        self.paramLayout.addLayout(formatRow)

        self.qualityEdit = LineEdit(self)
        self.qualityEdit.setPlaceholderText(self.globalText.QualityHint)
        self.qualityEdit.setText(cfg.get(cfg.toolImageConvertQuality))
        qualityRow = QHBoxLayout()
        qualityRow.addWidget(BodyLabel(self.globalText.Quality, self))
        qualityRow.addWidget(self.qualityEdit, 1)
        self.paramLayout.addLayout(qualityRow)

        self.formatCombo.currentIndexChanged.connect(self._onFormatChanged)
        self.qualityEdit.editingFinished.connect(self._onQualityChanged)

    def _formatIndex(self, fmtId: str) -> int:
        for i, (fid, *_rest) in enumerate(self._FORMATS):
            if fid == fmtId:
                return i
        return 0

    def _onFormatChanged(self, index: int):
        cfg.set(cfg.toolImageConvertFormat, self._FORMATS[index][0], save=True)

    def _onQualityChanged(self):
        cfg.set(cfg.toolImageConvertQuality, self.qualityEdit.text().strip(), save=True)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        _, _, ext, lossy = self._FORMATS[self.formatCombo.currentIndex()]
        output_path = str(
            Path(input_path).with_name(f"{Path(input_path).stem}_converted.{ext}")
        )
        args = ["-i", input_path]
        if lossy:
            q = self.qualityEdit.text().strip()
            if q:
                args += ["-q:v", q]
        args += ["-y", output_path]
        return args


class VideoConcatPage(FunctionPage):
    """视频拼接：合并多个视频文件（concat filter 重编码统一）"""

    _inputContainers = VIDEO_CONTAINERS
    _inputFilterName = "VideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.VideoConcat, parent)
        self._files: list = []

    def _initParams(self):
        # (模式标识, 显示名)
        self._MODES = [
            ("av", self.globalText.ConcatAv),
            ("video", self.globalText.ConcatVideo),
        ]
        self.modeCombo = ComboBox(self)
        for _, label in self._MODES:
            self.modeCombo.addItem(label)
        self.modeCombo.setCurrentIndex(
            self._modeIndex(cfg.get(cfg.toolVideoConcatMode))
        )
        modeRow = QHBoxLayout()
        modeRow.addWidget(BodyLabel(self.globalText.ConcatContent, self))
        modeRow.addWidget(self.modeCombo, 1)
        self.paramLayout.addLayout(modeRow)

        hint = CaptionLabel(self.globalText.ConcatHint, self)
        hint.setWordWrap(True)
        self.paramLayout.addWidget(hint)

        self.modeCombo.currentIndexChanged.connect(self._onModeChanged)

    def _modeIndex(self, modeId: str) -> int:
        for i, (mid, *_rest) in enumerate(self._MODES):
            if mid == modeId:
                return i
        return 0

    def _onModeChanged(self, index: int):
        cfg.set(cfg.toolVideoConcatMode, self._MODES[index][0], save=True)

    def _onSelectFile(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, self.globalText.SelectVideoFiles, "", self._buildInputFilter()
        )
        if paths:
            self._setFiles(paths)

    def _onFilesDropped(self, paths: list):
        self._setFiles(paths)

    def _setFiles(self, paths: list):
        self._files = paths
        self.filePathEdit.setText(self.globalText.FilesSelected.format(len(paths)))

    def _buildArgs(self):
        if len(self._files) < 2:
            return None
        mode = self._MODES[self.modeCombo.currentIndex()][0]
        n = len(self._files)
        args = []
        for f in self._files:
            args += ["-i", f]
        # scale2ref 链：后续视频缩放到第一个的尺寸，setsar 统一 SAR，
        # 保证 concat filter 输入参数一致（避免分辨率/SAR 不匹配报错）
        scale_filters = []
        ref = "0:v"
        for i in range(1, n):
            ref_out = f"v0r{i}"
            scale_filters.append(f"[{i}:v][{ref}]scale2ref[v{i}][{ref_out}]")
            ref = ref_out
        setsar_filters = [f"[{ref}]setsar=1[v0]"]
        for i in range(1, n):
            setsar_filters.append(f"[v{i}]setsar=1[v{i}s]")
        if mode == "video":
            concat_inputs = "[v0]" + "".join(f"[v{i}s]" for i in range(1, n))
            concat = f"concat=n={n}:v=1:a=0[v]"
            maps = ["-map", "[v]"]
        else:
            concat_inputs = "[v0][0:a]" + "".join(
                f"[v{i}s][{i}:a]" for i in range(1, n)
            )
            concat = f"concat=n={n}:v=1:a=1[v][a]"
            maps = ["-map", "[v]", "-map", "[a]"]
        vf = ";".join(scale_filters + setsar_filters) + ";" + concat_inputs + concat
        first = self._files[0]
        output = str(Path(first).with_name(f"{Path(first).stem}_concat.mp4"))
        args += ["-filter_complex", vf] + maps + ["-y", output]
        return args

    def _onExecute(self):
        if not self._files:
            return
        args = self._buildArgs()
        if not args:
            return
        output_path = Path(args[-1])
        info = ToolTaskInfo(
            input_path=self._files[0],
            args=args,
            output_name=output_path.name,
            save_folder=str(output_path.parent),
            title=self._title,
        )
        event_bus.addToolTaskSig.emit(info)


class _ProbeWorker(QThread):
    """媒体信息探测线程：运行 ffmpeg -i，从 stderr 取输入文件信息"""

    infoReady = Signal(str)

    def __init__(self, ffmpegPath: str, path: str, text: Text, parent=None):
        super().__init__(parent)
        self._ffmpeg = ffmpegPath
        self._path = path
        self._text = text

    def run(self):
        proc = QProcess()
        proc.start(self._ffmpeg, ["-i", self._path])
        if not proc.waitForStarted(5000):
            self.infoReady.emit(self._text.FailToStartFfmpeg.format(self._ffmpeg))
            return
        proc.waitForFinished(15000)
        stderr = bytes(proc.readAllStandardError()).decode("utf-8", errors="replace")
        self.infoReady.emit(self._parse(stderr))

    def _parse(self, stderr: str) -> str:
        if not stderr:
            return self._text.NoInfo
        lines = []
        m = re.search(r"Input #0, ([^,]+), from '([^']*)'", stderr)
        if m:
            lines.append(self._text.FileLabel.format(m.group(2)))
            lines.append(self._text.FormatLabel.format(m.group(1)))
        m = re.search(r"Duration:\s*([\d:.]+)", stderr)
        if m:
            lines.append(self._text.DurationLabel.format(m.group(1)))
        m = re.search(r"bitrate:\s*(\d+)\s*kb/s", stderr)
        if m:
            lines.append(self._text.BitrateLabel.format(m.group(1)))
        for raw in stderr.splitlines():
            if not raw.lstrip().startswith("Stream #"):
                continue
            sm = re.search(r"Stream #\d+:\d+.*?:\s*(Video|Audio):\s*(\S+)", raw)
            if not sm:
                continue
            ctype, codec = sm.group(1), sm.group(2)
            if ctype == "Video":
                res = re.search(r",\s*(\d+x\d+)", raw)
                fps = re.search(r",\s*(\d+(?:\.\d+)?)\s*fps", raw) or re.search(
                    r",\s*(\d+(?:\.\d+)?)\s*tbr", raw
                )
                parts = [self._text.VideoStreamLabel.format(codec)]
                if res:
                    parts.append(res.group(1))
                if fps:
                    parts.append(self._text.FpsLabel.format(fps.group(1)))
                lines.append(", ".join(parts))
            else:
                hz = re.search(r",\s*(\d+)\s*Hz", raw)
                ch = re.search(r",\s*(mono|stereo)", raw)
                parts = [self._text.AudioStreamLabel.format(codec)]
                if hz:
                    parts.append(self._text.HzLabel.format(hz.group(1)))
                if ch:
                    parts.append(
                        self._text.Mono if ch.group(1) == "mono" else self._text.Stereo
                    )
                lines.append(", ".join(parts))
        if not lines:
            return self._text.NoInfoParsed
        return "\n".join(lines)


class MediaInfoPage(FunctionPage):
    """媒体信息：查看编码/码率/时长等详细信息（QThread 异步探测，不走任务队列）"""

    _inputContainers = VIDEO_CONTAINERS | AUDIO_CONTAINERS | IMAGE_CONTAINERS
    _inputFilterName = "MediaFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.MediaInfo, parent)
        self._worker = None

    def _initParams(self):
        self.infoEdit = PlainTextEdit(self)
        self.infoEdit.setReadOnly(True)
        self.infoEdit.setPlaceholderText(self.globalText.MediaInfoPlaceholder)
        self.paramLayout.addWidget(self.infoEdit)

    def _onExecute(self):
        if self._worker is not None and self._worker.isRunning():
            return
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return
        self.executeButton.setEnabled(False)
        self.infoEdit.setPlainText(self.globalText.Probing)
        self._worker = _ProbeWorker(
            cfg.get(cfg.ffmpegPath), input_path, self.globalText
        )
        self._worker.infoReady.connect(self._onInfoReady)
        self._worker.start()

    def _onInfoReady(self, info: str):
        self.infoEdit.setPlainText(info)
        self.executeButton.setEnabled(bool(self.filePathEdit.text().strip()))


class MsStoreLogoPage(FunctionPage):
    """MS Store 徽标：一键生成上架微软商店的五个徽标"""

    # (文件名, 宽, 高)
    _SIZES = [
        ("Logo_720x1080.png", 720, 1080),
        ("Logo_1080x1080.png", 1080, 1080),
        ("Logo_300x300.png", 300, 300),
        ("Logo_150x150.png", 150, 150),
        ("Logo_71x71.png", 71, 71),
    ]
    _inputContainers = IMAGE_CONTAINERS
    _inputFilterName = "ImageFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.MsStoreLogo, parent)

    def _initParams(self):
        hint = CaptionLabel(
            self.globalText.MsStoreLogoHint.format(
                "、".join(name for name, _, _ in self._SIZES)
            ),
            self,
        )
        hint.setWordWrap(True)
        self.paramLayout.addWidget(hint)

    def _buildArgs(self):
        # 批量任务在 _onExecute 中提交，不用于单任务
        return None

    def _onExecute(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return
        folder = str(Path(input_path).parent)
        for name, w, h in self._SIZES:
            output = str(Path(folder) / name)
            # 保持原始比例缩放至画布内（contain），居中并用透明填充补齐到目标尺寸
            vf = (
                f"scale={w}:{h}:force_original_aspect_ratio=decrease:flags=lanczos,"
                f"pad={w}:{h}:-1:-1:color=black@0,format=rgba"
            )
            args = ["-i", input_path, "-vf", vf, "-y", output]
            info = ToolTaskInfo(
                input_path=input_path,
                args=args,
                output_name=name,
                save_folder=folder,
                title=self.globalText.MsStoreLogoTaskTitle.format(name),
                allow_duplicate=True,
            )
            event_bus.addToolTaskSig.emit(info)


class SubtitlePage(FunctionPage):
    """字幕处理：提取 / 嵌入硬字幕 / 嵌入软字幕 / 格式转换"""

    # (格式标识, 显示名, 扩展名)
    _CONVERT_FORMATS = [
        ("SRT", "SRT", ".srt"),
        ("ASS", "ASS", ".ass"),
        ("VTT", "VTT", ".vtt"),
    ]
    _inputContainers = VIDEO_CONTAINERS | SUBTITLE_CONTAINERS
    _inputFilterName = "MediaFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.Subtitle, parent)

    def _initParams(self):
        # (模式标识, 显示名)
        self._MODES = [
            ("extract", self.globalText.ModeSubtitleExtract),
            ("burn", self.globalText.ModeSubtitleBurn),
            ("embed", self.globalText.ModeSubtitleEmbed),
            ("convert", self.globalText.ModeSubtitleConvert),
        ]
        self.modeCombo = ComboBox(self)
        for _, label in self._MODES:
            self.modeCombo.addItem(label)
        self.modeCombo.setCurrentIndex(self._modeIndex(cfg.get(cfg.toolSubtitleMode)))
        modeRow = QHBoxLayout()
        modeRow.addWidget(BodyLabel(self.globalText.SubtitleMode, self))
        modeRow.addWidget(self.modeCombo, 1)
        self.paramLayout.addLayout(modeRow)

        # 字幕文件选择行（仅 burn/embed 可见）
        self.subContainer = QWidget(self)
        subRow = QHBoxLayout(self.subContainer)
        subRow.setContentsMargins(0, 0, 0, 0)
        subRow.addWidget(BodyLabel(self.globalText.SubtitleFile, self))
        self.subtitlePathEdit = LineEdit(self)
        self.subtitlePathEdit.setPlaceholderText(self.globalText.SelectSubtitleHint)
        subRow.addWidget(self.subtitlePathEdit, 1)
        self.subtitleSelectButton = PushButton(self.globalText.SelectSubtitle, self)
        subRow.addWidget(self.subtitleSelectButton)
        self.paramLayout.addWidget(self.subContainer)

        # 转换格式行（仅 convert 可见）
        self.convertContainer = QWidget(self)
        convertRow = QHBoxLayout(self.convertContainer)
        convertRow.setContentsMargins(0, 0, 0, 0)
        convertRow.addWidget(BodyLabel(self.globalText.OutputFormat, self))
        self.convertFormatCombo = ComboBox(self)
        for _, display, _ in self._CONVERT_FORMATS:
            self.convertFormatCombo.addItem(display)
        self.convertFormatCombo.setCurrentIndex(
            self._convertIndex(cfg.get(cfg.toolSubtitleConvertFormat))
        )
        convertRow.addWidget(self.convertFormatCombo, 1)
        self.paramLayout.addWidget(self.convertContainer)

        self.modeCombo.currentIndexChanged.connect(self._onModeChanged)
        self.subtitleSelectButton.clicked.connect(self._onSelectSubtitle)
        self.convertFormatCombo.currentIndexChanged.connect(
            self._onConvertFormatChanged
        )
        self._updateModeVisibility()

    def _updateModeVisibility(self):
        mode = self._MODES[self.modeCombo.currentIndex()][0]
        self.subContainer.setVisible(mode in ("burn", "embed"))
        self.convertContainer.setVisible(mode == "convert")

    def _modeIndex(self, modeId: str) -> int:
        for i, (mid, *_rest) in enumerate(self._MODES):
            if mid == modeId:
                return i
        return 0

    @classmethod
    def _convertIndex(cls, fmtId: str) -> int:
        for i, (fid, *_rest) in enumerate(cls._CONVERT_FORMATS):
            if fid == fmtId:
                return i
        return 0

    def _onModeChanged(self, index: int):
        cfg.set(cfg.toolSubtitleMode, self._MODES[index][0], save=True)
        self._updateModeVisibility()

    def _onConvertFormatChanged(self, index: int):
        cfg.set(
            cfg.toolSubtitleConvertFormat, self._CONVERT_FORMATS[index][0], save=True
        )

    def _onSelectSubtitle(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            self.globalText.SelectSubtitleFile,
            "",
            f"{buildFileFilter(self.globalText.SubtitleFiles, SUBTITLE_CONTAINERS)};;"
            f"{self.globalText.AllFiles} (*)",
        )
        if path:
            self.subtitlePathEdit.setText(path)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        mode = self._MODES[self.modeCombo.currentIndex()][0]
        stem = Path(input_path).stem

        if mode == "extract":
            # 提取第一条字幕轨到 SRT
            output = str(Path(input_path).with_name(f"{stem}_subtitle.srt"))
            return ["-i", input_path, "-map", "0:s:0", "-y", output]

        if mode == "burn":
            # 硬字幕：subtitles 滤镜烧录到画面，音频复制
            sub_path = self.subtitlePathEdit.text().strip()
            if not sub_path:
                return None
            # 转义路径用于 subtitles 滤镜（跨平台）：
            # Windows 反斜杠→正斜杠；转义 \ : ' 后用单引号包裹
            # ffmpeg 的 av_get_token 在单引号内仍处理 \ 转义，故 \: → : 等
            if sys.platform == "win32":
                sub_path = sub_path.replace("\\", "/")
            escaped = (
                sub_path.replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
            )
            output = str(Path(input_path).with_name(f"{stem}_subburned.mp4"))
            return [
                "-i",
                input_path,
                "-vf",
                f"subtitles='{escaped}'",
                "-c:a",
                "copy",
                "-y",
                output,
            ]

        if mode == "embed":
            # 软字幕：作为可选字幕轨嵌入，音视频复制
            sub_path = self.subtitlePathEdit.text().strip()
            if not sub_path:
                return None
            ext = Path(input_path).suffix
            output = str(Path(input_path).with_name(f"{stem}_subembedded{ext}"))
            # MP4 用 mov_text，MKV 等直接 copy
            sub_codec = "mov_text" if ext.lower() == ".mp4" else "copy"
            return [
                "-i",
                input_path,
                "-i",
                sub_path,
                "-c",
                "copy",
                "-c:s",
                sub_codec,
                "-y",
                output,
            ]

        # convert：字幕格式互转
        _, _, out_ext = self._CONVERT_FORMATS[self.convertFormatCombo.currentIndex()]
        output = str(Path(input_path).with_name(f"{stem}_converted{out_ext}"))
        return ["-i", input_path, "-y", output]


class LoudnormPage(FunctionPage):
    """音量归一化：EBU R128 标准响度 / 动态范围归一化"""

    _inputContainers = VIDEO_CONTAINERS | AUDIO_CONTAINERS
    _inputFilterName = "AudioVideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.Loudnorm, parent)

    def _initParams(self):
        # (模式标识, 显示名)
        self._MODES = [
            ("loudnorm", self.globalText.ModeLoudnorm),
            ("dynaudnorm", self.globalText.ModeDynaudnorm),
        ]
        self.modeCombo = ComboBox(self)
        for _, label in self._MODES:
            self.modeCombo.addItem(label)
        self.modeCombo.setCurrentIndex(self._modeIndex(cfg.get(cfg.toolLoudnormMode)))
        modeRow = QHBoxLayout()
        modeRow.addWidget(BodyLabel(self.globalText.LoudnormMode, self))
        modeRow.addWidget(self.modeCombo, 1)
        self.paramLayout.addLayout(modeRow)

        self.targetEdit = LineEdit(self)
        self.targetEdit.setPlaceholderText(self.globalText.TargetLoudnessHint)
        self.targetEdit.setText(cfg.get(cfg.toolLoudnormTarget))
        targetRow = QHBoxLayout()
        targetRow.addWidget(BodyLabel(self.globalText.TargetLoudness, self))
        targetRow.addWidget(self.targetEdit, 1)
        self.paramLayout.addLayout(targetRow)

        hint = CaptionLabel(self.globalText.LoudnormHint, self)
        hint.setWordWrap(True)
        self.paramLayout.addWidget(hint)

        self.modeCombo.currentIndexChanged.connect(self._onModeChanged)
        self.targetEdit.editingFinished.connect(self._onTargetChanged)

    def _modeIndex(self, modeId: str) -> int:
        for i, (mid, *_rest) in enumerate(self._MODES):
            if mid == modeId:
                return i
        return 0

    def _onModeChanged(self, index: int):
        cfg.set(cfg.toolLoudnormMode, self._MODES[index][0], save=True)

    def _onTargetChanged(self):
        cfg.set(cfg.toolLoudnormTarget, self.targetEdit.text().strip(), save=True)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        mode = self._MODES[self.modeCombo.currentIndex()][0]
        ext = Path(input_path).suffix
        output = str(
            Path(input_path).with_name(f"{Path(input_path).stem}_normalized{ext}")
        )
        is_audio_only = ext.lower() in AUDIO_CONTAINERS

        if mode == "loudnorm":
            target = self.targetEdit.text().strip() or "-16"
            af = f"loudnorm=I={target}:TP=-1.5:LRA=11"
        else:
            af = "dynaudnorm"

        args = ["-i", input_path, "-af", af]
        if not is_audio_only:
            args += ["-c:v", "copy"]
        args += ["-y", output]
        return args


class SpeedPage(FunctionPage):
    """速度调整：视频/音频变速（atempo 链式支持 0.25x–4x+）"""

    _inputContainers = VIDEO_CONTAINERS | AUDIO_CONTAINERS
    _inputFilterName = "AudioVideoFiles"

    def __init__(self, parent=None):
        self.globalText = Text()
        super().__init__(self.globalText.Speed, parent)

    def _initParams(self):
        # (模式标识, 显示名)
        self._MODES = [
            ("av", self.globalText.ModeSpeedAv),
            ("video", self.globalText.ModeSpeedVideo),
            ("audio", self.globalText.ModeSpeedAudio),
        ]
        self.factorEdit = LineEdit(self)
        self.factorEdit.setPlaceholderText(self.globalText.SpeedFactorHint)
        self.factorEdit.setText(cfg.get(cfg.toolSpeedFactor))
        factorRow = QHBoxLayout()
        factorRow.addWidget(BodyLabel(self.globalText.SpeedFactor, self))
        factorRow.addWidget(self.factorEdit, 1)
        self.paramLayout.addLayout(factorRow)

        self.modeCombo = ComboBox(self)
        for _, label in self._MODES:
            self.modeCombo.addItem(label)
        self.modeCombo.setCurrentIndex(self._modeIndex(cfg.get(cfg.toolSpeedMode)))
        modeRow = QHBoxLayout()
        modeRow.addWidget(BodyLabel(self.globalText.SpeedMode, self))
        modeRow.addWidget(self.modeCombo, 1)
        self.paramLayout.addLayout(modeRow)

        hint = CaptionLabel(self.globalText.SpeedHint, self)
        hint.setWordWrap(True)
        self.paramLayout.addWidget(hint)

        self.factorEdit.editingFinished.connect(self._onFactorChanged)
        self.modeCombo.currentIndexChanged.connect(self._onModeChanged)

    def _modeIndex(self, modeId: str) -> int:
        for i, (mid, *_rest) in enumerate(self._MODES):
            if mid == modeId:
                return i
        return 0

    def _onFactorChanged(self):
        cfg.set(cfg.toolSpeedFactor, self.factorEdit.text().strip(), save=True)

    def _onModeChanged(self, index: int):
        cfg.set(cfg.toolSpeedMode, self._MODES[index][0], save=True)

    @staticmethod
    def _build_atempo(factor: float) -> str:
        """构建 atempo 滤镜链，支持超出 0.5-2.0 范围的倍率（链式串联）

        atempo 单次有效范围 0.5-2.0，超出时通过串联实现：
        4x = atempo=2.0,atempo=2.0；0.25x = atempo=0.5,atempo=0.5
        """
        filters = []
        remaining = factor
        while remaining > 2.0:
            filters.append("atempo=2.0")
            remaining /= 2.0
        while remaining < 0.5:
            filters.append("atempo=0.5")
            remaining /= 0.5
        filters.append(f"atempo={remaining:.4f}")
        return ",".join(filters)

    def _buildArgs(self):
        input_path = self.filePathEdit.text().strip()
        if not input_path:
            return None
        factor_str = self.factorEdit.text().strip()
        try:
            factor = float(factor_str)
        except ValueError:
            return None
        if factor <= 0:
            return None
        mode = self._MODES[self.modeCombo.currentIndex()][0]
        ext = Path(input_path).suffix
        output = str(Path(input_path).with_name(f"{Path(input_path).stem}_speed{ext}"))
        atempo = self._build_atempo(factor)

        if mode == "av":
            vf = f"[0:v]setpts=PTS/{factor}[v];[0:a]{atempo}[a]"
            return [
                "-i",
                input_path,
                "-filter_complex",
                vf,
                "-map",
                "[v]",
                "-map",
                "[a]",
                "-y",
                output,
            ]
        if mode == "video":
            return [
                "-i",
                input_path,
                "-vf",
                f"setpts=PTS/{factor}",
                "-an",
                "-y",
                output,
            ]
        # audio
        return ["-i", input_path, "-af", atempo, "-vn", "-y", output]


class MoreInterface(QWidget):
    """更多功能页：卡片入口 + 功能页整页切换(QStackedWidget)

    入口页(卡片网格)作为 index 0，点击卡片整页切换到对应功能页；
    功能页顶部"返回"切回入口页。功能页通过 addFunctionPage() 注册。
    """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.globalText = Text()
        self._cards: dict[str, FunctionCard] = {}  # name -> card
        self._pageIndex: dict[str, int] = {}  # name -> stack 索引
        self._placeholderPage = None  # 占位页，懒创建

        self.stackedWidget = QStackedWidget(self)
        self.homePage = ScrollArea(self)  # 入口页（卡片网格）

        self.__initWidget()
        self._registerPages()

    def __initWidget(self):
        # addSubInterface 要求 objectName 非空，设到 MoreInterface 自身
        # （入口页 ScrollArea 内部另设同名用于样式表）
        self.setObjectName("moreInterface")
        self.__initLayout()
        self.__initHomePage()

    def __initLayout(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.stackedWidget)

    def _registerPages(self):
        """注册已实现的功能页（替换占位页）"""
        self.addFunctionPage("audio_extract", AudioExtractPage(self))
        self.addFunctionPage("video_snapshot", VideoSnapshotPage(self))
        self.addFunctionPage("gif_make", GifMakePage(self))
        self.addFunctionPage("video_cut", VideoCutPage(self))
        self.addFunctionPage("media_convert", MediaConvertPage(self))
        self.addFunctionPage("image_convert", ImageConvertPage(self))
        self.addFunctionPage("video_concat", VideoConcatPage(self))
        self.addFunctionPage("media_info", MediaInfoPage(self))
        self.addFunctionPage("ms_store_logo", MsStoreLogoPage(self))
        self.addFunctionPage("subtitle", SubtitlePage(self))
        self.addFunctionPage("loudnorm", LoudnormPage(self))
        self.addFunctionPage("speed", SpeedPage(self))

    def __initHomePage(self):
        """填充入口页：ScrollArea + 卡片网格（所有分组共用单一网格对齐）"""
        self.homePage.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.homePage.setWidgetResizable(True)
        self.homePage.setObjectName("moreInterface")
        self.homePage.enableTransparentBackground()

        view = ScrollArea(self.homePage)
        mainLayout = QVBoxLayout(view)
        mainLayout.setContentsMargins(36, 36, 36, 36)
        mainLayout.setSpacing(0)

        gridContainer = QWidget(view)
        gridLayout = QGridLayout(gridContainer)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setHorizontalSpacing(12)
        gridLayout.setVerticalSpacing(12)

        columns = 3
        t = self.globalText
        groups = [
            (
                t.ImageTools,
                [
                    (FIF.PHOTO, t.ImageConvert, t.ImageConvertDesc, "image_convert"),
                    (FIF.LAYOUT, t.MsStoreLogo, t.MsStoreLogoDesc, "ms_store_logo"),
                ],
            ),
            (
                t.FormatConvert,
                [
                    (
                        FIF.SYNC,
                        t.MediaConvert,
                        t.MediaConvertDesc,
                        "media_convert",
                    ),
                ],
            ),
            (
                t.Utilities,
                [
                    (FIF.IMAGE_EXPORT, t.GifMake, t.GifMakeDesc, "gif_make"),
                    (
                        FIF.CAMERA,
                        t.VideoSnapshot,
                        t.VideoSnapshotDesc,
                        "video_snapshot",
                    ),
                    (
                        FIF.SPEAKERS,
                        t.AudioExtract,
                        t.AudioExtractDesc,
                        "audio_extract",
                    ),
                    (FIF.CUT, t.VideoCut, t.VideoCutDesc, "video_cut"),
                    (FIF.LINK, t.VideoConcat, t.VideoConcatDesc, "video_concat"),
                    (FIF.INFO, t.MediaInfo, t.MediaInfoDesc, "media_info"),
                ],
            ),
            (
                t.AdvancedTools,
                [
                    (FIF.FONT, t.Subtitle, t.SubtitleDesc, "subtitle"),
                    (FIF.MESSAGE, t.Loudnorm, t.LoudnormDesc, "loudnorm"),
                    (FIF.SPEED_HIGH, t.Speed, t.SpeedDesc, "speed"),
                ],
            ),
        ]

        row = 0
        for groupIndex, (groupTitle, cards) in enumerate(groups):
            if groupIndex > 0:
                # 组间额外留白，区分分组
                gridLayout.setRowMinimumHeight(row, 24)
                row += 1

            # 分组标题跨满整行
            groupTitleLabel = StrongBodyLabel(groupTitle, gridContainer)
            gridLayout.addWidget(groupTitleLabel, row, 0, 1, columns)
            row += 1

            # 卡片按 3 列排列，跨组共享列宽
            for index, (icon, cardTitle, desc, name) in enumerate(cards):
                card = FunctionCard(
                    icon, cardTitle, desc, name=name, parent=gridContainer
                )
                card.clicked.connect(lambda n=name: self._onCardClicked(n))
                self._cards[name] = card

                cardRow = row + index // columns
                cardCol = index % columns
                gridLayout.addWidget(card, cardRow, cardCol)

            # 跳过本组卡片占用的行
            row += (len(cards) + columns - 1) // columns

        mainLayout.addWidget(gridContainer)
        mainLayout.addStretch(1)

        self.homePage.setWidget(view)
        self.stackedWidget.addWidget(self.homePage)

    def addFunctionPage(self, name: str, page: FunctionPage):
        """注册功能页：关联 name 到 stack 索引，连接返回信号

        子功能页实现后调用此方法注册，点击对应卡片即切换到该页，
        替换之前可能指向的占位页。
        """
        index = self.stackedWidget.addWidget(page)
        self._pageIndex[name] = index
        page.backRequested.connect(self._backToHome)

    def _onCardClicked(self, name: str):
        """卡片点击：切到对应功能页；未注册则切到占位页"""
        if name not in self._pageIndex:
            if self._placeholderPage is None:
                self._placeholderPage = _PlaceholderPage(self)
                self._placeholderPage.backRequested.connect(self._backToHome)
                self.stackedWidget.addWidget(self._placeholderPage)
            self._pageIndex[name] = self.stackedWidget.indexOf(self._placeholderPage)
        self.stackedWidget.setCurrentIndex(self._pageIndex[name])

    def _backToHome(self):
        """返回入口页"""
        self.stackedWidget.setCurrentIndex(0)
