from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import (
    QColor,
    QDoubleValidator,
    QIntValidator,
    QPainter,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QVBoxLayout,
)

from libs.qfluentwidgets_pro import (
    BodyLabel,
    CaptionLabel,
    ComboBox,
    GroupHeaderCardWidget,
    IconWidget,
    LineEdit,
    MultiSelectionLiteFilter,
    PlainTextEdit,
    PushButton,
    SimpleCardWidget,
    SwitchButton,
    isDarkTheme,
)

from ..common.config import cfg
from ..common.icon import Logo
from ..common.text import Text


def _clamp_int(text: str, min_value: int, max_value: int):
    """将文本解析为 int 并夹取到 [min_value, max_value]，非法输入返回 None"""
    try:
        value = int(text)
    except (TypeError, ValueError):
        return None
    return max(min_value, min(max_value, value))


def _clamp_float(text: str, min_value: float, max_value: float):
    """将文本解析为 float 并夹取到 [min_value, max_value]，非法输入返回 None"""
    try:
        value = float(text)
    except (TypeError, ValueError):
        return None
    return max(min_value, min(max_value, value))


def _apply_int(lineedit, item, text: str, lo: int, hi: int):
    """将文本夹取到合法 int 范围：越界则修正输入框内容，并写入配置"""
    value = _clamp_int(text, lo, hi)
    if value is None:
        return
    if value != int(text):
        lineedit.setText(str(value))
    cfg.set(item, value)


def _apply_float(lineedit, item, text: str, lo: float, hi: float):
    """将文本夹取到合法 float 范围：越界则修正输入框内容，并写入配置"""
    value = _clamp_float(text, lo, hi)
    if value is None:
        return
    if value != float(text):
        lineedit.setText(str(value))
    cfg.set(item, value)


class DetectionCard(QFrame):
    def __init__(self, icon, title, content, parent=None):
        super().__init__(parent)
        self.globalText = Text()
        self.iconWidget = IconWidget(icon)
        self.titleLabel = BodyLabel(title, self)
        self.contentLabel = CaptionLabel(content, self)
        self.openButton = PushButton(self.globalText.Detect, self)

        self.hBoxLayout = QHBoxLayout(self)
        self.vBoxLayout = QVBoxLayout()

        self.setFixedHeight(73)
        self.iconWidget.setFixedSize(16, 16)
        self.contentLabel.setTextColor("#606060", "#d2d2d2")
        self.openButton.setFixedWidth(130)

        self.hBoxLayout.setContentsMargins(20, 11, 11, 11)
        self.hBoxLayout.setSpacing(15)
        self.hBoxLayout.addWidget(self.iconWidget)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.addWidget(self.contentLabel, 0, Qt.AlignVCenter)
        self.vBoxLayout.setAlignment(Qt.AlignVCenter)
        self.hBoxLayout.addLayout(self.vBoxLayout)

        self.hBoxLayout.addStretch(1)
        self.hBoxLayout.addWidget(self.openButton, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(5)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        if isDarkTheme():
            painter.setBrush(QColor(255, 255, 255, 13))
            painter.setPen(QColor(0, 0, 0, 50))
        else:
            painter.setBrush(QColor(255, 255, 255, 170))
            painter.setPen(QColor(0, 0, 0, 19))

        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 6, 6)


