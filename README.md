# WebP Image Converter

A simple, user-friendly tool to batch convert WebP images to PNG (preserving transparency) or JPEG (smaller, no transparency). Includes both a graphical interface and command-line support.

## Features
- Convert WebP images to PNG or JPEG
- Preserve transparency when converting to PNG
- Batch process entire folders
- Sequential renaming or keep original filenames
- Choose input/output folders
- Option to delete originals after conversion
- Simple GUI (no command line needed)
- Cross-platform (Windows, Mac, Linux)

## Screenshot
![GUI Screenshot](screenshot.png)

## Installation
1. Install Python 3.7+
2. Install dependencies:
   ```sh
   pip install Pillow
   ```

## Usage

### GUI (Recommended)
Run:
```sh
python webp_jpeg_gui.py
```
A window will open for you to select folders and options.

### Command Line
Run:
```sh
python webp_jpeg_converter.py
```
Follow the prompts in your terminal.

## Requirements
- Python 3.7 or higher
- Pillow

## License
This project is licensed under the MIT License. See [LICENSE](LICENSE) for details. 