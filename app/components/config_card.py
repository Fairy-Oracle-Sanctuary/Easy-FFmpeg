import sys

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
        self.globalText = Text()
        self.setTitle(self.globalText.EncoderSettings)

        self.softWareVideoCodecComboBox = ComboBox()
        self.isUseHardWareVideoCodecBtn = SwitchButton()
        self.hardWareVideoCodecPlatformComboBox = ComboBox()
        self.hardWareVideoCodecComboBox = ComboBox()

        if sys.platform == "darwin":
            self.hardWareVideoCodecDict = {
                "Apple": ["h264_videotoolbox", "hevc_videotoolbox", "av1_videotoolbox"],
            }
        else:
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
            title=self.globalText.SoftwareEncoder,
            content=self.globalText.SoftwareEncoderDesc,
            widget=self.softWareVideoCodecComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.HARDWARE,
            title=self.globalText.UseHardwareEncoder,
            content=self.globalText.UseHardwareEncoderDesc,
            widget=self.isUseHardWareVideoCodecBtn,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.PLATFORM,
            title=self.globalText.HardwarePlatform,
            content=(
                self.globalText.HardwarePlatformMac
                if sys.platform == "darwin"
                else self.globalText.HardwarePlatformDesc
            ),
            widget=self.hardWareVideoCodecPlatformComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.GPU,
            title=self.globalText.HardwareEncoder,
            content=self.globalText.HardwareEncoderDesc,
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
        self.globalText = Text()
        self.setTitle(self.globalText.FilterQuality)

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
            title=self.globalText.QualityControlMode,
            content=self.globalText.QualityControlModeDesc,
            widget=self.qualityModeComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.CRF,
            title=self.globalText.CrfParam,
            content=self.globalText.CrfParamDesc,
            widget=self.crfLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.BITRATE,
            title=self.globalText.VideoTargetBitrate,
            content=self.globalText.VideoTargetBitrateDesc,
            widget=self.videoBitrateLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.TWO_PASS,
            title=self.globalText.TwoPass,
            content=self.globalText.TwoPassDesc,
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
        # two-pass 仅 Bitrate 模式有意义，CRF 模式下禁用开关（配置保留，切回 Bitrate 仍生效）
        self.twoPassBtn.setEnabled(mode == "Bitrate")


class AdvancedPresetConfigCard(GroupHeaderCardWidget):
    """Advanced preset config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.globalText = Text()
        self.setTitle(self.globalText.FilterPreset)

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
            title=self.globalText.EncodeSpeedPreset,
            content=self.globalText.EncodeSpeedPresetDesc,
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
        self.globalText = Text()
        self.setTitle(self.globalText.FilterResolution)

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
            title=self.globalText.FilterResolution,
            content=self.globalText.ResolutionDesc,
            widget=self.resolutionComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.CUSTOM_WIDTH,
            title=self.globalText.CustomWidth,
            content=self.globalText.CustomWidthDesc,
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
        self.globalText = Text()
        self.setTitle(self.globalText.FilterFrameRate)

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
            title=self.globalText.FilterFrameRate,
            content=self.globalText.FrameRateDesc,
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
        self.globalText = Text()
        self.setTitle(self.globalText.FilterAudio)

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
            title=self.globalText.AudioEncoder,
            content=self.globalText.AudioEncoderDesc,
            widget=self.audioCodecComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.AUDIO_BITRATE,
            title=self.globalText.AudioBitrateCard,
            content=self.globalText.AudioBitrateCardDesc,
            widget=self.audioBitrateComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.REMOVE_AUDIO,
            title=self.globalText.RemoveAudioTrack,
            content=self.globalText.RemoveAudioTrackDesc,
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


class AdvancedImageConfigCard(GroupHeaderCardWidget):
    """Advanced image config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.globalText = Text()
        self.setTitle(self.globalText.FilterImage)

        self.imageQualityComboBox = ComboBox()

        self._initWidgets()

    def _initWidgets(self):
        self.setBorderRadius(8)

        self.imageQualityComboBox.setMinimumWidth(120)
        self.imageQualityComboBox.addItems(cfg.ffmpegImageQuality.options)
        self.imageQualityComboBox.setCurrentText(cfg.get(cfg.ffmpegImageQuality))

        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        self.addGroup(
            icon=Logo.IMAGE_QUALITY,
            title=self.globalText.ImageQualityCard,
            content=self.globalText.ImageQualityCardDesc,
            widget=self.imageQualityComboBox,
            wordWrap=True,
        )

    def _connectSignalToSlot(self):
        self.imageQualityComboBox.currentTextChanged.connect(
            lambda v: cfg.set(cfg.ffmpegImageQuality, v)
        )


