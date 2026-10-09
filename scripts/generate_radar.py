#!/usr/bin/env python3
"""
generate_radar.py - Generates compact, seamless Titanium Silver Competency Radar Chart
- Plain on page (ZERO Mac OS window components, zero traffic lights, zero outer card boxes).
- Unified Titanium Silver / Liquid Metal / Platinum Grey palette (no color riots).
- Compact, centered footprint (500x330).
"""

import math
import html
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_FILE = BASE_DIR / "assets" / "radar-chart.svg"

# Skills and scores (0 to 100)
SKILLS = [
    ("Autonomous Agents (OS/BWA)", 98),
    ("Systems & Architecture", 96),
    ("Full-Stack & Mobile (React/Next/Expo)", 94),
    ("3D / WebGL / Shaders (Three/Godot)", 90),
    ("Cloud & DevOps (Docker/VPS/Sentry)", 92),
    ("FinTech & Quantitative Systems", 91),
]

def make_radar():
    w, h = 500, 330
    cx, cy = 250, 160
    max_r = 100
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

    for i, (name, val) in enumerate(SKILLS):
        escaped_name = html.escape(name)
        angle = -math.pi / 2 + i * (2 * math.pi / n)
        r = max_r * (val / 100.0)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        data_pts.append(f"{x:.1f},{y:.1f}")

        # Vertex circle in titanium silver / liquid chrome
        node_circles.append(f'''
        <g>
          <circle cx="{x:.1f}" cy="{y:.1f}" r="3.5" fill="#ffffff"/>
          <circle cx="{x:.1f}" cy="{y:.1f}" r="7" fill="none" stroke="#cbd5e1" stroke-width="1.0" opacity="0.6">
            <animate attributeName="r" values="4;8;4" dur="2.4s" repeatCount="indefinite" begin="{i * 0.3:.1f}s"/>
            <animate attributeName="opacity" values="0.7;0.1;0.7" dur="2.4s" repeatCount="indefinite" begin="{i * 0.3:.1f}s"/>
          </circle>
        </g>
        ''')

        # Outer label placement
        label_r = max_r + 20
        lx = cx + label_r * math.cos(angle)
        ly = cy + label_r * math.sin(angle)
        
        if abs(math.cos(angle)) < 0.15:
            anchor = "middle"
            if math.sin(angle) < 0:
                ly -= 6
            else:
                ly += 12
        elif math.cos(angle) > 0:
            anchor = "start"
            lx += 6
        else:
            anchor = "end"
            lx -= 6

        label_elements.append(f'''
        <g>
          <text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-family="monospace" font-size="10" font-weight="700" fill="#f8fafc">{escaped_name}</text>
          <text x="{lx:.1f}" y="{ly + 12:.1f}" text-anchor="{anchor}" font-family="monospace" font-size="9" font-weight="600" fill="#94a3b8">[{val}%]</text>
        </g>
        ''')

    data_polygon = " ".join(data_pts)

    rings_svg = "\n    ".join([
        f'<polygon points="{pts}" fill="none" stroke="#1e293b" stroke-width="1" stroke-dasharray="3,3"/>'
        for pts in ring_paths[:-1]
    ] + [
        f'<polygon points="{ring_paths[-1]}" fill="none" stroke="#334155" stroke-width="1.2"/>'
    ])

    spokes_svg = "\n    ".join([
        f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#1e293b" stroke-width="1"/>'
        for x1, y1, x2, y2 in spokes
    ])

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">
  <defs>
    <!-- Titanium Silver / Liquid Metal Polygon Gradient -->
    <linearGradient id="titaniumRadarGrad" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" stop-color="#f8fafc" stop-opacity="0.32"/>
      <stop offset="50%" stop-color="#cbd5e1" stop-opacity="0.22"/>
      <stop offset="100%" stop-color="#94a3b8" stop-opacity="0.28"/>
    </linearGradient>
  </defs>

  <!-- Radar Background Grid -->
  <g>
    {rings_svg}
    {spokes_svg}
  </g>

  <!-- Animated Rotating Sweep Line in Liquid Silver -->
  <g transform="translate({cx}, {cy})">
    <line x1="0" y1="0" x2="0" y2="-{max_r}" stroke="#cbd5e1" stroke-width="1.2" opacity="0.25">
      <animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="8s" repeatCount="indefinite"/>
    </line>
  </g>

  <!-- Data Filled Hexagon: Titanium Silver -->
  <polygon points="{data_polygon}" fill="url(#titaniumRadarGrad)" stroke="#e2e8f0" stroke-width="1.8">
    <animate attributeName="stroke-opacity" values="0.75;1;0.75" dur="2.8s" repeatCount="indefinite"/>
  </polygon>

  <!-- Data Nodes -->
  {"".join(node_circles)}

  <!-- Labels -->
  {"".join(label_elements)}
</svg>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated compact seamless radar chart at {OUT_FILE}")

if __name__ == "__main__":
    make_radar()
