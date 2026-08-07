import os
import shutil
import sys

from app.common.setting import VERSION


def _check_linux_deps():
    """Check Linux build dependencies (required by Nuitka standalone mode)"""
    required = {
        "patchelf": "apt install patchelf",
        "readelf": "apt install binutils",
        "gcc": "apt install build-essential",
    }
    missing = []
    for tool, hint in required.items():
        if shutil.which(tool) is None:
            missing.append(f"  {tool}  ->  {hint}")
    if missing:
        print("Missing build dependencies:")
        print("\n".join(missing))
        print("\nInstall them first, then retry.")
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
        # Bundle tools/ffmpeg.exe into Easy-FFmpeg.dist/tools/
        "--include-data-dir=tools=tools",
        # Exclude unused heavy libraries to reduce package size
        "--nofollow-import-to=numpy",
        "--nofollow-import-to=scipy",
        # Exclude optional acrylic-blur dependencies (falls back when numpy/scipy missing)
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
        # Link-time optimization to significantly reduce exe size
        "--lto=yes",
        # Drop unused Qt translation files
        "--noinclude-qt-translations",
        "--output-dir=dist",
        "Easy-FFmpeg.py",
    ]
elif sys.platform == "darwin":
    args = [
        sys.executable,
        "-m",
        "nuitka",
        "--standalone",
        "--macos-create-app-bundle",
        "--plugin-enable=pyside6",
        "--include-qt-plugins=sensible",
        "--assume-yes-for-downloads",
        "--show-memory",
        "--show-progress",
        "--macos-app-icon=app/resource/images/logo.icns",
        "--macos-app-name=Easy-FFmpeg",
        # Bundle tools/ffmpeg into .app's Contents/MacOS/tools/
        "--include-data-dir=tools=tools",
        f"--file-version={VERSION}",
        f"--product-version={VERSION}",
        "--file-description=Easy-FFmpeg",
        # Exclude unused heavy libraries to reduce package size
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
        # Link-time optimization to significantly reduce binary size
        "--lto=yes",
        # Drop unused Qt translation files
        "--noinclude-qt-translations",
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
        # Exclude unused heavy libraries to reduce package size
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
        # Link-time optimization to significantly reduce binary size
        "--lto=yes",
        # Drop unused Qt translation files
        "--noinclude-qt-translations",
        "--output-dir=dist",
        "Easy-FFmpeg.py",
    ]


os.system(" ".join(args))


def cleanup_dist(dist_dir: str):
    """Remove unneeded Qt plugins/dlls from dist (Nuitka plugin set is not precise)"""
    removable = [
        # QtPdf collected by mistake (normally blocked by --nofollow-import-to; belt and braces)
        "qt6pdf.dll",
        "qt6pdfwidgets.dll",
        "pythoncom39.dll",
        # platforms: qwindows is enough; qdirect2d is a redundant software-rendering backend
        r"PySide6\qt-plugins\platforms\qdirect2d.dll",
        # imageformats: app only uses png/jpg/ico/svg, the rest are redundant decoders
        r"PySide6\qt-plugins\imageformats\qwebp.dll",
        r"PySide6\qt-plugins\imageformats\qtiff.dll",
        r"PySide6\qt-plugins\imageformats\qicns.dll",
        r"PySide6\qt-plugins\imageformats\qtga.dll",
        r"PySide6\qt-plugins\imageformats\qwbmp.dll",
        r"PySide6\qt-plugins\imageformats\qpdf.dll",
        r"PySide6\qt-plugins\imageformats\qgif.dll",
        # tls: keep openssl + schannel backends; certonly is redundant
        r"PySide6\qt-plugins\tls\qcertonlybackend.dll",
    ]
    removed = 0
    for rel in removable:
        fp = os.path.join(dist_dir, rel)
        if os.path.isfile(fp):
            size = os.path.getsize(fp)
            os.remove(fp)
            removed += size
            print(f"  Removed {rel} ({size / 1024:.0f} KB)")
    if removed:
        print(f"  Total cleaned {removed / 1024 / 1024:.1f} MB")


if sys.platform == "win32":
    dist_dir = os.path.join("dist", "Easy-FFmpeg.dist")
    if os.path.isdir(dist_dir):
        cleanup_dist(dist_dir)
