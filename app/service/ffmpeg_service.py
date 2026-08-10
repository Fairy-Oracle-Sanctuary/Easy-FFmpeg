import re
import time
from pathlib import Path

from PySide6.QtCore import QDateTime, QEventLoop, QProcess, QRunnable

from ..common.config import cfg
from ..common.event_bus import event_bus
from ..common.logger import Logger
from ..common.task_status import TaskStatus
from ..common.text import Text

# 解析 ffmpeg 输出
DURATION_RE = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)")
TIME_RE = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}\.\d+)")
SIZE_RE = re.compile(r"size=\s*(\S+)")
BITRATE_RE = re.compile(r"bitrate=\s*(\S+)")
SPEED_RE = re.compile(r"speed=\s*([\d.]+)")


class FFmpegTask:
    _task_id = 0

    def __init__(
        self,
        args: list,
        fileName: str,
        videoPath: str,
        saveFolder: str,
        outputName: str = "",
        two_pass: bool = False,
        args_pass1: list = None,
        passlogfile: str = "",
        is_custom_args: bool = False,
        custom_template: str = "",
        is_audio: bool = False,
        is_image: bool = False,
        is_tool_task: bool = False,
    ):
        FFmpegTask._task_id += 1
        self.task_id: int = FFmpegTask._task_id
        self.args: list = args
        self.fileName: str = fileName
        self.videoPath: str = videoPath
        self.saveFolder: str = saveFolder
        self.outputName: str = outputName
        self.logPath = None
        self.createTime = QDateTime.currentDateTime()
        # two-pass 支持：pass1 参数与 passlog 文件前缀（用于完成后清理）
        self.two_pass: bool = two_pass
        self.args_pass1: list = args_pass1 or []
        self.passlogfile: str = passlogfile
        # 重试重建参数所需元信息
        self.is_custom_args: bool = is_custom_args
        self.custom_template: str = custom_template
        self.is_audio: bool = is_audio
        self.is_image: bool = is_image
        # 工具任务（功能页自定义命令）：args 固定，重试时不重建参数
        self.is_tool_task: bool = is_tool_task