class AdvancedEncoderConfigCard(GroupHeaderCardWidget):
    """Advanced encoder config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("编码器设置")

        self.softWareVideoCodecComboBox = ComboBox()
        self.isUseHardWareVideoCodecBtn = SwitchButton()
        self.hardWareVideoCodecPlatformComboBox = ComboBox()
        self.hardWareVideoCodecComboBox = ComboBox()

        self.hardWareVideoCodecDict = {
            "NVIDIA": ["h264_nvenc", "hevc_nvenc", "av1_nvenc"],
            "Intel": ["h264_qsv", "hevc_qsv", "av1_qsv"],
            "AMD": ["h264_amf", "hevc_amf", "av1_amf"],
        }

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.softWareVideoCodecComboBox.setMinimumWidth(120)
        self.softWareVideoCodecComboBox.addItems(cfg.ffmpegSoftWareVideoCodec.options)
        self.softWareVideoCodecComboBox.setCurrentText(
            cfg.get(cfg.ffmpegSoftWareVideoCodec)
        )

        self.isUseHardWareVideoCodecBtn.setChecked(
            cfg.get(cfg.ffmpegUseHardWareVideoCodec)
        )
        self._updateUseHardWareVideoCodec(cfg.get(cfg.ffmpegUseHardWareVideoCodec))

        self.hardWareVideoCodecPlatformComboBox.setMinimumWidth(120)
        self.hardWareVideoCodecPlatformComboBox.addItems(
            cfg.ffmpegHardWareVideoCodecPlatform.options
        )
        self.hardWareVideoCodecPlatformComboBox.setCurrentText(
            cfg.get(cfg.ffmpegHardWareVideoCodecPlatform)
        )

        self.hardWareVideoCodecComboBox.setMinimumWidth(120)
        self._updateHardWareVideoCodec(cfg.get(cfg.ffmpegHardWareVideoCodecPlatform))
        self.hardWareVideoCodecComboBox.setCurrentText(
            cfg.get(cfg.ffmpegHardWareVideoCodec)
        )

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.ENCODER,
            title="软件编码器",
            content="libx264兼容性好,libx265同画质更小,VP9流媒体友好,AV1体积最小但极慢",
            widget=self.softWareVideoCodecComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.HARDWARE,
            title="是否使用硬件编码器",
            content="启用后使用显卡进行硬件加速编码,速度远快于软件编码但画质略逊",
            widget=self.isUseHardWareVideoCodecBtn,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.PLATFORM,
            title="硬件编码器平台",
            content="选择显卡厂商对应的编码平台,NVIDIA为NVENC,Intel为QSV,AMD为AMF",
            widget=self.hardWareVideoCodecPlatformComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.GPU,
            title="硬件编码器",
            content="选择具体硬件编码器,可用项取决于平台与显卡型号,不支持时ffmpeg会报错",
            widget=self.hardWareVideoCodecComboBox,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.softWareVideoCodecComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegSoftWareVideoCodec, v)
        )
        self.isUseHardWareVideoCodecBtn.checkedChanged.connect(
            self._updateUseHardWareVideoCodec
        )
        self.hardWareVideoCodecPlatformComboBox.currentTextChanged.connect(
            self._updateHardWareVideoCodec
        )
        self.hardWareVideoCodecComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegHardWareVideoCodec, v)
        )

    def _updateUseHardWareVideoCodec(self, checked):
        cfg.set(cfg.ffmpegUseHardWareVideoCodec, checked)
        self.softWareVideoCodecComboBox.setEnabled(not checked)
        self.hardWareVideoCodecPlatformComboBox.setEnabled(checked)
        self.hardWareVideoCodecComboBox.setEnabled(checked)

    def _updateHardWareVideoCodec(self, platform):
        cfg.set(cfg.ffmpegHardWareVideoCodecPlatform, platform)
        self.hardWareVideoCodecComboBox.clear()
        self.hardWareVideoCodecComboBox.addItems(self.hardWareVideoCodecDict[platform])
        self.hardWareVideoCodecComboBox.setCurrentIndex(0)


class AdvancedQualityConfigCard(GroupHeaderCardWidget):
    """Advanced quality config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("质量控制")

        self.qualityModeComboBox = ComboBox()
        self.crfLineEdit = LineEdit()
        self.videoBitrateLineEdit = LineEdit()
        self.twoPassBtn = SwitchButton()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.qualityModeComboBox.setMinimumWidth(120)
        self.qualityModeComboBox.addItems(cfg.ffmpegQualityMode.options)
        self.qualityModeComboBox.setCurrentText(cfg.get(cfg.ffmpegQualityMode))
        self._updateQualityMode(cfg.get(cfg.ffmpegQualityMode))

        self.crfLineEdit.setFixedWidth(120)
        self.crfLineEdit.setPlaceholderText("0-51")
        self.crfLineEdit.setValidator(QIntValidator(0, 51))
        self.crfLineEdit.setText(str(cfg.get(cfg.ffmpegCrf)))

        self.videoBitrateLineEdit.setFixedWidth(120)
        self.videoBitrateLineEdit.setPlaceholderText("kbps")
        self.videoBitrateLineEdit.setValidator(QIntValidator(100, 50000))
        self.videoBitrateLineEdit.setText(str(cfg.get(cfg.ffmpegVideoBitrate)))

        self.twoPassBtn.setChecked(cfg.get(cfg.ffmpegTwoPass))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.QUALITY_MODE,
            title="质量控制模式",
            content="CRF恒定质量画质优先,Bitrate目标码率控制输出体积,二选一",
            widget=self.qualityModeComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.CRF,
            title="CRF质量参数",
            content="数值越低画质越高体积越大,0为无损,常用18-28",
            widget=self.crfLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.BITRATE,
            title="视频目标码率",
            content="单位kbps,仅在Bitrate模式下生效",
            widget=self.videoBitrateLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.TWO_PASS,
            title="二次编码",
            content="码率控制更精准但耗时翻倍,仅Bitrate模式有意义",
            widget=self.twoPassBtn,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.qualityModeComboBox.currentTextChanged.connect(self._updateQualityMode)
        self.crfLineEdit.textChanged.connect(
            lambda t: _apply_int(self.crfLineEdit, cfg.ffmpegCrf, t, 0, 51)
        )
        self.videoBitrateLineEdit.textChanged.connect(
            lambda t: _apply_int(
                self.videoBitrateLineEdit, cfg.ffmpegVideoBitrate, t, 100, 50000
            )
        )
        self.twoPassBtn.checkedChanged.connect(lambda v: cfg.set(cfg.ffmpegTwoPass, v))

    def _updateQualityMode(self, mode):
        cfg.set(cfg.ffmpegQualityMode, mode)
        self.crfLineEdit.setEnabled(mode == "CRF")
        self.videoBitrateLineEdit.setEnabled(mode == "Bitrate")


