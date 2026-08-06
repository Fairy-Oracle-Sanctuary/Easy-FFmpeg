import os
import shutil
import sys

from app.common.setting import VERSION


def _check_linux_deps():
    """检查 Linux 打包所需系统依赖（Nuitka standalone 模式硬依赖）"""
    required = {
        "patchelf": "apt install patchelf",
        "readelf": "apt install binutils",
        "gcc": "apt install build-essential",
    }
    missing = []
    for tool, hint in required.items():
        if shutil.which(tool) is None:
            missing.append(f"  {tool}  →  {hint}")
    if missing:
        print("缺少打包所需系统依赖：")
        print("\n".join(missing))
        print("\n请先安装后重试。")
        sys.exit(1)


if sys.platform == "linux":
    _check_linux_deps()

if sys.platform == "win32":
    args = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--windows-disable-console",
        "--plugin-enable=pyside6",
        "--include-qt-plugins=sensible",
        "--assume-yes-for-downloads",
        # '--msvc=latest',              # Use MSVC
        "--mingw64",  # Use MinGW
        "--show-memory",
        "--show-progress",
        "--windows-icon-from-ico=app/resource/images/logo.ico",
        f"--windows-file-version={VERSION}",
        f"--windows-product-version={VERSION}",
        '--windows-file-description="Easy-FFmpeg"',
        # 排除未使用的重型库，减小打包体积
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        # 排除 acrylic 模糊的可选依赖（numpy/scipy 缺失时本就走 fallback）
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=colorthief",
        "--nofollow-import-to=PySide6.QtWebChannel",
        "--nofollow-import-to=PySide6.QtWebEngineCore",
        "--nofollow-import-to=PySide6.QtWebEngineWidgets",
        "--nofollow-import-to=PySide6.QtPositioning",
        "--nofollow-import-to=PySide6.QtQml",
        "--nofollow-import-to=PySide6.QtQmlModels",
        "--nofollow-import-to=PySide6.QtQuick",
        "--nofollow-import-to=PySide6.QtQuickWidgets",
        "--nofollow-import-to=PySide6.QtPrintSupport",
        "--nofollow-import-to=PySide6.QtOpenGL",
        "--nofollow-import-to=PySide6.QtPdf",
        "--nofollow-import-to=pythoncom",
        # 链接期优化，显著减小 exe 体积
        "--lto=yes",
        # 去掉未使用的 Qt 翻译文件
        "--noinclude-qt-translations",
        "--output-dir=dist",
        "Easy-FFmpeg.py",
    ]
elif sys.platform == "darwin":
    args = [
        "python3 -m nuitka",
        "--standalone",
        "--plugin-enable=pyside6",
        "--include-qt-plugins=sensible",
        "--show-memory",
        "--show-progress",
        "--macos-create-app-bundle",
        "--assume-yes-for-download",
        "--macos-disable-console",
        f"--macos-app-version={VERSION}",
        "--macos-app-name=Easy-FFmpeg",
        "--macos-app-icon=app/resource/images/logo.icns",
        "--copyright=zhiyiYo",
        "--output-dir=dist",
        "Easy-FFmpeg.py",
    ]
else:
    args = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--plugin-enable=pyside6",
        "--include-qt-plugins=sensible",
        "--assume-yes-for-downloads",
        "--show-memory",
        "--show-progress",
        "--linux-icon=app/resource/images/logo.icns",
        f"--file-version={VERSION}",
        f"--product-version={VERSION}",
        "--file-description=Easy-FFmpeg",
        # 排除未使用的重型库，减小打包体积
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        "--nofollow-import-to=PIL",
        "--nofollow-import-to=colorthief",
        "--nofollow-import-to=PySide6.QtWebChannel",
        "--nofollow-import-to=PySide6.QtWebEngineCore",
        "--nofollow-import-to=PySide6.QtWebEngineWidgets",
        "--nofollow-import-to=PySide6.QtPositioning",
        "--nofollow-import-to=PySide6.QtQml",
        "--nofollow-import-to=PySide6.QtQmlModels",
        "--nofollow-import-to=PySide6.QtQuick",
        "--nofollow-import-to=PySide6.QtQuickWidgets",
        "--nofollow-import-to=PySide6.QtPrintSupport",
        "--nofollow-import-to=PySide6.QtOpenGL",
        "--nofollow-import-to=PySide6.QtPdf",
        # 链接期优化，显著减小体积
        "--lto=yes",
        # 去掉未使用的 Qt 翻译文件
        "--noinclude-qt-translations",
        "--output-dir=dist",
        "Easy-FFmpeg.py",
    ]


os.system(" ".join(args))


def cleanup_dist(dist_dir: str):
    """编译后清理 dist 中多余的 Qt 插件/dll（Nuitka 插件集无法精确到单个插件）"""
    removable = [
        # QtPdf 误收集（正常已被 --nofollow-import-to 拦截，双保险）
        "qt6pdf.dll",
        "qt6pdfwidgets.dll",
        "pythoncom39.dll",
        # platforms：qwindows 已够用，qdirect2d 是多余的软件渲染后端
        r"PySide6\qt-plugins\platforms\qdirect2d.dll",
        # imageformats：应用只用 png/jpg/ico/svg，其余格式解码插件全部多余
        r"PySide6\qt-plugins\imageformats\qwebp.dll",
        r"PySide6\qt-plugins\imageformats\qtiff.dll",
        r"PySide6\qt-plugins\imageformats\qicns.dll",
        r"PySide6\qt-plugins\imageformats\qtga.dll",
        r"PySide6\qt-plugins\imageformats\qwbmp.dll",
        r"PySide6\qt-plugins\imageformats\qpdf.dll",
        r"PySide6\qt-plugins\imageformats\qgif.dll",
        # tls：保留 openssl + schannel 后端即可，certonly 冗余
        r"PySide6\qt-plugins\tls\qcertonlybackend.dll",
    ]
    removed = 0
    for rel in removable:
        fp = os.path.join(dist_dir, rel)
        if os.path.isfile(fp):
            size = os.path.getsize(fp)
            os.remove(fp)
            removed += size
            print(f"  清理 {rel} ({size / 1024:.0f} KB)")
    if removed:
        print(f"  共清理 {removed / 1024 / 1024:.1f} MB")


if sys.platform == "win32":
    dist_dir = os.path.join("dist", "Easy-FFmpeg.dist")
    if os.path.isdir(dist_dir):
        cleanup_dist(dist_dir)
