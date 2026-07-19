#!/usr/bin/env python3
"""
Merges the ASCII animation panel + neofetch info card + a shared
contribution-stats footer into ONE combined SVG, instead of two separate
<img> tags placed side by side in a table. This is what makes it read as
one cohesive terminal window instead of two floating boxes.

Trade-off worth knowing: switching animation styles now means re-running
THIS script (one command), not just editing the README's <img src=...>
line -- because the animation frames are baked directly into this merged
file rather than living in three separate standalone SVGs.

USAGE: change STYLE below, then:
    python3 make_terminal_panel.py
writes terminal-panel.svg
"""
import datetime
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import make_ascii_svg as ascii_mod  # reuse frame generators, safe: guarded by __main__
import make_info_card as card_mod   # reuse ROWS/esc/colors -- import itself has no
                                     # side effects now; we call card_mod.build_and_write()
                                     # explicitly below when this script is run directly.

# ---- the one line you change -------------------------------------------
STYLE = "rain"   # "donut" | "rain" | "boot"
# ---------------------------------------------------------------------

OUT_PATH = os.path.join(HERE, "..", "terminal-panel.svg")
CONTRIB_JSON = os.path.join(HERE, "..", "data", "contributions.json")

BG = "#211E2B"
BG2 = "#2B2738"
FRAME = "#FFFFFF"
MUTED = "#A9A4BC"
TEXT = "#EAEAEA"
ACCENT = "#7FFFD4"
CORAL = "#FF6E6E"
GOLD = "#f2cc60"
TITLEBAR_H = 30
PAD = 18

LEFT_W = int(ascii_mod.COLS * ascii_mod.CHAR_W) + PAD * 2
LEFT_H = int((ascii_mod.ROWS - 2) * ascii_mod.CHAR_H) + PAD * 2
RIGHT_W = card_mod.W - 2 * card_mod.PAD  # card content width, borderless
FOOTER_H = 70
DIVIDER_GAP = 26

CANVAS_W = LEFT_W + DIVIDER_GAP + card_mod.W - PAD
CANVAS_H = TITLEBAR_H + max(LEFT_H, card_mod.H - card_mod.TITLEBAR_H - 20) + FOOTER_H + PAD


def gen_frames_for_style(style):
    if style == "donut":
        return ascii_mod.gen_donut_frames(), True, 0.06
    if style == "rain":
        return ascii_mod.gen_rain_frames(), False, 0.11
    if style == "boot":
        return ascii_mod.gen_boot_frames(), True, 0.28
    raise SystemExit(f"unknown STYLE: {style!r}")


def ascii_block_svg(x0, y0, frames, monochrome, seconds_per_frame):
    n = len(frames)
    duration = n * seconds_per_frame
    pulse_pct = 100 / n
    style_id = f"cycle_{id(frames) % 99999}"
    css = (f"@keyframes {style_id} {{0%{{opacity:1;}} {pulse_pct:.4f}%{{opacity:1;}} "
           f"{pulse_pct+0.01:.4f}%{{opacity:0;}} 100%{{opacity:0;}}}} "
           f".af{{opacity:0;animation:{style_id} {duration:.3f}s steps(1) infinite;}}")
    parts = [f"<style>{css}</style>"]
    colors = {"head": CORAL, "bright": ACCENT, "dim": "#3d5a52"}
    for i, rows in enumerate(frames):
        # positive delay plays frames forward -- see the note in
        # make_ascii_svg.py's build_svg for why this must not be negative.
        delay = i * seconds_per_frame
        g = [f'<g class="af" style="animation-delay:{delay:.4f}s">']
        if monochrome:
            for r, line in enumerate(rows):
                y = y0 + PAD + (r + 1) * ascii_mod.CHAR_H
                esc = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                g.append(f'<text x="{x0+PAD}" y="{y:.1f}" font-size="{ascii_mod.FONT_SIZE}" '
                         f'fill="{ACCENT}" xml:space="preserve">{esc}</text>')
        else:
            for r, row in enumerate(rows):
                y = y0 + PAD + (r + 1) * ascii_mod.CHAR_H
                spans, run_color, run_chars = [], None, []
                for ch, tag in row:
                    color = colors[tag] if ch != " " else None
                    if color != run_color:
                        if run_chars:
                            txt = "".join(run_chars).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                            spans.append(f'<tspan fill="{run_color}">{txt}</tspan>' if run_color else txt)
                        run_color, run_chars = color, [ch]
                    else:
                        run_chars.append(ch)
                if run_chars:
                    txt = "".join(run_chars).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    spans.append(f'<tspan fill="{run_color}">{txt}</tspan>' if run_color else txt)
                g.append(f'<text x="{x0+PAD}" y="{y:.1f}" font-size="{ascii_mod.FONT_SIZE}" '
                         f'fill="{ACCENT}" xml:space="preserve">{"".join(spans)}</text>')
        g.append("</g>")
        parts.append("".join(g))
    return "".join(parts)


