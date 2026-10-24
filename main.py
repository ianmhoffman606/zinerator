"""Zinerator - Desktop application entry point."""

from pathlib import Path
import sys
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QApplication

from gui import ZineratorWindow
from styles import DARK_THEME_QSS


def main():
    if sys.platform == "win32":
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("zinerator.app")
        except Exception:
            pass

    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_QSS)

    icon_path = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "favicon.ico"
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))

    window = ZineratorWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
