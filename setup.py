import PyInstaller.__main__
import os

VERSION = "1.0.0"

def build():
    """Build executable using PyInstaller"""
    script_path = os.path.join(os.path.dirname(__file__), "zinerator_gui.py")
    
    PyInstaller.__main__.run([
        script_path,
        f'--name=Zinerator {VERSION}',
        '--onefile',
        '--windowed',
        '--icon=NONE',
        '--hidden-import=tkinter',
        '--hidden-import=tkinterdnd2',
        '--hidden-import=PIL',
        '--collect-all=PIL',
        '--clean',
    ])

if __name__ == "__main__":
    build()