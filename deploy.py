import os
import sys

from app.common.setting import VERSION

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
        "pyinstaller",
        "-w",
        "Easy-FFmpeg.py",
    ]


os.system(" ".join(args))
