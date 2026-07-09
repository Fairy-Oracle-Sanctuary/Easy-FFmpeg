# coding: utf-8
"""FFmpeg 扫描服务：扫描系统 FFmpeg 可执行文件及其能力"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import List, Set

from PySide6.QtCore import QObject, QThread, Signal


# ---------------------------------------------------------------------------
# 常见 FFmpeg 安装路径（按平台区分）
# ---------------------------------------------------------------------------
_COMMON_WIN_PATHS = [
    # 默认 tools 目录
    "tools/ffmpeg.exe",
    "tools/ffmpeg/ffmpeg.exe",
    # 用户目录
    r"%USERPROFILE%\scoop\shims\ffmpeg.exe",
    r"%USERPROFILE%\AppData\Local\Microsoft\WinGet\Packages\ffmpeg.exe",
    r"%USERPROFILE%\AppData\Local\ffmpeg\ffmpeg.exe",
    # 标准 Program Files
    r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
    r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
    r"C:\ffmpeg\bin\ffmpeg.exe",
    r"C:\ffmpeg\ffmpeg.exe",
    # Chocolatey
    r"C:\ProgramData\chocolatey\bin\ffmpeg.exe",
]

_COMMON_MAC_PATHS = [
    "tools/ffmpeg",
    "tools/ffmpeg/ffmpeg",
    # Homebrew
    "/usr/local/bin/ffmpeg",
    "/opt/homebrew/bin/ffmpeg",
    # MacPorts
    "/opt/local/bin/ffmpeg",
]

_COMMON_LINUX_PATHS = [
    "tools/ffmpeg",
    "tools/ffmpeg/ffmpeg",
    "/usr/bin/ffmpeg",
    "/usr/local/bin/ffmpeg",
    "/snap/bin/ffmpeg",
]


def _get_common_paths() -> List[str]:
    """返回当前平台下的常见 ffmpeg 候选路径列表"""
    if sys.platform == "win32":
        paths = list(_COMMON_WIN_PATHS)
        # 展开环境变量
        paths = [os.path.expandvars(p) for p in paths]
    elif sys.platform == "darwin":
        paths = list(_COMMON_MAC_PATHS)
    else:
        paths = list(_COMMON_LINUX_PATHS)
    return paths


# ---------------------------------------------------------------------------
# 纯函数式扫描工具（可直接在 QThread.run 中调用）
# ---------------------------------------------------------------------------


def find_ffmpeg_paths() -> List[str]:
    """扫描系统中所有能找到的 ffmpeg 可执行文件路径

    返回按优先级排序的路径列表（越靠前越推荐）。
    """
    found: List[str] = []

    # 1. 从 PATH 环境变量查找
    which_path = shutil.which("ffmpeg")
    if which_path:
        found.append(which_path)

    # 2. 检查默认 tools 目录
    default_path = Path(f"tools/ffmpeg{'.exe' if sys.platform == 'win32' else ''}")
    if default_path.exists():
        found.append(str(default_path.absolute()))

    # 3. 扫描常见安装路径
    for p in _get_common_paths():
        expanded = os.path.expandvars(p) if sys.platform == "win32" else p
        fp = Path(expanded)
        if fp.exists() and fp.is_file():
            if str(fp.absolute()) not in found:
                found.append(str(fp.absolute()))

    return found


def get_ffmpeg_version(ffmpeg_path: str) -> str:
    """获取 FFmpeg 版本信息

    返回版本字符串，如 ``"7.1"``；失败时返回空字符串。
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            timeout=15,
        )
        first_line = result.stdout.decode("utf-8", errors="replace").splitlines()[0]
        # 解析版本号: ffmpeg version x.y.z
        match = re.search(r"version\s+(\S+)", first_line)
        return match.group(1) if match else first_line.strip()
    except Exception:
        return ""


def get_ffmpeg_full_version_text(ffmpeg_path: str) -> str:
    """获取完整的 ffmpeg -version 输出（含编译配置）"""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-version"],
            capture_output=True,
            timeout=15,
        )
        return result.stdout.decode("utf-8", errors="replace").strip()
    except Exception:
        return ""


