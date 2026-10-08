#!/usr/bin/env python3
"""
generate.py - Generates viral cyberpunk terminal hero banner SVGs
Inspired by emmi-lili/emmi-lili and Gargi Bhardwaj.
Generates:
- assets/banner-dark.v1.svg
- assets/banner-light.v1.svg
- scripts/banner/data/portrait-dark.npy
- scripts/banner/data/portrait-light.npy
"""

import os
from pathlib import Path
from PIL import Image, ImageOps, ImageEnhance
import numpy as np

BASE_DIR = Path(__file__).resolve().parent.parent.parent
SOURCE_IMG = BASE_DIR / "assets" / "source" / "me.png"
DATA_DIR = BASE_DIR / "scripts" / "banner" / "data"
ASSETS_DIR = BASE_DIR / "assets"

DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)


def process_portrait(source_path, grid_w=52, grid_h=62):
    """
    Crops, normalizes, applies gamma lifting and Floyd-Steinberg dithering
    to create clean dot matrices for Delight's portrait.
    """
    img = Image.open(source_path).convert("RGB")
    # Crop head and upper shoulders (Delight centered with glasses & turtleneck)
    crop = img.crop((210, 110, 814, 830))
    gray = ImageOps.grayscale(crop)

    # 1. Dark Mode: Boost midtones so face and glasses pop on dark background
    arr = np.array(gray, dtype=float)
    boosted_dark = np.power(arr / 255.0, 0.58) * 255.0
    
    # Soft vignette to cleanly isolate subject
    h, w = arr.shape
    Y, X = np.ogrid[:h, :w]
    cx, cy = w / 2, h * 0.45
    dist = np.sqrt(((X - cx) / (w * 0.48)) ** 2 + ((Y - cy) / (h * 0.55)) ** 2)
    vignette = np.clip(1.0 - (dist - 0.78) / 0.22, 0, 1)
    
    clean_dark = (boosted_dark * vignette).astype(np.uint8)
    small_dark = Image.fromarray(clean_dark).resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    enh_dark = ImageEnhance.Contrast(small_dark).enhance(1.4)
    dither_dark = enh_dark.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    arr_dark = np.array(dither_dark)

    # 2. Light Mode: Inverted contrast for dark dots on light background
    inv_arr = 255.0 - boosted_dark
    clean_light = (inv_arr * vignette).astype(np.uint8)
    small_light = Image.fromarray(clean_light).resize((grid_w, grid_h), Image.Resampling.LANCZOS)
    enh_light = ImageEnhance.Contrast(small_light).enhance(1.3)
    dither_light = enh_light.convert("1", dither=Image.Dither.FLOYDSTEINBERG)
    arr_light = np.array(dither_light)

    np.save(DATA_DIR / "portrait-dark.npy", arr_dark)
    np.save(DATA_DIR / "portrait-light.npy", arr_light)
    print(f"Saved dot matrices: dark={np.sum(arr_dark == True)} dots, light={np.sum(arr_light == True)} dots")
    return arr_dark, arr_light


