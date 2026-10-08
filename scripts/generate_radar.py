#!/usr/bin/env python3
"""
generate_radar.py - Generates high-tech animated hexagonal radar chart SVG
Visualizes Delight's engineering competency dimensions.
"""

import math
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_FILE = BASE_DIR / "assets" / "radar-chart.svg"

# Skills and scores (0 to 100)
SKILLS = [
    ("Autonomous Agents (OS/BWA)", 98, "#38bdf8"),
    ("Systems & Architecture", 96, "#10b981"),
    ("Full-Stack & Mobile (React/Next/Expo)", 94, "#a855f7"),
    ("3D / WebGL / Shaders (Three/Godot)", 90, "#ec4899"),
    ("Cloud & DevOps (Docker/VPS/Sentry)", 92, "#f59e0b"),
    ("FinTech & Quantitative Systems", 91, "#06b6d4"),
]

def make_radar():
    w, h = 640, 420
    cx, cy = 320, 205
    max_r = 135
    n = len(SKILLS)

    # Concentric rings
    rings = [0.25, 0.50, 0.75, 1.00]
    ring_paths = []
    for scale in rings:
        r = max_r * scale
        pts = []
        for i in range(n):
            angle = -math.pi / 2 + i * (2 * math.pi / n)
            x = cx + r * math.cos(angle)
            y = cy + r * math.sin(angle)
            pts.append(f"{x:.1f},{y:.1f}")
        ring_paths.append(" ".join(pts))

    # Axis spokes
    spokes = []
    for i in range(n):
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        x = cx + max_r * math.cos(angle)
        y = cy + max_r * math.sin(angle)
        spokes.append((cx, cy, x, y))

    # Data polygon points
    data_pts = []
    node_circles = []
    label_elements = []

    for i, (name, val, color) in enumerate(SKILLS):
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        r = max_r * (val / 100.0)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        data_pts.append(f"{x:.1f},{y:.1f}")

        # Vertex circle
        node_circles.append(f'''
        <g>
          <circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>
          <circle cx="{x:.1f}" cy="{y:.1f}" r="8" fill="none" stroke="{color}" stroke-width="1.2" opacity="0.6">
            <animate attributeName="r" values="5;10;5" dur="2.4s" repeatCount="indefinite" begin="{i * 0.3}s"/>
            <animate attributeName="opacity" values="0.8;0.1;0.8" dur="2.4s" repeatCount="indefinite" begin="{i * 0.3}s"/>
          </circle>
        </g>
        ''')

        # Outer label placement
        label_r = max_r + 28
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        
        # Text anchor adjustment
        if abs(math.cos(angle)) < 0.15:
            anchor = "middle"
            if math.sin(angle) < 0:
                ly -= 6
            else:
                ly += 14
        elif math.cos(angle) > 0:
            anchor = "start"
            lx += 8
        else:
            anchor = "end"
            lx -= 8

        label_elements.append(f'''
        <g>
          <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-family="monospace" font-size="11" font-weight="700" fill="{color}">{name}</text>
          <text x="{lx:.1f}" y="{ly + 13:.1f}" text-anchor="{anchor}" font-family="monospace" font-size="10" font-weight="600" fill="#94a3b8">[{val}% MASTERY]</text>
        </g>
        ''')

    data_polygon = " ".join(data_pts)

    rings_svg = "\n    ".join([
        f'<polygon points="{pts}" fill="none" stroke="#1e293b" stroke-width="1" stroke-dasharray="3,3"/>'
        for pts in ring_paths[:-1]
    ] + [
        f'<polygon points="{ring_paths[-1]}" fill="none" stroke="#334155" stroke-width="1.4"/>'
    ])

    spokes_svg = "\n    ".join([
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#1e293b" stroke-width="1"/>'
        for x1, y1, x2, y2 in spokes
    ])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">
  <defs>
    <radialGradient id="radarGlow" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.35"/>
      <stop offset="60%" stop-color="#10b981" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="#090d16" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="polyGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#38bdf8" stop-opacity="0.45"/>
      <stop offset="50%" stop-color="#818cf8" stop-opacity="0.35"/>
      <stop offset="100%" stop-color="#10b981" stop-opacity="0.45"/>
    </linearGradient>
    <filter id="bloom" x="-20%" y="-20%" width="140%" height="140%">
      <feGaussianBlur stdDeviation="3" result="blur"/>
      <feComposite in="SourceGraphic" in2="blur" operator="over"/>
    </filter>
  </defs>

  <!-- Container Box -->
  <rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="#090d16" stroke="#1e293b" stroke-width="1.2"/>
  
  <!-- Top Header Bar -->
  <rect x="0" y="0" width="{w}" height="36" rx="10" fill="#0f172a"/>
  <rect x="0" y="26" width="{w}" height="10" fill="#0f172a"/>
  <line x1="0" y1="36" x2="{w}" y2="36" stroke="#1e293b" stroke-width="1"/>

  <circle cx="18" cy="18" r="4.5" fill="#ef4444"/>
  <circle cx="32" cy="18" r="4.5" fill="#f59e0b"/>
  <circle cx="46" cy="18" r="4.5" fill="#10b981"/>
  <text x="64" y="22" font-family="monospace" font-size="11" font-weight="600" fill="#64748b">delight@auscera: ~ / telemetry / radar.svg</text>
  
  <text x="{w - 24}" y="22" text-anchor="end" font-family="monospace" font-size="10" font-weight="700" fill="#38bdf8">[ DOMAIN COMPETENCY RADAR ]</text>

  <!-- Radar Background Grid -->
  <g>
    {rings_svg}
    {spokes_svg}
  </g>

  <!-- Animated Rotating Sweep Line -->
  <g transform="translate({cx}, {cy})">
    <line x1="0" y1="0" x2="0" y2="-{max_r}" stroke="#38bdf8" stroke-width="1.5" opacity="0.4">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="8s" repeatCount="indefinite"/>
    </line>
  </g>

  <!-- Data Filled Hexagon -->
  <polygon points="{data_polygon}" fill="url(#polyGrad)" stroke="#38bdf8" stroke-width="2" filter="url(#bloom)">
    <animate attributeName="stroke-opacity" values="0.7;1;0.7" dur="2.8s" repeatCount="indefinite"/>
  </polygon>

  <!-- Data Nodes -->
  {"".join(node_circles)}

  <!-- Labels -->
  {"".join(label_elements)}

  <!-- Bottom HUD Summary -->
  <line x1="20" y1="{h - 26}" x2="{w - 20}" y2="{h - 26}" stroke="#1e293b" stroke-width="0.8"/>
  <text x="24" y="{h - 10}" font-family="monospace" font-size="9" fill="#64748b">SYS_METRIC: COMPREHENSIVE ARCHITECTURAL RATING: 93.5/100</text>
  <text x="{w - 24}" y="{h - 10}" text-anchor="end" font-family="monospace" font-size="9" fill="#10b981">● AGENTIC SYNCHRONY 100%</text>
</svg>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated radar chart at {OUT_FILE}")

if __name__ == "__main__":
    make_radar()