def scan_hwaccels(ffmpeg_path: str) -> List[str]:
    """扫描支持的硬件加速器

    返回列表如 ``["cuda", "qsv", "dxva2"]``。
    """
    try:
        result = subprocess.run(
            [ffmpeg_path, "-hwaccels"],
            capture_output=True,
            timeout=15,
        )
        lines = result.stdout.decode("utf-8", errors="replace").splitlines()
        # 第一行通常是 "Hardware acceleration methods:"，跳过
        hwaccels = []
        for line in lines:
            line = line.strip()
            if line and not line.startswith("Hardware"):
                hwaccels.append(line)
        return hwaccels
    except Exception:
        return []


def scan_encoders(ffmpeg_path: str, keyword: str = "") -> Set[str]:
    """扫描支持的编码器

    Args:
        ffmpeg_path: ffmpeg 可执行文件路径
        keyword: 可选过滤关键字，如 ``"nvenc"`` 只返回包含 nvenc 的编码器

    Returns:
        编码器名称集合
    """
    return _scan_list_output(ffmpeg_path, "-encoders", keyword)


def scan_decoders(ffmpeg_path: str, keyword: str = "") -> Set[str]:
    """扫描支持的解码器

    Args:
        ffmpeg_path: ffmpeg 可执行文件路径
        keyword: 可选过滤关键字

    Returns:
        解码器名称集合
    """
    return _scan_list_output(ffmpeg_path, "-decoders", keyword)


def scan_demuxers(ffmpeg_path: str, keyword: str = "") -> Set[str]:
    """扫描支持的解封装格式"""
    return _scan_list_output(ffmpeg_path, "-demuxers", keyword)


def scan_muxers(ffmpeg_path: str, keyword: str = "") -> Set[str]:
    """扫描支持的封装格式"""
    return _scan_list_output(ffmpeg_path, "-muxers", keyword)


def scan_protocols(ffmpeg_path: str) -> Set[str]:
    """扫描支持的协议"""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-protocols"],
            capture_output=True,
            timeout=15,
        )
        lines = result.stdout.decode("utf-8", errors="replace").splitlines()
        protocols: Set[str] = set()
        for line in lines:
            # 协议行通常以空格开头，包含协议名
            stripped = line.strip()
            if stripped and not stripped.startswith(("Input", "Output", "File", "protocols")):
                parts = stripped.split()
                for part in parts:
                    if part.isascii() and part.islower() and ":" not in part:
                        protocols.add(part)
        return protocols
    except Exception:
        return set()


def _scan_list_output(ffmpeg_path: str, flag: str, keyword: str = "") -> Set[str]:
    """通用的 ffmpeg -list 输出解析"""
    try:
        result = subprocess.run(
            [ffmpeg_path, flag],
            capture_output=True,
            timeout=30,
        )
        output = result.stdout.decode("utf-8", errors="replace")
        items: Set[str] = set()
        for line in output.splitlines():
            # 格式通常如 " DEV.L. h264                 H.264 / AVC"
            stripped = line.strip()
            if not stripped or stripped.startswith(("Encoders", "Decoders", "Codecs")):
                continue
            parts = stripped.split()
            # 跳过 flags 行（如 " DEV.L. "）
            if len(parts) >= 2 and parts[0].isupper() and len(parts[0]) <= 6:
                name = parts[1] if len(parts) > 1 else ""
            else:
                name = parts[0] if parts else ""
            if name and not keyword or (keyword.lower() in name.lower()):
                items.add(name)
        return items
    except Exception:
        return set()


def scan_codecs(ffmpeg_path: str, keyword: str = "") -> Set[str]:
    """扫描支持的编解码器（codecs）"""
    try:
        result = subprocess.run(
            [ffmpeg_path, "-codecs"],
            capture_output=True,
            timeout=30,
        )
        output = result.stdout.decode("utf-8", errors="replace")
        codecs: Set[str] = set()
        for line in output.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("Codecs"):
                continue
            # 格式: " DEV.L. h264                 H.264 / AVC / MPEG-4 AVC"
            parts = stripped.split()
            if len(parts) >= 2 and parts[0].isupper() and len(parts[0]) <= 6:
                name = parts[1]
                if not keyword or keyword.lower() in name.lower():
                    codecs.add(name)
        return codecs
    except Exception:
        return set()


# ---------------------------------------------------------------------------
# 扫描结果聚合
# ---------------------------------------------------------------------------


