import os
import argparse
from PIL import Image

def find_image_path(directory, base_name):
    """
    Finds an image file with a given base name, checking for common extensions.

    Args:
        directory (str): The directory to search in.
        base_name (str): The base filename (e.g., 'FRONT', '1').

    Returns:
        str: The full path to the image file, or None if not found.
    """
    for ext in ['.png', '.jpeg', '.jpg']:
        path = os.path.join(directory, f"{base_name}{ext}")
        if os.path.exists(path):
            return path
    return None

def create_zine_layout(input_dir, side_margin, top_bottom_margin):
    """
    Arranges 8 photos into a standard 8-page zine layout on a single sheet.

    The script expects 8 images named:
    FRONT, BACK, 1, 2, 3, 4, 5, 6 (with .png or .jpeg extensions)

    The layout uses portrait-oriented pages. The top row is rotated 180
    degrees for correct orientation after folding. The final output is a
    high-resolution image with a landscape 11x8.5 aspect ratio for printing.

    """
    # Use the correct imposition layout based on folding
    layout_grid = [
        ['2', '1', 'FRONT', 'BACK'],  # Top row (will be rotated)
        ['3', '4', '5', '6']          # Bottom row (upright)
    ]

    FINAL_WIDTH = 3300
    FINAL_HEIGHT = 2550
    
    print("--- Zine Layout Generator ---")
    print(f"Final output resolution will be {FINAL_WIDTH}x{FINAL_HEIGHT} pixels.")
    print(f"Applying side margins of {side_margin}px and top/bottom margins of {top_bottom_margin}px.")

    total_horizontal_margin = side_margin * 2
    total_vertical_margin = top_bottom_margin * 2

    # Error checking for margins that are too large
    if total_horizontal_margin >= FINAL_WIDTH or total_vertical_margin >= FINAL_HEIGHT:
        print("Error: Margins are too large for the specified final dimensions.")
        return

    page_width = (FINAL_WIDTH - total_horizontal_margin) // 4
    page_height = (FINAL_HEIGHT - total_vertical_margin) // 2

    if page_width <= 0 or page_height <= 0:
        print("Error: After applying margins, the page dimensions are zero or negative.")
        return
    
    print(f"Each page slot will be {page_width}x{page_height} pixels.")

    # Create the final canvas for the zine layout
    zine_sheet = Image.new('RGB', (FINAL_WIDTH, FINAL_HEIGHT), 'white')

    print(f"Searching for images in: {input_dir}")
    image_paths = {}
    required_names = set(name for row in layout_grid for name in row)
    for base_name in required_names:
        path = find_image_path(input_dir, base_name)
        if path is None:
            print(f"Error: Image for '{base_name}.png/jpeg' not found.")
            return
        image_paths[base_name] = path
    
    print(f"All {len(required_names)} required images found.")

    for row_idx, row_of_names in enumerate(layout_grid):
        for col_idx, base_name in enumerate(row_of_names):
            try:
                with Image.open(image_paths[base_name]) as img:
                    # If image is landscape, rotate it to portrait
                    if img.width > img.height:
                        img = img.rotate(90, expand=True)

                    # Stretch the image to the exact page dimensions, ignoring aspect ratio.
                    final_page_img = img.resize((page_width, page_height), Image.Resampling.LANCZOS)

                    # Rotate the pages in the top row (row_idx == 0) 180 degrees
                    if row_idx == 0:
                        final_page_img = final_page_img.rotate(180)

                    paste_x = side_margin + (col_idx * page_width)
                    paste_y = top_bottom_margin + (row_idx * page_height)

                    zine_sheet.paste(final_page_img, (paste_x, paste_y))
            except Exception as e:
                print(f"Error processing image '{base_name}': {e}")
                return

    dir_name = os.path.basename(os.path.normpath(input_dir))
    output_file = f"{dir_name}_zine_layout_printable.jpg"
    
    try:
        zine_sheet = zine_sheet.rotate(90, expand=True)
        zine_sheet.save(output_file, quality=95)
        print("\nSuccess!")
        print(f"Zine layout saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving the final image: {e}")

def main():
    parser = argparse.ArgumentParser(
        description="Arrange 8 photos into a printable 8-page zine layout.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_dir",
        nargs='?',
        default=None,
        help="The directory containing your 8 named images. Defaults to script directory if not provided."
    )

    parser.add_argument(
        "--side-margin",
        type=int,
        default=60,
        help="Margin in pixels for the left and right sides. Default: 0"
    )

    parser.add_argument(
        "--top-bottom-margin",
        type=int,
        default=60,
        help="Margin in pixels for the top and bottom. Default: 0"
    )
    args = parser.parse_args()

    # If no input directory is provided, use the script's directory
    if args.input_dir is None:
        args.input_dir = os.path.dirname(os.path.abspath(__file__))
        print(f"No input directory specified. Using script directory: {args.input_dir}")

    create_zine_layout(args.input_dir, args.side_margin, args.top_bottom_margin)

if __name__ == "__main__":
    main()