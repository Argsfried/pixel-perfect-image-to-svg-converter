#!/usr/bin/env python3
"""
img2svg_pixelperfect_ui.py

Pixel-perfect Image -> SVG converter (UI)
- Pure Python: requires only Pillow and CustomTkinter.
- Button-based UI only.
- Produces SVGs made of <rect> horizontal runs (lossless pixel-perfect).
- Output: ./converted_svgs/*.svg next to script or exe.
"""

import os
import sys
from pathlib import Path
from PIL import Image
import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk

# ---------------- Config ----------------
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

if getattr(sys, "frozen", False):
    # Running as PyInstaller EXE
    BASE_DIR = Path(sys.executable).resolve().parent
else:
    # Running as script
    BASE_DIR = Path(__file__).resolve().parent

OUTPUT_DIR = BASE_DIR / "converted_svgs"
OUTPUT_DIR.mkdir(exist_ok=True)

SUPPORTED_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".gif", ".tif", ".tiff", ".webp"}

# ---------------- Pixel-perfect converter ----------------
def rgba_to_svg_fill(r, g, b, a):
    return f"#{r:02X}{g:02X}{b:02X}", (a / 255.0)

def image_to_svg_vector(pil_img: Image.Image, out_path: Path):
    img = pil_img.convert("RGBA")
    w, h = img.size
    pixels = img.load()

    with open(out_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            'shape-rendering="crispEdges">\n'
        )

        for y in range(h):
            x = 0
            while x < w:
                r, g, b, a = pixels[x, y]
                if a == 0:
                    x += 1
                    continue
                run_start = x
                run_r, run_g, run_b, run_a = r, g, b, a
                x += 1
                while x < w and pixels[x, y] == (run_r, run_g, run_b, run_a):
                    x += 1
                run_len = x - run_start
                fill_hex, fill_opacity = rgba_to_svg_fill(run_r, run_g, run_b, run_a)
                f.write(
                    f'  <rect x="{run_start}" y="{y}" width="{run_len}" height="1" fill="{fill_hex}"'
                )
                if fill_opacity < 1.0:
                    f.write(f' fill-opacity="{fill_opacity:.6f}"')
                f.write('/>\n')

        f.write("</svg>\n")

