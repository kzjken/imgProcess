# Image Converter

## Overview
Image Converter is a desktop GUI application that helps you rename and compress photos based on their EXIF metadata. It supports batch processing of JPG images and allows flexible renaming structures.

## Features
- Rename photos using EXIF data such as date, time, camera model, and more.
- Compress photos to reduce file size with adjustable quality.
- Preview file renaming before executing.
- Supports multithreading for smooth UI experience.

## Installation
Requires Python 3.x and the following packages:
- Pillow

Install dependencies with:
```bash
pip install Pillow
```

## Usage
1. Select the source folder containing images.
2. Choose the destination folder to save processed images.
3. Select functions: Rename and/or Compress.
4. Adjust compression quality (if Compress is selected).
5. Customize the rename structure (Index, Date, Time, Original Name, Camera, Hash).
6. Click "Preview" to see the planned changes.
7. Click "Execute" to apply changes.

## License
MIT License

---

Author: Z.Kang  
Version: 1.0.0
