#!/usr/bin/env python3
"""
generate_trophies.py - Generates custom gamified cyberpunk achievement trophies SVG
Reliable, offline, and self-hosted (avoids third-party Vercel 402 Payment Required errors).
"""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
OUT_FILE = BASE_DIR / "assets" / "trophies.svg"

TROPHIES = [
    {
        "title": "Autonomous Architect",
        "rank": "SSS",
        "desc": "Agent OS / BWA",
        "icon": "🏆",
        "color": "#f59e0b",
        "rank_bg": "rgba(245, 158, 11, 0.15)",
    },
    {
        "title": "Agentic Engineer",
        "rank": "SS",
        "desc": "Multi-Agent Loops",
        "icon": "⚡",
        "color": "#38bdf8",
        "rank_bg": "rgba(56, 189, 248, 0.15)",
    },
    {
        "title": "Auscera Founder",
        "rank": "S",
        "desc": "Systemic Leadership",
        "icon": "🚀",
        "color": "#10b981",
        "rank_bg": "rgba(16, 185, 129, 0.15)",
    },
    {
        "title": "Resilient Systems",
        "rank": "S",
        "desc": "Zero-Crash Infra",
        "icon": "🛡️",
        "color": "#a855f7",
        "rank_bg": "rgba(168, 85, 247, 0.15)",
    },
    {
        "title": "Full-Stack Native",
        "rank": "A",
        "desc": "Next • Tauri • Expo",
        "icon": "🌐",
        "color": "#ec4899",
        "rank_bg": "rgba(236, 72, 153, 0.15)",
    },
    {
        "title": "Polyglot Master",
        "rank": "A",
        "desc": "TS • Py • Rust • Go",
        "icon": "💎",
        "color": "#06b6d4",
        "rank_bg": "rgba(6, 182, 212, 0.15)",
    },
]

def make_trophies():
    w, h = 880, 160
    cards_y = 48
    card_w = 132
    card_h = 96
    spacing = 10
    total_cards_w = len(TROPHIES) * card_w + (len(TROPHIES) - 1) * spacing
    start_x = (w - total_cards_w) / 2

    cards_svg = []
    for i, t in enumerate(TROPHIES):
        cx = start_x + i * (card_w + spacing)
        color = t["color"]
        rank = t["rank"]
        title = t["title"]
        desc = t["desc"]
        icon = t["icon"]

        card = f"""
    <!-- Trophy Card: {title} -->
    <g transform="translate({cx:.1f}, {cards_y})">
      <rect x="0" y="0" width="{card_w}" height="{card_h}" rx="8" fill="#0f172a" stroke="#1e293b" stroke-width="1.2"/>
      
      <!-- Rank Pill Badge -->
      <g transform="translate({card_w - 42}, 8)">
        <rect x="0" y="0" width="34" height="16" rx="4" fill="{t['rank_bg']}" stroke="{color}" stroke-width="1"/>
        <text x="17" y="11.5" text-anchor="middle" font-family="monospace" font-size="10" font-weight="800" fill="{color}">{rank}</text>
      </g>

      <!-- Icon with Pulse Glow -->
      <g transform="translate(14, 18)">
        <text x="0" y="18" font-size="22">{icon}</text>
      </g>

      <!-- Trophy Title -->
      <text x="10" y="58" font-family="-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif" font-size="10.5" font-weight="700" fill="#f8fafc">{title}</text>
      
      <!-- Trophy Desc -->
      <text x="10" y="74" font-family="monospace" font-size="9" font-weight="500" fill="#94a3b8">{desc}</text>

      <!-- Status Indicator Line -->
      <line x1="10" y1="84" x2="{card_w - 10}" y2="84" stroke="{color}" stroke-width="1.8" stroke-linecap="round" opacity="0.8">
        <animate attributeName="opacity" values="0.4;1;0.4" dur="2.5s" repeatCount="indefinite" begin="{i * 0.3}s"/>
      </line>
    </g>"""
        cards_svg.append(card)

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" height="100%">
  <!-- Container Box -->
  <rect x="0" y="0" width="{w}" height="{h}" rx="10" fill="#090d16" stroke="#1e293b" stroke-width="1.2"/>

  <!-- Top Header Bar -->
  <rect x="0" y="0" width="{w}" height="32" rx="10" fill="#0f172a"/>
  <rect x="0" y="22" width="{w}" height="10" fill="#0f172a"/>
  <line x1="0" y1="32" x2="{w}" y2="32" stroke="#1e293b" stroke-width="1"/>

  <circle cx="18" cy="16" r="4.5" fill="#ef4444"/>
  <circle cx="32" cy="16" r="4.5" fill="#f59e0b"/>
  <circle cx="46" cy="16" r="4.5" fill="#10b981"/>
  <text x="64" y="20" font-family="monospace" font-size="11" font-weight="600" fill="#64748b">delight@auscera: ~ / telemetry / achievements.svg</text>
  
  <text x="{w - 20}" y="20" text-anchor="end" font-family="monospace" font-size="10" font-weight="700" fill="#f59e0b">[ GAMIFIED TROPHY MATRIX ]</text>

  <!-- Cards -->
  {''.join(cards_svg)}
</svg>"""

    with open(OUT_FILE, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated custom trophies SVG at {OUT_FILE}")

if __name__ == "__main__":
    make_trophies()