def generate_svg(mode="dark", arr=None):
    """
    Generates terminal SVG with:
    - Window chrome & controls
    - [ VISUAL.MAP ] dot-matrix holographic portrait with staggered SMIL reveal
    - Animated laser sweep scanner
    - [ SYSTEM.INFO ] terminal telemetry HUD with typewriter effects
    - Telemetry gauges and blinking cursor
    """
    is_dark = mode == "dark"

    # Theme palette
    if is_dark:
        bg_fill = "#090d16"
        card_border = "#1e293b"
        card_header_bg = "#0f172a"
        text_dim = "#64748b"
        text_light = "#94a3b8"
        text_bright = "#f8fafc"
        accent_cyan = "#38bdf8"
        accent_emerald = "#10b981"
        accent_violet = "#818cf8"
        accent_amber = "#f59e0b"
        dot_active = "#38bdf8"
        dot_inactive = "rgba(30, 41, 59, 0.45)"
        scan_color = "#00f5ff"
        meter_fill = "#0284c7"
        meter_bg = "#1e293b"
    else:
        bg_fill = "#f8fafc"
        card_border = "#cbd5e1"
        card_header_bg = "#f1f5f9"
        text_dim = "#64748b"
        text_light = "#475569"
        text_bright = "#0f172a"
        accent_cyan = "#0284c7"
        accent_emerald = "#059669"
        accent_violet = "#6366f1"
        accent_amber = "#d97706"
        dot_active = "#0f172a"
        dot_inactive = "rgba(203, 213, 225, 0.5)"
        scan_color = "#0284c7"
        meter_fill = "#0284c7"
        meter_bg = "#e2e8f0"

    svg_w, svg_h = 880, 360

    # Portrait grid parameters
    rows, cols = arr.shape
    p_x0, p_y0 = 36, 82
    p_w, p_h = 240, 235
    dx = p_w / cols
    dy = p_h / rows
    r = 1.45

    dots_svg = []
    # Staggered SMIL animation
    for r_idx in range(rows):
        for c_idx in range(cols):
            cx = p_x0 + c_idx * dx + dx / 2
            cy = p_y0 + r_idx * dy + dy / 2
            is_active = arr[r_idx, c_idx]
            
            if is_active:
                # Staggered reveal based on distance / scanline
                delay = round((r_idx / rows) * 0.9 + (c_idx / cols) * 0.25, 3)
                dot_el = (
                    f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{dot_active}">'
                    f'<animate attributeName="opacity" values="0;0.2;1" dur="0.8s" begin="{delay}s" fill="freeze"/>'
                    f'</circle>'
                )
                dots_svg.append(dot_el)
            else:
                # Faint background matrix dot for holographic CRT look
                dot_el = f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="0.8" fill="{dot_inactive}" opacity="0.35"/>'
                dots_svg.append(dot_el)

    dots_content = "\n      ".join(dots_svg)

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {svg_w} {svg_h}" width="100%" height="100%">
  <defs>
    <linearGradient id="scanGrad-{mode}" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="{scan_color}" stop-opacity="0"/>
      <stop offset="50%" stop-color="{scan_color}" stop-opacity="0.7"/>
      <stop offset="100%" stop-color="{scan_color}" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="headerGrad-{mode}" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" stop-color="{accent_cyan}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{accent_emerald}" stop-opacity="0.05"/>
    </linearGradient>
    <filter id="glow-{mode}" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="2" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <style>
    .mono {{ font-family: 'SF Mono', 'JetBrains Mono', 'Fira Code', Menlo, Consolas, monospace; }}
    .title-text {{ font-size: 12px; font-weight: 600; fill: {text_dim}; }}
    .hud-title {{ font-size: 11px; font-weight: 700; letter-spacing: 0.8px; }}
    .hud-label {{ font-size: 11px; font-weight: 600; fill: {text_dim}; }}
    .hud-val {{ font-size: 11px; font-weight: 500; fill: {text_bright}; }}
    .hud-cmd {{ font-size: 11px; font-weight: 600; fill: {accent_cyan}; }}
    .badge-text {{ font-size: 9.5px; font-weight: 700; }}
    .scan-line {{ stroke: {scan_color}; stroke-width: 1.5; opacity: 0.65; }}
  </style>

  <!-- Terminal Window Chrome -->
  <rect x="0" y="0" width="{svg_w}" height="{svg_h}" rx="10" fill="{bg_fill}" stroke="{card_border}" stroke-width="1.2"/>
  <rect x="0" y="0" width="{svg_w}" height="38" rx="10" fill="{card_header_bg}"/>
  <rect x="0" y="28" width="{svg_w}" height="10" fill="{card_header_bg}"/>
  <line x1="0" y1="38" x2="{svg_w}" y2="38" stroke="{card_border}" stroke-width="1"/>

  <!-- macOS Window Traffic Lights -->
  <circle cx="20" cy="19" r="5.5" fill="#ef4444"/>
  <circle cx="38" cy="19" r="5.5" fill="#f59e0b"/>
  <circle cx="56" cy="19" r="5.5" fill="#10b981"/>

  <!-- Terminal Header Title -->
  <text x="80" y="23" class="mono title-text">delight@auscera: ~ / profile.sh --live</text>
  
  <!-- Top Right Status Indicators -->
  <g transform="translate(680, 12)">
    <rect x="0" y="0" width="85" height="15" rx="3" fill="{accent_cyan}" fill-opacity="0.12" stroke="{accent_cyan}" stroke-width="0.8"/>
    <circle cx="9" cy="7.5" r="3" fill="{accent_cyan}">
      <animate attributeName="opacity" values="1;0.3;1" dur="1.8s" repeatCount="indefinite"/>
    </circle>
    <text x="18" y="11" class="mono badge-text" fill="{accent_cyan}">AGENT-OS v2.4</text>
  </g>
  <g transform="translate(775, 12)">
    <rect x="0" y="0" width="90" height="15" rx="3" fill="{accent_emerald}" fill-opacity="0.12" stroke="{accent_emerald}" stroke-width="0.8"/>
    <circle cx="9" cy="7.5" r="3" fill="{accent_emerald}">
      <animate attributeName="opacity" values="1;0.2;1" dur="1.2s" repeatCount="indefinite"/>
    </circle>
    <text x="18" y="11" class="mono badge-text" fill="{accent_emerald}">SYS_ONLINE</text>
  </g>

  <!-- ==================== LEFT COLUMN: VISUAL.MAP ==================== -->
  <g transform="translate(0, 0)">
    <text x="36" y="62" class="mono hud-title" fill="{accent_cyan}">┌── [ VISUAL.MAP: DELIGHT_CHUKWUBUIHEM ]</text>
    
    <!-- Matrix Outer Frame -->
    <rect x="34" y="76" width="244" height="243" rx="4" fill="none" stroke="{card_border}" stroke-dasharray="3,3"/>
    
    <!-- Corner Targeting Reticles -->
    <path d="M 34 88 L 34 76 L 46 76" fill="none" stroke="{accent_cyan}" stroke-width="2"/>
    <path d="M 266 76 L 278 76 L 278 88" fill="none" stroke="{accent_cyan}" stroke-width="2"/>
    <path d="M 34 307 L 34 319 L 46 319" fill="none" stroke="{accent_cyan}" stroke-width="2"/>
    <path d="M 266 319 L 278 319 L 278 307" fill="none" stroke="{accent_cyan}" stroke-width="2"/>

    <!-- Dot Matrix Representation of Delight -->
    <g>
      {dots_content}
    </g>

    <!-- Holographic Laser Scan Sweep -->
    <line x1="34" y1="78" x2="278" y2="78" class="scan-line" filter="url(#glow-{mode})">
      <animate attributeName="y1" values="78;315;78" dur="4.2s" repeatCount="indefinite" begin="0.8s"/>
      <animate attributeName="y2" values="78;315;78" dur="4.2s" repeatCount="indefinite" begin="0.8s"/>
      <animate attributeName="opacity" values="0.75;0.15;0.75" dur="4.2s" repeatCount="indefinite" begin="0.8s"/>
    </line>

    <!-- Matrix Footnote / Telemetry -->
    <text x="36" y="331" class="mono" font-size="9" fill="{text_dim}">TARGET_ID: 0xAUSCERA-DLG // BIOMETRIC_LOCKED</text>
  </g>

  <!-- ==================== VERTICAL SEPARATOR ==================== -->
  <line x1="298" y1="46" x2="298" y2="335" stroke="{card_border}" stroke-width="1" stroke-dasharray="2,3"/>

  <!-- ==================== RIGHT COLUMN: SYSTEM.INFO ==================== -->
  <g transform="translate(315, 0)">
    <!-- Header -->
    <text x="0" y="62" class="mono hud-title" fill="{accent_emerald}">┌── [ SYSTEM.TELEMETRY: HOST_KERNEL ]</text>
    
    <!-- Command Execution Line -->
    <g transform="translate(0, 82)">
      <text x="0" y="0" class="mono hud-cmd">> sys.inspect --architect delightc123 --verbose</text>
    </g>

    <!-- Metadata Fields with Typographic Hierarchy -->
    <g transform="translate(0, 102)">
      <text x="0" y="0" class="mono hud-label">ARCHITECT   :</text>
      <text x="110" y="0" class="mono hud-val" font-weight="700">Delight Chukwubuihem</text>
    </g>

    <g transform="translate(0, 120)">
      <text x="0" y="0" class="mono hud-label">ROLE        :</text>
      <text x="110" y="0" class="mono hud-val" fill="{accent_cyan}">Chief Systems Architect &amp; Founder</text>
    </g>

    <g transform="translate(0, 138)">
      <text x="0" y="0" class="mono hud-label">ORGANIZATION:</text>
      <text x="110" y="0" class="mono hud-val">Auscera Tech Ltd</text>
    </g>

    <g transform="translate(0, 156)">
      <text x="0" y="0" class="mono hud-label">CORE FOCUS  :</text>
      <text x="110" y="0" class="mono hud-val">Autonomous Agent OS • Systems Engineering • High-Scale Apps</text>
    </g>

    <g transform="translate(0, 174)">
      <text x="0" y="0" class="mono hud-label">CORE STACK  :</text>
      <text x="110" y="0" class="mono hud-val">TypeScript • Python • Rust • C# • Go • GLSL • Next.js • Tauri</text>
    </g>

    <g transform="translate(0, 192)">
      <text x="0" y="0" class="mono hud-label">FRAMEWORKS  :</text>
      <text x="110" y="0" class="mono hud-val">React Native / Expo • Three.js • Godot 4 • Convex • Supabase</text>
    </g>

    <g transform="translate(0, 210)">
      <text x="0" y="0" class="mono hud-label">CLOUD INFRA :</text>
      <text x="110" y="0" class="mono hud-val">DigitalOcean • Azure • Cloudflare • Docker • Vercel • Sentry</text>
    </g>

    <g transform="translate(0, 228)">
      <text x="0" y="0" class="mono hud-label">FLAGSHIPS   :</text>
      <text x="110" y="0" class="mono hud-val" fill="{accent_amber}">Agent OS • Nexa • Scaleo Capital • CleoNotch • COD • Rivera</text>
    </g>

    <!-- Telemetry Gauges Section -->
    <g transform="translate(0, 252)">
      <rect x="0" y="0" width="535" height="42" rx="4" fill="{card_header_bg}" stroke="{card_border}" stroke-width="0.8"/>
      
      <!-- Gauge 1: Systems Architecture Engine -->
      <g transform="translate(12, 12)">
        <text x="0" y="0" class="mono" font-size="9" font-weight="600" fill="{text_dim}">SYS_INTEGRITY</text>
        <rect x="0" y="6" width="155" height="7" rx="3" fill="{meter_bg}"/>
        <rect x="0" y="6" width="152" height="7" rx="3" fill="{accent_cyan}">
          <animate attributeName="width" values="140;152;146;152" dur="3s" repeatCount="indefinite"/>
        </rect>
        <text x="128" y="2" class="mono" font-size="8.5" fill="{accent_cyan}">99.98%</text>
      </g>

      <!-- Gauge 2: Autonomous Agent Cores -->
      <g transform="translate(190, 12)">
        <text x="0" y="0" class="mono" font-size="9" font-weight="600" fill="{text_dim}">AGENT_CORES</text>
        <rect x="0" y="6" width="155" height="7" rx="3" fill="{meter_bg}"/>
        <rect x="0" y="6" width="148" height="7" rx="3" fill="{accent_emerald}">
          <animate attributeName="width" values="135;148;142;148" dur="4s" repeatCount="indefinite"/>
        </rect>
        <text x="122" y="2" class="mono" font-size="8.5" fill="{accent_emerald}">8 SYNCED</text>
      </g>

      <!-- Gauge 3: Latency & Security -->
      <g transform="translate(368, 12)">
        <text x="0" y="0" class="mono" font-size="9" font-weight="600" fill="{text_dim}">SECURE_TUNNEL</text>
        <rect x="0" y="6" width="155" height="7" rx="3" fill="{meter_bg}"/>
        <rect x="0" y="6" width="155" height="7" rx="3" fill="{accent_violet}"/>
        <text x="110" y="2" class="mono" font-size="8.5" fill="{accent_violet}">TLS 1.3 / 11ms</text>
      </g>
    </g>

    <!-- Active Terminal Prompt with Blinking Cursor -->
    <g transform="translate(0, 314)">
      <text x="0" y="0" class="mono" font-size="11" fill="{accent_emerald}">delight@auscera</text>
      <text x="96" y="0" class="mono" font-size="11" fill="{text_dim}">:</text>
      <text x="104" y="0" class="mono" font-size="11" fill="{accent_cyan}">~/portfolio</text>
      <text x="180" y="0" class="mono" font-size="11" fill="{text_bright}">$ git status --ready</text>
      <rect x="336" y="-10" width="7" height="13" fill="{accent_cyan}">
        <animate attributeName="opacity" values="1;0;1" dur="0.8s" repeatCount="indefinite"/>
      </rect>
    </g>

    <!-- Bottom subtext -->
    <text x="0" y="331" class="mono" font-size="9" fill="{text_dim}">SESSION_ID: 0x9F4B2-PROD • MEMORY: AGENTIC-SYSTEMS • DISCOVERY: ACTIVE</text>
  </g>
</svg>"""

    out_file = ASSETS_DIR / f"banner-{mode}.v1.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Generated {out_file.name} ({len(svg_content) / 1024:.1f} KB)")


def main():
    print("Processing portrait source...")
    arr_dark, arr_light = process_portrait(SOURCE_IMG, grid_w=52, grid_h=62)
    print("Generating Dark Mode Banner...")
    generate_svg("dark", arr_dark)
    print("Generating Light Mode Banner...")
    generate_svg("light", arr_light)
    print("Done generating viral terminal hero banners!")


if __name__ == "__main__":
    main()
