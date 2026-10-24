"""PyQt6 Graphical User Interface for Zinerator."""

import os
from pathlib import Path
import subprocess
from typing import Dict, Optional
from PIL import Image

from PyQt6.QtCore import QByteArray, QMimeData, QPoint, Qt, QThread, pyqtSignal
from PyQt6.QtGui import QAction, QDrag, QImage, QPixmap
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QFileDialog,
    QFrame,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from engine import (
    ALL_SLOTS,
    IMAGE_EXTENSIONS,
    LAYOUT_GRID,
    POSTER_SLOT,
    STANDARD_PAGES,
    FitMode,
    OutputFormat,
    assemble_sheet,
    export_zine,
    load_and_orient_image,
    resize_image,
    scan_folder_for_images,
)

SWAP_MIME_TYPE = "application/x-zinerator-slot-swap"

SLOT_TITLES = {
    "FRONT": "FRONT COVER",
    "BACK": "BACK COVER",
    "1": "PAGE 1",
    "2": "PAGE 2",
    "3": "PAGE 3",
    "4": "PAGE 4",
    "5": "PAGE 5",
    "6": "PAGE 6",
    "FULL_BACK": "POSTER (FULL BACK)"
}


class PageSlotWidget(QFrame):
    """An interactive page slot with drag-and-drop and drag-to-swap support."""

    imageChanged = pyqtSignal(str, str)   # (slot_id, file_path)
    swapRequested = pyqtSignal(str, str)  # (source_slot_id, target_slot_id)
    cleared = pyqtSignal(str)            # (slot_id)

    def __init__(self, slot_id: str, is_upside_down: bool = False, parent=None):
        super().__init__(parent)
        self.slot_id = slot_id
        self.is_upside_down = is_upside_down
        self.current_path: Optional[Path] = None
        self._drag_start_pos: Optional[QPoint] = None

        self.setObjectName("PageSlotWidget")
        self.setProperty("class", "PageSlotWidget")
        self.setProperty("dragOver", False)
        self.setProperty("hasImage", False)
        self.setAcceptDrops(True)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setMinimumSize(140, 200)

        self._init_ui()

    def _init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header Bar
        self.header_frame = QFrame(self)
        self.header_frame.setObjectName("slotHeader")
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(8, 4, 8, 4)
        header_layout.setSpacing(6)

        display_name = SLOT_TITLES.get(self.slot_id, self.slot_id)
        self.title_label = QLabel(display_name, self.header_frame)
        self.title_label.setObjectName("slotName")
        header_layout.addWidget(self.title_label)

        if self.is_upside_down:
            badge = QLabel("180°", self.header_frame)
            badge.setObjectName("slotBadge")
            badge.setToolTip("Printed rotated 180° for standard folding imposition")
            header_layout.addWidget(badge)

        header_layout.addStretch()

        self.clear_btn = QPushButton("✕", self.header_frame)
        self.clear_btn.setObjectName("slotClearBtn")
        self.clear_btn.setToolTip("Remove image from this slot")
        self.clear_btn.setVisible(False)
        self.clear_btn.clicked.connect(lambda: self.clear_image(True))
        header_layout.addWidget(self.clear_btn)

        main_layout.addWidget(self.header_frame)

        # Thumbnail Area
        self.thumb_frame = QFrame(self)
        self.thumb_frame.setObjectName("thumbnailArea")
        thumb_layout = QVBoxLayout(self.thumb_frame)
        thumb_layout.setContentsMargins(6, 6, 6, 6)

        self.image_label = QLabel(self.thumb_frame)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setText("Click or drag\nimage here")
        self.image_label.setWordWrap(True)
        self.image_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        thumb_layout.addWidget(self.image_label)

        main_layout.addWidget(self.thumb_frame, 1)

    def set_image_file(self, path: Optional[Path], emit_signal: bool = True):
        """Set image file path and update preview."""
        if path and Path(path).is_file():
            self.current_path = Path(path).resolve()
            self.setProperty("hasImage", True)
            self.clear_btn.setVisible(True)
            self.setToolTip(f"{self.current_path.name}\n({self.current_path})")
            self._update_preview()
            if emit_signal:
                self.imageChanged.emit(self.slot_id, str(self.current_path))
        else:
            self.clear_image(emit_signal=emit_signal)
        self._restyle()

    def clear_image(self, emit_signal: bool = True):
        """Clear current image."""
        self.current_path = None
        self.setProperty("hasImage", False)
        self.clear_btn.setVisible(False)
        self.image_label.setPixmap(QPixmap())
        self.image_label.setText("Click or drag\nimage here")
        self.setToolTip("")
        self._restyle()
        if emit_signal:
            self.cleared.emit(self.slot_id)

    def _update_preview(self):
        """Render a thumbnail maintaining slot proportions."""
        if not self.current_path or not self.current_path.is_file():
            return
        try:
            pil_img = load_and_orient_image(self.current_path, force_portrait=True)
            w = max(120, self.thumb_frame.width() - 12)
            h = max(160, self.thumb_frame.height() - 12)

            preview_img = resize_image(pil_img, (w, h), fit_mode=FitMode.COVER)
            data = preview_img.convert("RGBA").tobytes("raw", "RGBA")
            qim = QImage(data, preview_img.width, preview_img.height, QImage.Format.Format_RGBA8888)
            pix = QPixmap.fromImage(qim)

            self.image_label.setText("")
            self.image_label.setPixmap(pix)
        except Exception:
            self.image_label.setText(f"Error loading:\n{self.current_path.name}")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.current_path:
            self._update_preview()

    def _restyle(self):
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    # Drag and Drop handlers
    def dragEnterEvent(self, event):
        mime = event.mimeData()
        if mime.hasFormat(SWAP_MIME_TYPE):
            src_slot = str(mime.data(SWAP_MIME_TYPE), "utf-8")
            if src_slot != self.slot_id:
                self.setProperty("dragOver", True)
                self._restyle()
                event.acceptProposedAction()
                return

        if mime.hasUrls():
            for url in mime.urls():
                p = Path(url.toLocalFile())
                if p.suffix.lower() in IMAGE_EXTENSIONS or p.is_dir():
                    self.setProperty("dragOver", True)
                    self._restyle()
                    event.acceptProposedAction()
                    return

        event.ignore()

    def dragLeaveEvent(self, event):
        self.setProperty("dragOver", False)
        self._restyle()
        event.accept()

    def dropEvent(self, event):
        self.setProperty("dragOver", False)
        self._restyle()
        mime = event.mimeData()

        # Internal slot swap
        if mime.hasFormat(SWAP_MIME_TYPE):
            source_slot = str(mime.data(SWAP_MIME_TYPE), "utf-8")
            if source_slot != self.slot_id:
                event.acceptProposedAction()
                self.swapRequested.emit(source_slot, self.slot_id)
                return

        # OS file drop
        if mime.hasUrls():
            for url in mime.urls():
                local_path = Path(url.toLocalFile())
                if local_path.is_file() and local_path.suffix.lower() in IMAGE_EXTENSIONS:
                    event.acceptProposedAction()
                    self.set_image_file(local_path)
                    return

        event.ignore()

    # Drag initiation for swapping
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start_pos = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if not (event.buttons() & Qt.MouseButton.LeftButton):
            return
        if not self._drag_start_pos or not self.current_path:
            return

        dist = (event.pos() - self._drag_start_pos).manhattanLength()
        if dist < 10:
            return

        drag = QDrag(self)
        mime = QMimeData()
        mime.setData(SWAP_MIME_TYPE, QByteArray(self.slot_id.encode("utf-8")))
        drag.setMimeData(mime)

        if self.image_label.pixmap() and not self.image_label.pixmap().isNull():
            small_pix = self.image_label.pixmap().scaled(
                60, 80, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
            )
            drag.setPixmap(small_pix)
            drag.setHotSpot(QPoint(small_pix.width() // 2, small_pix.height() // 2))

        drag.exec(Qt.DropAction.MoveAction)
        self._drag_start_pos = None

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.choose_file_dialog()

    def choose_file_dialog(self):
        start_dir = str(self.current_path.parent) if self.current_path else ""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Select image for {SLOT_TITLES.get(self.slot_id, self.slot_id)}",
            start_dir,
            "Images (*.png *.jpg *.jpeg *.webp *.bmp *.tiff);;All Files (*.*)"
        )
        if file_path:
            self.set_image_file(Path(file_path))

    def contextMenuEvent(self, event):
        menu = QMenu(self)
        act_choose = QAction("Choose Image...", self)
        act_choose.triggered.connect(self.choose_file_dialog)
        menu.addAction(act_choose)

        if self.current_path:
            act_clear = QAction("Remove Image", self)
            act_clear.triggered.connect(lambda: self.clear_image(True))
            menu.addAction(act_clear)

        menu.exec(event.globalPos())


class SheetPreviewDialog(QDialog):
    """Modal dialog displaying the full composite print sheet."""

    def __init__(self, sheet_image: Image.Image, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Zinerator - Printable Sheet Preview (3300 x 2550 px)")
        self.resize(1000, 750)
        self.original_image = sheet_image
        self.zoom_factor = 1.0

        img_rgb = sheet_image.convert("RGB")
        data = img_rgb.tobytes("raw", "RGB")
        qim = QImage(data, img_rgb.width, img_rgb.height, img_rgb.width * 3, QImage.Format.Format_RGB888)
        self.original_pixmap = QPixmap.fromImage(qim)

        self._init_ui()
        self.fit_to_window()

    def _init_ui(self):
        layout = QVBoxLayout(self)

        bar = QHBoxLayout()
        btn_fit = QPushButton("Fit to Window", self)
        btn_fit.clicked.connect(self.fit_to_window)
        bar.addWidget(btn_fit)

        btn_zoom_in = QPushButton("Zoom In (+)", self)
        btn_zoom_in.clicked.connect(self.zoom_in)
        bar.addWidget(btn_zoom_in)

        btn_zoom_out = QPushButton("Zoom Out (-)", self)
        btn_zoom_out.clicked.connect(self.zoom_out)
        bar.addWidget(btn_zoom_out)

        btn_100 = QPushButton("100% (1:1)", self)
        btn_100.clicked.connect(self.zoom_100)
        bar.addWidget(btn_100)

        bar.addStretch()

        btn_copy = QPushButton("Copy to Clipboard", self)
        btn_copy.clicked.connect(self.copy_to_clipboard)
        bar.addWidget(btn_copy)

        btn_close = QPushButton("Close", self)
        btn_close.clicked.connect(self.accept)
        bar.addWidget(btn_close)

        layout.addLayout(bar)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.canvas_label = QLabel(self.scroll_area)
        self.canvas_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.scroll_area.setWidget(self.canvas_label)
        layout.addWidget(self.scroll_area)

    def fit_to_window(self):
        avail_w = self.scroll_area.viewport().width() - 20
        avail_h = self.scroll_area.viewport().height() - 20
        if avail_w <= 0 or avail_h <= 0:
            avail_w, avail_h = 960, 640

        scale = min(avail_w / self.original_pixmap.width(), avail_h / self.original_pixmap.height())
        self.zoom_factor = scale
        self._update_display()

    def zoom_in(self):
        self.zoom_factor = min(2.0, self.zoom_factor * 1.25)
        self._update_display()

    def zoom_out(self):
        self.zoom_factor = max(0.1, self.zoom_factor / 1.25)
        self._update_display()

    def zoom_100(self):
        self.zoom_factor = 1.0
        self._update_display()

    def _update_display(self):
        target_w = int(self.original_pixmap.width() * self.zoom_factor)
        target_h = int(self.original_pixmap.height() * self.zoom_factor)
        scaled_pix = self.original_pixmap.scaled(
            target_w, target_h, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
        )
        self.canvas_label.setPixmap(scaled_pix)
        self.canvas_label.adjustSize()

    def copy_to_clipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(self.original_pixmap)


class GenerationWorker(QThread):
    """Background worker thread for generating and exporting zines without blocking."""
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, slot_paths, output_path, side_margin, tb_margin, fit_mode, output_format, full_back_path):
        super().__init__()
        self.slot_paths = slot_paths
        self.output_path = output_path
        self.side_margin = side_margin
        self.tb_margin = tb_margin
        self.fit_mode = fit_mode
        self.output_format = output_format
        self.full_back_path = full_back_path

    def run(self):
        try:
            sheet = assemble_sheet(
                self.slot_paths,
                side_margin=self.side_margin,
                top_bottom_margin=self.tb_margin,
                fit_mode=self.fit_mode,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            saved_file = export_zine(
                sheet_img=sheet,
                output_path=self.output_path,
                output_format=self.output_format,
                full_back_path=self.full_back_path,
                fit_mode=self.fit_mode,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            self.finished.emit(str(saved_file))
        except Exception as e:
            self.error.emit(str(e))


class PreviewWorker(QThread):
    """Background worker thread for rendering preview sheet."""
    progress = pyqtSignal(int, str)
    rendered = pyqtSignal(object)
    error = pyqtSignal(str)

    def __init__(self, slot_paths, side_margin, tb_margin, fit_mode):
        super().__init__()
        self.slot_paths = slot_paths
        self.side_margin = side_margin
        self.tb_margin = tb_margin
        self.fit_mode = fit_mode

    def run(self):
        try:
            sheet = assemble_sheet(
                self.slot_paths,
                side_margin=self.side_margin,
                top_bottom_margin=self.tb_margin,
                fit_mode=self.fit_mode,
                progress_callback=lambda p, m: self.progress.emit(p, m)
            )
            self.rendered.emit(sheet)
        except Exception as e:
            self.error.emit(str(e))


class ZineratorWindow(QMainWindow):
    """Main Application Window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Zinerator - Assemble Your Zine!")
        self.resize(1260, 820)
        self.setMinimumSize(1020, 720)
        self.setAcceptDrops(True)

        self.slots: Dict[str, Optional[Path]] = {s: None for s in ALL_SLOTS}
        self.slot_widgets: Dict[str, PageSlotWidget] = {}
        self.worker: Optional[QThread] = None

        self._init_ui()
        self._update_status()

    def _init_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Header Bar
        header = QFrame(self)
        header.setObjectName("headerFrame")
        h_layout = QHBoxLayout(header)
        h_layout.setContentsMargins(18, 12, 18, 12)

        title_box = QVBoxLayout()
        title_lbl = QLabel("Zinerator", header)
        title_lbl.setObjectName("titleLabel")
        sub_lbl = QLabel("Drag & drop photos to design your printable 8-page mini-zine", header)
        sub_lbl.setObjectName("subtitleLabel")
        title_box.addWidget(title_lbl)
        title_box.addWidget(sub_lbl)
        h_layout.addLayout(title_box)

        h_layout.addStretch()

        btn_folder = QPushButton("📁 Load Folder...", header)
        btn_folder.setToolTip("Scan a directory and auto-populate matching zine images")
        btn_folder.clicked.connect(self.choose_folder)
        h_layout.addWidget(btn_folder)

        btn_clear = QPushButton("Clear All", header)
        btn_clear.setObjectName("clearButton")
        btn_clear.clicked.connect(self.confirm_clear_all)
        h_layout.addWidget(btn_clear)

        root_layout.addWidget(header)

        # Main Workspace
        workspace = QWidget(self)
        work_layout = QHBoxLayout(workspace)
        work_layout.setContentsMargins(14, 14, 14, 14)
        work_layout.setSpacing(14)

        # Left: Imposition Grid
        grid_container = QWidget(workspace)
        grid_vbox = QVBoxLayout(grid_container)
        grid_vbox.setContentsMargins(0, 0, 0, 0)
        grid_vbox.setSpacing(8)

        grid_hint = QLabel("💡 Imposition Layout: Top row folds upside down. Drag between slots to swap pages.", grid_container)
        grid_hint.setStyleSheet("color: #9ca3af; font-size: 11px; font-style: italic;")
        grid_vbox.addWidget(grid_hint)

        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(10)

        # Top row (upside down in imposition)
        for col_idx, page_name in enumerate(LAYOUT_GRID[0]):
            w = PageSlotWidget(page_name, is_upside_down=True, parent=grid_container)
            self._connect_slot(w)
            self.slot_widgets[page_name] = w
            self.grid_layout.addWidget(w, 0, col_idx)

        # Bottom row (upright in imposition)
        for col_idx, page_name in enumerate(LAYOUT_GRID[1]):
            w = PageSlotWidget(page_name, is_upside_down=False, parent=grid_container)
            self._connect_slot(w)
            self.slot_widgets[page_name] = w
            self.grid_layout.addWidget(w, 1, col_idx)

        grid_vbox.addLayout(self.grid_layout)
        work_layout.addWidget(grid_container, 3)

        # Right: Sidebar Panel
        sidebar = QFrame(workspace)
        sidebar.setFixedWidth(310)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(12)

        # Poster Slot Card
        poster_group = QGroupBox("Full Back Cover Poster (Optional)", sidebar)
        poster_layout = QVBoxLayout(poster_group)
        poster_layout.setContentsMargins(10, 10, 10, 10)
        poster_layout.setSpacing(6)

        poster_note = QLabel("Appended to reverse side of PDF (8.5x11\")", poster_group)
        poster_note.setStyleSheet("color: #9ca3af; font-size: 11px;")
        poster_layout.addWidget(poster_note)

        self.poster_widget = PageSlotWidget(POSTER_SLOT, is_upside_down=False, parent=poster_group)
        self.poster_widget.setFixedHeight(180)
        self._connect_slot(self.poster_widget)
        self.slot_widgets[POSTER_SLOT] = self.poster_widget
        poster_layout.addWidget(self.poster_widget)
        sidebar_layout.addWidget(poster_group)

        # Settings Card
        settings_group = QGroupBox("Output Settings", sidebar)
        set_layout = QVBoxLayout(settings_group)
        set_layout.setContentsMargins(10, 12, 10, 12)
        set_layout.setSpacing(10)

        # Margins
        margin_h = QHBoxLayout()
        side_lbl = QLabel("Side Margins:", settings_group)
        self.side_margin_spin = QSpinBox(settings_group)
        self.side_margin_spin.setRange(0, 500)
        self.side_margin_spin.setValue(60)
        self.side_margin_spin.setSuffix(" px")
        margin_h.addWidget(side_lbl)
        margin_h.addWidget(self.side_margin_spin)
        set_layout.addLayout(margin_h)

        tb_h = QHBoxLayout()
        tb_lbl = QLabel("Top/Bottom Margins:", settings_group)
        self.tb_margin_spin = QSpinBox(settings_group)
        self.tb_margin_spin.setRange(0, 500)
        self.tb_margin_spin.setValue(60)
        self.tb_margin_spin.setSuffix(" px")
        tb_h.addWidget(tb_lbl)
        tb_h.addWidget(self.tb_margin_spin)
        set_layout.addLayout(tb_h)

        # Fit Mode
        fit_h = QHBoxLayout()
        fit_lbl = QLabel("Image Fitting:", settings_group)
        self.fit_mode_combo = QComboBox(settings_group)
        self.fit_mode_combo.addItem("Stretch / Fill (Default)", FitMode.STRETCH)
        self.fit_mode_combo.addItem("Fit (Letterbox)", FitMode.FIT)
        self.fit_mode_combo.addItem("Cover (Crop to fill)", FitMode.COVER)
        fit_h.addWidget(fit_lbl)
        fit_h.addWidget(self.fit_mode_combo)
        set_layout.addLayout(fit_h)

        # Format
        fmt_h = QHBoxLayout()
        fmt_lbl = QLabel("File Format:", settings_group)
        self.format_combo = QComboBox(settings_group)
        self.format_combo.addItem("PDF Document (.pdf)", OutputFormat.PDF)
        self.format_combo.addItem("JPEG Image (.jpg)", OutputFormat.JPG)
        fmt_h.addWidget(fmt_lbl)
        fmt_h.addWidget(self.format_combo)
        set_layout.addLayout(fmt_h)

        sidebar_layout.addWidget(settings_group)

        # Actions Card
        action_group = QGroupBox("Generate & Export", sidebar)
        act_layout = QVBoxLayout(action_group)
        act_layout.setContentsMargins(10, 12, 10, 12)
        act_layout.setSpacing(10)

        self.status_label = QLabel("Status: Ready", action_group)
        self.status_label.setWordWrap(True)
        act_layout.addWidget(self.status_label)

        self.progress_bar = QProgressBar(action_group)
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(False)
        act_layout.addWidget(self.progress_bar)

        self.btn_preview = QPushButton("🔍 Preview Sheet", action_group)
        self.btn_preview.clicked.connect(self.preview_sheet)
        act_layout.addWidget(self.btn_preview)

        self.btn_generate = QPushButton("✨ Generate Zine", action_group)
        self.btn_generate.setObjectName("generateButton")
        self.btn_generate.clicked.connect(self.generate_zine)
        act_layout.addWidget(self.btn_generate)

        sidebar_layout.addWidget(action_group)
        sidebar_layout.addStretch()

        work_layout.addWidget(sidebar, 1)
        root_layout.addWidget(workspace, 1)

    def _connect_slot(self, widget: PageSlotWidget):
        widget.imageChanged.connect(self.on_slot_image_changed)
        widget.swapRequested.connect(self.on_slot_swap_requested)
        widget.cleared.connect(self.on_slot_cleared)

    def on_slot_image_changed(self, slot_id: str, path_str: str):
        self.slots[slot_id] = Path(path_str)
        self._update_status()

    def on_slot_cleared(self, slot_id: str):
        self.slots[slot_id] = None
        self._update_status()

    def on_slot_swap_requested(self, slot_a: str, slot_b: str):
        path_a = self.slots.get(slot_a)
        path_b = self.slots.get(slot_b)
        self.slots[slot_a], self.slots[slot_b] = path_b, path_a

        if slot_a in self.slot_widgets:
            self.slot_widgets[slot_a].set_image_file(path_b, emit_signal=False)
        if slot_b in self.slot_widgets:
            self.slot_widgets[slot_b].set_image_file(path_a, emit_signal=False)

        self._update_status()

    def _update_status(self):
        loaded = sum(1 for s in STANDARD_PAGES if self.slots.get(s) is not None)
        has_poster = self.slots.get(POSTER_SLOT) is not None
        poster_txt = " + Poster" if has_poster else ""
        self.status_label.setText(f"Status: {loaded}/8 pages loaded{poster_txt}")
        self.btn_generate.setEnabled(loaded == 8)
        self.btn_preview.setEnabled(loaded == 8)

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Choose folder containing zine photos")
        if folder:
            self.load_from_directory(Path(folder))

    def load_from_directory(self, directory: Path):
        assigned, _ = scan_folder_for_images(directory)
        count = 0
        for slot, path in assigned.items():
            if path and slot in self.slot_widgets:
                self.slot_widgets[slot].set_image_file(path)
                count += 1

        self._update_status()
        if count == 0:
            QMessageBox.information(
                self,
                "No Matching Images",
                f"No standard zine images found in:\n{directory}\n\n"
                "Tip: Name files FRONT, BACK, 1, 2, 3, 4, 5, 6 or drop 8 photos in sequence."
            )

    def confirm_clear_all(self):
        self.clear_all(confirm=True)

    def clear_all(self, confirm: bool = False):
        loaded_count = sum(1 for p in ALL_SLOTS if self.slots.get(p) is not None)
        if confirm and loaded_count > 0:
            reply = QMessageBox.question(
                self,
                "Clear All Images",
                "Are you sure you want to clear all loaded images?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        for w in self.slot_widgets.values():
            w.clear_image(emit_signal=False)
        for s in ALL_SLOTS:
            self.slots[s] = None
        self._update_status()

    # Window-level drag and drop
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def dropEvent(self, event):
        mime = event.mimeData()
        if not mime.hasUrls():
            event.ignore()
            return

        urls = [Path(u.toLocalFile()) for u in mime.urls()]
        event.acceptProposedAction()

        if len(urls) == 1 and urls[0].is_dir():
            self.load_from_directory(urls[0])
            return

        image_files = [p for p in urls if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS]
        if image_files:
            empty_slots = [s for s in STANDARD_PAGES if self.slots.get(s) is None]
            for slot, img in zip(empty_slots, image_files):
                self.slot_widgets[slot].set_image_file(img)

    def preview_sheet(self):
        missing = [p for p in STANDARD_PAGES if self.slots.get(p) is None]
        if missing:
            QMessageBox.warning(self, "Missing Pages", f"Please add images for: {', '.join(sorted(missing))}")
            return

        self.btn_preview.setEnabled(False)
        self.btn_generate.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(10)
        self.status_label.setText("Status: Rendering preview...")

        slot_paths = {p: self.slots[p] for p in STANDARD_PAGES}
        self.worker = PreviewWorker(
            slot_paths,
            side_margin=self.side_margin_spin.value(),
            tb_margin=self.tb_margin_spin.value(),
            fit_mode=self.fit_mode_combo.currentData()
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.rendered.connect(self._on_preview_rendered)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_preview_rendered(self, sheet_image: Image.Image):
        self.btn_preview.setEnabled(True)
        self.btn_generate.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._update_status()

        dialog = SheetPreviewDialog(sheet_image, self)
        dialog.exec()

    def generate_zine(self):
        missing = [p for p in STANDARD_PAGES if self.slots.get(p) is None]
        if missing:
            QMessageBox.warning(self, "Missing Pages", f"Please add images for: {', '.join(sorted(missing))}")
            return

        fmt = self.format_combo.currentData()
        is_pdf = fmt == OutputFormat.PDF
        ext_filter = "PDF Document (*.pdf)" if is_pdf else "JPEG Image (*.jpg)"
        default_name = "zinerator_output.pdf" if is_pdf else "zinerator_output.jpg"

        save_path, _ = QFileDialog.getSaveFileName(
            self, "Save Zine Layout As...", default_name, f"{ext_filter};;All Files (*.*)"
        )
        if not save_path:
            return

        self.btn_preview.setEnabled(False)
        self.btn_generate.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(5)
        self.status_label.setText("Status: Starting generation...")

        slot_paths = {p: self.slots[p] for p in STANDARD_PAGES}
        poster_path = self.slots.get(POSTER_SLOT)

        self.worker = GenerationWorker(
            slot_paths=slot_paths,
            output_path=Path(save_path),
            side_margin=self.side_margin_spin.value(),
            tb_margin=self.tb_margin_spin.value(),
            fit_mode=self.fit_mode_combo.currentData(),
            output_format=fmt,
            full_back_path=poster_path
        )
        self.worker.progress.connect(self._on_progress)
        self.worker.finished.connect(self._on_generation_finished)
        self.worker.error.connect(self._on_error)
        self.worker.start()

    def _on_progress(self, percent: int, msg: str):
        self.progress_bar.setValue(percent)
        self.status_label.setText(f"Status: {msg}")

    def _on_generation_finished(self, saved_file_str: str):
        self.btn_preview.setEnabled(True)
        self.btn_generate.setEnabled(True)
        self.progress_bar.setVisible(False)
        self._update_status()

        saved_path = Path(saved_file_str)
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Zine Generated Successfully!")
        msg_box.setText(f"Your printable zine layout has been generated!\n\nSaved to:\n{saved_path}")
        msg_box.setIcon(QMessageBox.Icon.Information)

        btn_open_file = msg_box.addButton("Open File", QMessageBox.ButtonRole.ActionRole)
        btn_open_dir = msg_box.addButton("Open Folder", QMessageBox.ButtonRole.ActionRole)
        msg_box.addButton("Close", QMessageBox.ButtonRole.AcceptRole)

        msg_box.exec()

        if msg_box.clickedButton() == btn_open_file:
            try:
                os.startfile(str(saved_path))
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open file: {e}")
        elif msg_box.clickedButton() == btn_open_dir:
            try:
                subprocess.run(["explorer", "/select,", str(saved_path)])
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Could not open directory: {e}")

    def _on_error(self, err_msg: str):
        self.btn_preview.setEnabled(True)
        self.btn_generate.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.status_label.setText("Status: Error during generation")
        QMessageBox.critical(self, "Generation Failed", f"An error occurred while generating the zine:\n\n{err_msg}")
