import os
import sys

from PySide6.QtCore import QFile, QLocale, Qt, QTranslator

from app.common.application import SingletonApplication
from app.common.config import Language, cfg
from app.resource import resource_rc  # noqa
from app.view.main_window import MainWindow
from libs.qfluentwidgets_pro import FluentTranslator


def main():
    # 界面缩放
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    # 创建应用程序实例
    app = SingletonApplication(sys.argv, "Easy-FFmpeg")
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    if sys.platform == "darwin":
        from AppKit import NSApplication

        NSApplication.sharedApplication()

    # 安装翻译器
    language = cfg.get(cfg.language)
    locale = QLocale.system() if language == Language.AUTO else language.value
    translator = FluentTranslator(locale)
    galleryTranslator = QTranslator()
    if language != Language.AUTO or QFile.exists(f":/app/i18n/app.{locale.name()}.qm"):
        galleryTranslator.load(locale, "app", ".", ":/app/i18n")

    app.installTranslator(translator)
    app.installTranslator(galleryTranslator)

    # 创建并显示主窗口
    window = MainWindow()
    app.aboutToQuit.connect(window.onExit)
    window.show()

    # 运行应用程序
    return app.exec()


if __name__ == "__main__":
    print(sys.platform)
    sys.exit(main())

# Easy-FFmpeg
