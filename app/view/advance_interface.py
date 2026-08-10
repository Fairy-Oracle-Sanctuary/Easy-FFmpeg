from PySide6.QtCore import Qt
from PySide6.QtWidgets import QStackedWidget, QVBoxLayout, QWidget

from libs.qfluentwidgets_pro import FluentIcon as FIF
from libs.qfluentwidgets_pro import ScrollArea, SwitchSettingCard

from ..common.config import cfg
from ..common.text import Text
from ..components.config_card import (
    AdvancedAudioConfigCard,
    AdvancedEncoderConfigCard,
    AdvancedExtraConfigCard,
    AdvancedFrameRateConfigCard,
    AdvancedImageConfigCard,
    AdvancedPresetConfigCard,
    AdvancedQualityConfigCard,
    AdvancedResolutionConfigCard,
    ConfigFilterCard,
    CustomArgsConfigCard,
)
from ..components.info_card import EasyFFmpegInfoCard


class AdvanceInterface(ScrollArea):
    """Advance interface"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.globalText = Text()
        self.view = QWidget(self)
        self.mainLayout = QVBoxLayout(self.view)

        self.infoCard = EasyFFmpegInfoCard(self)
        self.isUseCustomArgsCard = SwitchSettingCard(
            FIF.PENCIL_INK,
            self.globalText.UseCustomArgs,
            self.globalText.UseCustomArgsDesc,
            cfg.ffmpegIsUseCustomArgs,
        )

        self.encoderConfigCard = AdvancedEncoderConfigCard(self)
        self.qualityConfigCard = AdvancedQualityConfigCard(self)
        self.presetConfigCard = AdvancedPresetConfigCard(self)
        self.resolutionConfigCard = AdvancedResolutionConfigCard(self)
        self.frameRateConfigCard = AdvancedFrameRateConfigCard(self)
        self.audioConfigCard = AdvancedAudioConfigCard(self)
        self.imageConfigCard = AdvancedImageConfigCard(self)
        self.extraConfigCard = AdvancedExtraConfigCard(self)
        self.customArgsConfigCard = CustomArgsConfigCard(self)

        self.stackWidget = QStackedWidget(self)
        self.advancedConfigPage = QWidget(self)
        self.advancedConfigLayout = QVBoxLayout(self.advancedConfigPage)
        self.advancedConfigLayout.setContentsMargins(0, 0, 0, 0)
        self.customArgsPage = QWidget(self)
        self.customArgsLayout = QVBoxLayout(self.customArgsPage)
        self.customArgsLayout.setContentsMargins(0, 0, 0, 0)
        self.customArgsLayout.addWidget(self.customArgsConfigCard)
        self.stackWidget.addWidget(self.advancedConfigPage)
        self.stackWidget.addWidget(self.customArgsPage)

        # 卡片过滤器：让用户决定启用哪些高级设置块
        self.configFilterCard = ConfigFilterCard(self)
        # 标识符与卡片的映射
        self._cardFilterMap = {
            "encoder": self.encoderConfigCard,
            "quality": self.qualityConfigCard,
            "preset": self.presetConfigCard,
            "resolution": self.resolutionConfigCard,
            "frame_rate": self.frameRateConfigCard,
            "audio": self.audioConfigCard,
            "image": self.imageConfigCard,
            "extra": self.extraConfigCard,
        }

        self._initWidget()

    def _initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)
        self.setObjectName("advanceInterface")

        self.enableTransparentBackground()

        # initialize layout
        self._initLayout()
        self._connectSignalToSlot()

    def _initLayout(self):
        """Initialize layout"""
        self.mainLayout.addWidget(self.infoCard, 0, Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addWidget(
            self.isUseCustomArgsCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.configFilterCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.encoderConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.qualityConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.presetConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.resolutionConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.frameRateConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.audioConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.imageConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addWidget(
            self.extraConfigCard, 0, Qt.AlignmentFlag.AlignTop
        )
        self.advancedConfigLayout.addStretch()
        self.mainLayout.addWidget(self.stackWidget, 0, Qt.AlignmentFlag.AlignTop)
        self.mainLayout.addStretch()
        self._setIsUseCustomArgs(cfg.get(cfg.ffmpegIsUseCustomArgs))
        self._updateStackHeight()

    def _connectSignalToSlot(self):
        self.isUseCustomArgsCard.checkedChanged.connect(
            lambda v: self._setIsUseCustomArgs(v)
        )
        self.configFilterCard.currentItemsChanged.connect(self._onFilterChanged)
        self.stackWidget.currentChanged.connect(self._updateStackHeight)
        # 应用配置中保存的初始过滤器状态
        self._onFilterChanged(self.configFilterCard.currentItems())

    def _onFilterChanged(self, items: list):
        """根据过滤器选择显示/隐藏对应的配置卡片"""
        for identifier, card in self._cardFilterMap.items():
            card.setVisible(identifier in items)
        self._updateStackHeight()

    def _setIsUseCustomArgs(self, isUseCustomArgs: bool = True):
        """切换"高级参数配置"与"自定义参数"页面"""
        self.stackWidget.setCurrentIndex(1 if isUseCustomArgs else 0)

    def _updateStackHeight(self):
        """同步 stackWidget 高度为当前页实际高度，并回顶部

        QStackedWidget 默认高度取所有页面 sizeHint 的最大值，
        切到矮页面时会产生巨大空白。这里跟随当前页收缩高度，
        同时把滚动条重置到顶部，避免切页后停留在旧位置。
        """
        current = self.stackWidget.currentWidget()
        if current is None:
            return

        current.adjustSize()
        self.stackWidget.setFixedHeight(current.sizeHint().height())
        self.view.adjustSize()
        self.verticalScrollBar().setValue(0)
