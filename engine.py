"""Core zine layout, image processing, and export engine."""

from enum import Enum
from pathlib import Path
import re
from typing import Callable, Dict, List, Optional, Tuple, Union
from PIL import Image, ImageOps

# Standard 8-page imposition layout
# Top row is rotated 180° so pages are right-side up after horizontal fold
LAYOUT_GRID = [
    ["2", "1", "FRONT", "BACK"],  # Top row (rotated 180°)
    ["3", "4", "5", "6"]           # Bottom row (upright)
]

STANDARD_PAGES = ["FRONT", "BACK", "1", "2", "3", "4", "5", "6"]
POSTER_SLOT = "FULL_BACK"
ALL_SLOTS = STANDARD_PAGES + [POSTER_SLOT]

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

# Standard sheet dimensions: 11" x 8.5" at 300 DPI
SHEET_WIDTH = 3300
SHEET_HEIGHT = 2550


class FitMode(str, Enum):
    """How images should scale inside page slots."""
    FIT = "fit"          # Preserve aspect ratio, letterbox with clean background
    COVER = "cover"      # Preserve aspect ratio, center-crop to fill slot completely
    STRETCH = "stretch"  # Distort to exact slot dimensions (legacy v1.0)

    @classmethod
    def from_value(cls, val: object) -> "FitMode":
        if isinstance(val, cls):
            return val
        s = str(val).lower().strip()
        for member in cls:
            if member.value in s:
                return member
        return cls.STRETCH


class OutputFormat(str, Enum):
    """Output document format."""
    PDF = "pdf"
    JPG = "jpg"

    @classmethod
    def from_value(cls, val: object) -> "OutputFormat":
        if isinstance(val, cls):
            return val
        s = str(val).lower().strip()
        if "jpg" in s or "jpeg" in s:
            return cls.JPG
        return cls.PDF


