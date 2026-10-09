#!/usr/bin/env python3
"""
generate_decrypt_hero.py - Generates Cryptographic Decrypt / Encrypt Fragment Hero SVG
- Unpacks / decrypts puzzle fragment voxels in pseudo-random bursts across the image.
- Decrypts into the pristine real portrait of Delight.
- Re-encrypts and fragments back into the Titanium Silver / Liquid Metal ASCII dot matrix.
- Clean wipe: Zero leftover ASCII particles when decrypted.
"""

import base64
from io import BytesIO
import random
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_SRC = BASE_DIR / "assets" / "source" / "portrait.jpg"
OUT_V4 = BASE_DIR / "assets" / "header-scanner.v4.svg"
OUT_LEGACY = BASE_DIR / "assets" / "header-portrait.svg"

def make_decrypt_hero():
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
                matrix_dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="0.70" fill="#1e293b" opacity="0.25"/>')

    dots_content = "\n      ".join(matrix_dots)

    # ==================== CRYPTOGRAPHIC PUZZLE / FRAGMENT CLIPS ====================
    # 10x10 = 100 tiles
    cols, rows = 10, 10
    tile_w = size / cols
    tile_h = size / rows

    # Deterministic pseudo-random seed for repeatable, natural-looking cryptographic reveal
    rng = random.Random(2026)
    indices = list(range(cols * rows))
    
    # Shuffle for decryption sequence
    decrypt_order = indices.copy()
    rng.shuffle(decrypt_order)
    
    # Shuffle for encryption sequence (different pattern)
    encrypt_order = indices.copy()
    rng.shuffle(encrypt_order)

    dur = 7.5 # seconds total loop

    # Timeline benchmarks in seconds:
    # 0.0s - 1.2s: Full ASCII matrix (stable)
    # 1.2s - 3.4s: Decrypting (fragments unpacking across image)
    # 3.4s - 4.8s: Full Real Photo (stable, pristine, 0 particles)
    # 4.8s - 6.8s: Encrypting (fragments re-scrambling back into ASCII)
    # 6.8s - 7.5s: Full ASCII matrix (stable)

    photo_clips = []
    ascii_clips = []

    for idx in range(cols * rows):
        c = idx % cols
        r_idx = idx // cols
        x0 = c * tile_w
        y0 = r_idx * tile_h
        tcx = x0 + tile_w / 2
        tcy = y0 + tile_h / 2

        # Decrypt timing
        dec_rank = decrypt_order.index(idx)
        dec_frac = dec_rank / (cols * rows - 1)
        t_dec_start = 1.1 + dec_frac * 1.5   # 1.1s to 2.6s
        t_dec_end = t_dec_start + 0.45       # 1.55s to 3.05s

        # Encrypt timing
        enc_rank = encrypt_order.index(idx)
        enc_frac = enc_rank / (cols * rows - 1)
        t_enc_start = 4.8 + enc_frac * 1.4   # 4.8s to 6.2s
        t_enc_end = t_enc_start + 0.45       # 5.25s to 6.65s

        # Normalized keyTimes:
        kt0 = 0.0
        kt1 = round(t_dec_start / dur, 3)
        kt2 = round(t_dec_end / dur, 3)
        kt3 = round(t_enc_start / dur, 3)
        kt4 = round(t_enc_end / dur, 3)
        kt5 = 1.0

        key_times_str = f"{kt0}; {kt1}; {kt2}; {kt3}; {kt4}; {kt5}"

        # Photo tile: starts at 0, expands to full, stays full, collapses to 0, stays 0
        photo_x = f"{tcx:.1f}; {tcx:.1f}; {x0:.1f}; {x0:.1f}; {tcx:.1f}; {tcx:.1f}"
        photo_y = f"{tcy:.1f}; {tcy:.1f}; {y0:.1f}; {y0:.1f}; {tcy:.1f}; {tcy:.1f}"
        photo_w = f"0; 0; {tile_w:.1f}; {tile_w:.1f}; 0; 0"
        photo_h = f"0; 0; {tile_h:.1f}; {tile_h:.1f}; 0; 0"

        photo_rect = (
            f'<rect x="{tcx:.1f}" y="{tcy:.1f}" width="0" height="0">\n'
            f'        <animate attributeName="x" values="{photo_x}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'        <animate attributeName="y" values="{photo_y}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'        <animate attributeName="width" values="{photo_w}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'        <animate attributeName="height" values="{photo_h}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'      </rect>'
        )
        photo_clips.append(photo_rect)

        # ASCII tile: starts at full, collapses to 0, stays 0, expands to full, stays full
        ascii_x = f"{x0:.1f}; {x0:.1f}; {tcx:.1f}; {tcx:.1f}; {x0:.1f}; {x0:.1f}"
        ascii_y = f"{y0:.1f}; {y0:.1f}; {tcy:.1f}; {tcy:.1f}; {y0:.1f}; {y0:.1f}"
        ascii_w = f"{tile_w:.1f}; {tile_w:.1f}; 0; 0; {tile_w:.1f}; {tile_w:.1f}"
        ascii_h = f"{tile_h:.1f}; {tile_h:.1f}; 0; 0; {tile_h:.1f}; {tile_h:.1f}"

        ascii_rect = (
            f'<rect x="{x0:.1f}" y="{y0:.1f}" width="{tile_w:.1f}" height="{tile_h:.1f}">\n'
            f'        <animate attributeName="x" values="{ascii_x}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'        <animate attributeName="y" values="{ascii_y}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'        <animate attributeName="width" values="{ascii_w}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'        <animate attributeName="height" values="{ascii_h}" keyTimes="{key_times_str}" dur="{dur}s" repeatCount="indefinite"/>\n'
            f'      </rect>'
        )
        ascii_clips.append(ascii_rect)

    photo_clips_content = "\n      ".join(photo_clips)
    ascii_clips_content = "\n      ".join(ascii_clips)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <!-- Multi-Tile Decryption ClipPath for Real Photo: Unpacks fragments outward -->
    <clipPath id="decryptPhotoClip">
      {photo_clips_content}
    </clipPath>

    <!-- Multi-Tile Encryption ClipPath for Titanium ASCII Matrix: Collapses fragments inward -->
    <clipPath id="encryptAsciiClip">
      {ascii_clips_content}
    </clipPath>

    <!-- Warm backlight radial glow matching Delight's jacket & rim lighting -->
    <radialGradient id="decryptBackglow" cx="50%" cy="48%" r="50%">
      <stop offset="0%" stop-color="#ef4444" stop-opacity="0.28"/>
      <stop offset="50%" stop-color="#f59e0b" stop-opacity="0.10"/>
      <stop offset="100%" stop-color="#090d16" stop-opacity="0"/>
    </radialGradient>
  </defs>

  <!-- Ambient Glowing Aura Behind Subject -->
  <circle cx="{cx}" cy="{cy}" r="{size / 2}" fill="url(#decryptBackglow)">
    <animate attributeName="r" values="{size * 0.44};{size * 0.50};{size * 0.44}" dur="4s" repeatCount="indefinite"/>
  </circle>

  <!-- LAYER 1: Titanium Silver / Liquid Metal ASCII Matrix (Clipped out completely when decrypted) -->
  <g clip-path="url(#encryptAsciiClip)">
    {dots_content}
  </g>

  <!-- LAYER 2: Original Real Photo (Cryptographically Assembled via Fragment Tiles) -->
  <g clip-path="url(#decryptPhotoClip)">
    <image xlink:href="data:image/png;base64,{b64_photo}" x="0" y="0" width="{size}" height="{size}" preserveAspectRatio="xMidYMid meet"/>
  </g>

  <!-- Subtle Cybernetic Targeting Reticles at Corners -->
  <g opacity="0.6">
    <path d="M 12 24 L 12 12 L 24 12" fill="none" stroke="#94a3b8" stroke-width="1.4"/>
    <path d="M {size - 24} 12 L {size - 12} 12 L {size - 12} 24" fill="none" stroke="#94a3b8" stroke-width="1.4"/>
    <path d="M 12 {size - 24} L 12 {size - 12} L 24 {size - 12}" fill="none" stroke="#94a3b8" stroke-width="1.4"/>
    <path d="M {size - 24} {size - 12} L {size - 12} {size - 12} L {size - 12} {size - 24}" fill="none" stroke="#94a3b8" stroke-width="1.4"/>
  </g>
</svg>"""

    for p in [OUT_V4, OUT_LEGACY]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {p.name} ({len(svg) / 1024:.1f} KB)")

if __name__ == "__main__":
    make_decrypt_hero()
