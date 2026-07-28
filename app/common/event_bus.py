# core/event_bus.py
from PySide6.QtCore import QObject, Signal
from ..common.task_status import TaskStatus

class GlobalEventBus(QObject):
    """全局事件总线，负责组件间通信"""

    # 检查更新
    checkUpdateSig = Signal()

    # 通知服务
    notification_service = None

    # 添加任务
    addTaskSig = Signal(set, set)  # 视频文件集合，音频文件集合

    # 任务完成
    finishTaskSig = Signal(int, bool)  # task_id, 是否成功

    # 删除任务
    deleteTaskSig = Signal(int, bool)  # task_id, 是否同时删除文件

    # 更新任务状态进度
    updateTaskStatusSig = Signal(int, int, TaskStatus, str, float, str, float)  
    #                         task_id, progress, status, size, time, bitrate, speed

    # 取消任务
    cancelTaskSig = Signal(int)  # task_id

    # 重试任务
    retryTaskSig = Signal(int)  # task_id

    # 任务数量变化
    taskCountChanged = Signal(int)  # 当前任务数量

    # 是否存在失败任务
    hasFailedTasks = Signal(bool)


# 创建全局单例
event_bus = GlobalEventBus()
