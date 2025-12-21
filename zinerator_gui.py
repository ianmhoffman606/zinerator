import os
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk
import shutil
from pathlib import Path

# ===== UI CUSTOMIZATION =====
# Colors
BG_COLOR = "#1c1d21"            # Main background
CONTROL_BG = "#1f2026"         # Control panel background
SLOT_BG = "#262830"             # Slot frame background
SLOT_BORDER = "ridge"          # Slot border style
SLOT_BORDER_COLOR = "#3a3d46"  # Border + highlights
IMAGE_AREA_BG = "#1f2026"      # Image area background
LABEL_FG = "#e6e6e6"           # Primary text
SUBTLE_FG = "#b0b0b5"          # Secondary text
STATUS_FG = "#cfd2d8"          # Status text
GENERATE_BTN_BG = "#4cc29a"    # Accent green
GENERATE_BTN_FG = "#0f1418"    # Button text dark
CLEAR_BTN_BG = "#e07a5f"       # Accent terracotta
CLEAR_BTN_FG = "#0f1418"       # Button text dark

# Fonts
FONT_FAMILY = "Segoe UI"      # Main font family
TITLE_FONT = (FONT_FAMILY, 24, "bold")
SUBTITLE_FONT = (FONT_FAMILY, 12, "bold")
SLOT_LABEL_FONT = (FONT_FAMILY, 14, "bold")
GENERATE_BTN_FONT = (FONT_FAMILY, 11, "bold")
CLEAR_BTN_FONT = (FONT_FAMILY, 10)
STATUS_LABEL_FONT = (FONT_FAMILY, 10, "bold")
INSTRUCTION_FONT = (FONT_FAMILY, 10, "italic")
# ============================


class ZineratorGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Zinerator - GUI")
        self.root.geometry("1200x800")
        self.root.configure(bg=BG_COLOR)
        
        # Store image paths for each page
        self.image_paths = {
            'FRONT': None, 'BACK': None,
            '1': None, '2': None, '3': None, '4': None,
            '5': None, '6': None
        }
        
        # Maintain mapping of the layout
        self.layout_order = [
            ['2', '1', 'FRONT', 'BACK'],
            ['3', '4', '5', '6']
        ]
        
        # Photo references to prevent garbage collection
        self.photo_refs = {}
        
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the main UI layout"""
        # Title
        title_frame = tk.Frame(self.root, bg=BG_COLOR)
        title_frame.pack(fill=tk.X, padx=20, pady=10)
        
        title_label = tk.Label(title_frame, text="Zinerator GUI", 
                      font=TITLE_FONT, bg=BG_COLOR, fg=LABEL_FG)
        title_label.pack(side=tk.LEFT)
        
        # Control panel on the right
        control_frame = tk.Frame(self.root, bg=CONTROL_BG, relief=tk.SUNKEN, bd=1,
                     highlightbackground=SLOT_BORDER_COLOR,
                     highlightcolor=SLOT_BORDER_COLOR,
                     highlightthickness=1)
        control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=10, pady=10, ipadx=10, ipady=10)
        
        # Margins section
        margins_label = tk.Label(control_frame, text="Output Settings", 
                    font=SUBTITLE_FONT, bg=CONTROL_BG, fg=LABEL_FG)
        margins_label.pack(pady=10)
        
        # Side margin
        side_margin_frame = tk.Frame(control_frame, bg=CONTROL_BG)
        side_margin_frame.pack(fill=tk.X, pady=5)
        tk.Label(side_margin_frame, text="Side Margin (px):", bg=CONTROL_BG, fg=LABEL_FG).pack(side=tk.LEFT)
        self.side_margin_var = tk.IntVar(value=60)
        tk.Spinbox(side_margin_frame, from_=0, to=200, textvariable=self.side_margin_var, width=10,
               bg=CONTROL_BG, fg=LABEL_FG, insertbackground=LABEL_FG,
               disabledbackground=CONTROL_BG, disabledforeground=SUBTLE_FG,
               highlightbackground=SLOT_BORDER_COLOR).pack(side=tk.LEFT, padx=5)
        
        # Top/bottom margin
        tb_margin_frame = tk.Frame(control_frame, bg=CONTROL_BG)
        tb_margin_frame.pack(fill=tk.X, pady=5)
        tk.Label(tb_margin_frame, text="Top/Bottom Margin (px):", bg=CONTROL_BG, fg=LABEL_FG).pack(side=tk.LEFT)
        self.tb_margin_var = tk.IntVar(value=60)
        tk.Spinbox(tb_margin_frame, from_=0, to=200, textvariable=self.tb_margin_var, width=10,
               bg=CONTROL_BG, fg=LABEL_FG, insertbackground=LABEL_FG,
               disabledbackground=CONTROL_BG, disabledforeground=SUBTLE_FG,
               highlightbackground=SLOT_BORDER_COLOR).pack(side=tk.LEFT, padx=5)

        # Output format
        format_frame = tk.Frame(control_frame, bg=CONTROL_BG)
        format_frame.pack(fill=tk.X, pady=5)
        tk.Label(format_frame, text="Output Format:", bg=CONTROL_BG, fg=LABEL_FG).pack(side=tk.LEFT)
        self.output_format_var = tk.StringVar(value="jpg")
        format_menu = tk.OptionMenu(format_frame, self.output_format_var, "jpg", "pdf")
        format_menu.configure(bg=CONTROL_BG, fg=LABEL_FG, activebackground=CONTROL_BG, activeforeground=LABEL_FG, highlightthickness=0)
        format_menu.pack(side=tk.LEFT, padx=5)
        
        # Generate button
        tk.Frame(control_frame, height=20, bg=CONTROL_BG).pack()
        generate_btn = tk.Button(control_frame, text="Generate Zine", 
                                command=self.generate_zine, bg=GENERATE_BTN_BG, 
                    fg=GENERATE_BTN_FG, font=GENERATE_BTN_FONT,
                    padx=20, pady=10, borderwidth=0,
                    activebackground=GENERATE_BTN_BG, activeforeground=GENERATE_BTN_FG,
                    relief=tk.FLAT)
        generate_btn.pack(pady=10)
        
        # Clear all button
        clear_btn = tk.Button(control_frame, text="Clear All", 
                             command=self.clear_all, bg=CLEAR_BTN_BG,
                             fg=CLEAR_BTN_FG, font=CLEAR_BTN_FONT,
                             padx=15, pady=8, borderwidth=0,
                             activebackground=CLEAR_BTN_BG, activeforeground=CLEAR_BTN_FG,
                             relief=tk.FLAT)
        clear_btn.pack(pady=5)
        
        # Status
        status_label = tk.Label(control_frame, text="Status:", 
                       font=STATUS_LABEL_FONT, bg=CONTROL_BG, fg=SUBTLE_FG)
        status_label.pack(pady=(20, 5))
        self.status_var = tk.StringVar(value="Ready")
        status_text = tk.Label(control_frame, textvariable=self.status_var, 
                      bg=CONTROL_BG, fg=STATUS_FG, wraplength=180, justify=tk.LEFT)
        status_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Main canvas area for image slots
        canvas_frame = tk.Frame(self.root, bg=BG_COLOR)
        canvas_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Instructions
        instructions = tk.Label(canvas_frame, text="Drag and drop images onto each rectangle", 
                       font=INSTRUCTION_FONT, bg=BG_COLOR, fg=SUBTLE_FG)
        instructions.pack(pady=(0, 10))
        
        # Create the grid of image slots
        self.create_image_slots(canvas_frame)
    
    def create_image_slots(self, parent):
        """Create 8 drag-and-drop image slot boxes"""
        # Top row
        top_row_frame = tk.Frame(parent, bg=BG_COLOR)
        top_row_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        for page_name in ['2', '1', 'FRONT', 'BACK']:
            self.create_slot(top_row_frame, page_name)
        
        # Bottom row
        bottom_row_frame = tk.Frame(parent, bg=BG_COLOR)
        bottom_row_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        for page_name in ['3', '4', '5', '6']:
            self.create_slot(bottom_row_frame, page_name)
    
    def create_slot(self, parent, page_name):
        """Create a single drag-and-drop slot"""
        slot_frame = tk.Frame(parent, bg=SLOT_BG, relief=SLOT_BORDER, bd=2, width=150, height=250,
                       highlightbackground=SLOT_BORDER_COLOR,
                       highlightcolor=SLOT_BORDER_COLOR,
                       highlightthickness=1)
        slot_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        slot_frame.pack_propagate(False)
        
        # Label
        label = tk.Label(slot_frame, text=page_name, 
                font=SLOT_LABEL_FONT, bg=SLOT_BG, fg=LABEL_FG)
        label.pack(side=tk.TOP, pady=5)
        
        # Image display area - fixed portrait aspect ratio
        image_frame = tk.Frame(slot_frame, bg=IMAGE_AREA_BG)
        image_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))
        
        # Store reference to the image label
        image_label = tk.Label(image_frame, bg=IMAGE_AREA_BG, fg=SUBTLE_FG, text='Click or drag\nimage here')
        image_label.pack(fill=tk.BOTH, expand=True)
        
        # Bind click events
        image_label.bind('<Button-1>', lambda e: self.select_image(page_name, image_label))
        image_frame.bind('<Button-1>', lambda e: self.select_image(page_name, image_label))
        
        # Bind drag and drop events
        image_label.drop_target_register(DND_FILES)
        image_label.dnd_bind('<<Drop>>', lambda e: self.on_drop(e, page_name, image_label))
        
        # Store reference for later updates
        if not hasattr(self, 'slot_labels'):
            self.slot_labels = {}
        self.slot_labels[page_name] = image_label
    
    def select_image(self, page_name, image_label):
        """Open file dialog to select an image"""
        file_path = filedialog.askopenfilename(
            title=f"Select image for page '{page_name}'",
            filetypes=[("Image files", "*.png *.jpg *.jpeg"), ("All files", "*.*")]
        )
        
        if file_path:
            self.set_image(page_name, file_path, image_label)
    
    def on_drop(self, event, page_name, image_label):
        """Handle file drop event"""
        # Get the dropped file path
        file_path = event.data
        
        # Handle file paths with curly braces (multiple files or special chars)
        if file_path.startswith('{'):
            file_path = file_path.strip('{}')
        
        # Take only the first file if multiple were dropped
        if ' ' in file_path and not os.path.exists(file_path):
            file_path = file_path.split()[0]
        
        # Clean up the path
        file_path = file_path.strip()
        
        if os.path.exists(file_path) and os.path.isfile(file_path):
            self.set_image(page_name, file_path, image_label)
        else:
            messagebox.showerror("Error", f"Invalid file: {file_path}")
    
    
    def set_image(self, page_name, file_path, image_label):
        """Set the image for a page and update the display"""
        try:
            # Store the original file path first
            self.image_paths[page_name] = file_path
            
            # Schedule image update after widget is ready
            self.root.after(10, lambda: self.update_slot_image(page_name, file_path, image_label))
            
            # Update status
            loaded_count = sum(1 for path in self.image_paths.values() if path is not None)
            self.status_var.set(f"Loaded: {loaded_count}/8")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def update_slot_image(self, page_name, file_path, image_label):
        """Update the slot with properly sized and oriented image"""
        try:
            # Get the current size of the label
            width = image_label.winfo_width()
            height = image_label.winfo_height()
            
            # Skip if widget not ready yet
            if width <= 1 or height <= 1:
                self.root.after(50, lambda: self.update_slot_image(page_name, file_path, image_label))
                return
            
            # Open image
            img = Image.open(file_path)
            
            # Rotate to portrait if landscape (final orientation is vertical)
            if img.width > img.height:
                img = img.rotate(90, expand=True)
            
            # Flip upside down for top row (pages 2, 1, FRONT, BACK)
            if page_name in ['2', '1', 'FRONT', 'BACK']:
                img = img.rotate(180)
            
            # Calculate scaling to fill the entire slot while maintaining aspect ratio
            img_aspect = img.width / img.height
            slot_aspect = width / height
            
            if img_aspect > slot_aspect:
                # Image is wider - fit to height
                new_height = height
                new_width = int(height * img_aspect)
            else:
                # Image is taller - fit to width
                new_width = width
                new_height = int(width / img_aspect)
            
            # Resize image to fill slot
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Convert to PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # Update label
            image_label.config(image=photo, text='')
            self.photo_refs[page_name] = photo
            
        except Exception as e:
            print(f"Failed to update image for {page_name}: {e}")
    
    def clear_all(self):
        """Clear all loaded images"""
        self.image_paths = {name: None for name in self.image_paths}
        self.photo_refs = {}
        
        for page_name, label in self.slot_labels.items():
            label.config(image='', text='Click or drag\nimage here', fg=SUBTLE_FG)
        
        self.status_var.set("Ready")
    
    def generate_zine(self):
        """Generate the zine layout"""
        # Check if all images are loaded
        missing = [name for name, path in self.image_paths.items() if path is None]
        if missing:
            messagebox.showwarning("Missing Images", 
                                  f"Please select images for: {', '.join(sorted(missing))}")
            return
        
        # Ask where to save the output
        output_dir = filedialog.askdirectory(title="Choose where to save your zine")
        if not output_dir:
            self.status_var.set("Canceled")
            return
        output_dir = Path(output_dir)
        ext = ".pdf" if self.output_format_var.get().lower() == "pdf" else ".jpg"
        output_file = output_dir / f"zinerator_output{ext}"

        try:
            self.status_var.set("Generating...")
            self.root.update()
            
            # Import and run the zine layout generator using the chosen paths directly
            from zinerator import create_zine_layout
            create_zine_layout(
                None,
                self.side_margin_var.get(),
                self.tb_margin_var.get(),
                str(output_dir),
                self.image_paths,
                output_format=self.output_format_var.get().lower(),
            )
            
            self.status_var.set("Success!")
            messagebox.showinfo(
                "Success",
                f"Zine layout generated successfully!\nSaved to:\n{output_file}"
            )
            
        except Exception as e:
            self.status_var.set("Error!")
            messagebox.showerror("Error", f"Failed to generate zine: {e}")


def main():
    root = TkinterDnD.Tk()  # Use TkinterDnD instead of regular Tk
    app = ZineratorGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
