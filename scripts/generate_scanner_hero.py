#!/usr/bin/env python3
"""
generate_scanner_hero.py - Generates cybernetic scanner hero SVG
Transitions smoothly between Titanium Liquid Metal ASCII and the full original photo of Delight:
- As laser sweeps UP: reveals the full original image and clips out all ASCII particles.
- At the top: 100% clean photo, zero leftover particles around head/silhouette.
- As laser sweeps DOWN: wipes back into the Titanium Silver / Liquid Metal ASCII format.
- Palette: Polished titanium silver (#f8fafc, #e2e8f0, #cbd5e1, #94a3b8) with chrome liquid highlights.
"""

import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_SRC = BASE_DIR / "assets" / "source" / "portrait.jpg"
OUT_V3 = BASE_DIR / "assets" / "header-scanner.v3.svg"
OUT_LEGACY = BASE_DIR / "assets" / "header-portrait.svg"

def make_scanner_svg():
    size = 420
    im = Image.open(PORTRAIT_SRC).convert("RGB")
    
    # Crop to capture full head + upper chest and red studded jacket
    # Image is 1280x1280
    crop = im.crop((100, 40, 1180, 1120)) # 1080x1080
    resized = crop.resize((size, size), Image.Resampling.LANCZOS)
    w, h = resized.size

    # Soft circular/elliptical feather around edges so black background blends seamlessly
    arr = np.array(resized, dtype=float)
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h * 0.48
    dist = np.sqrt(((X - cx) / (w * 0.48)) ** 2 + ((Y - cy) / (h * 0.49)) ** 2)
    alpha = np.clip(1.0 - (dist - 0.72) / 0.28, 0, 1)

    # Real Photo Layer (Base64 PNG)
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.clip(arr, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

    img_out = Image.fromarray(rgba, "RGBA")
    buf = BytesIO()
    img_out.save(buf, format="PNG", optimize=True)
    b64_photo = base64.b64encode(buf.getvalue()).decode("utf-8")

    # Generate Titanium Silver / Liquid Metal Dot Matrix
    gray = ImageOps.grayscale(resized)
    gray_arr = np.array(gray, dtype=float)
    boosted = np.power(gray_arr / 255.0, 0.48) * 255.0
    
    grid_w, grid_h = 58, 58
    small = Image.fromarray(boosted.astype(np.uint8)).resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    enh = ImageEnhance.Contrast(small).enhance(1.35)
    dither = enh.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    arr_dith = np.array(dither)
    small_arr = np.array(small)

    dx = size / grid_w
    dy = size / grid_h
    r = 1.65

    matrix_dots = []
    for r_idx in range(grid_h):
        for c_idx in range(grid_w):
            x = c_idx * dx + dx / 2
            y = r_idx * dy + dy / 2
            norm_dist = np.sqrt(((x - cx) / (w * 0.48)) ** 2 + ((y - cy) / (h * 0.49)) ** 2)
            if norm_dist > 1.0:
                continue

            if arr_dith[r_idx, c_idx]:
                lum = small_arr[r_idx, c_idx]
                # Titanium Silver / Liquid Metal Shading
                if lum > 175:
                    dot_color = "#ffffff"       # Specular liquid chrome reflection
                    dot_r = r + 0.15
                elif lum > 115:
                    dot_color = "#e2e8f0"       # High-polish titanium silver
                    dot_r = r
                else:
                    dot_color = "#94a3b8"       # Brushed titanium grey
                    dot_r = r - 0.2
                matrix_dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{dot_r:.2f}" fill="{dot_color}"/>')
            else:
                # Faint dark steel background dot
                matrix_dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.70" fill="#1e293b" opacity="0.25"/>')

    dots_content = "\n      ".join(matrix_dots)

    # 7-second synchronized loop:
    # 0s -> 2.5s (0% -> 36%): Laser sweeps UP (420 -> 0).
    #   Photo rect expands (y: 420 -> 0, height: 0 -> 420)
    #   ASCII rect height shrinks (420 -> 0) -> wipes OUT all ASCII particles!
    # 2.5s -> 3.5s (36% -> 50%): Pause at top.
    #   Photo is 100% visible.
    #   ASCII rect height is 0 -> 0 particles visible!
    # 3.5s -> 6.0s (50% -> 86%): Laser sweeps DOWN (0 -> 420).
    #   Photo rect shrinks (y: 0 -> 420, height: 420 -> 0)
    #   ASCII rect height expands (0 -> 420) -> wipes back into liquid metal ASCII!
    # 6.0s -> 7.0s (86% -> 100%): Pause at bottom.
    #   Full liquid metal ASCII visible.
    
    splines = "0.25 0.1 0.25 1; 0 0 1 1; 0.25 0.1 0.25 1; 0 0 1 1"
    key_times = "0; 0.36; 0.50; 0.86; 1"
    
    # Laser position Y:
    laser_y_vals = f"{size}; 0; 0; {size}; {size}"
    laser_op_vals = "0.9; 0.9; 0.2; 0.9; 0.2"
    
    # Photo clip rect (reveals below laser):
    photo_y_vals = f"{size}; 0; 0; {size}; {size}"
    photo_h_vals = f"0; {size}; {size}; 0; 0"

    # ASCII clip rect (reveals above laser, completely clips out when laser reaches top):
    ascii_h_vals = f"{size}; 0; 0; {size}; {size}"

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <!-- Wipe ClipPath for Real Photo: reveals below the laser line -->
    <clipPath id="scannerPhotoWipe">
      <rect x="0" y="{size}" width="{size}" height="0">
        <animate attributeName="y" values="{photo_y_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
        <animate attributeName="height" values="{photo_h_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
      </rect>
    </clipPath>

    <!-- Wipe ClipPath for Titanium ASCII Matrix: wipes OUT as laser moves up, completely hiding all particles at top -->
    <clipPath id="scannerAsciiWipe">
      <rect x="0" y="0" width="{size}" height="{size}">
        <animate attributeName="height" values="{ascii_h_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
      </rect>
    </clipPath>

    <!-- Warm backlight radial glow matching Delight's jacket & rim lighting -->
    <radialGradient id="scannerBackglow" cx="50%" cy="48%" r="50%">
      <stop offset="0%" stop-color="#ef4444" stop-opacity="0.28"/>
      <stop offset="50%" stop-color="#f59e0b" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#090d16" stop-opacity="0"/>
    </radialGradient>

    <!-- Liquid Silver Laser Beam Glow Filter -->
    <filter id="silverBloom" x="-20%" y="-100%" width="140%" height="300%">
      <feGaussianBlur stdDeviation="2.5" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Ambient Glowing Aura Behind Subject -->
  <circle cx="{cx}" cy="{cy}" r="{size / 2}" fill="url(#scannerBackglow)">
    <animate attributeName="r" values="{size * 0.44};{size * 0.50};{size * 0.44}" dur="4s" repeatCount="indefinite"/>
  </circle>

  <!-- LAYER 1: Titanium Silver / Liquid Metal ASCII Matrix (Clipped out completely when photo displays) -->
  <g clip-path="url(#scannerAsciiWipe)">
    {dots_content}
  </g>

  <!-- LAYER 2: Original Real Photo (Revealed/Masked by Laser Scanner) -->
  <g clip-path="url(#scannerPhotoWipe)">
    <image xlink:href="data:image/png;base64,{b64_photo}" x="0" y="0" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- LAYER 3: Liquid Titanium / Chrome Laser Scanner Line -->
  <g filter="url(#silverBloom)">
    <!-- Outer Silver Sheen Beam -->
    <line x1="8" y1="{size}" x2="{size - 8}" y2="{size}" stroke="#cbd5e1" stroke-width="2.5" opacity="0.85">
      <animate attributeName="y1" values="{laser_y_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
      <animate attributeName="y2" values="{laser_y_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
      <animate attributeName="opacity" values="{laser_op_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite"/>
    </line>

    <!-- Core Brilliant Chrome / Specular White Beam -->
    <line x1="16" y1="{size}" x2="{size - 16}" y2="{size}" stroke="#ffffff" stroke-width="1.2" opacity="0.95">
      <animate attributeName="y1" values="{laser_y_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
      <animate attributeName="y2" values="{laser_y_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite" calcMode="spline" keySplines="{splines}"/>
      <animate attributeName="opacity" values="{laser_op_vals}" keyTimes="{key_times}" dur="7s" repeatCount="indefinite"/>
    </line>
  </g>
</svg>"""

    for out_path in [OUT_V3, OUT_LEGACY]:
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {out_path.name} ({len(svg) / 1024:.1f} KB)")

if __name__ == "__main__":
    make_scanner_svg()
