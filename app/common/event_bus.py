# core/event_bus.py
from PySide6.QtCore import QObject, Signal


class GlobalEventBus(QObject):
    """全局事件总线，负责组件间通信"""

    # 检查更新
    checkUpdateSig = Signal()

    # 通知服务
    notification_service = None


# 创建全局单例
event_bus = GlobalEventBus()