# ---------------- UI App ----------------
class PixelPerfectApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Pixel2SVG Converter")
        self.geometry("900x620")
        self.resizable(True, True)

        # internal state
        self.selected_paths = []  # absolute file paths (strings)
        self.last_folder = BASE_DIR  # initial folder

        # build UI
        self._build_ui()

    def _build_ui(self):
        pad = 14
        main = ctk.CTkFrame(self, corner_radius=12)
        main.pack(expand=True, fill="both", padx=pad, pady=pad)

        title = ctk.CTkLabel(main, text="🖼 Pixel-Perfect Image → SVG", font=("Helvetica", 20, "bold"))
        title.pack(pady=(8, 6))

        info = ctk.CTkLabel(main, text=f"Working folder: {BASE_DIR}\nOutput folder: {OUTPUT_DIR}", wraplength=820, justify="center")
        info.pack(pady=(0, 12))

        # Buttons row
        btn_row = ctk.CTkFrame(main)
        btn_row.pack(fill="x", padx=20, pady=(0, 12))

        btn_select_folder = ctk.CTkButton(btn_row, text="📂 Select Folder (top-level)", width=220, command=self.select_folder)
        btn_select_folder.pack(side="left", padx=8)

        btn_select_files = ctk.CTkButton(btn_row, text="📁 Select Files", width=180, command=self.select_files)
        btn_select_files.pack(side="left", padx=8)

        self.btn_convert = ctk.CTkButton(btn_row, text="▶ Convert Selected", width=220, fg_color="#16a34a", hover_color="#10b981", command=self.convert_selected)
        self.btn_convert.pack(side="left", padx=8)

        btn_clear = ctk.CTkButton(btn_row, text="🗑 Clear Converted", width=160, fg_color="#ef4444", hover_color="#f43f5e", command=self.clear_converted)
        btn_clear.pack(side="left", padx=8)

        # Selected files list (Treeview)
        list_frame = ctk.CTkFrame(main)
        list_frame.pack(fill="both", expand=False, padx=20, pady=(0, 12))

        lbl = ctk.CTkLabel(list_frame, text="Selected (will be converted):", anchor="w")
        lbl.pack(fill="x", padx=6, pady=(6, 4))

        columns = ("name", "path")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=5)
        self.tree.heading("name", text="Filename")
        self.tree.heading("path", text="Full path")
        self.tree.column("name", width=200)
        self.tree.column("path", width=600)
        self.tree.pack(fill="both", expand=True, padx=6, pady=(0, 6))

        # results box
        results_frame = ctk.CTkFrame(main)
        results_frame.pack(fill="both", expand=True, padx=20, pady=(0, 12))

        results_label = ctk.CTkLabel(results_frame, text="Results / Log", anchor="w")
        results_label.pack(fill="x", padx=8, pady=(8, 0))

        self.results_box = ctk.CTkTextbox(results_frame, wrap="word")
        self.results_box.pack(fill="both", expand=True, padx=8, pady=8)

        # status bar
        self.status_label = ctk.CTkLabel(main, text=self._status_text(), anchor="w")
        self.status_label.pack(fill="x", padx=20, pady=(0, 8))

    def _status_text(self):
        return f"Output folder: {OUTPUT_DIR}  •  Skips existing files"

    def _log(self, text: str):
        self.results_box.insert("end", text + "\n")
        self.results_box.see("end")

    # ---------------- Browse buttons ----------------
    def select_files(self):
        filetypes = [("Image files", "*.png *.jpg *.jpeg *.bmp *.gif *.tiff *.webp")]
        paths = filedialog.askopenfilenames(title="Select images", filetypes=filetypes, initialdir=str(self.last_folder))
        if paths:
            self.last_folder = str(Path(paths[0]).parent)
            self._add_paths(paths)

    def select_folder(self):
        folder = filedialog.askdirectory(title="Select folder (top-level images will be used)", initialdir=str(self.last_folder))
        if folder:
            self.last_folder = folder
            self._add_paths([folder])

    # ---------------- Selection helpers ----------------
    def _add_paths(self, paths):
        """Add absolute file paths to selected_paths and TreeView (dedup)."""
        added = 0
        for p in paths:
            p = str(Path(p).resolve())
            if p in self.selected_paths:
                continue
            if Path(p).is_dir():
                folder = Path(p)
                for fname in os.listdir(folder):
                    if Path(fname).suffix.lower() in SUPPORTED_EXT:
                        fpath = str((folder / fname).resolve())
                        if fpath not in self.selected_paths:
                            self.selected_paths.append(fpath)
                            self._tree_insert(fpath)
                            added += 1
            elif Path(p).is_file():
                if Path(p).suffix.lower() in SUPPORTED_EXT:
                    self.selected_paths.append(p)
                    self._tree_insert(p)
                    added += 1
        if added:
            self._log(f"Added {added} file(s).")
        else:
            self._log("No supported images added.")

    def _tree_insert(self, fullpath):
        name = Path(fullpath).name
        self.tree.insert("", "end", values=(name, fullpath))

    # ---------------- Convert / Clear ----------------
    def convert_selected(self):
        if not self.selected_paths:
            messagebox.showwarning("No files", "No files selected. Use the buttons to select files or folders.")
            return

        OUTPUT_DIR.mkdir(exist_ok=True)
        converted = []
        skipped = []
        errors = []

        for p in list(self.selected_paths):
            try:
                src = Path(p)
                if not src.exists():
                    errors.append(f"{src.name} (missing)")
                    continue
                out_svg = OUTPUT_DIR / (src.stem + ".svg")
                if out_svg.exists():
                    skipped.append(src.name)
                    continue
                with Image.open(src) as im:
                    image_to_svg_vector(im, out_svg)
                converted.append(src.name)
                self._log(f"Converted: {src.name}")
            except Exception as e:
                errors.append(f"{src.name} (error: {e})")
                self._log(f"Error converting {src.name}: {e}")

        # Clear selection and TreeView
        self.selected_paths.clear()
        for item in self.tree.get_children():
            self.tree.delete(item)

        # summary
        if converted:
            self._log(f"\n✅ Converted ({len(converted)}):")
            for n in converted:
                self._log(f"  - {n}")
        if skipped:
            self._log(f"\n⏩ Skipped ({len(skipped)} already exist):")
            for n in skipped:
                self._log(f"  - {n}")
        if errors:
            self._log(f"\n❌ Errors ({len(errors)}):")
            for e in errors:
                self._log(f"  - {e}")

        self.status_label.configure(text=self._status_text())

    def clear_converted(self):
        if OUTPUT_DIR.exists():
            for f in OUTPUT_DIR.iterdir():
                try:
                    f.unlink()
                except Exception:
                    pass
            try:
                OUTPUT_DIR.rmdir()
            except Exception:
                pass
            self._log("Cleared converted_svgs folder.")
        else:
            self._log("No converted_svgs folder to clear.")
        self.status_label.configure(text=self._status_text())

# ---------------- Run ----------------
def main():
    app = PixelPerfectApp()
    app.mainloop()

if __name__ == "__main__":
    main()
