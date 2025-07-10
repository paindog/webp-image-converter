#!/usr/bin/env python3
"""
WebP to JPEG Converter and Image Renamer
Converts WebP images to JPEG format and renames all images with simple sequential names.
"""

import os
import sys
from PIL import Image
import argparse
from pathlib import Path

def convert_and_rename_images(folder_path, output_folder=None, prefix="image", start_number=1, rename_files=True, overwrite_originals=False, output_format='PNG', output_ext='.png', logger=None):
    """
    Convert WebP images to JPEG/PNG and optionally rename all images with simple sequential names.
    
    Args:
        folder_path (str): Path to the folder containing images
        output_folder (str): Optional output folder path. If None, uses input folder
        prefix (str): Prefix for renamed files (default: "image")
        start_number (int): Starting number for sequential naming (default: 1)
        rename_files (bool): Whether to rename files or keep original names (default: True)
        overwrite_originals (bool): Whether to delete original files after conversion (default: False)
        logger: Optional function to receive log messages (for GUI); if None, uses print.
    """
    
    def log(msg):
        if logger:
            logger(msg)
        else:
            print(msg)

    # Convert to Path objects
    input_path = Path(folder_path)
    if not input_path.exists():
        log(f"Error: Folder '{folder_path}' does not exist.")
        return
    
    # Set output path - if no output folder specified and not overwriting, use input folder
    if output_folder:
        output_path = Path(output_folder)
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path = input_path
    
    # Supported image formats
    supported_formats = {'.webp', '.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif'}
    
    # Get all image files
    image_files = []
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in supported_formats:
            image_files.append(file_path)
    
    if not image_files:
        log("No supported image files found in the folder.")
        return
    
    log(f"Found {len(image_files)} image files to process.")

    # Sort files to ensure consistent ordering
    image_files.sort()

    # --- NEW: Determine starting number for sequential naming if output folder exists and has files ---
    if rename_files:
        existing_numbers = []
        for f in output_path.iterdir():
            if f.is_file() and f.suffix.lower() == output_ext and f.name.startswith(prefix + '_'):
                try:
                    num_part = f.stem[len(prefix)+1:]
                    existing_numbers.append(int(num_part))
                except Exception:
                    continue
        if existing_numbers:
            counter = max(existing_numbers) + 1 if start_number <= max(existing_numbers) else start_number
        else:
            counter = start_number
    else:
        counter = start_number

    converted_count = 0
    renamed_count = 0
    accept_all_overwrites = False

    for file_path in image_files:
        try:
            # Generate new filename
            if rename_files:
                new_filename = f"{prefix}_{counter:03d}{output_ext}"
            else:
                # Keep original name but change extension to .jpg
                original_name = file_path.stem  # filename without extension
                new_filename = f"{original_name}{output_ext}"
            
            new_file_path = output_path / new_filename
            
            # --- NEW: Overwrite prompt for non-renaming mode ---
            if new_file_path.exists() and not overwrite_originals:
                if rename_files:
                    log(f"Skipping {file_path.name} - output file {new_filename} already exists")
                    counter += 1
                    continue
                else:
                    if not accept_all_overwrites:
                        while True:
                            # For GUI, skip prompt; for CLI, prompt
                            if logger:
                                log(f"Skipping {file_path.name} - output file {new_filename} already exists (GUI mode)")
                                break
                            resp = input(f"File {new_filename} already exists. Overwrite? (Y/n/A for all): ").strip().lower()
                            if resp in ('y', 'yes', ''):
                                break
                            elif resp in ('n', 'no'):
                                log(f"Skipping {file_path.name}")
                                break
                            elif resp == 'a':
                                accept_all_overwrites = True
                                break
                        if logger and not accept_all_overwrites:
                            continue
                        if not logger and resp in ('n', 'no'):
                            continue

            # Open and process the image
            with Image.open(file_path) as img:
                # Convert to RGB if necessary for JPEG, preserve for PNG
                if output_format == 'JPEG':
                    if img.mode in ('RGBA', 'LA', 'P'):
                        # Create white background for transparent images
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                        img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                
                # Save as JPEG
                img.save(new_file_path, 'JPEG', quality=95, optimize=True)
                
                log(f"Converted: {file_path.name} → {new_filename}")
                
                if file_path.suffix.lower() == '.webp':
                    converted_count += 1
                else:
                    renamed_count += 1
                
                # Only remove original file if overwrite_originals is True and we're not working in place
                if overwrite_originals and (output_folder or file_path.name != new_filename):
                    try:
                        file_path.unlink()  # Delete original file
                    except Exception as e:
                        log(f"Warning: Could not delete original file {file_path.name}: {e}")
                
                if rename_files:
                    counter += 1
                
        except Exception as e:
            log(f"Error processing {file_path.name}: {e}")
            if rename_files:
                counter += 1
            continue
    
    log(f"\nProcessing complete!")
    log(f"WebP files converted: {converted_count}")
    log(f"Other files renamed: {renamed_count}")
    log(f"Total files processed: {converted_count + renamed_count}")

