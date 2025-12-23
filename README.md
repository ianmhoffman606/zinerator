# Zinerator

A user-friendly tool for creating and designing zines. This project provides a graphical user interface (GUI) to streamline the zine creation process, from layout design to PDF export.

## Features

-   **Graphical User Interface:** Intuitive GUI for designing zine layouts without command-line knowledge.
-   **Intituive Page Layouts:** Drag and drop JPGs/PNGs into each page.
-   **PDF Export:** Generate print-ready PDF files from your zine designs.
-   **Optional Poster:** If output is PDF, a poster can be added that can be printed on the back of the zine.

## Prerequisites

-   Python 3.7+
-   Pip (Python package installer)

## Installation

1.  Clone the repository:
    ```sh
    git clone https://github.com/ianmhoffman606/zinerator.git
    cd zinerator
    ```

2.  Install the required packages from `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```

3. Build the program using PyInstaller
    ```sh
    python setup.py
    ```

## How to Run

### GUI Application

To launch the graphical interface install and build as directed above, or:

Run the executable in Releases!

## Project Structure

```
zinerator/
├── zinerator.py        # Main CLI application
├── zinerator_gui.py    # GUI application entry point
├── setup.py            # Package setup and distribution configuration
├── requirements.txt    # Project dependencies
└── README.md           # This file
```

## Future Work

Here are some planned improvements:

-   [ ] Add more built-in zine templates.
-   [ ] Implement image editing tools within the GUI.
-   [ ] Support for custom fonts and typography options.

## Built With

-   Python - Core application language
-   Tkinter - GUI framework
-   PyInstaller - Build python to exe
