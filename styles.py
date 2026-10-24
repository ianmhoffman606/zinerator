"""Modern dark theme styling for Zinerator desktop application."""

DARK_THEME_QSS = """
QMainWindow {
    background-color: #16171d;
    color: #e5e7eb;
}

QWidget {
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, "Helvetica Neue", Arial, sans-serif;
    font-size: 13px;
    color: #e5e7eb;
}

/* Header & Panels */
#headerFrame {
    background-color: #1e2029;
    border-bottom: 1px solid #2d313e;
    padding: 10px 16px;
}

#titleLabel {
    font-size: 20px;
    font-weight: 700;
    color: #ffffff;
}

#subtitleLabel {
    font-size: 12px;
    color: #9ca3af;
}

QGroupBox {
    background-color: #1e2029;
    border: 1px solid #2e3342;
    border-radius: 8px;
    margin-top: 24px;
    padding-top: 18px;
    font-weight: 600;
    font-size: 13px;
    color: #f3f4f6;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    left: 14px;
    top: 4px;
    padding: 2px 8px;
    background-color: #272a36;
    border: 1px solid #3b4254;
    border-radius: 4px;
    color: #10b981;
}

/* Page Slots */
.PageSlotWidget {
    background-color: #20232d;
    border: 1px solid #323746;
    border-radius: 8px;
}

.PageSlotWidget[dragOver="true"] {
    border: 2px dashed #10b981;
    background-color: #233430;
}

.PageSlotWidget[hasImage="true"] {
    border: 1px solid #3b4356;
}

#slotHeader {
    background-color: #282c38;
    border-top-left-radius: 7px;
    border-top-right-radius: 7px;
    padding: 4px 8px;
    border-bottom: 1px solid #323746;
}

#slotName {
    font-weight: 700;
    font-size: 12px;
    color: #f9fafb;
}

#slotBadge {
    font-size: 9px;
    font-weight: 700;
    background-color: #374151;
    color: #fbbf24;
    border-radius: 3px;
    padding: 2px 4px;
}

#thumbnailArea {
    background-color: #161820;
    border-bottom-left-radius: 7px;
    border-bottom-right-radius: 7px;
}

#thumbnailArea QLabel {
    color: #6b7280;
    font-size: 11px;
}

/* Buttons */
QPushButton {
    background-color: #2d3240;
    color: #f3f4f6;
    border: 1px solid #3e4557;
    border-radius: 6px;
    padding: 7px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #383e50;
    border-color: #4f586f;
}

QPushButton:pressed {
    background-color: #232733;
}

QPushButton:disabled {
    background-color: #1e212b;
    color: #4b5563;
    border-color: #2a2e3b;
}

#generateButton {
    background-color: #10b981;
    color: #064e3b;
    border: 1px solid #059669;
    font-size: 14px;
    font-weight: 700;
    padding: 10px 18px;
    border-radius: 6px;
}

#generateButton:hover {
    background-color: #34d399;
}

#generateButton:pressed {
    background-color: #059669;
}

#clearButton {
    background-color: #374151;
    color: #ef4444;
    border: 1px solid #4b5563;
}

#clearButton:hover {
    background-color: #451a1a;
    border-color: #ef4444;
}

#slotClearBtn {
    background: transparent;
    color: #9ca3af;
    border: none;
    font-size: 14px;
    font-weight: bold;
    padding: 0 4px;
}

#slotClearBtn:hover {
    color: #ef4444;
}

/* Form Controls */
QSpinBox, QComboBox {
    background-color: #16171f;
    border: 1px solid #374151;
    border-radius: 5px;
    padding: 5px 8px;
    color: #f3f4f6;
}

QSpinBox:focus, QComboBox:focus {
    border-color: #10b981;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox QAbstractItemView {
    background-color: #1e2029;
    border: 1px solid #374151;
    selection-background-color: #10b981;
    selection-color: #064e3b;
    color: #f3f4f6;
}

/* Progress Bar */
QProgressBar {
    background-color: #161820;
    border: 1px solid #323746;
    border-radius: 5px;
    text-align: center;
    color: #f3f4f6;
    font-size: 11px;
    font-weight: bold;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #10b981;
    border-radius: 4px;
}

/* ScrollBars */
QScrollBar:vertical {
    border: none;
    background: #16171f;
    width: 10px;
    margin: 0;
}

QScrollBar::handle:vertical {
    background: #374151;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background: #4b5563;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QToolTip {
    background-color: #1e2029;
    color: #f3f4f6;
    border: 1px solid #374151;
    padding: 4px 8px;
    border-radius: 4px;
}
"""
