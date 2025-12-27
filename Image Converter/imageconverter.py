import argparse
import sys
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path
from PIL import Image

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

SUPPORTED_IN = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}
SUPPORTED_OUT = {".png", ".jpg", ".jpeg", ".webp", ".bmp", ".tif", ".tiff"}

def convert_image(src_path: Path, out_ext: str, out_dir: Path | None = None, jpeg_quality: int = 92):
    out_ext = out_ext.lower().strip()
    if not out_ext.startswith("."):
        out_ext = "." + out_ext

    if src_path.suffix.lower() not in SUPPORTED_IN:
        raise ValueError(f"Unsupported input type: {src_path.suffix}")

    if out_ext not in SUPPORTED_OUT:
        raise ValueError(f"Unsupported output type: {out_ext}")

    out_dir = out_dir or src_path.parent
    if not out_dir.exists():
        out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / (src_path.stem + out_ext)

    with Image.open(src_path) as im:
        # Handle PNG/WebP transparency when exporting to JPEG
        if out_ext in {".jpg", ".jpeg"}:
            if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
                bg = Image.new("RGB", im.size, (255, 255, 255))  # white background
                bg.paste(im.convert("RGBA"), mask=im.convert("RGBA").split()[-1])
                im = bg
            else:
                im = im.convert("RGB")
            im.save(out_path, quality=jpeg_quality, optimize=True)
        else:
            # Keep alpha where supported (PNG/WebP/TIFF), convert if needed
            im.save(out_path)

    return out_path

def batch_convert(folder: Path, out_ext: str, out_dir: Path | None = None, recursive: bool = False, quality: int = 92, parallel: bool = False):
    pattern = "**/*" if recursive else "*"
    files = [p for p in folder.glob(pattern) if p.is_file() and p.suffix.lower() in SUPPORTED_IN]
    
    if not files:
        print("No supported images found.")
        return

    print(f"Found {len(files)} images to convert.")

    if parallel:
        with ProcessPoolExecutor() as executor:
            futures = {executor.submit(convert_image, f, out_ext, out_dir, quality): f for f in files}
            for future in futures:
                f = futures[future]
                try:
                    out = future.result()
                    print(f"Converted: {f.name} -> {out.name}")
                except Exception as e:
                    print(f"Failed: {f.name} ({e})")
    else:
        for f in files:
            try:
                out = convert_image(f, out_ext, out_dir, quality)
                print(f"Converted: {f.name} -> {out.name}")
            except Exception as e:
                print(f"Failed: {f.name} ({e})")

class ImageConverterGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Converter")
        self.root.geometry("600x550")

        # Main Container
        self.main_frame = ctk.CTkFrame(root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Title
        ctk.CTkLabel(self.main_frame, text="Image Converter", font=("Roboto", 24, "bold")).pack(pady=(10, 20))

        # Input
        ctk.CTkLabel(self.main_frame, text="Input Source:", font=("Roboto", 14)).pack(anchor="w", padx=20)
        self.input_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.input_path = ctk.StringVar()
        self.entry_input = ctk.CTkEntry(self.input_frame, textvariable=self.input_path, placeholder_text="Select file or folder...")
        self.entry_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        ctk.CTkButton(self.input_frame, text="File", width=60, command=self.browse_file).pack(side="left", padx=(0, 5))
        ctk.CTkButton(self.input_frame, text="Folder", width=60, command=self.browse_folder).pack(side="left")

        # Output Format
        ctk.CTkLabel(self.main_frame, text="Output Format:", font=("Roboto", 14)).pack(anchor="w", padx=20)
        self.format_var = ctk.StringVar(value="jpg")
        self.format_menu = ctk.CTkOptionMenu(self.main_frame, variable=self.format_var, values=["jpg", "png", "webp", "bmp", "tiff"])
        self.format_menu.pack(anchor="w", padx=20, pady=(5, 15))

        # Output Directory
        ctk.CTkLabel(self.main_frame, text="Output Directory (Optional):", font=("Roboto", 14)).pack(anchor="w", padx=20)
        self.out_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.out_frame.pack(fill="x", padx=20, pady=(5, 15))
        
        self.out_path = ctk.StringVar()
        ctk.CTkEntry(self.out_frame, textvariable=self.out_path, placeholder_text="Default: Same as source").pack(side="left", fill="x", expand=True, padx=(0, 10))
        ctk.CTkButton(self.out_frame, text="Browse", width=80, command=self.browse_out).pack(side="left")

        # Options Grid
        self.opts_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.opts_frame.pack(fill="x", padx=20, pady=(5, 15))

        self.recursive_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.opts_frame, text="Recursive Search", variable=self.recursive_var).pack(side="left", padx=(0, 20))
        
        self.parallel_var = ctk.BooleanVar()
        ctk.CTkCheckBox(self.opts_frame, text="Parallel Processing", variable=self.parallel_var).pack(side="left")

        # Quality
        ctk.CTkLabel(self.main_frame, text="JPEG Quality:", font=("Roboto", 14)).pack(anchor="w", padx=20)
        self.quality_var = ctk.IntVar(value=92)
        self.quality_slider = ctk.CTkSlider(self.main_frame, from_=1, to=100, variable=self.quality_var)
        self.quality_slider.pack(fill="x", padx=20, pady=(5, 5))
        self.quality_label = ctk.CTkLabel(self.main_frame, textvariable=self.quality_var)
        self.quality_label.pack(anchor="e", padx=20)

        # Convert Button
        self.btn_convert = ctk.CTkButton(self.main_frame, text="START CONVERSION", height=50, font=("Roboto", 16, "bold"), command=self.start_conversion, fg_color="#2CC985", hover_color="#229965")
        self.btn_convert.pack(fill="x", padx=20, pady=(10, 20))

        # Status
        self.status_var = ctk.StringVar(value="Ready")
        self.lbl_status = ctk.CTkLabel(self.root, textvariable=self.status_var, text_color="gray")
        self.lbl_status.pack(side="bottom", pady=10)

    def browse_file(self):
        f = filedialog.askopenfilename()
        if f: self.input_path.set(f)

    def browse_folder(self):
        d = filedialog.askdirectory()
        if d: self.input_path.set(d)

    def browse_out(self):
        d = filedialog.askdirectory()
        if d: self.out_path.set(d)

    def start_conversion(self):
        input_path = self.input_path.get()
        if not input_path:
            messagebox.showerror("Error", "Please select an input file or directory.")
            return
        
        self.status_var.set("Converting...")
        self.btn_convert.configure(state="disabled", text="CONVERTING...")
        threading.Thread(target=self.run_conversion, daemon=True).start()

    def run_conversion(self):
        inp = Path(self.input_path.get())
        fmt = self.format_var.get()
        out = self.out_path.get()
        out = Path(out) if out else None
        rec = self.recursive_var.get()
        qual = self.quality_var.get()
        par = self.parallel_var.get()

        try:
            if inp.is_file():
                convert_image(inp, fmt, out, qual)
            else:
                batch_convert(inp, fmt, out, rec, qual, par)
            
            self.root.after(0, lambda: self.status_var.set("Conversion Complete!"))
            self.root.after(0, lambda: messagebox.showinfo("Success", "Conversion Complete!"))
        except Exception as e:
            self.root.after(0, lambda: self.status_var.set(f"Error: {e}"))
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_convert.configure(state="normal", text="START CONVERSION"))

def run_gui():
    root = ctk.CTk()
    ImageConverterGUI(root)
    root.mainloop()

def main():
    if len(sys.argv) == 1:
        run_gui()
        return

    parser = argparse.ArgumentParser(description="Batch Image Converter")
    parser.add_argument("input", type=Path, help="Input file or directory")
    parser.add_argument("format", help="Output format (e.g., jpg, png, webp)")
    parser.add_argument("-o", "--output", type=Path, help="Output directory (optional)")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursive search for images")
    parser.add_argument("-q", "--quality", type=int, default=92, help="JPEG quality (default: 92)")
    parser.add_argument("-p", "--parallel", action="store_true", help="Enable parallel processing")

    args = parser.parse_args()

    if not args.input.exists():
        print(f"Error: {args.input} does not exist.")
        sys.exit(1)

    if args.input.is_file():
        try:
            out = convert_image(args.input, args.format, args.output, args.quality)
            print(f"Converted: {out}")
        except Exception as e:
            print(f"Error: {e}")
    else:
        batch_convert(args.input, args.format, args.output, args.recursive, args.quality, args.parallel)

if __name__ == "__main__":
    main()
