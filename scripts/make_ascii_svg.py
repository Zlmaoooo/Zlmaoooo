#!/usr/bin/env python3
"""
Generates an animated ASCII SVG for the profile README, replacing the
blog's photo->ASCII portrait with a procedurally-generated animation.

Why procedural instead of video-to-ASCII: a real "Bad Apple"-style ASCII
video bakes every frame of a captured video into the file -- thousands of
frames, multi-MB SVGs that GitHub often refuses to render cleanly and are
slow to load on a profile page. A procedural animation (a rotating 3D
shape, falling-rain, or a scripted boot log) only needs a formula and a
modest frame count to loop seamlessly, so the file stays small (tens of
KB) and reliable.

USAGE: change STYLE below to "donut", "rain", or "boot" and re-run.
    python3 make_ascii_svg.py
writes sajid-ascii.svg
"""
import math
import random
import os

# ---- the one line you change -------------------------------------------
STYLE = "donut"   # "donut" | "rain" | "boot"
# ---------------------------------------------------------------------

HERE = os.path.dirname(__file__)
OUT_PATH = os.path.join(HERE, "..", "sajid-ascii.svg")

COLS, ROWS = 62, 32
FONT_SIZE = 9.5
CHAR_W = FONT_SIZE * 0.6
CHAR_H = FONT_SIZE * 1.15
PAD = 14
CANVAS_W = int(COLS * CHAR_W + PAD * 2)
CANVAS_H = int(ROWS * CHAR_H + PAD * 2 + 26)  # +26 for title bar

BG = "#211E2B"
BG2 = "#2B2738"
FRAME = "#FFFFFF"
MUTED = "#A9A4BC"
ACCENT = "#7FFFD4"   # main glyph color
CORAL = "#FF6E6E"    # highlight / head-character color
TITLEBAR_H = 26


# ===========================================================================
# STYLE 1 -- rotating ASCII donut (adapted from Andy Sloane's donut.c)
# ===========================================================================
def gen_donut_frames(n_frames=60, cols=COLS, rows=ROWS - 2):
    frames = []
    R1, R2, K2 = 1, 2, 5
    K1 = cols * K2 * 3 / (8 * (R1 + R2))
    # step A and B so both complete whole rotations over n_frames -> seamless loop
    dA = (2 * math.pi * 2) / n_frames
    dB = (2 * math.pi * 1) / n_frames
    A, B = 0.0, 0.0
    for _ in range(n_frames):
        output = [[" "] * cols for _ in range(rows)]
        zbuf = [[0.0] * cols for _ in range(rows)]
        cosA, sinA = math.cos(A), math.sin(A)
        cosB, sinB = math.cos(B), math.sin(B)
        for theta in [i * 0.07 for i in range(90)]:
            costheta, sintheta = math.cos(theta), math.sin(theta)
            for phi in [i * 0.02 for i in range(315)]:
                cosphi, sinphi = math.cos(phi), math.sin(phi)
                circlex, circley = R2 + R1 * costheta, R1 * sintheta
                x = circlex * (cosB * cosphi + sinA * sinB * sinphi) - circley * cosA * sinB
                y = circlex * (sinB * cosphi - sinA * cosB * sinphi) + circley * cosA * cosB
                z = 5 + cosA * circlex * sinphi + circley * sinA
                ooz = 1 / z
                xp = int(cols / 2 + K1 * ooz * x)
                yp = int(rows / 2 - K1 * ooz * y * 0.5)
                L = (cosphi * costheta * sinB - cosA * costheta * sinphi
                     - sinA * sintheta + cosB * (cosA * sintheta - costheta * sinA * sinphi))
                if 0 <= xp < cols and 0 <= yp < rows and ooz > zbuf[yp][xp]:
                    zbuf[yp][xp] = ooz
                    luminance_index = int(L * 8)
                    ramp = ".,-~:;=!*#$@"
                    output[yp][xp] = ramp[max(0, min(len(ramp) - 1, luminance_index))]
        frames.append(["".join(row) for row in output])
        A += dA
        B += dB
    return frames


