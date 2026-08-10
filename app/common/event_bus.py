# core/event_bus.py
from dataclasses import dataclass

from PySide6.QtCore import QObject, Signal

from ..common.task_status import TaskStatus


@dataclass
class ToolTaskInfo:
    """功能页提交的工具任务信息（走主任务队列，复用 FFmpegWorker）

    功能页（音频提取/GIF 制作等）构建好完整 ffmpeg args 后封装为本类，
    通过 event_bus.addToolTaskSig 提交。输出路径约定为 args 末尾元素。
    """

    input_path: str
    args: list
    output_name: str = ""
    save_folder: str = ""
    title: str = ""
    allow_duplicate: bool = False  # 允许相同输入重复添加（如批量生成多尺寸徽标）


class GlobalEventBus(QObject):
    """全局事件总线，负责组件间通信"""

    # 云母效果启用状态变化
    micaEnableChanged = Signal(bool)

    # 应用消息信号
    appMessageSig = Signal(str)

    # 应用错误信号
    appErrorSig = Signal(str)

    # 检查更新
    checkUpdateSig = Signal()

    # 检查更新状态变化 True=开始检查 False=完成
    checkUpdateStateChanged = Signal(bool)

    # 新版本检测到（传入新版本号，空字符串=无新版本，供按钮显示版本号徽标）
    newVersionDetected = Signal(str)

    # 通知服务
    notification_service = None

    # 添加任务
    addTaskSig = Signal(set, set, set)  # 视频文件集合，音频文件集合，图片文件集合

    # 添加工具任务（功能页自定义 ffmpeg 命令），payload: ToolTaskInfo
    addToolTaskSig = Signal(object)

    # 任务完成
    finishTaskSig = Signal(int, bool, str)  # task_id, 是否成功, logPath

    # 删除任务
    deleteTaskSig = Signal(int, bool)  # task_id, 是否同时删除文件

    # 更新任务状态进度
    updateTaskStatusSig = Signal(int, int, TaskStatus, str, float, str, float)
    #                         task_id, progress, status, size, time, bitrate, speed

    # two-pass 阶段切换（task_id, 阶段文案），仅 two-pass 任务会 emit
    taskStageChangedSig = Signal(int, str)

    # 取消任务
    cancelTaskSig = Signal(int)  # task_id

    # 重试任务
    retryTaskSig = Signal(int)  # task_id

    # 任务数量变化
    taskCountChanged = Signal(int)  # 当前任务数量

    # 是否存在失败任务
    hasFailedTasks = Signal(bool)

    # 托盘消息 (title, message, type)  type: "info" | "warning"
    trayMessageSig = Signal(str, str, str)

    # 关闭应用
    forceQuitSig = Signal()


# 创建全局单例
event_bus = GlobalEventBus()