class AdvancedExtraConfigCard(GroupHeaderCardWidget):
    """Advanced extra config card"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.globalText = Text()
        self.setTitle(self.globalText.FilterExtra)

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
        self.startTimeLineEdit.setPlaceholderText(self.globalText.Seconds)
        self.startTimeLineEdit.setValidator(QDoubleValidator(0, 2147483647, 2))
        self.startTimeLineEdit.setText(str(cfg.get(cfg.ffmpegStartTime)))

        self.durationLineEdit.setFixedWidth(120)
        self.durationLineEdit.setPlaceholderText(self.globalText.Seconds)
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
            title=self.globalText.Tune,
            content=self.globalText.TuneDesc,
            widget=self.tuneComboBox,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.START_TIME,
            title=self.globalText.CutStartTime,
            content=self.globalText.CutStartTimeDesc,
            widget=self.startTimeLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.DURATION,
            title=self.globalText.CutDuration,
            content=self.globalText.CutDurationDesc,
            widget=self.durationLineEdit,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.DEINTERLACE,
            title=self.globalText.Deinterlace,
            content=self.globalText.DeinterlaceDesc,
            widget=self.deinterlaceBtn,
            wordWrap=True,
        )
        self.addGroup(
            icon=Logo.ROTATION,
            title=self.globalText.Rotation,
            content=self.globalText.RotationDesc,
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
        self.globalText = Text()
        self.vBoxlayout = QVBoxLayout(self)

        self.videoArgsLabel = BodyLabel(self.globalText.VideoArgs)
        self.videoArgsEdit = PlainTextEdit()
        self.audioArgsLabel = BodyLabel(self.globalText.AudioArgs)
        self.audioArgsEdit = PlainTextEdit()
        self.imageArgsLabel = BodyLabel(self.globalText.ImageArgs)
        self.imageArgsEdit = PlainTextEdit()

        self._initWidgets()

    def _initWidgets(self):
        self.videoArgsEdit.setMaximumHeight(100)
        self.videoArgsEdit.setPlainText(cfg.get(cfg.ffmpegCustomVideoArgs))

        self.audioArgsEdit.setMaximumHeight(100)
        self.audioArgsEdit.setPlainText(cfg.get(cfg.ffmpegCustomAudioArgs))

        self.imageArgsEdit.setMaximumHeight(100)
        self.imageArgsEdit.setPlainText(cfg.get(cfg.ffmpegCustomImageArgs))

        self.vBoxlayout.addWidget(self.videoArgsLabel)
        self.vBoxlayout.addWidget(self.videoArgsEdit)
        self.vBoxlayout.addWidget(self.audioArgsLabel)
        self.vBoxlayout.addWidget(self.audioArgsEdit)
        self.vBoxlayout.addWidget(self.imageArgsLabel)
        self.vBoxlayout.addWidget(self.imageArgsEdit)

        self._connectSignalToSlot()

    def _connectSignalToSlot(self):
        self.videoArgsEdit.textChanged.connect(
            lambda: cfg.set(cfg.ffmpegCustomVideoArgs, self.videoArgsEdit.toPlainText())
        )
        self.audioArgsEdit.textChanged.connect(
            lambda: cfg.set(cfg.ffmpegCustomAudioArgs, self.audioArgsEdit.toPlainText())
        )
        self.imageArgsEdit.textChanged.connect(
            lambda: cfg.set(cfg.ffmpegCustomImageArgs, self.imageArgsEdit.toPlainText())
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
            "image": "FilterImage",
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