def main():
    parser = argparse.ArgumentParser(description='Convert WebP images to JPEG and rename with simple sequential names')
    parser.add_argument('folder', help='Path to the folder containing images')
    parser.add_argument('-o', '--output', help='Output folder path (optional)')
    parser.add_argument('-p', '--prefix', default='image', help='Prefix for renamed files (default: image)')
    parser.add_argument('-s', '--start', type=int, default=1, help='Starting number for sequential naming (default: 1)')
    parser.add_argument('-r', '--rename', action='store_true', help='Rename files with sequential numbers')
    parser.add_argument('--no-rename', action='store_true', help='Keep original filenames (just convert format)')
    parser.add_argument('--create-converted', action='store_true', help='Create a "converted" folder in script directory')
    parser.add_argument('--overwrite', action='store_true', help='Delete original files after conversion (default: keep originals)')
    
    args = parser.parse_args()
    
    # Check if PIL is available
    try:
        from PIL import Image
    except ImportError:
        print("Error: Pillow library is required. Install it with: pip install Pillow")
        sys.exit(1)
    
    convert_and_rename_images(args.folder, args.output, args.prefix, args.start)

if __name__ == "__main__":
    # If run without command line arguments, prompt for folder path
    if len(sys.argv) == 1:
        print("WebP to JPEG Converter and Image Renamer")
        print("=" * 40)
        
        folder_path = input("Enter the path to the folder containing images to convert (press Enter for current directory): ").strip()
        if not folder_path:
            folder_path = '.'
        folder_path = folder_path.strip('"\'')

        # --- NEW: Ask for output format ---
        print("\nChoose output format:")
        print("1. PNG (preserve transparency, default)")
        print("2. JPEG (smaller, no transparency)")
        format_choice = input("Convert to (1=PNG, 2=JPEG)? [1]: ").strip()
        if format_choice == '2':
            output_format = 'JPEG'
            output_ext = '.jpg'
        else:
            output_format = 'PNG'
            output_ext = '.png'

        # Ask about renaming
        print("\nRenaming options:")
        print("1. Rename files with sequential numbers (image_001{} etc.)".format(output_ext))
        print("2. Keep original filenames (just convert format)")
        choice = input("Choose option (1 or 2): ").strip()
        rename_files = choice != "2"
        
        # Ask about output folder
        print("\nOutput options:")
        print("1. Convert in place (replace original files)")
        print("2. Create 'converted' folder in script directory")
        print("3. Specify custom output folder")
        output_choice = input("Choose option (1, 2, or 3): ").strip()
        
        output_folder = None
        overwrite_originals = False
        
        if output_choice == "1":
            overwrite_choice = input("Delete original files after conversion? (y/n): ").strip().lower()
            overwrite_originals = overwrite_choice in ['y', 'yes']
        elif output_choice == "2":
            script_dir = Path(__file__).parent
            output_folder = script_dir / "converted"
        elif output_choice == "3":
            output_folder = input("Enter the path where converted images should be saved (press Enter for default location): ").strip()
            if output_folder:
                output_folder = output_folder.strip('"\'')
        
        prefix = "image"
        start_number = 1
        if rename_files:
            custom_prefix = input("Enter filename prefix (default: 'image'): ").strip()
            if custom_prefix:
                prefix = custom_prefix
            try:
                start_num = input("Enter starting number (default: 1): ").strip()
                if start_num:
                    start_number = int(start_num)
            except ValueError:
                print("Invalid number, using default: 1")
        
        convert_and_rename_images(folder_path, output_folder, prefix, start_number, rename_files, overwrite_originals, output_format, output_ext)
    else:
        main()