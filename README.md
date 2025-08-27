# Pixel-Perfect Image to SVG Converter

A simple Python-based app that converts raster images to pixel-perfect SVGs. The app features a modern UI built with **CustomTkinter**, outputs lossless SVGs composed of `<rect>` horizontal runs, and is ready to package into an `.exe` for Windows.

---

## Features

* Pixel-perfect conversion: Each colored pixel is preserved in the SVG.
* Supports common image formats: PNG, JPG, JPEG, BMP, GIF, TIFF, WEBP.
* Fully GUI-driven (CustomTkinter): No command-line required.
* Batch conversion: Convert multiple files or an entire folder.
* Automatic output folder: `converted_svgs` created next to the `.exe`.
* Skips existing SVGs to avoid overwriting.
* Clear converted folder functionality.
* User-friendly Windows EXE packaging with icon support.

## Screenshots

<img width="902" height="652" alt="image" src="https://github.com/user-attachments/assets/0932de19-6a8e-424a-8b1f-79944e7e6bd1" />

## Installation

1. Clone or download the repository:

```bash
git clone https://github.com/argsfried/pixel-perfect-image-to-svg-converter.git
cd pixel-perfect-image-to-svg-converter
```

2. Install dependencies:

```bash
pip install pillow customtkinter
```

## Running the App

### Python Run

```bash
python pixel-perfect-image-to-svg-converter.py
```

### Windows EXE

Use **PyInstaller** to create an executable:

```bash
pyinstaller --onefile --windowed --icon=pixel-perfect-svg-converter.ico --name "Pixel Perfect Image to SVG Converter" pixel-perfect-image-to-svg-converter.py
```

* The EXE will appear in `dist/`.
* Running the EXE will create a `converted_svgs` folder next to it.

## Usage

1. Click **Select Folder** or **Select Files**.
2. Selected images appear in the list.
3. Press **Convert Selected**.
4. Converted SVGs appear in `converted_svgs`.
5. Optionally, clear converted SVGs with **Clear Converted**.

## File Naming

* Output SVGs preserve the original filename.

## Notes

* Skips already converted SVGs to avoid duplicates.

## Dependencies

* [Pillow](https://pypi.org/project/Pillow/)
* [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter)

Install with:

```bash
pip install pillow customtkinter
```

## License

[MIT License](LICENSE)
