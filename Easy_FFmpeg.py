import os
import sys

from PySide6.QtCore import QSharedMemory, QTranslator
from PySide6.QtWidgets import QApplication

from app.common.config import cfg
from app.common.setting import TEAM, VERSION
from app.resource import resource_rc  # noqa
from app.view.main_window import MainWindow
from libs.qfluentwidgets_pro import FluentTranslator


def is_app_running():
    """检查应用程序是否已经在运行"""
    # 使用共享内存或系统信号量来确保单例
    app_id = "Easy-FFmpeg"
    shared_memory = QSharedMemory(app_id)

    if shared_memory.attach():
        # 已经有一个实例在运行
        return True
    else:
        # 这是第一个实例
        shared_memory.create(1)
        return False


def main():
    # 检查是否已经有实例在运行
    if is_app_running():
        # 可以尝试激活已运行的实例
        print("应用程序已经在运行中")
        return 1

    # 界面缩放
    if cfg.get(cfg.dpiScale) != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

    # 创建应用程序实例
    app = QApplication(sys.argv)
    app.setApplicationName("Easy-FFmpeg")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName(TEAM)

    # 安装翻译器
    locale = cfg.get(cfg.language).value
    translator = FluentTranslator(locale)
    galleryTranslator = QTranslator()
    galleryTranslator.load(locale, "app", ".", ":/app/i18n")

    app.installTranslator(translator)
    app.installTranslator(galleryTranslator)

    # 创建并显示主窗口
    window = MainWindow()
    window.show()

    # 运行应用程序
    return app.exec()


if __name__ == "__main__":
    print(sys.platform)
    sys.exit(main())

# Easy-FFmpeg
