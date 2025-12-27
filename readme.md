Image Swapper / Converter (Python)

I built this tool to quickly and easily convert images between formats such as PNG, JPG/JPEG, WebP, BMP, and TIFF. It’s lightweight, simple to use, and designed to handle single images or batch conversions without unnecessary complexity.

This project focuses on doing one thing well: swapping image formats reliably.

Features

Convert images between common formats (PNG, JPG/JPEG, WebP, BMP, TIFF)

Batch conversion support

Automatically handles transparency when converting to JPEG

Fast and lightweight

Easy to extend or integrate into other projects

Requirements

Python 3.9+

Pillow (PIL)

Install dependencies:

pip install pillow

How It Works

Place your images in the same folder as the script (or point it to a folder), choose the output format, and run the script. Converted images are saved alongside the originals.

Example usage:

python converter.py


You can also batch convert entire folders by adjusting the path and output format in the script.

Why I Made This

I wanted a simple image converter that didn’t rely on online tools or bloated software. This script gives me full control, works offline, and can be expanded into a GUI or full desktop app later.

Future Improvements

Drag-and-drop GUI

Quality and compression controls

Resize and optimisation options

Standalone .exe build