class AdvancedPresetConfigCard(GroupHeaderCardWidget):
    """Advanced preset config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("编码速度")

        self.presetComboBox = ComboBox()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.presetComboBox.setMinimumWidth(120)
        self.presetComboBox.addItems(cfg.ffmpegPreset.options)
        self.presetComboBox.setCurrentText(cfg.get(cfg.ffmpegPreset))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.PRESET,
            title="编码速度预设",
            content="越慢压缩体积越小但耗时越长,medium为平衡默认",
            widget=self.presetComboBox,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.presetComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegPreset, v)
        )


class AdvancedResolutionConfigCard(GroupHeaderCardWidget):
    """Advanced resolution config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("分辨率")

        self.resolutionComboBox = ComboBox()
        self.customWidthLineEdit = LineEdit()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.resolutionComboBox.setMinimumWidth(120)
        self.resolutionComboBox.addItems(cfg.ffmpegResolution.options)
        self.resolutionComboBox.setCurrentText(cfg.get(cfg.ffmpegResolution))
        self._updateResolution(cfg.get(cfg.ffmpegResolution))

        self.customWidthLineEdit.setFixedWidth(120)
        self.customWidthLineEdit.setPlaceholderText("px")
        self.customWidthLineEdit.setValidator(QIntValidator(2, 7680))
        self.customWidthLineEdit.setText(str(cfg.get(cfg.ffmpegCustomWidth)))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.RESOLUTION,
            title="分辨率",
            content="origin保持原分辨率,1080p/720p/480p常用档,custom自定义宽度",
            widget=self.resolutionComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.CUSTOM_WIDTH,
            title="自定义宽度",
            content="高度按比例自动计算,需为偶数,仅在custom模式下生效",
            widget=self.customWidthLineEdit,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.resolutionComboBox.currentTextChanged.connect(self._updateResolution)
        self.customWidthLineEdit.textChanged.connect(
            lambda t: _apply_int(
                self.customWidthLineEdit, cfg.ffmpegCustomWidth, t, 2, 7680
            )
        )

    def _updateResolution(self, resolution):
        cfg.set(cfg.ffmpegResolution, resolution)
        self.customWidthLineEdit.setEnabled(resolution == "custom")