class FFmpegScanResult:
    """一次完整扫描的结果快照"""

    def __init__(self):
        self.ffmpeg_path: str = ""  # 找到的 ffmpeg 路径
        self.version: str = ""  # 版本号
        self.version_text: str = ""  # -version 完整输出
        self.hwaccels: List[str] = []  # 硬件加速器列表
        self.encoders: Set[str] = set()  # 编码器
        self.decoders: Set[str] = set()  # 解码器
        self.demuxers: Set[str] = set()  # 解封装格式
        self.muxers: Set[str] = set()  # 封装格式
        self.protocols: Set[str] = set()  # 协议
        self.codecs: Set[str] = set()  # 编解码器
        self.has_nvenc: bool = False  # NVIDIA NVENC 编码
        self.has_qsv: bool = False  # Intel QuickSync
        self.has_videotoolbox: bool = False  # macOS VideoToolbox
        self.has_amf: bool = False  # AMD AMF

    @property
    def available(self) -> bool:
        """是否成功找到可用的 FFmpeg"""
        return bool(self.ffmpeg_path) and bool(self.version)


def run_full_scan(ffmpeg_path: str = "") -> FFmpegScanResult:
    """执行一次完整的 FFmpeg 扫描

    Args:
        ffmpeg_path: 指定 ffmpeg 路径。为空时自动扫描系统。

    Returns:
        FFmpegScanResult 扫描结果
    """
    result = FFmpegScanResult()

    # 1. 定位 ffmpeg
    if not ffmpeg_path:
        paths = find_ffmpeg_paths()
        if not paths:
            return result
        ffmpeg_path = paths[0]

    result.ffmpeg_path = ffmpeg_path

    # 2. 版本
    result.version = get_ffmpeg_version(ffmpeg_path)
    result.version_text = get_ffmpeg_full_version_text(ffmpeg_path)

    if not result.version:
        return result

    # 3. 硬件加速
    result.hwaccels = scan_hwaccels(ffmpeg_path)
    result.has_nvenc = "cuda" in result.hwaccels
    result.has_qsv = "qsv" in result.hwaccels
    result.has_videotoolbox = "videotoolbox" in result.hwaccels
    result.has_amf = "amf" in result.hwaccels

    # 4. 编码器（按常见硬件编码器关键字过滤做二次确认）
    result.encoders = scan_encoders(ffmpeg_path)
    if not result.has_nvenc:
        nvenc_encoders = {e for e in result.encoders if "nvenc" in e}
        if nvenc_encoders:
            result.has_nvenc = True
    if not result.has_qsv:
        qsv_encoders = {e for e in result.encoders if "qsv" in e}
        if qsv_encoders:
            result.has_qsv = True
    if not result.has_videotoolbox:
        vt_encoders = {e for e in result.encoders if "videotoolbox" in e}
        if vt_encoders:
            result.has_videotoolbox = True
    if not result.has_amf:
        amf_encoders = {e for e in result.encoders if "amf" in e}
        if amf_encoders:
            result.has_amf = True

    # 5. 解码器、格式等
    result.decoders = scan_decoders(ffmpeg_path)
    result.demuxers = scan_demuxers(ffmpeg_path)
    result.muxers = scan_muxers(ffmpeg_path)

    return result


# ---------------------------------------------------------------------------
# QThread 封装（用于 UI 异步调用）
# ---------------------------------------------------------------------------


class FFmpegScanThread(QThread):
    """FFmpeg 扫描线程

    发射信号:
        progress(str): 当前扫描阶段描述
        finished(FFmpegScanResult): 扫描结果
    """

    progress = Signal(str)
    finished = Signal(object)

    def __init__(self, ffmpeg_path: str = "", parent=None):
        super().__init__(parent=parent)
        self.ffmpeg_path = ffmpeg_path

    def run(self):
        """执行扫描（在子线程中运行）"""
        self.progress.emit("正在定位 FFmpeg...")

        if not self.ffmpeg_path:
            paths = find_ffmpeg_paths()
            if not paths:
                self.finished.emit(FFmpegScanResult())
                return
            self.ffmpeg_path = paths[0]

        self.progress.emit("正在获取版本信息...")
        result = run_full_scan(self.ffmpeg_path)
        self.finished.emit(result)
