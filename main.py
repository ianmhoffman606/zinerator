"""Zinerator - Desktop application entry point."""

import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QApplication

from gui import ZineratorWindow
from styles import DARK_THEME_QSS


def main():
    if hasattr(Qt.ApplicationAttribute, "AA_EnableHighDpiScaling"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    if hasattr(Qt.ApplicationAttribute, "AA_UseHighDpiPixmaps"):
        QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setStyleSheet(DARK_THEME_QSS)

    window = ZineratorWindow()
    window.show()

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
