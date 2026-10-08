#!/usr/bin/env python3
"""
generate_standalone_portrait.py - Generates isolated animated 3D roll-up portrait SVG
NO banner container, NO Mac window chrome, NO text, NO buttons.
JUST the animated roll-up portrait of Delight with warm rim lighting.
"""

import base64
from io import BytesIO
from pathlib import Path
from PIL import Image
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_SRC = BASE_DIR / "assets" / "source" / "portrait.jpg"
OUT_SVG = BASE_DIR / "assets" / "header-portrait.svg"

def process_image(src_path, target_size=(440, 440)):
    im = Image.open(src_path).convert("RGB")
    # Delight centered-left in 1280x1280. Crop head, face, earring, collar
    crop = im.crop((180, 80, 1100, 1000))
    resized = crop.resize(target_size, Image.Resampling.LANCZOS)
    w, h = resized.size

    arr = np.array(resized, dtype=float)
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h * 0.48
    dist = np.sqrt(((X - cx) / (w * 0.46)) ** 2 + ((Y - cy) / (h * 0.48)) ** 2)
    # Smooth alpha feathering towards edges
    alpha = np.clip(1.0 - (dist - 0.70) / 0.30, 0, 1)

    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.clip(arr, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

    img_out = Image.fromarray(rgba, "RGBA")
    buf = BytesIO()
    img_out.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    return b64

def make_svg():
    b64_img = process_image(PORTRAIT_SRC, target_size=(440, 440))
    size = 320
    cx, cy = size / 2, size / 2

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <!-- Animated roll-up clipPath: reveals from bottom to top -->
    <clipPath id="portraitRollup">
      <rect x="0" y="{size}" width="{size}" height="0">
        <animate attributeName="y" values="{size};0" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
        <animate attributeName="height" values="0;{size}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      </rect>
    </clipPath>

    <!-- Warm backlight radial glow matching Delight's jacket & rim lighting -->
    <radialGradient id="backglow" cx="50%" cy="48%" r="50%">
      <stop offset="0%" stop-color="#ef4444" stop-opacity="0.30"/>
      <stop offset="50%" stop-color="#f59e0b" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="#090d16" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Ambient Glowing Aura Behind Subject -->
  <circle cx="{cx}" cy="{cy}" r="{size / 2}" fill="url(#backglow)">
    <animate attributeName="r" values="{size * 0.44};{size * 0.50};{size * 0.44}" dur="4s" repeatCount="indefinite"/>
  </circle>

  <!-- Animated Roll-Up Portrait (Isolated Image Only) -->
  <g clip-path="url(#portraitRollup)">
    <image xlink:href="data:image/png;base64,{b64_img}" x="0" y="0" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet"/>
    
    <!-- Neon reveal laser sweeping upwards with unroll -->
    <line x1="10" y1="{size}" x2="{size - 10}" y2="{size}" stroke="#ef4444" stroke-width="2.5" opacity="0.9">
      <animate attributeName="y1" values="{size};0" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      <animate attributeName="y2" values="{size};0" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      <animate attributeName="opacity" values="0.9;0.9;0" keyTimes="0;0.9;1" dur="1.8s" fill="freeze"/>
    </line>
  </g>
</svg>"""

    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated standalone roll-up portrait SVG at {OUT_SVG} ({len(svg) / 1024:.1f} KB)")

if __name__ == "__main__":
    make_svg()