class FFmpegWorker(QRunnable):
    def __init__(self, task: FFmpegTask, text=None):
        super().__init__()
        self.task: FFmpegTask = task
        self._text = text or Text()
        self.args: list = self.task.args
        self.duration: float = 0.0
        self._last_emit = 0.0
        self.taskLogger = None
        self.process = None
        # two-pass 阶段：0=单 pass, 1=pass1 分析, 2=pass2 编码
        self._stage = 0
        self._cancelled = False
        # 多输入(如 concat)时长累加：编码开始前累积 stderr，反复求和所有 Duration
        self._stderr_buffer = ""
        self._duration_frozen = False

    def run(self):
        # create logger
        currentTime = self.task.createTime.toString("yyyy-MM-dd_hh-mm-ss")
        self.taskLogger = Logger(
            "Tasks/" + currentTime + f"_taskID-{self.task.task_id}", False
        )
        self.task.logPath = str(self.taskLogger.logFile.absolute())
        message = f"addTask args: {cfg.get(cfg.ffmpegPath)} {' '.join(self.args)}"
        self.taskLogger.info(message)
        if self.task.two_pass:
            self.taskLogger.info(
                f"two-pass enabled, pass1 args: {cfg.get(cfg.ffmpegPath)} "
                f"{' '.join(self.task.args_pass1)}"
            )

        event_bus.updateTaskStatusSig.emit(
            self.task.task_id,
            0,
            TaskStatus.Pending,
            "0KiB",
            0.0,
            "0kbits/s",
            0.0,
        )

        if self.task.two_pass:
            # pass 1：仅分析，输出到空设备
            event_bus.taskStageChangedSig.emit(
                self.task.task_id, self._text.PassOneAnalyze
            )
            if not self._run_stage(self.task.args_pass1, 1):
                self._finish(False)
                return
            if self._cancelled or self.process.exitCode() != 0:
                self._finish(False)
                return
            # pass 2：基于分析结果编码
            event_bus.taskStageChangedSig.emit(
                self.task.task_id, self._text.PassTwoEncode
            )
            if not self._run_stage(self.args, 2):
                self._finish(False)
                return
            success = self.process.exitCode() == 0 and not self._cancelled
        else:
            if not self._run_stage(self.args, 0):
                self._finish(False)
                return
            success = self.process.exitCode() == 0 and not self._cancelled

        self._finish(success)

    def _run_stage(self, args, stage) -> bool:
        """执行单阶段 ffmpeg，返回是否成功启动

        stage: 0=单 pass, 1=two-pass 第一遍, 2=two-pass 第二遍。
        每阶段重置 duration，使进度解析基于当前阶段重新解析视频时长。
        self.process 始终指向当前阶段进程，便于取消时 kill。
        """
        self._stage = stage
        self.duration = 0.0
        self._last_emit = 0.0
        self._stderr_buffer = ""
        self._duration_frozen = False
        self.process = QProcess()
        self.process.readyReadStandardError.connect(self._handle_stderr)
        loop = QEventLoop()
        self.process.finished.connect(loop.quit)
        self.process.start(cfg.get(cfg.ffmpegPath), args)
        if not self.process.waitForStarted():
            return False
        loop.exec()
        return True

    def cancel(self):
        """取消任务：标记并 kill 当前阶段进程

        供 TaskInterface._handle_cancel_task 调用，替代直接访问 self.process.kill()。
        标记 _cancelled 后，pass 1 结束不会自动启动 pass 2，_finish 也不 emit 完成信号
        （取消状态已由调用方设为 Cancelled）。
        """
        self._cancelled = True
        if self.process:
            self.process.kill()

    def _try_parse_duration(self, data: str):
        """解析视频总时长：多输入(如 concat)时累加所有 Duration 求和

        反复从已累积的 stderr 缓冲重新解析全部 Duration 行求和，避免跨块
        去重问题。一旦出现 time=（编码开始），所有输入已探测完毕，冻结
        时长不再更新。
        """
        matches = DURATION_RE.findall(data)
        if matches:
            self.duration = sum(
                int(h) * 3600 + int(m) * 60 + float(s) for h, m, s in matches
            )
        if TIME_RE.search(data):
            self._duration_frozen = True

    def _parse_progress(self, data: str):
        """解析当前压制进度，节流到每秒最多 4 次

        two-pass 下进度按阶段映射：
        - pass 1 → 0%–50%
        - pass 2 → 50%–100%
        单 pass 维持 0%–100%。
        """
        # size=     256KiB  time=00:00:32.23  bitrate=  65.1kbits/s  speed=61.9x  elapsed=0:00:00.52
        if self.duration <= 0:
            return
        now = time.time()
        if now - self._last_emit < 0.25:
            return
        match = TIME_RE.search(data)
        if not match:
            return

        self._last_emit = now
        hours = int(match.group(1))
        minutes = int(match.group(2))
        seconds = float(match.group(3))
        current = round(hours * 3600 + minutes * 60 + seconds, 2)
        ratio = current / self.duration
        if self._stage == 1:
            progress = int(ratio * 50)
        elif self._stage == 2:
            progress = 50 + int(ratio * 50)
        else:
            progress = int(ratio * 100)

        # 解析其他字段
        size = ""
        size_match = SIZE_RE.search(data)
        if size_match:
            size = size_match.group(1)

        bitrate = ""
        bitrate_match = BITRATE_RE.search(data)
        if bitrate_match:
            bitrate = bitrate_match.group(1)

        speed = 0.0
        speed_match = SPEED_RE.search(data)
        if speed_match:
            speed = round(float(speed_match.group(1)), 2)

        event_bus.updateTaskStatusSig.emit(
            self.task.task_id,
            progress,
            TaskStatus.Processing,
            size,
            current,
            bitrate,
            speed,
        )

    def _handle_stderr(self):
        """ffmpeg 全部输出到 stderr"""
        data = (
            self.process.readAllStandardError().data().decode("utf-8", errors="ignore")
        )
        # 编码开始前累积 stderr，供 _try_parse_duration 反复求和所有 Duration
        # 一旦冻结（time= 出现），停止累积，避免长任务内存增长
        if not self._duration_frozen:
            self._stderr_buffer += data
            self._try_parse_duration(self._stderr_buffer)
        self._parse_progress(data)
        self.taskLogger.info(data)

    def _finish(self, success: bool):
        """任务结束统一处理：关日志、清临时文件、emit 完成信号"""
        if self.taskLogger:
            self.taskLogger.close()
        # 清理 two-pass 临时日志文件（ffmpeg2pass-*.log）
        if self.task.two_pass and self.task.passlogfile:
            self._cleanup_passlog()
        # 取消的任务不 emit finishTaskSig（状态已由 _handle_cancel_task 设为 Cancelled）
        if self._cancelled:
            return
        event_bus.finishTaskSig.emit(self.task.task_id, success, self.task.logPath)

    def _cleanup_passlog(self):
        """删除 ffmpeg two-pass 生成的临时日志文件

        ffmpeg 会在 passlogfile 路径后追加 -0.log 及衍生后缀：
        - -0.log          pass 1 正常完成后的统计文件
        - -0.log.mbtree   宏块树统计（libx264/libx265）
        - -0.log.temp     pass 1 被中断时未重命名的临时文件
        用 glob 匹配 -0.log* 一并清理，避免取消时残留 .log.temp。
        """
        base = Path(self.task.passlogfile)
        for p in base.parent.glob(f"{base.name}-0.log*"):
            try:
                p.unlink()
            except OSError:
                pass