class AdvancedFrameRateConfigCard(GroupHeaderCardWidget):
    """Advanced frame rate config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("帧率")

        self.frameRateComboBox = ComboBox()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.frameRateComboBox.setMinimumWidth(120)
        self.frameRateComboBox.addItems(cfg.ffmpegFrameRate.options)
        self.frameRateComboBox.setCurrentText(cfg.get(cfg.ffmpegFrameRate))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.FRAME_RATE,
            title="帧率",
            content="origin保持原帧率,可固定为24/30/60",
            widget=self.frameRateComboBox,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.frameRateComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegFrameRate, v)
        )


class AdvancedAudioConfigCard(GroupHeaderCardWidget):
    """Advanced audio config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("音频")

        self.audioCodecComboBox = ComboBox()
        self.audioBitrateComboBox = ComboBox()
        self.removeAudioBtn = SwitchButton()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.audioCodecComboBox.setMinimumWidth(120)
        self.audioCodecComboBox.addItems(cfg.ffmpegAudioCodec.options)
        self.audioCodecComboBox.setCurrentText(cfg.get(cfg.ffmpegAudioCodec))

        self.audioBitrateComboBox.setMinimumWidth(120)
        self.audioBitrateComboBox.addItems(cfg.ffmpegAudioBitrate.options)
        self.audioBitrateComboBox.setCurrentText(cfg.get(cfg.ffmpegAudioBitrate))

        self.removeAudioBtn.setChecked(cfg.get(cfg.ffmpegRemoveAudio))
        self._updateRemoveAudio(cfg.get(cfg.ffmpegRemoveAudio))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.AUDIO_CODEC,
            title="音频编码器",
            content="aac默认,libmp3lame兼容性好,libopus高质量低码率,copy不重编码",
            widget=self.audioCodecComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.AUDIO_BITRATE,
            title="音频码率",
            content="128k默认,192k/320k音质更高但体积更大",
            widget=self.audioBitrateComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.REMOVE_AUDIO,
            title="删除音轨",
            content="启用后不编码音频,输出视频无声音",
            widget=self.removeAudioBtn,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.audioCodecComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegAudioCodec, v)
        )
        self.audioBitrateComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegAudioBitrate, v)
        )
        self.removeAudioBtn.checkedChanged.connect(self._updateRemoveAudio)

    def _updateRemoveAudio(self, checked):
        cfg.set(cfg.ffmpegRemoveAudio, checked)
        self.audioCodecComboBox.setEnabled(not checked)
        self.audioBitrateComboBox.setEnabled(not checked)


class AdvancedExtraConfigCard(GroupHeaderCardWidget):
    """Advanced extra config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle("进阶设置")

        self.tuneComboBox = ComboBox()
        self.startTimeLineEdit = LineEdit()
        self.durationLineEdit = LineEdit()
        self.deinterlaceBtn = SwitchButton()
        self.rotationComboBox = ComboBox()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.tuneComboBox.setMinimumWidth(120)
        self.tuneComboBox.addItems(cfg.ffmpegTune.options)
        self.tuneComboBox.setCurrentText(cfg.get(cfg.ffmpegTune))

        self.startTimeLineEdit.setFixedWidth(120)
        self.startTimeLineEdit.setPlaceholderText("秒")
        self.startTimeLineEdit.setValidator(QDoubleValidator(0, 2147483647, 2))
        self.startTimeLineEdit.setText(str(cfg.get(cfg.ffmpegStartTime)))

        self.durationLineEdit.setFixedWidth(120)
        self.durationLineEdit.setPlaceholderText("秒")
        self.durationLineEdit.setValidator(QDoubleValidator(0, 2147483647, 2))
        self.durationLineEdit.setText(str(cfg.get(cfg.ffmpegDuration)))

        self.deinterlaceBtn.setChecked(cfg.get(cfg.ffmpegDeinterlace))

        self.rotationComboBox.setMinimumWidth(120)
        self.rotationComboBox.addItems(cfg.ffmpegRotation.options)
        self.rotationComboBox.setCurrentText(cfg.get(cfg.ffmpegRotation))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        # add widget to group
        self.addGroup(
            icon=Logo.TUNE,
            title="调优",
            content="针对内容类型优化编码,仅libx264/libx265生效",
            widget=self.tuneComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.START_TIME,
            title="裁剪起始时间",
            content="单位秒,留空表示从头开始",
            widget=self.startTimeLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.DURATION,
            title="裁剪持续时间",
            content="单位秒,留空表示到结尾",
            widget=self.durationLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.DEINTERLACE,
            title="反交错",
            content="消除隔行扫描产生的横纹,适合老式DVD源",
            widget=self.deinterlaceBtn,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.ROTATION,
            title="旋转角度",
            content="none不旋转,90/180/270逆时针旋转",
            widget=self.rotationComboBox,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.tuneComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegTune, v)
        )
        self.startTimeLineEdit.textChanged.connect(
            lambda t: _apply_float(
                self.startTimeLineEdit, cfg.ffmpegStartTime, t, 0, 2147483647
            )
        )
        self.durationLineEdit.textChanged.connect(
            lambda t: _apply_float(
                self.durationLineEdit, cfg.ffmpegDuration, t, 0, 2147483647
            )
        )
        self.deinterlaceBtn.checkedChanged.connect(
            lambda v: cfg.set(cfg.ffmpegDeinterlace, v)
        )
        self.rotationComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegRotation, v)
        )


class CustomArgsConfigCard(SimpleCardWidget):
    """Custom args config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxlayout = QVBoxLayout(self)

        self.videoArgsLabel = BodyLabel("视频参数:")
        self.videoArgsEdit = PlainTextEdit()
        self.audioArgsLabel = BodyLabel("音频参数:")
        self.audioArgsEdit = PlainTextEdit()

        self._initWidgets()

    def _initWidgets(self):
        self.videoArgsEdit.setMaximumHeight(100)
        self.videoArgsEdit.setPlainText(cfg.get(cfg.ffmpegCustomVideoArgs))

        self.audioArgsEdit.setMaximumHeight(100)
        self.audioArgsEdit.setPlainText(cfg.get(cfg.ffmpegCustomAudioArgs))

        self.vBoxlayout.addWidget(self.videoArgsLabel)
        self.vBoxlayout.addWidget(self.videoArgsEdit)
        self.vBoxlayout.addWidget(self.audioArgsLabel)
        self.vBoxlayout.addWidget(self.audioArgsEdit)

        self._connectSignalToSlot()

    def _connectSignalToSlot(self):
        self.videoArgsEdit.textChanged.connect(
            lambda: cfg.set(cfg.ffmpegCustomVideoArgs, self.videoArgsEdit.toPlainText())
        )
        self.audioArgsEdit.textChanged.connect(
            lambda: cfg.set(cfg.ffmpegCustomAudioArgs, self.audioArgsEdit.toPlainText())
        )


