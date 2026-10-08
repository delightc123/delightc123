#!/usr/bin/env python3
"""
generate_ascii_avatar.py - Generates compact ACASCI / dot-matrix avatar from the new portrait
For embedding inside the ~/ whoami terminal card.
"""

from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_SRC = BASE_DIR / "assets" / "source" / "portrait_cropped.jpg"
OUT_FILE = BASE_DIR / "assets" / "portrait-matrix.svg"

def make_ascii_avatar():
    img = Image.open(PORTRAIT_SRC).convert("RGB")
    gray = ImageOps.grayscale(img)
    arr = np.array(gray, dtype=float)

    # Boost contrast & lift face midtones
    boosted = np.power(arr / 255.0, 0.55) * 255.0
    
    # Vignette
    h, w = arr.shape
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h * 0.46
    dist = np.sqrt(((X - cx) / (w * 0.46)) ** 2 + ((Y - cy) / (h * 0.48)) ** 2)
    mask = np.clip(1.0 - (dist - 0.7) / 0.3, 0, 1)

    clean = (boosted * mask).astype(np.uint8)
    
    # 44 dots wide x 48 dots high
    grid_w, grid_h = 44, 48
    small = Image.fromarray(clean).resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(small).enhance(1.4)
    dither = enh.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    arr_dith = np.array(dither)

    size = 220
    dx = size / grid_w
    dy = size / grid_h
    r = 1.6

    dots = []
    rows, cols = arr_dith.shape
    for r_idx in range(rows):
        for c_idx in range(cols):
            x = c_idx * dx + dx / 2
            y = r_idx * dy + dy / 2
            if arr_dith[r_idx, c_idx]:
                delay = round((r_idx / rows) * 0.8 + (c_idx / cols) * 0.2, 3)
                dots.append(
                    f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="#38bdf8">'
                    f'<animate attributeName="opacity" values="0;0.3;1" dur="0.8s" begin="{delay}s" fill="freeze"/>'
                    f'</circle>'
                )
            else:
                dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.7" fill="#1e293b" opacity="0.3"/>')

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <rect x="0" y="0" width="{size}" height="{size}" rx="10" fill="#090d16" stroke="#1e293b" stroke-width="1.2"/>
  
  <!-- Corner targeting brackets -->
  <path d="M 10 22 L 10 10 L 22 10" fill="none" stroke="#38bdf8" stroke-width="1.8"/>
  <path d="M {size - 22} 10 L {size - 10} 10 L {size - 10} 22" fill="none" stroke="#38bdf8" stroke-width="1.8"/>
  <path d="M 10 {size - 22} L 10 {size - 10} L 22 {size - 10}" fill="none" stroke="#38bdf8" stroke-width="1.8"/>
  <path d="M {size - 22} {size - 10} L {size - 10} {size - 10} L {size - 10} {size - 22}" fill="none" stroke="#38bdf8" stroke-width="1.8"/>

  <!-- Dot Matrix -->
  <g transform="translate(0, 0)">
    {''.join(dots)}
  </g>

  <!-- Laser sweep scanline -->
  <line x1="10" y1="12" x2="{size - 10}" y2="12" stroke="#00f5ff" stroke-width="1.5" opacity="0.7">
    <animate attributeName="y1" values="12;{size - 12};12" dur="3.5s" repeatCount="indefinite" begin="0.8s"/>
    <animate attributeName="y2" values="12;{size - 12};12" dur="3.5s" repeatCount="indefinite" begin="0.8s"/>
  </line>
</svg>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated dot matrix avatar at {OUT_FILE}")

if __name__ == "__main__":
    make_ascii_avatar()
