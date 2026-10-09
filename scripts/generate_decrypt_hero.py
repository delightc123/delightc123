#!/usr/bin/env python3
"""
generate_decrypt_hero.py - Generates Cryptographic Decrypt / Encrypt Fragment Hero SVG
- Unpacks / decrypts puzzle fragment voxels in pseudo-random bursts across the image.
- Decrypts into the pristine real portrait of Delight.
- Re-encrypts and fragments back into the Titanium Silver / Liquid Metal ASCII dot matrix.
- Clean wipe: Zero leftover ASCII particles when decrypted.
- Optical Camera Autofocus Lens: Corner focus reticles pull in and zoom outward, snapping into target lock during ASCII encryption, and smoothly settling during decryption.
"""

import base64
from io import BytesIO
import random
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_SRC = BASE_DIR / "assets" / "source" / "portrait.jpg"
OUT_V5 = BASE_DIR / "assets" / "header-scanner.v5.svg"
OUT_LEGACY = BASE_DIR / "assets" / "header-portrait.svg"

def make_decrypt_hero():
    size = 420
    im = Image.open(PORTRAIT_SRC).convert("RGB")
    
    # Crop to capture full head + upper chest and red studded jacket (1280x1280 source)
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
    cols, rows = 10, 10
    tile_w = size / cols
    tile_h = size / rows

    rng = random.Random(2026)
    indices = list(range(cols * rows))
    decrypt_order = indices.copy()
    rng.shuffle(decrypt_order)
    encrypt_order = indices.copy()
    rng.shuffle(encrypt_order)

    dur = 7.5 # seconds total loop

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

        kt0 = 0.0
        kt1 = round(t_dec_start / dur, 3)
        kt2 = round(t_dec_end / dur, 3)
        kt3 = round(t_enc_start / dur, 3)
        kt4 = round(t_enc_end / dur, 3)
        kt5 = 1.0

        key_times_str = f"{kt0}; {kt1}; {kt2}; {kt3}; {kt4}; {kt5}"

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

    # ==================== OPTICAL CAMERA AUTOFOCUS LENS RETICLE ====================
    # Timeline:
    # 0.0s - 1.1s: ASCII state -> reticles locked at corners (0,0 offset)
    # 1.1s - 3.4s: Decrypting -> reticles stay smoothly locked at corners
    # 3.4s - 4.8s: Real photo -> reticles stay softly locked (opacity 0.45)
    # 4.8s - 5.3s: Encryption begins -> reticles contract inward (zoom-in pull)
    # 5.3s - 6.2s: Zoom-out snap! -> reticles expand outward and snap into corner lock
    # 6.2s - 7.5s: Locked on ASCII matrix (opacity 0.85)

    lens_kt = "0; 0.147; 0.453; 0.640; 0.707; 0.827; 1"
    
    # Offsets for each corner (dx, dy):
    # Top-Left (pulls toward center by +32,+32 then snaps to 0,0)
    tl_offsets = "0,0; 0,0; 0,0; 0,0; 32,32; 0,0; 0,0"
    # Top-Right (pulls toward center by -32,+32 then snaps to 0,0)
    tr_offsets = "0,0; 0,0; 0,0; 0,0; -32,32; 0,0; 0,0"
    # Bottom-Left (pulls toward center by +32,-32 then snaps to 0,0)
    bl_offsets = "0,0; 0,0; 0,0; 0,0; 32,-32; 0,0; 0,0"
    # Bottom-Right (pulls toward center by -32,-32 then snaps to 0,0)
    br_offsets = "0,0; 0,0; 0,0; 0,0; -32,-32; 0,0; 0,0"
    
    # Opacity pulse: subtle during photo, bright focus lock during ASCII snap
    lens_op = "0.75; 0.75; 0.45; 0.45; 0.95; 0.85; 0.75"

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

  <!-- LAYER 3: Optical Camera Autofocus Lens Reticles (Snap into position during ASCII encryption) -->
  <g>
    <!-- Top-Left Focus Bracket -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="{tl_offsets}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.16 1 0.3 1; 0.25 0.1 0.25 1"/>
      <path d="M 14 30 L 14 14 L 30 14" fill="none" stroke="#cbd5e1" stroke-width="1.8" stroke-linecap="round">
        <animate attributeName="opacity" values="{lens_op}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite"/>
      </path>
    </g>

    <!-- Top-Right Focus Bracket -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="{tr_offsets}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.16 1 0.3 1; 0.25 0.1 0.25 1"/>
      <path d="M {size - 30} 14 L {size - 14} 14 L {size - 14} 30" fill="none" stroke="#cbd5e1" stroke-width="1.8" stroke-linecap="round">
        <animate attributeName="opacity" values="{lens_op}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite"/>
      </path>
    </g>

    <!-- Bottom-Left Focus Bracket -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="{bl_offsets}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.16 1 0.3 1; 0.25 0.1 0.25 1"/>
      <path d="M 14 {size - 30} L 14 {size - 14} L 30 {size - 14}" fill="none" stroke="#cbd5e1" stroke-width="1.8" stroke-linecap="round">
        <animate attributeName="opacity" values="{lens_op}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite"/>
      </path>
    </g>

    <!-- Bottom-Right Focus Bracket -->
    <g>
      <animateTransform attributeName="transform" type="translate" values="{br_offsets}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite" calcMode="spline" keySplines="0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.25 0.1 0.25 1; 0.16 1 0.3 1; 0.25 0.1 0.25 1"/>
      <path d="M {size - 30} {size - 14} L {size - 14} {size - 14} L {size - 14} {size - 30}" fill="none" stroke="#cbd5e1" stroke-width="1.8" stroke-linecap="round">
        <animate attributeName="opacity" values="{lens_op}" keyTimes="{lens_kt}" dur="{dur}s" repeatCount="indefinite"/>
      </path>
    </g>

    <!-- Subtle Optical Autofocus Range Ticks -->
    <g opacity="0.4">
      <line x1="{cx - 12}" y1="14" x2="{cx + 12}" y2="14" stroke="#94a3b8" stroke-width="1"/>
      <line x1="{cx - 12}" y1="{size - 14}" x2="{cx + 12}" y2="{size - 14}" stroke="#94a3b8" stroke-width="1"/>
      <line x1="14" y1="{cy - 12}" x2="14" y2="{cy + 12}" stroke="#94a3b8" stroke-width="1"/>
      <line x1="{size - 14}" y1="{cy - 12}" x2="{size - 14}" y2="{cy + 12}" stroke="#94a3b8" stroke-width="1"/>
    </g>
  </g>
</svg>"""

    for p in [OUT_V5, OUT_LEGACY]:
        with open(p, "w", encoding="utf-8") as f:
            f.write(svg)
        print(f"Generated {p.name} ({len(svg) / 1024:.1f} KB)")

if __name__ == "__main__":
    make_decrypt_hero()
