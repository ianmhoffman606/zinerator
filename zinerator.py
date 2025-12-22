import os
import argparse
from PIL import Image

def create_zine_layout(input_dir, side_margin, top_bottom_margin, output_dir=None, 
                       image_paths_override=None, output_format="jpg", full_back_path=None):
    """
    Arranges 8 photos into a standard 8-page zine layout on a single sheet.
    
    The script expects 8 images named: FRONT, BACK, 1, 2, 3, 4, 5, 6
    
    The layout uses portrait-oriented pages. The top row is rotated 180 degrees
    for correct orientation after folding. The final output is a high-resolution
    image with a landscape 11x8.5 aspect ratio for printing.
    
    If full_back_path is provided and output_format is PDF, a full-page back
    cover will be appended to the PDF.
    """
    # Define the correct imposition layout based on folding
    layout_grid = [
        ['2', '1', 'FRONT', 'BACK'],  # Top row (rotated 180°)
        ['3', '4', '5', '6']           # Bottom row (upright)
    ]

    # Final output dimensions (300 DPI for 11x8.5 inch print)
    FINAL_WIDTH = 3300
    FINAL_HEIGHT = 2550
    
    print("--- Zine Layout Generator ---")
    print(f"Final output resolution: {FINAL_WIDTH}x{FINAL_HEIGHT} pixels")
    print(f"Margins: {side_margin}px (sides), {top_bottom_margin}px (top/bottom)")

    # Calculate total margins
    total_horizontal_margin = side_margin * 2
    total_vertical_margin = top_bottom_margin * 2

    # Validate margins are not too large
    if total_horizontal_margin >= FINAL_WIDTH or total_vertical_margin >= FINAL_HEIGHT:
        print("Error: Margins are too large for the specified final dimensions.")
        return

    # Calculate individual page dimensions
    page_width = (FINAL_WIDTH - total_horizontal_margin) // 4
    page_height = (FINAL_HEIGHT - total_vertical_margin) // 2

    if page_width <= 0 or page_height <= 0:
        print("Error: Margins too large - page dimensions are zero or negative")
        return
    
    print(f"Page dimensions: {page_width}x{page_height} pixels")

    # Create the final canvas
    zine_sheet = Image.new('RGB', (FINAL_WIDTH, FINAL_HEIGHT), 'white')

    # Collect required page names from layout grid
    required_names = set(name for row in layout_grid for name in row)

    # Validate and store image paths
    image_paths = {}
    for base_name in required_names:
        path = image_paths_override.get(base_name)
        if not path or not os.path.isfile(path):
            print(f"Error: Image for '{base_name}' not found at provided path")
            return
        image_paths[base_name] = path
    
    print(f"All {len(required_names)} required images found")

    # Process each page in the layout grid
    for row_idx, row_of_names in enumerate(layout_grid):
        for col_idx, base_name in enumerate(row_of_names):
            try:
                with Image.open(image_paths[base_name]) as img:
                    # Convert landscape images to portrait orientation
                    if img.width > img.height:
                        img = img.rotate(90, expand=True)

                    # Resize image to exact page dimensions
                    final_page_img = img.resize((page_width, page_height), Image.Resampling.LANCZOS)

                    # Rotate top row 180 degrees for correct folding orientation
                    if row_idx == 0:
                        final_page_img = final_page_img.rotate(180)

                    # Calculate paste position
                    paste_x = side_margin + (col_idx * page_width)
                    paste_y = top_bottom_margin + (row_idx * page_height)

                    # Paste onto canvas
                    zine_sheet.paste(final_page_img, (paste_x, paste_y))
            except Exception as e:
                print(f"Error processing image '{base_name}': {e}")
                return

    # Determine output file path
    if output_dir is not None or image_paths_override is not None:
        target_dir = output_dir if output_dir is not None else (input_dir or os.getcwd())
        os.makedirs(target_dir, exist_ok=True)
        ext = ".pdf" if str(output_format).lower() == "pdf" else ".jpg"
        output_file = os.path.join(target_dir, f"zinerator_output{ext}")
    else:
        dir_name = os.path.basename(os.path.normpath(input_dir))
        ext = ".pdf" if str(output_format).lower() == "pdf" else ".jpg"
        output_file = f"{dir_name}_zine_layout_printable{ext}"
    
    # Save the final output
    try:
        # Rotate to portrait orientation for printing
        zine_sheet = zine_sheet.rotate(90, expand=True)
        fmt = str(output_format).lower()
        
        if fmt == "pdf":
            # Prepare images for PDF (300 DPI, letter size: 2550x3300)
            images_to_save = [zine_sheet.convert("RGB")]
            
            # Add full back cover as second page if provided
            if full_back_path and os.path.isfile(full_back_path):
                try:
                    full_back_img = Image.open(full_back_path)
                    
                    # Convert to portrait if landscape
                    if full_back_img.width > full_back_img.height:
                        full_back_img = full_back_img.rotate(90, expand=True)
                    
                    # Resize to letter size at 300 DPI
                    full_back_img = full_back_img.resize((2550, 3300), Image.Resampling.LANCZOS)
                    images_to_save.append(full_back_img.convert("RGB"))
                    print("Adding full back cover as second page")
                except Exception as e:
                    print(f"Warning: Could not add full back cover: {e}")
            
            # Save as multi-page or single-page PDF
            if len(images_to_save) > 1:
                images_to_save[0].save(output_file, "PDF", resolution=300.0, 
                                      save_all=True, append_images=images_to_save[1:])
            else:
                images_to_save[0].save(output_file, "PDF", resolution=300.0)
        else:
            zine_sheet.save(output_file, quality=95)
        
        print("\nSuccess!")
        print(f"Zine layout saved to: {output_file}")
    except Exception as e:
        print(f"\nError saving the final image: {e}")

def main():
    """Command-line interface for zine layout generation."""
    parser = argparse.ArgumentParser(
        description="Arrange 8 photos into a printable 8-page zine layout.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "input_dir",
        nargs='?',
        default=None)