# ===========================================================================
# STYLE 2 -- Matrix-style digital rain
# ===========================================================================
def gen_rain_frames(n_frames=30, cols=COLS, rows=ROWS - 2):
    glyphs = "01ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉ"
    heads = [random.randint(-rows, 0) for _ in range(cols)]
    speeds = [random.choice([1, 1, 2]) for _ in range(cols)]
    trail_len = [random.randint(5, 14) for _ in range(cols)]
    col_chars = [[random.choice(glyphs) for _ in range(rows)] for _ in range(cols)]
    frames = []
    for _ in range(n_frames):
        grid = [[(" ", "dim") for _ in range(cols)] for _ in range(rows)]
        for c in range(cols):
            head = heads[c]
            for k in range(trail_len[c]):
                r = head - k
                if 0 <= r < rows:
                    ch = col_chars[c][r]
                    tag = "head" if k == 0 else ("bright" if k < 3 else "dim")
                    grid[r][c] = (ch, tag)
            heads[c] += speeds[c]
            if heads[c] - trail_len[c] > rows:
                heads[c] = random.randint(-rows // 2, 0)
                col_chars[c] = [random.choice(glyphs) for _ in range(rows)]
            if random.random() < 0.05:
                col_chars[c][max(0, head % rows)] = random.choice(glyphs)
        frames.append(grid)
    return frames  # list of grids of (char, tag)


# ===========================================================================
# STYLE 3 -- scripted terminal boot sequence
# ===========================================================================
BOOT_LINES = [
    "[  OK  ] Started sajid-kernel v2.6",
    "[  OK  ] Mounted /home/invenza (django+postgres)",
    "[  OK  ] Loaded nexus-discord.service (100 astralites)",
    "[  OK  ] Reached target Final-Year-CSE.target",
    "[ WARN ] current_stock still reads raw form input -- fix pending",
    "[  OK  ] Synced leetcode.stats -> auto-refresh armed",
    "[  OK  ] Starting build-system...",
    "        Compiling Invenza backend models... done",
    "        Applying migrations... done",
    "[  OK  ] Reached target ready.",
    "",
    "sajid@nexus login: _",
]


def gen_boot_frames(hold_frames=14):
    frames = []
    for i in range(1, len(BOOT_LINES) + 1):
        frame = BOOT_LINES[:i]
        frames.append(frame)
    # hold on the full boot screen for a bit before looping
    frames += [BOOT_LINES] * hold_frames
    return frames


# ===========================================================================
# SVG assembly -- phase-shifted keyframe trick so N frames cycle with one
# @keyframes block: each frame group shares the same animation but gets a
# negative delay of i * (duration/N), so its visibility window lands at a
# different point in the shared cycle. steps(1) prevents any crossfade.
# ===========================================================================
def build_svg(frame_texts, seconds_per_frame=0.12, monochrome=True):
    n = len(frame_texts)
    duration = n * seconds_per_frame
    pulse_pct = 100 / n

    css = f"""
@keyframes cycle {{
  0% {{ opacity: 1; }}
  {pulse_pct:.4f}% {{ opacity: 1; }}
  {pulse_pct + 0.01:.4f}% {{ opacity: 0; }}
  100% {{ opacity: 0; }}
}}
.frame {{ opacity: 0; animation: cycle {duration:.3f}s steps(1) infinite; }}
@keyframes flicker {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.55; }}
}}
.blink {{ animation: flicker 1s steps(1) infinite; }}
""".strip()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CANVAS_W}" height="{CANVAS_H}" '
        f'viewBox="0 0 {CANVAS_W} {CANVAS_H}" font-family="ui-monospace, SFMono-Regular, Menlo, Consolas, monospace">',
        f'<style>{css}</style>',
        '<defs>'
        f'<linearGradient id="pbg" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{BG2}"/><stop offset="1" stop-color="{BG}"/></linearGradient>'
        '</defs>',
        f'<rect width="{CANVAS_W}" height="{CANVAS_H}" rx="12" fill="url(#pbg)"/>',
        f'<rect x="0.5" y="0.5" width="{CANVAS_W-1}" height="{CANVAS_H-1}" rx="12" '
        f'fill="none" stroke="{FRAME}" stroke-width="1" stroke-opacity="0.55"/>',
        f'<line x1="0" y1="{TITLEBAR_H}" x2="{CANVAS_W}" y2="{TITLEBAR_H}" stroke="{FRAME}" stroke-opacity="0.35"/>',
    ]
    for i, dotcol in enumerate(["#FF6E6E", "#F2CC60", "#7FFFD4"]):
        parts.append(f'<circle cx="{PAD + i*16}" cy="{TITLEBAR_H/2}" r="5" fill="{dotcol}"/>')
    parts.append(f'<text x="{CANVAS_W/2}" y="{TITLEBAR_H/2 + 4}" fill="{MUTED}" font-size="11" '
                 f'text-anchor="middle">sajid@nexus: ~ $ ./{STYLE}.sh</text>')

    top = TITLEBAR_H + PAD
    for i, rows in enumerate(frame_texts):
        delay = -(i * seconds_per_frame)
        g = [f'<g class="frame" style="animation-delay:{delay:.4f}s">']
        if monochrome:
            for r, line in enumerate(rows):
                y = top + (r + 1) * CHAR_H
                esc = (line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
                g.append(f'<text x="{PAD}" y="{y:.1f}" font-size="{FONT_SIZE}" fill="{ACCENT}" xml:space="preserve">{esc}</text>')
        else:
            # rain frames: list of rows of (char, tag) tuples -> ONE tspan per
            # contiguous run of the same color, not one per character (the
            # per-char version blew up to 2.9MB for 48 frames -- exactly the
            # bloat this whole procedural approach exists to avoid).
            colors = {"head": CORAL, "bright": ACCENT, "dim": "#3d5a52"}
            for r, row in enumerate(rows):
                y = top + (r + 1) * CHAR_H
                spans = []
                run_color, run_chars = None, []
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
                g.append(f'<text x="{PAD}" y="{y:.1f}" font-size="{FONT_SIZE}" fill="{ACCENT}" xml:space="preserve">{"".join(spans)}</text>')
        g.append("</g>")
        parts.append("".join(g))

    # persistent CRT flicker overlay -- a handful of static scanline glints
    for _ in range(6):
        fx = PAD + random.random() * (CANVAS_W - 2 * PAD)
        fy = top + random.random() * (CANVAS_H - top - PAD)
        parts.append(f'<rect class="blink" x="{fx:.1f}" y="{fy:.1f}" width="{CHAR_W:.1f}" height="1.5" '
                     f'fill="{CORAL}" opacity="0.35"/>')

    parts.append("</svg>")
    return "".join(parts)


if __name__ == "__main__":
    random.seed(7)
    if STYLE == "donut":
        frames = gen_donut_frames()
        svg = build_svg(frames, seconds_per_frame=0.06, monochrome=True)
    elif STYLE == "rain":
        frames = gen_rain_frames()
        svg = build_svg(frames, seconds_per_frame=0.11, monochrome=False)
    elif STYLE == "boot":
        frames = gen_boot_frames()
        svg = build_svg(frames, seconds_per_frame=0.28, monochrome=True)
    else:
        raise SystemExit(f"unknown STYLE: {STYLE!r}")

    with open(OUT_PATH, "w") as f:
        f.write(svg)
    print(f"[{STYLE}] wrote {OUT_PATH} ({len(svg)} bytes, {len(frames)} frames)")
