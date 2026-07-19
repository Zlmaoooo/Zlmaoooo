#!/usr/bin/env python3
"""
Builds the neofetch-style info card SVG for Sajid's README -- sits next to
the ASCII animation. Same row-model as the reference repo's
make_info_card.py (host / kv / sec / bul rows, staggered fade-in) but:
  - plum/coral palette matching his existing theme=aura_dark stat embeds
  - content is his (student status, Invenza, Nexus, real stack) not a
    reskinned copy of someone else's job history
  - the LeetCode highlight line is NOT hardcoded -- it's read from
    data/leetcode.json (written by fetch_leetcode.py) so the number
    updates automatically whenever that script re-runs.

Run AFTER fetch_leetcode.py so data/leetcode.json exists, otherwise this
falls back to a placeholder line instead of crashing.
"""
import html
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "info-card.svg")
LEETCODE_JSON = os.path.join(HERE, "..", "data", "leetcode.json")
STATIC = bool(os.environ.get("STATIC"))

W, H = 480, 372
PAD = 20
TITLEBAR_H = 30
KEY_X = PAD
VAL_X = PAD + 92
LINE_H = 20.5

BG = "#211E2B"
BG2 = "#2B2738"       # Sajid's existing bg_color
FRAME = "#FFFFFF"     # Sajid's existing border_color, low opacity
MUTED = "#A9A4BC"
INK = "#EAEAEA"       # Sajid's existing text_color
KEY = "#FF6E6E"       # Sajid's existing title_color -- used for keys
SECTION = "#7FFFD4"   # Sajid's existing icon_color -- used for section headers
GREEN = "#7FFFD4"
ACCENT = "#FF6E6E"

# ---- pull the live LeetCode count, with a safe fallback ----
try:
    with open(LEETCODE_JSON) as f:
        lc = json.load(f)
    leetcode_line = f"{lc['total_solved']} problems solved (LeetCode, auto-updated)"
except FileNotFoundError:
    leetcode_line = "LeetCode stats pending first sync"

ROWS = [
    ("host",),
    ("kv", "Status", "Final-Year CSE Student, Assam Downtown University"),
    ("kv", "Building", "Invenza -- Django + PostgreSQL Inventory System"),
    ("kv", "Runs", "Nexus Discord -- 100 Astralites, since Nov 2022"),
    ("kv", "Edu", "B.Tech CSE, 2028"),
    ("gap",),
    ("sec", "Stack"),
    ("kv", "Languages", "Python, Java, C, Bash"),
    ("kv", "Backend", "Django, Flask, Node.js"),
    ("kv", "Data/DB", "PostgreSQL, MySQL, MongoDB"),
    ("kv", "DevOps", "Git, Docker, GitHub Actions, Vercel"),
    ("gap",),
    ("sec", "Highlights"),
    ("bul", leetcode_line),
    ("bul", "2 Hackathons -- 1 regional, 1 international"),
]


def esc(s):
    return html.escape(s)


def rise(inner, i):
    """fade + slight upward slide, staggered by row index; freezes visible."""
    if STATIC:
        return f"<g>{inner}</g>"
    delay = 0.15 + i * 0.06
    return (f'<g opacity="0" transform="translate(0,5)">{inner}'
            f'<animate attributeName="opacity" from="0" to="1" begin="{delay:.2f}s" dur="0.4s" fill="freeze"/>'
            f'<animateTransform attributeName="transform" type="translate" from="0 5" to="0 0" '
            f'begin="{delay:.2f}s" dur="0.4s" fill="freeze" calcMode="spline" keySplines="0.2 0.8 0.2 1"/></g>')


parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
    f'font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
    '<defs>'
    f'<linearGradient id="ibg" x1="0" y1="0" x2="0" y2="1">'
    f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
    f'<rect width="{W}" height="{H}" rx="12" fill="url(#ibg)"/>',
    f'<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="12" fill="none" stroke="{FRAME}" stroke-opacity="0.55"/>',
    f'<line x1="0" y1="{TITLEBAR_H}" x2="{W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
]
for i, dotcol in enumerate(["#FF6E6E", "#F2CC60", "#7FFFD4"]):
    parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
parts.append(f'<text x="{W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
             f'text-anchor="middle">zlmaoooo@nexus: ~$ neofetch</text>')

y = TITLEBAR_H + 30
for i, row in enumerate(ROWS):
    kind = row[0]
    if kind == "gap":
        y += LINE_H * 0.5
        continue
    if kind == "host":
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" font-size="14" font-weight="700">'
                 f'<tspan fill="{GREEN}">zlmaoooo</tspan><tspan fill="{MUTED}">@</tspan>'
                 f'<tspan fill="{ACCENT}">nexus</tspan></text>'
                 f'<line x1="{KEY_X+140}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.5"/>')
    elif kind == "sec":
        title = esc(row[1])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{SECTION}" font-size="12.5" font-weight="700">'
                 f'&#8212; {title}</text>'
                 f'<line x1="{KEY_X + 12 + len(row[1])*8}" y1="{y-4:.1f}" x2="{W-PAD}" y2="{y-4:.1f}" '
                 f'stroke="{FRAME}" stroke-opacity="0.5"/>')
    elif kind == "kv":
        key, val = esc(row[1]), esc(row[2])
        inner = (f'<text x="{KEY_X}" y="{y:.1f}" fill="{KEY}" font-size="12.5" font-weight="700">{key}</text>'
                 f'<text x="{VAL_X}" y="{y:.1f}" fill="{INK}" font-size="11.5">{val}</text>')
    elif kind == "bul":
        txt = esc(row[1])
        inner = (f'<circle cx="{KEY_X+3}" cy="{y-4:.1f}" r="2.5" fill="{GREEN}"/>'
                 f'<text x="{KEY_X+14}" y="{y:.1f}" fill="{INK}" font-size="12.5">{txt}</text>')
    else:
        continue
    parts.append(rise(inner, i))
    y += LINE_H

parts.append("</svg>")
svg = "".join(parts)
with open(OUT, "w", encoding="utf-8") as f:
    f.write(svg)
print("wrote", OUT, len(svg), "bytes;", W, "x", H, "content_bottom", round(y))
