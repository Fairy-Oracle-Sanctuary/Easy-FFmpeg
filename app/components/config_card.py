from PySide6.QtCore import Qt
from PySide6.QtGui import (
    QColor,
    QFont,
    QIntValidator,
    QPainter,
    QValidator,
)
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QSpacerItem,
    QVBoxLayout,
)

from libs.qfluentwidgets_pro import (
    BodyLabel,
    CaptionLabel,
    ComboBox,
    Flyout,
    FlyoutAnimationType,
    IconWidget,
    LineEdit,
    PasswordLineEdit,
    PlainTextEdit,
    PushButton,
    SettingCard,
    ToolButton,
    isDarkTheme,
    qconfig,
    setFont,
)
from libs.qfluentwidgets_pro import FluentIcon as FIF
from libs.qfluentwidgets_pro import SettingCardGroup as CardGroup

from ..common.config import cfg
from ..common.text import Text


class DictSettingCard(SettingCard):
    """Setting card with a combo box"""

    def __init__(
        self,
        configItem,
        icon,
        title,
        content=None,
        options_dict=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.comboBox = ComboBox(self)
        self.hBoxLayout.addWidget(self.comboBox, 0, Qt.AlignRight)
        self.hBoxLayout.addSpacing(16)

        self.optionToText = options_dict or {}
        for option, text in self.optionToText.items():
            self.comboBox.addItem(text, userData=option)

        self.comboBox.setCurrentText(self.optionToText.get(qconfig.get(configItem), ""))
        self.comboBox.currentIndexChanged.connect(self._onCurrentIndexChanged)
        configItem.valueChanged.connect(self.setValue)

    def _onCurrentIndexChanged(self, index: int):
        qconfig.set(self.configItem, self.comboBox.itemData(index))

    def setValue(self, value):
        if value not in self.optionToText:
            return

        self.comboBox.setCurrentText(self.optionToText[value])
        qconfig.set(self.configItem, value)


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


class SettingCardGroup(CardGroup):
    def __init__(self, title: str, parent=None):
        super().__init__(title, parent)
        setFont(self.titleLabel, 14, QFont.Weight.DemiBold)


class LineEditSettingCard(SettingCard):
    """自定义文本输入设置卡片"""

    def __init__(
        self, configItem, icon, title, content=None, placeholderText="", parent=None
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem

        self.lineEdit = LineEdit(self)
        self.lineEdit.setFixedWidth(250)
        self.lineEdit.setPlaceholderText(placeholderText)
        self.lineEdit.setText(str(self.configItem.value))
        self.lineEdit.textChanged.connect(self._onTextChanged)

        self.hBoxLayout.addWidget(self.lineEdit, 1)
        self.hBoxLayout.addSpacing(16)

    def _onTextChanged(self, text):
        """文本改变时的处理"""
        cfg.set(self.configItem, text)


class PlainTextEditSettingCard(SettingCard):
    """自定义文本输入设置卡片"""

    def __init__(
        self, configItem, icon, title, content=None, placeholderText="", parent=None
    ):
        super().__init__(icon, title, content, parent)
        self.globalText = Text()
        self.configItem = configItem

        self.toolButton = ToolButton(FIF.TAG)
        self.toolButton.clicked.connect(self.showFlyout)

        self.lineEdit = PlainTextEdit(self)
        self.lineEdit.setFixedWidth(400)
        self.lineEdit.setFixedHeight(100)
        self.lineEdit.setPlaceholderText(placeholderText)
        self.lineEdit.setPlainText(str(self.configItem.value))
        self.lineEdit.textChanged.connect(self._onTextChanged)

        self.hBoxLayout.addWidget(self.toolButton)
        self.hBoxLayout.addSpacing(5)
        self.hBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.addSpacing(16)

    def _onTextChanged(self):
        """文本改变时的处理"""
        cfg.set(self.configItem, self.lineEdit.toPlainText())

    def showFlyout(self):
        Flyout.create(
            title=self.globalText.PromptWritingHelp,
            content=self.globalText.OLRTSLTLRTTLCRTTTBT,
            target=self.toolButton,
            parent=self,
            isClosable=True,
            aniType=FlyoutAnimationType.PULL_UP,
        )


class PasswordLineEditSettingCard(SettingCard):
    """自定义密码输入设置卡片"""

    def __init__(
        self, configItem, icon, title, content=None, placeholderText="", parent=None
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem

        self.lineEdit = PasswordLineEdit(self)
        self.lineEdit.setFixedWidth(250)
        self.lineEdit.setPlaceholderText(placeholderText)
        self.lineEdit.setText(str(self.configItem.value))
        self.lineEdit.textChanged.connect(self._onTextChanged)

        self.hBoxLayout.addWidget(self.lineEdit, 1)
        self.hBoxLayout.addSpacing(16)

    def _onTextChanged(self, text):
        """文本改变时的处理"""
        cfg.set(self.configItem, text)


class NumberLineEditSettingCard(SettingCard):
    """数字输入设置卡片，带验证"""

    def __init__(
        self,
        configItem,
        icon,
        title,
        content=None,
        placeholderText="",
        validator=None,
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.configItem = configItem
        self.validator = validator

        self.lineEdit = LineEdit(self)
        self.lineEdit.setFixedWidth(250)
        self.lineEdit.setPlaceholderText(placeholderText)
        self.lineEdit.setText(str(self.configItem.value))

        # 设置验证器
        if self.validator:
            self.lineEdit.setValidator(self.validator)

        self.lineEdit.textChanged.connect(self._onTextChanged)

        self.hBoxLayout.addWidget(self.lineEdit, 1)
        self.hBoxLayout.addSpacing(16)

    def _onTextChanged(self, text):
        """文本改变时的处理，带验证"""
        if text and self.validator:
            # 检查输入是否有效
            state, _, _ = self.validator.validate(text, 0)
            if state == QValidator.Acceptable:  # 修改为使用 QValidator.Acceptable
                # 根据配置项类型转换值
                if isinstance(self.validator, QIntValidator):
                    value = int(text)
                else:  # QDoubleValidator
                    value = float(text)
                cfg.set(self.configItem, value)
            # 如果输入无效，不更新配置


class ChooseFileSettingCard(SettingCard):
    """自定义选择文件设置卡片"""

    def __init__(
        self,
        icon,
        title,
        content=None,
        placeholderText="",
        parent=None,
    ):
        super().__init__(icon, title, content, parent)
        self.globalText = Text()

        self.lineEdit = LineEdit(self)
        self.lineEdit.setPlaceholderText(placeholderText)
        self.lineEdit.setReadOnly(True)

        self.browseBtn = PushButton(self.globalText.BrowseFile)

        self.remove_stretch()
        self.hBoxLayout.addSpacing(24)
        self.hBoxLayout.addWidget(self.lineEdit)
        self.hBoxLayout.addSpacing(8)
        self.hBoxLayout.addWidget(self.browseBtn)
        self.hBoxLayout.addSpacing(16)

    def remove_stretch(self):
        """删除弹簧"""
        last_index = self.hBoxLayout.count() - 1
        if last_index >= 0:
            item = self.hBoxLayout.itemAt(last_index)
            # 检查是否为弹簧
            if isinstance(item, QSpacerItem):
                self.hBoxLayout.removeItem(item)
                del item