class ConfigFilterCard(SimpleCardWidget):
    currentItemsChanged = Signal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.globalText = Text()

        # 标识符 → Text 属性名
        self._itemKeys = {
            "encoder": "FilterEncoder",
            "quality": "FilterQuality",
            "preset": "FilterPreset",
            "resolution": "FilterResolution",
            "frame_rate": "FilterFrameRate",
            "audio": "FilterAudio",
            "extra": "FilterExtra",
        }

        # 标识符 ↔ 显示文本 的双向映射
        self._idToText = {}
        self._textToId = {}
        for identifier, attr in self._itemKeys.items():
            text = getattr(self.globalText, attr)
            self._idToText[identifier] = text
            self._textToId[text] = identifier

        self._initLayout()

    def _initLayout(self):
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(24, 16, 24, 16)
        self.vBoxLayout.setSpacing(8)

        self.hintLabel = CaptionLabel(self.globalText.FilterConfigHint)
        self.filterWidget = MultiSelectionLiteFilter(self)
        self.filterWidget.addItems(list(self._idToText.values()))
        # 从配置加载已启用的参数块
        enabled = cfg.get(cfg.ffmpegEnabledBlocks)
        if not enabled:
            enabled = list(self._idToText.keys())
        self.filterWidget.setCurrentItems(
            [self._idToText[i] for i in enabled if i in self._idToText]
        )
        self.filterWidget.currentItemsChanged.connect(self._onItemsChanged)

        self.vBoxLayout.addWidget(self.hintLabel)
        self.vBoxLayout.addWidget(self.filterWidget)

    def _onItemsChanged(self, texts: list):
        """将显示文本列表转换为标识符列表后发出，并持久化"""
        ids = [self._textToId[t] for t in texts if t in self._textToId]
        cfg.set(cfg.ffmpegEnabledBlocks, ids)
        self.currentItemsChanged.emit(ids)

    def setCurrentItems(self, identifiers: list):
        """按标识符列表设置选中项"""
        texts = [self._idToText[i] for i in identifiers if i in self._idToText]
        self.filterWidget.setCurrentItems(texts)

    def currentItems(self) -> list:
        """返回当前选中的标识符列表"""
        return [
            self._textToId[t]
            for t in self.filterWidget.currentItems()
            if t in self._textToId
        ]
