#!/usr/bin/env python3
"""
generate_gargi_header.py - Generates Gargi Bhardwaj-style animated 3D roll-up hero banner
Uses Delight's new photo (5956540644060761474_121.jpg) with soft vignette and SVG roll-up clipPath.
"""

import base64
from io import BytesIO
from pathlib import Path
from PIL import Image, ImageOps
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent
PORTRAIT_SRC = BASE_DIR / "assets" / "source" / "portrait.jpg"
OUT_SVG = BASE_DIR / "assets" / "header-gargi.svg"

def process_portrait(src_path):
    im = Image.open(src_path).convert("RGB")
    # Delight is centered-left in 1280x1280.
    # Crop head and upper jacket (from x: 140 to 1140, y: 50 to 1050)
    crop = im.crop((160, 60, 1140, 1040)) # 980x980
    resized = crop.resize((480, 480), Image.Resampling.LANCZOS)
    w, h = resized.size

    # Create smooth radial/elliptical vignette mask so dark edges fade to transparent
    arr = np.array(resized, dtype=float)
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h * 0.46
    # Distance from center
    dist = np.sqrt(((X - cx) / (w * 0.46)) ** 2 + ((Y - cy) / (h * 0.48)) ** 2)
    # Mask: 1 in center, decays to 0 at edges
    alpha = np.clip(1.0 - (dist - 0.65) / 0.35, 0, 1)

    # Convert to RGBA
    rgba = np.zeros((h, w, 4), dtype=np.uint8)
    rgba[:, :, :3] = np.clip(arr, 0, 255).astype(np.uint8)
    rgba[:, :, 3] = (alpha * 255).astype(np.uint8)

    img_out = Image.fromarray(rgba, "RGBA")
    buf = BytesIO()
    img_out.save(buf, format="PNG", optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("utf-8")
    print(f"Processed portrait PNG base64 size: {len(b64) / 1024:.1f} KB")
    return b64

def make_header():
    b64_img = process_portrait(PORTRAIT_SRC)

    w, h = 880, 430
    cx = w / 2

    # Portrait dimensions inside banner
    p_w, p_h = 240, 240
    p_x = cx - p_w / 2
    p_y = 50

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="100%" height="100%">
  <defs>
    <!-- Gargi roll-up clipPath: animated reveal from bottom to top -->
    <clipPath id="headerRollup">
      <rect x="{p_x}" y="{p_y + p_h}" width="{p_w}" height="0">
        <animate attributeName="y" values="{p_y + p_h};{p_y}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
        <animate attributeName="height" values="0;{p_h}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      </rect>
    </clipPath>

    <!-- Warm backlight radial gradient matching Delight's jacket & rim lighting -->
    <radialGradient id="portraitAura" cx="50%" cy="45%" r="50%">
      <stop offset="0%" stop-color="#ef4444" stop-opacity="0.32"/>
      <stop offset="45%" stop-color="#f59e0b" stop-opacity="0.14"/>
      <stop offset="100%" stop-color="#090d16" stop-opacity="0"/>
    </radialGradient>

    <!-- Button subtle gradients -->
    <linearGradient id="btnLinkedin" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#0a66c2"/>
      <stop offset="100%" stop-color="#0284c7"/>
    </linearGradient>
    <linearGradient id="btnTwitter" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#18181b"/>
      <stop offset="100%" stop-color="#27272a"/>
    </linearGradient>
    <linearGradient id="btnInsta" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#f43f5e"/>
      <stop offset="50%" stop-color="#ec4899"/>
      <stop offset="100%" stop-color="#8b5cf6"/>
    </linearGradient>
    <linearGradient id="btnYoutube" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#dc2626"/>
      <stop offset="100%" stop-color="#ef4444"/>
    </linearGradient>
    <linearGradient id="btnEmail" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#ea4335"/>
      <stop offset="100%" stop-color="#f87171"/>
    </linearGradient>
    <linearGradient id="btnPortfolio" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="#10b981"/>
      <stop offset="100%" stop-color="#059669"/>
    </linearGradient>
  </defs>

  <style>
    .mono {{ font-family: 'SF Mono', 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace; }}
    .name-text {{ font-size: 20px; font-weight: 800; fill: #4ade80; letter-spacing: 0.5px; }}
    .role-text {{ font-size: 12.5px; font-weight: 600; fill: #94a3b8; }}
    .btn-text {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; font-size: 10px; font-weight: 700; fill: #ffffff; letter-spacing: 0.5px; }}
    .badge-view {{ font-family: monospace; font-size: 9.5px; font-weight: 700; }}
  </style>

  <!-- Container Box -->
  <rect x="0" y="0" width="{w}" height="{h}" rx="12" fill="#090d16" stroke="#1e293b" stroke-width="1.2"/>

  <!-- Top Terminal Header Bar -->
  <rect x="0" y="0" width="{w}" height="36" rx="12" fill="#0f172a"/>
  <rect x="0" y="26" width="{w}" height="10" fill="#0f172a"/>
  <line x1="0" y1="36" x2="{w}" y2="36" stroke="#1e293b" stroke-width="1"/>

  <!-- Window Dots -->
  <circle cx="20" cy="18" r="5" fill="#ef4444"/>
  <circle cx="36" cy="18" r="5" fill="#f59e0b"/>
  <circle cx="52" cy="18" r="5" fill="#10b981"/>

  <!-- Terminal Window Title -->
  <text x="72" y="22" class="mono" font-size="11.5" font-weight="600" fill="#64748b">delightc123/README.md</text>

  <!-- Live Status Badge -->
  <g transform="translate({w - 110}, 11)">
    <rect x="0" y="0" width="92" height="15" rx="3" fill="#10b981" fill-opacity="0.12" stroke="#10b981" stroke-width="0.8"/>
    <circle cx="9" cy="7.5" r="3" fill="#10b981">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.4s" repeatCount="indefinite"/>
    </circle>
    <text x="18" y="11" class="mono" font-size="9" font-weight="700" fill="#10b981">SYS_ONLINE</text>
  </g>

  <!-- Center Ambient Glowing Aura Behind Portrait -->
  <circle cx="{cx}" cy="{p_y + p_h / 2}" r="150" fill="url(#portraitAura)">
    <animate attributeName="r" values="140;160;140" dur="4s" repeatCount="indefinite"/>
  </circle>

  <!-- Animated Roll-Up Portrait -->
  <g clip-path="url(#headerRollup)">
    <image xlink:href="data:image/png;base64,{b64_img}" x="{p_x}" y="{p_y}" width="{p_w}" height="{p_h}" preserveAspectRatio="xMidYMid meet"/>
    
    <!-- Neon reveal laser sweeping upwards with unroll -->
    <line x1="{p_x}" y1="{p_y + p_h}" x2="{p_x + p_w}" y2="{p_y + p_h}" stroke="#ef4444" stroke-width="2.5" opacity="0.9">
      <animate attributeName="y1" values="{p_y + p_h};{p_y}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      <animate attributeName="y2" values="{p_y + p_h};{p_y}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      <animate attributeName="opacity" values="0.9;0.9;0" keyTimes="0;0.9;1" dur="1.8s" fill="freeze"/>
    </line>
  </g>

  <!-- Name: Gargi Green Monospace -->
  <text x="{cx}" y="318" text-anchor="middle" class="mono name-text">Delight Chukwubuihem</text>
  
  <!-- Subtitle -->
  <text x="{cx}" y="338" text-anchor="middle" class="mono role-text">Chief Systems Architect &amp; Founder @Auscera Tech Ltd</text>

  <!-- Gargi Style Horizontal Button Badges Row -->
  <g transform="translate({cx}, 365)">
    <!-- Total width ~ 580px, centered around 0 -->
    <!-- Button 1: LinkedIn -->
    <a xlink:href="https://www.linkedin.com/in/delight-chukwubuihem-b4293b30a/" target="_blank">
      <g transform="translate(-275, 0)">
        <rect x="0" y="0" width="82" height="22" rx="4" fill="url(#btnLinkedin)"/>
        <text x="41" y="15" text-anchor="middle" class="btn-text">LINKEDIN</text>
      </g>
    </a>

    <!-- Button 2: Twitter / X -->
    <a xlink:href="https://x.com/delightchukwu_" target="_blank">
      <g transform="translate(-185, 0)">
        <rect x="0" y="0" width="78" height="22" rx="4" fill="url(#btnTwitter)" stroke="#3f3f46" stroke-width="0.8"/>
        <text x="39" y="15" text-anchor="middle" class="btn-text">X / TWITTER</text>
      </g>
    </a>

    <!-- Button 3: Instagram -->
    <a xlink:href="https://instagram.com/delightchukwu_" target="_blank">
      <g transform="translate(-99, 0)">
        <rect x="0" y="0" width="86" height="22" rx="4" fill="url(#btnInsta)"/>
        <text x="43" y="15" text-anchor="middle" class="btn-text">INSTAGRAM</text>
      </g>
    </a>

    <!-- Button 4: YouTube -->
    <a xlink:href="https://www.youtube.com/@delight_chukwu" target="_blank">
      <g transform="translate(-5, 0)">
        <rect x="0" y="0" width="78" height="22" rx="4" fill="url(#btnYoutube)"/>
        <text x="39" y="15" text-anchor="middle" class="btn-text">YOUTUBE</text>
      </g>
    </a>

    <!-- Button 5: Email -->
    <a xlink:href="mailto:delightene8@gmail.com" target="_blank">
      <g transform="translate(81, 0)">
        <rect x="0" y="0" width="72" height="22" rx="4" fill="url(#btnEmail)"/>
        <text x="36" y="15" text-anchor="middle" class="btn-text">EMAIL</text>
      </g>
    </a>

    <!-- Button 6: Portfolio -->
    <a xlink:href="https://delightchukwubuihem.com" target="_blank">
      <g transform="translate(161, 0)">
        <rect x="0" y="0" width="86" height="22" rx="4" fill="url(#btnPortfolio)"/>
        <text x="43" y="15" text-anchor="middle" class="btn-text">PORTFOLIO</text>
      </g>
    </a>
  </g>

  <!-- Bottom System Status Line -->
  <line x1="20" y1="404" x2="{w - 20}" y2="404" stroke="#1e293b" stroke-width="0.8"/>
  <text x="24" y="420" class="mono" font-size="9" fill="#64748b">SYS_ID: 0xAUSCERA-DLG • SPECIALIZATION: AUTONOMOUS AGENT OS • DISCOVERY: ACTIVE</text>
  <text x="{w - 24}" y="420" text-anchor="end" class="mono" font-size="9" fill="#4ade80">● KERNEL: BWA-v2.6 ONLINE</text>
</svg>"""

    with open(OUT_SVG, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated Gargi-style animated header at {OUT_SVG} ({len(svg) / 1024:.1f} KB)")

if __name__ == "__main__":
    make_header()
