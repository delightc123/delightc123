#!/usr/bin/env python3
"""
generate_rollup.py - Generates Gargi-style animated roll-up portrait SVG
Uses SVG clipPath <animate> to create the signature bottom-to-top unroll reveal.
"""

import base64
from io import BytesIO
from pathlib import Path
from PIL import Image

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_IMG = BASE_DIR / "assets" / "source" / "me_cropped.png"
OUT_FILE = BASE_DIR / "assets" / "portrait-rollup.svg"

def make_rollup():
    img = Image.open(SOURCE_IMG).convert("RGB")
    # Resize to crisp 360x360 for high PPI on retina displays
    img_resized = img.resize((360, 360), Image.Resampling.LANCZOS)
    
    buf = BytesIO()
    img_resized.save(buf, format="JPEG", quality=88)
    b64_data = base64.b64encode(buf.getvalue()).decode("utf-8")

    size = 280
    cx, cy = size / 2, size / 2
    r = 120

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {size} {size}" width="{size}" height="{size}">
  <defs>
    <!-- Circular clip for portrait -->
    <clipPath id="circleMask">
      <circle cx="{cx}" cy="{cy}" r="{r}"/>
    </clipPath>

    <!-- Gargi roll-up clipPath: animated from bottom to top -->
    <clipPath id="rollupMask">
      <rect x="0" y="{size}" width="{size}" height="0">
        <animate attributeName="y" values="{size};0" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
        <animate attributeName="height" values="0;{size}" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
      </rect>
    </clipPath>

    <!-- Neon rotating gradient ring -->
    <linearGradient id="orbitGlow" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8"/>
      <stop offset="50%" stop-color="#a855f7"/>
      <stop offset="100%" stop-color="#10b981"/>
    </linearGradient>

    <filter id="ringBloom" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Background halo -->
  <circle cx="{cx}" cy="{cy}" r="{r + 12}" fill="none" stroke="#1e293b" stroke-width="1.5" stroke-dasharray="4,4"/>

  <!-- Rotating Neon Orbit Ring -->
  <circle cx="{cx}" cy="{cy}" r="{r + 6}" fill="none" stroke="url(#orbitGlow)" stroke-width="2.5" filter="url(#ringBloom)">
    <animateTransform attributeName="transform" type="rotate" from="0 {cx} {cy}" to="360 {cx} {cy}" dur="10s" repeatCount="indefinite"/>
  </circle>

  <!-- Nested Masked Image: Circle Mask + Rollup Animation Mask -->
  <g clip-path="url(#circleMask)">
    <rect x="0" y="0" width="{size}" height="{size}" fill="#090d16"/>
    <g clip-path="url(#rollupMask)">
      <image href="data:image/jpeg;base64,{b64_data}" x="10" y="0" width="{size - 20}" height="{size}" preserveAspectRatio="xMidYMid slice"/>
      
      <!-- Cyan scan line traveling up with the reveal -->
      <line x1="0" y1="{size}" x2="{size}" y2="{size}" stroke="#00f5ff" stroke-width="3" opacity="0.9">
        <animate attributeName="y1" values="{size};0" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
        <animate attributeName="y2" values="{size};0" dur="1.8s" fill="freeze" calcMode="spline" keySplines="0.16 1 0.3 1"/>
        <animate attributeName="opacity" values="0.9;0.9;0" keyTimes="0;0.9;1" dur="1.8s" fill="freeze"/>
      </line>
    </g>
  </g>

  <!-- Status pill badge at bottom -->
  <g transform="translate({cx - 55}, {size - 22})">
    <rect x="0" y="0" width="110" height="20" rx="10" fill="#090d16" stroke="#38bdf8" stroke-width="1"/>
    <circle cx="12" cy="10" r="3.5" fill="#10b981">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.4s" repeatCount="indefinite"/>
    </circle>
    <text x="22" y="14" font-family="monospace" font-size="9" font-weight="700" fill="#f8fafc">FOUNDER/DEV</text>
  </g>
</svg>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated rollup portrait SVG at {OUT_FILE} ({len(svg) / 1024:.1f} KB)")

if __name__ == "__main__":
    make_rollup()
