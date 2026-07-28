import re
import time

from PySide6.QtCore import QEventLoop, QProcess, QRunnable

from ..common.config import cfg
from ..common.event_bus import event_bus
from ..common.task_status import TaskStatus

# 解析 ffmpeg 输出
DURATION_RE = re.compile(r"Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)")
TIME_RE = re.compile(r"time=(\d{2}):(\d{2}):(\d{2}\.\d+)")
SIZE_RE = re.compile(r"size=\s*(\S+)")
BITRATE_RE = re.compile(r"bitrate=\s*(\S+)")
SPEED_RE = re.compile(r"speed=\s*([\d.]+)")


class FFmpegTask:
    _task_id = 0

    def __init__(self, args: list, fileName: str, videoPath: str, saveFolder: str, outputName: str = ""):
        FFmpegTask._task_id += 1
        self.task_id: int = FFmpegTask._task_id
        self.args: list = args
        self.fileName = fileName
        self.videoPath = videoPath
        self.saveFolder = saveFolder
        self.outputName = outputName
        
class FFmpegWorker(QRunnable):
    def __init__(self, task: FFmpegTask):
        super().__init__()
        self.task: FFmpegTask = task
        self.args: list = self.task.args
        self.duration: float = 0.0
        self._last_emit = 0.0

    def run(self):
        self.process = QProcess()
        self.process.readyReadStandardError.connect(self._handle_stderr)
        self.process.finished.connect(self._handle_finished)
        event_bus.updateTaskStatusSig.emit(
            self.task.task_id, 0, TaskStatus.Pending,
            "0KiB", 0.0, "0kbits/s", 0.0,
        )
        loop = QEventLoop()
        self.process.finished.connect(loop.quit)
        self.process.start(cfg.get(cfg.ffmpegPath), self.args)

        if not self.process.waitForStarted():
            return
        loop.exec()

    def _try_parse_duration(self, data: str):
        """解析视频总时长（仅首次成功前尝试）"""
        if self.duration > 0:
            return
        match = DURATION_RE.search(data)
        if match:
            hours = int(match.group(1))
            minutes = int(match.group(2))
            seconds = float(match.group(3))
            self.duration = hours * 3600 + minutes * 60 + seconds

    def _parse_progress(self, data: str):
        """解析当前压制进度，节流到每秒最多 4 次"""
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
        progress = int(current / self.duration * 100)

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
            self.task.task_id, progress, TaskStatus.Processing,
            size, current, bitrate, speed,
        )

    def _handle_stderr(self):
        """ffmpeg 全部输出到 stderr"""
        data = self.process.readAllStandardError().data().decode("utf-8", errors="ignore")
        self._try_parse_duration(data)
        self._parse_progress(data)

    def _handle_finished(self):
        """ffmpeg 执行完成"""
        event_bus.finishTaskSig.emit(self.task.task_id, self.process.exitCode() == 0)