def load_and_orient_image(
    source: Union[str, Path, Image.Image],
    force_portrait: bool = True,
    bg_color: Tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """Load an image, correct EXIF orientation, convert to RGB, and ensure portrait."""
    if isinstance(source, Image.Image):
        img = source.copy()
    else:
        img = Image.open(source)

    # Correct EXIF rotation if present
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # Clean RGB conversion
    if img.mode == "RGBA":
        bg = Image.new("RGB", img.size, bg_color)
        bg.paste(img, mask=img.split()[3])
        img = bg
    elif img.mode != "RGB":
        img = img.convert("RGB")

    # Rotate landscape to portrait
    if force_portrait and img.width > img.height:
        img = img.rotate(90, expand=True)

    return img


def resize_image(
    img: Image.Image,
    target_size: Tuple[int, int],
    fit_mode: FitMode = FitMode.FIT,
    bg_color: Tuple[int, int, int] = (255, 255, 255)
) -> Image.Image:
    """Resize image to target_size (width, height) using the specified FitMode."""
    target_w, target_h = target_size
    mode = FitMode.from_value(fit_mode)

    if mode == FitMode.STRETCH:
        return img.resize((target_w, target_h), Image.Resampling.LANCZOS)

    src_w, src_h = img.width, img.height
    if src_w == 0 or src_h == 0:
        raise ValueError("Source image has zero dimension")

    if mode == FitMode.FIT:
        scale = min(target_w / src_w, target_h / src_h)
        new_w = max(1, int(round(src_w * scale)))
        new_h = max(1, int(round(src_h * scale)))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        canvas = Image.new("RGB", (target_w, target_h), bg_color)
        paste_x = (target_w - new_w) // 2
        paste_y = (target_h - new_h) // 2
        canvas.paste(resized, (paste_x, paste_y))
        return canvas

    elif mode == FitMode.COVER:
        scale = max(target_w / src_w, target_h / src_h)
        new_w = max(target_w, int(round(src_w * scale)))
        new_h = max(target_h, int(round(src_h * scale)))
        resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        crop_x = (new_w - target_w) // 2
        crop_y = (new_h - target_h) // 2
        return resized.crop((crop_x, crop_y, crop_x + target_w, crop_y + target_h))

    return img.resize((target_w, target_h), Image.Resampling.LANCZOS)


def scan_folder_for_images(folder: Path) -> Tuple[Dict[str, Optional[Path]], List[Path]]:
    """Scan a folder and map images to the standard zine slots + poster."""
    if not folder.is_dir():
        return ({s: None for s in ALL_SLOTS}, [])

    def natural_key(p: Path):
        return [int(c) if c.isdigit() else c.lower() for c in re.split(r"(\d+)", p.name)]

    all_images = [f for f in folder.iterdir() if f.is_file() and f.suffix.lower() in IMAGE_EXTENSIONS]
    all_images.sort(key=natural_key)

    assigned: Dict[str, Optional[Path]] = {s: None for s in ALL_SLOTS}
    used = set()

    aliases = {
        "FRONT": ["front", "cover", "front_cover", "cover_front"],
        "BACK": ["back", "rear", "back_cover", "cover_back"],
        "FULL_BACK": ["poster", "full_back", "fullback", "back_poster"],
        "1": ["1", "p1", "page1", "page_1"],
        "2": ["2", "p2", "page2", "page_2"],
        "3": ["3", "p3", "page3", "page_3"],
        "4": ["4", "p4", "page4", "page_4"],
        "5": ["5", "p5", "page5", "page_5"],
        "6": ["6", "p6", "page6", "page_6"],
    }

    # Match aliases
    for slot, words in aliases.items():
        for path in all_images:
            if path in used:
                continue
            stem = path.stem.lower()
            tokens = re.split(r"[-_\s]+", stem)
            if stem in words or any(w in tokens for w in words):
                assigned[slot] = path
                used.add(path)
                break

    # Sequential fallback if 8 files found and slots are empty
    remaining = [img for img in all_images if img not in used]
    empty_slots = [s for s in STANDARD_PAGES if assigned[s] is None]

    if len(remaining) == 8 and len(empty_slots) == 8:
        assigned["FRONT"] = remaining[0]
        assigned["1"] = remaining[1]
        assigned["2"] = remaining[2]
        assigned["3"] = remaining[3]
        assigned["4"] = remaining[4]
        assigned["5"] = remaining[5]
        assigned["6"] = remaining[6]
        assigned["BACK"] = remaining[7]
        used.update(remaining)
    elif len(remaining) == len(empty_slots) and len(remaining) > 0:
        for slot, img in zip(empty_slots, remaining):
            assigned[slot] = img
            used.add(img)

    unassigned = [img for img in all_images if img not in used]
    return assigned, unassigned


def assemble_sheet(
    slot_paths: Dict[str, Union[str, Path]],
    side_margin: int = 60,
    top_bottom_margin: int = 60,
    fit_mode: FitMode = FitMode.STRETCH,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Image.Image:
    """Assemble 8 photos into the printable 3300x2550 imposition layout sheet."""
    # Check margins
    total_h_margin = side_margin * 2
    total_v_margin = top_bottom_margin * 2
    if total_h_margin >= SHEET_WIDTH or total_v_margin >= SHEET_HEIGHT:
        raise ValueError("Margins are too large for the 3300x2550 sheet dimensions.")

    page_w = (SHEET_WIDTH - total_h_margin) // 4
    page_h = (SHEET_HEIGHT - total_v_margin) // 2
    if page_w <= 0 or page_h <= 0:
        raise ValueError("Margins leave zero or negative page dimensions.")

    # Validate 8 required slots
    missing = [p for p in STANDARD_PAGES if not slot_paths.get(p) or not Path(slot_paths[p]).is_file()]
    if missing:
        raise FileNotFoundError(f"Missing required images: {', '.join(sorted(missing))}")

    if progress_callback:
        progress_callback(5, "Creating canvas...")

    canvas = Image.new("RGB", (SHEET_WIDTH, SHEET_HEIGHT), (255, 255, 255))
    total_pages = 8
    processed = 0

    for row_idx, row_names in enumerate(LAYOUT_GRID):
        for col_idx, page_name in enumerate(row_names):
            processed += 1
            if progress_callback:
                pct = int(5 + (processed / total_pages) * 85)
                progress_callback(pct, f"Processing page {processed}/{total_pages} ({page_name})...")

            path = slot_paths[page_name]
            img = load_and_orient_image(path, force_portrait=True)
            page_img = resize_image(img, (page_w, page_h), fit_mode=fit_mode)

            # Top row is upside-down for folding
            if row_idx == 0:
                page_img = page_img.rotate(180)

            paste_x = side_margin + (col_idx * page_w)
            paste_y = top_bottom_margin + (row_idx * page_h)
            canvas.paste(page_img, (paste_x, paste_y))

    if progress_callback:
        progress_callback(95, "Finalizing sheet layout...")

    return canvas


def export_zine(
    sheet_img: Image.Image,
    output_path: Union[str, Path],
    output_format: OutputFormat = OutputFormat.PDF,
    full_back_path: Optional[Union[str, Path]] = None,
    fit_mode: FitMode = FitMode.STRETCH,
    progress_callback: Optional[Callable[[int, str], None]] = None
) -> Path:
    """Save the assembled zine layout to a print-ready PDF or JPG."""
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if progress_callback:
        progress_callback(96, "Orienting canvas for print...")

    # Standard print orientation is portrait (2550 x 3300)
    final_sheet = sheet_img.rotate(90, expand=True)
    fmt = OutputFormat.from_value(output_format)

    if fmt == OutputFormat.PDF:
        if progress_callback:
            progress_callback(97, "Preparing PDF...")

        images_to_save = [final_sheet.convert("RGB")]

        # Add optional full-page back cover poster
        if full_back_path and Path(full_back_path).is_file():
            try:
                if progress_callback:
                    progress_callback(98, "Adding full back cover poster...")
                poster_img = load_and_orient_image(full_back_path, force_portrait=True)
                poster_resized = resize_image(poster_img, (final_sheet.width, final_sheet.height), fit_mode=fit_mode)
                images_to_save.append(poster_resized.convert("RGB"))
            except Exception as e:
                print(f"Warning: Could not add poster: {e}")

        if progress_callback:
            progress_callback(99, "Writing PDF file...")

        if len(images_to_save) > 1:
            images_to_save[0].save(output_path, "PDF", resolution=300.0, save_all=True, append_images=images_to_save[1:])
        else:
            images_to_save[0].save(output_path, "PDF", resolution=300.0)

    else:  # JPG
        if progress_callback:
            progress_callback(98, "Writing JPEG file...")
        final_sheet.convert("RGB").save(output_path, "JPEG", quality=95, dpi=(300, 300))

        if full_back_path and Path(full_back_path).is_file():
            try:
                poster_out = output_path.with_name(f"{output_path.stem}_poster.jpg")
                poster_img = load_and_orient_image(full_back_path, force_portrait=True)
                poster_resized = resize_image(poster_img, (final_sheet.width, final_sheet.height), fit_mode=fit_mode)
                poster_resized.convert("RGB").save(poster_out, "JPEG", quality=95, dpi=(300, 300))
            except Exception as e:
                print(f"Warning: Could not save poster JPG: {e}")

    if progress_callback:
        progress_callback(100, "Done!")

    return output_path