def card_block_svg(x0, y0):
    """Re-draw the info-card ROWS at a custom offset (borderless, no own titlebar)."""
    parts = []
    y = y0 + 20
    for i, row in enumerate(card_mod.ROWS):
        kind = row[0]
        if kind == "gap":
            y += card_mod.LINE_H * 0.5
            continue
        if kind == "host":
            parts.append(
                f'<text x="{x0}" y="{y:.1f}" font-size="14" font-weight="700">'
                f'<tspan fill="{ACCENT}">zlmaoooo</tspan><tspan fill="{MUTED}">@</tspan>'
                f'<tspan fill="{CORAL}">nexus</tspan></text>'
                f'<line x1="{x0+140}" y1="{y-4:.1f}" x2="{x0+RIGHT_W}" y2="{y-4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.5"/>')
        elif kind == "sec":
            title = card_mod.esc(row[1])
            parts.append(
                f'<text x="{x0}" y="{y:.1f}" fill="{ACCENT}" font-size="12.5" font-weight="700">'
                f'&#8212; {title}</text>'
                f'<line x1="{x0 + 12 + len(row[1])*8}" y1="{y-4:.1f}" x2="{x0+RIGHT_W}" y2="{y-4:.1f}" '
                f'stroke="{FRAME}" stroke-opacity="0.5"/>')
        elif kind == "kv":
            key, val = card_mod.esc(row[1]), card_mod.esc(row[2])
            parts.append(
                f'<text x="{x0}" y="{y:.1f}" fill="{CORAL}" font-size="12.5" font-weight="700">{key}</text>'
                f'<text x="{x0+92}" y="{y:.1f}" fill="{TEXT}" font-size="11.5">{val}</text>')
        elif kind == "bul":
            txt = card_mod.esc(row[1])
            parts.append(
                f'<circle cx="{x0+3}" cy="{y-4:.1f}" r="2.5" fill="{ACCENT}"/>'
                f'<text x="{x0+14}" y="{y:.1f}" fill="{TEXT}" font-size="12.5">{txt}</text>')
        y += card_mod.LINE_H
    return "".join(parts)


def footer_svg(y0):
    data = json.load(open(CONTRIB_JSON))
    cs = data["current_streak"]["length"]
    ls = data["longest_streak"]["length"]
    total = data["total_contributions"]
    best = data["best_day"]
    rng = data["range"]
    parts = [f'<line x1="0" y1="{y0}" x2="{CANVAS_W}" y2="{y0}" stroke="{FRAME}" stroke-opacity="0.25"/>']
    ly = y0 + 24
    parts.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{CORAL}">'
                 f'<tspan font-weight="700">{total:,}</tspan>'
                 f'<tspan fill="{MUTED}"> contributions in the last year</tspan></text>')
    parts.append(f'<text x="{CANVAS_W - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'{rng["start"]} &#8594; {rng["end"]}</text>')
    ly += 24
    parts.append(f'<text x="{PAD}" y="{ly}" font-size="13" fill="{MUTED}">current streak '
                 f'<tspan fill="{ACCENT}" font-weight="700">{cs} days</tspan>'
                 f'<tspan fill="{MUTED}">   &#183;   longest </tspan>'
                 f'<tspan fill="{ACCENT}" font-weight="700">{ls} days</tspan></text>')
    parts.append(f'<text x="{CANVAS_W - PAD}" y="{ly}" font-size="12" fill="{MUTED}" text-anchor="end">'
                 f'best day <tspan fill="{GOLD}" font-weight="700">{best["count"]}</tspan> on {best["date"]}</text>')
    return "".join(parts)


def build():
    frames, monochrome, spf = gen_frames_for_style(STYLE)
    body_top = TITLEBAR_H
    footer_top = CANVAS_H - FOOTER_H

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        '<defs>'
        f'<linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient></defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="14" fill="url(#pbg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="14" '
        f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]
    for i, dotcol in enumerate(["#FF6E6E", "#F2CC60", "#7FFFD4"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="12" '
                 f'text-anchor="middle">zlmaoooo@nexus: ~ $ whoami --style={STYLE}</text>')

    parts.append(ascii_block_svg(0, body_top, frames, monochrome, spf))

    div_x = LEFT_W + DIVIDER_GAP / 2
    parts.append(f'<line x1="{div_x:.1f}" y1="{body_top+14}" x2="{div_x:.1f}" y2="{footer_top-14}" '
                 f'stroke="{FRAME}" stroke-opacity="0.3"/>')

    parts.append(card_block_svg(LEFT_W + DIVIDER_GAP, body_top))
    parts.append(footer_svg(footer_top))
    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    card_mod.build_and_write()   # explicit now, not an import side effect
    svg = build()
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"[{STYLE}] wrote {OUT_PATH} ({len(svg)} bytes) size={CANVAS_W}x{CANVAS_H}")
