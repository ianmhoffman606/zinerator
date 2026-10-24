"""Build script to create a standalone executable using PyInstaller."""

import os
import PyInstaller.__main__

APP_NAME = "Zinerator"
ENTRY_POINT = "main.py"


def build():
    print(f"Building {APP_NAME} standalone executable...")
    base_dir = os.path.dirname(os.path.abspath(__file__))
    entry_path = os.path.join(base_dir, ENTRY_POINT)

    PyInstaller.__main__.run([
        entry_path,
        f"--name={APP_NAME}",
        "--onefile",
        "--windowed",
        "--collect-all=PIL",
        "--collect-all=PyQt6",
        "--clean",
    ])
    print("\nBuild complete! Executable is located in the 'dist' directory.")


if __name__ == "__main__":
    build()
