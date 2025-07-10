import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
import threading
from PIL import Image
import sys
import os

# Import the conversion logic from webp_jpeg_converter.py
from webp_jpeg_converter import convert_and_rename_images

def run_conversion(input_folder, output_folder, prefix, start_number, rename_files, overwrite_originals, output_format, output_ext, status_callback):
    try:
        convert_and_rename_images(
            input_folder,
            output_folder,
            prefix,
            start_number,
            rename_files,
            overwrite_originals,
            output_format,
            output_ext
        )
        status_callback("Conversion complete!")
    except Exception as e:
        status_callback(f"Error: {e}")

class ConverterApp:
    def __init__(self, root):
        self.root = root
        root.title("WebP Image Converter")
        root.geometry("500x400")
        self.input_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.prefix = tk.StringVar(value="image")
        self.start_number = tk.IntVar(value=1)
        self.rename_files = tk.BooleanVar(value=True)
        self.overwrite_originals = tk.BooleanVar(value=False)
        self.output_format = tk.StringVar(value="PNG")
        self.status = tk.StringVar()
        self.accept_all_overwrites = False
        self.create_widgets()

    def create_widgets(self):
        row = 0
        tk.Label(self.root, text="Input Folder:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.input_folder, width=40).grid(row=row, column=1, padx=5)
        tk.Button(self.root, text="Browse", command=self.browse_input).grid(row=row, column=2, padx=5)
        row += 1
        tk.Label(self.root, text="Output Folder:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.output_folder, width=40).grid(row=row, column=1, padx=5)
        tk.Button(self.root, text="Browse", command=self.browse_output).grid(row=row, column=2, padx=5)
        row += 1
        tk.Label(self.root, text="Output Format:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Radiobutton(self.root, text="PNG (preserve transparency)", variable=self.output_format, value="PNG").grid(row=row, column=1, sticky="w")
        row += 1
        tk.Radiobutton(self.root, text="JPEG (no transparency)", variable=self.output_format, value="JPEG").grid(row=row, column=1, sticky="w")
        row += 1
        tk.Label(self.root, text="Renaming:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Radiobutton(self.root, text="Sequential (image_001, ...)", variable=self.rename_files, value=True).grid(row=row, column=1, sticky="w")
        row += 1
        tk.Radiobutton(self.root, text="Keep original filenames", variable=self.rename_files, value=False).grid(row=row, column=1, sticky="w")
        row += 1
        tk.Label(self.root, text="Prefix:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.prefix, width=15).grid(row=row, column=1, sticky="w")
        row += 1
        tk.Label(self.root, text="Start Number:").grid(row=row, column=0, sticky="e", padx=5, pady=5)
        tk.Entry(self.root, textvariable=self.start_number, width=8).grid(row=row, column=1, sticky="w")
        row += 1
        tk.Checkbutton(self.root, text="Delete original files after conversion", variable=self.overwrite_originals).grid(row=row, column=1, sticky="w")
        row += 1
        tk.Button(self.root, text="Start Conversion", command=self.start_conversion).grid(row=row, column=1, pady=15)
        row += 1
        tk.Label(self.root, textvariable=self.status, fg="blue").grid(row=row, column=0, columnspan=3, pady=10)

    def browse_input(self):
        folder = filedialog.askdirectory()
        if folder:
            self.input_folder.set(folder)

    def browse_output(self):
        folder = filedialog.askdirectory()
        if folder:
            self.output_folder.set(folder)

    def start_conversion(self):
        input_folder = self.input_folder.get() or '.'
        output_folder = self.output_folder.get() or None
        prefix = self.prefix.get() or 'image'
        try:
            start_number = int(self.start_number.get())
        except Exception:
            start_number = 1
        rename_files = self.rename_files.get()
        overwrite_originals = self.overwrite_originals.get()
        output_format = self.output_format.get()
        output_ext = '.png' if output_format == 'PNG' else '.jpg'
        self.status.set("Converting...")
        threading.Thread(target=run_conversion, args=(
            input_folder, output_folder, prefix, start_number, rename_files, overwrite_originals, output_format, output_ext, self.status.set
        ), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = ConverterApp(root)
    root.mainloop() 