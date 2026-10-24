# Zinerator

A user-friendly tool for creating and designing zines. This project provides a graphical user interface (GUI) to streamline the zine creation process, from layout design to PDF export.

## Features

- **Intuitive GUI:** Visual 8-page imposition grid showing exact folding orientation (with top row rotated 180° for standard single-sheet folding).
- **Drag-and-Drop & Slot Swapping:** Drag image files directly onto page slots, or drag between slots to swap page positions effortlessly.
- **Multiple Image Fit Modes:** Choose between Fit (letterbox), Cover (crop to fill), or Stretch.
- **Print-Ready PDF & JPG Export:** Generates high-resolution 300 DPI 11" x 8.5" imposition sheets ready for standard paper printing.
- **Optional Full-Back Poster:** Append a full-page poster to the reverse side of the PDF layout.
- **Standalone Executable:** Fully self-contained single-file executable built with PyInstaller for distribution without requiring a Python environment.

## Prerequisites

- Python 3.8+
- Pip

## Getting Started

1. **Clone the repository:**
   ```sh
   git clone https://github.com/ianmhoffman606/zinerator.git
   cd zinerator
   ```

2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```sh
   python main.py
   ```

## Building the Standalone Executable

To compile a single, standalone `.exe` (or platform binary) using PyInstaller:

```sh
python build.py
```

The compiled binary will be placed in the `dist/` directory (e.g., `dist/Zinerator.exe`).

## Running Tests

To run the automated test suite:

```sh
pytest
```

## Project Structure

```
zinerator/
├── main.py             # Desktop application entry point & crash handling
├── gui.py              # PyQt6 user interface, drag-and-drop, and worker threads
├── engine.py           # Core imposition layout math and image processing (Pillow)
├── styles.py           # Modern dark-theme QSS stylesheet
├── build.py            # Standalone PyInstaller build script
├── requirements.txt    # Project dependencies (runtime, build, and test)
├── pyproject.toml      # Tool configurations (pytest)
├── tests/              # Automated unit and GUI test suite
└── images/             # Sample images for testing and demonstration
```

## Built With

- [PyQt6](https://www.riverbankcomputing.com/software/pyqt/) - GUI framework
- [Pillow](https://python-pillow.org/) - Image processing and PDF composition
- [PyInstaller](https://pyinstaller.org/) - Standalone executable compiler
