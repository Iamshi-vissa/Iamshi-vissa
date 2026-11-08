#!/usr/bin/env python3
"""Sunset over the town — writes sunset.svg (static art, no data)."""
import math
import random
from pathlib import Path

PAPER, INK, SOFT, RED = "#F2EADB", "#1A1714", "#7A6F62", "#B4432B"
MONO = "'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif"
SERIF = MONO
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
W, H = 1200, 360
G = 250           # street line
SUN = (660, 200, 84)
r = random.Random(11)
SHIFT = ' patternTransform="translate(4 0)"'


def tone_bands():
    """Manga screentone sky: dots grow toward the horizon."""
    pats, rects = [], []
    bands = 7
    top, bot = 24, G
    for i in range(bands):
        rad = 0.5 + i * 0.32
        pats.append(f'<pattern id="t{i}" width="8" height="8" patternUnits="userSpaceOnUse"'
                    f'{SHIFT if i % 2 else ""}>'
                    f'<circle cx="4" cy="4" r="{rad:.2f}" fill="{RED}" fill-opacity="{.22 + i*.05:.2f}"/></pattern>')
        y0 = top + (bot - top) * i / bands
        rects.append(f'<rect x="24" y="{y0:.0f}" width="{W-48}" height="{(bot-top)/bands + 1:.0f}" fill="url(#t{i})"/>')
    return "".join(pats), "".join(rects)


def sun():
    x, y, rad = SUN
    # the classic woodblock sun: solid disc, horizontal paper cuts that widen toward the bottom
    cuts = "".join(f'<rect x="{x-rad}" y="{y + 12 + k*k*2.1:.1f}" width="{2*rad}" height="{1 + k*0.9:.1f}" fill="{PAPER}"/>'
                   for k in range(1, 9))
    return (f'<g class="sun"><circle cx="{x}" cy="{y}" r="{rad+14}" fill="{PAPER}"/>'
            f'<g clip-path="url(#sunC)"><circle cx="{x}" cy="{y}" r="{rad}" fill="{RED}"/>{cuts}</g></g>')


def cloud(x, y, s, cls, delay):
    # ink-outlined cumulus, filled with paper so it sits in front of the tone
    lobes = [(0, 0, 26), (30, -12, 30), (64, -4, 24), (90, 6, 18), (-26, 8, 18)]
    fill = "".join(f'<circle cx="{x+dx*s:.0f}" cy="{y+dy*s:.0f}" r="{rr*s:.0f}"/>' for dx, dy, rr in lobes)
    base = f'<rect x="{x-44*s:.0f}" y="{y+6*s:.0f}" width="{150*s:.0f}" height="{20*s:.0f}" rx="{10*s:.0f}"/>'
    return (f'<g class="{cls}" style="animation-delay:{delay}s">'
            f'<g fill="none" stroke="{INK}" stroke-width="3">{fill}{base}</g>'
            f'<g fill="{PAPER}">{fill}{base}</g></g>')


def skyline():
    s = []
    ink = f'fill="{INK}"'
    # left: house with a tiled roof, pipes and a balcony
    s.append(f'<polygon {ink} points="40,{G} 40,150 30,150 110,104 196,150 186,150 186,{G}"/>')
    s.append(f'<rect {ink} x="120" y="70" width="12" height="60"/><rect {ink} x="112" y="70" width="28" height="8"/>')
    s.append(f'<rect x="62" y="172" width="26" height="30" fill="{PAPER}" opacity=".9"/><rect x="134" y="172" width="26" height="30" fill="{PAPER}" opacity=".9"/>')
    s.append(f'<rect {ink} x="196" y="168" width="60" height="{G-168}"/><path d="M196 196 H262" stroke="{INK}" stroke-width="3"/>'
             + "".join(f'<rect {ink} x="{200+i*9}" y="186" width="3" height="10"/>' for i in range(7)))
    # utility pole + sagging wires (the town's lazy afternoon)
    s.append(f'<rect {ink} x="300" y="60" width="7" height="{G-60}"/><rect {ink} x="282" y="76" width="44" height="5"/>'
             f'<rect {ink} x="288" y="96" width="32" height="4"/>')
    s.append(f'<g stroke="{INK}" stroke-width="1.6" fill="none"><path d="M120 74 Q 210 110 300 78"/><path d="M304 78 Q 520 128 700 70"/>'
             f'<path d="M304 98 Q 520 150 1000 96"/><path d="M1004 96 Q 1100 120 1176 104"/></g>')
    # mid: apartment blocks with a few lit windows
    for bx, bw, bh in [(340, 70, 120), (414, 52, 160), (470, 84, 96), (900, 66, 140), (970, 90, 104), (1064, 56, 150)]:
        s.append(f'<rect {ink} x="{bx}" y="{G-bh}" width="{bw}" height="{bh}"/>')
        for wy in range(G - bh + 14, G - 14, 18):
            for wx in range(bx + 8, bx + bw - 10, 16):
                lit = r.random() < .07
                if r.random() < .55 or lit:
                    s.append(f'<rect x="{wx}" y="{wy}" width="7" height="9" fill="{RED if lit else PAPER}" opacity="{1 if lit else .18}"/>')
    # the tower: tiered roofs, a drum, an onion dome and a spire
    tx = 800
    s.append(f'<rect {ink} x="{tx-46}" y="170" width="92" height="{G-170}"/>'
             f'<polygon {ink} points="{tx-78},176 {tx},138 {tx+78},176"/>'
             f'<rect {ink} x="{tx-36}" y="122" width="72" height="22"/>'
             f'<polygon {ink} points="{tx-62},126 {tx},96 {tx+62},126"/>'
             f'<rect {ink} x="{tx-24}" y="74" width="48" height="26"/>'
             f'<path {ink} d="M{tx-26} 76 C {tx-30} 40, {tx+30} 40, {tx+26} 76 Z"/>'
             f'<rect {ink} x="{tx-3}" y="18" width="6" height="34"/><circle {ink} cx="{tx}" cy="20" r="5"/>')
    s.append("".join(f'<rect x="{tx-30+i*14}" y="190" width="6" height="12" fill="{PAPER}" opacity=".22"/>' for i in range(5)))
    # trees: clumped ink canopies
    for cx, cy, n in [(574, 230, 3), (1140, 196, 7), (262, 226, 3)]:
        rr = random.Random(cx)
        s.append("".join(f'<circle {ink} cx="{cx + rr.uniform(-24, 24):.0f}" cy="{cy + rr.uniform(-18, 14):.0f}" r="{rr.uniform(14, 22):.0f}"/>' for _ in range(n)))
    # street
    s.append(f'<rect {ink} x="24" y="{G}" width="{W-48}" height="10"/>')
    return "".join(s)


def birds():
    out = []
    for i, (x, y, s) in enumerate([(380, 70, 1), (412, 82, .8), (440, 64, .7)]):
        out.append(f'<g class="bird" style="animation-delay:{i*.4}s"><path d="M{x} {y} q {6*s} {-6*s} {12*s} 0 q {6*s} {-6*s} {12*s} 0" '
                   f'stroke="{INK}" stroke-width="2" fill="none"/></g>')
    return "".join(out)


def build():
    pats, bands = tone_bands()
    x, y, rad = SUN
    defs = f'<defs>{pats}<clipPath id="sunC"><circle cx="{x}" cy="{y}" r="{rad}"/></clipPath>' \
           f'<clipPath id="panel"><rect x="24" y="24" width="{W-48}" height="{G-14}"/></clipPath></defs>'
    body = (f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
            f'<g clip-path="url(#panel)">{bands}{sun()}'
            f'{cloud(160, 78, .8, "cl a", 0)}{cloud(990, 74, .9, "cl b", 0)}{cloud(520, 92, .5, "cl c", 0)}'
            f'{birds()}{skyline()}</g>'
            f'<rect x="20" y="20" width="{W-40}" height="{G-6}" fill="none" stroke="{INK}" stroke-width="4"/>'
            # caption row
            f'<text x="{W/2}" y="{G+64}" text-anchor="middle" font-family="{SERIF}" font-weight="300" font-size="26" letter-spacing="1" fill="{INK}">Clouds drift. Code ships.</text>'
            f'<text x="24" y="{H-22}" font-family="{MONO}" font-weight="300" font-size="11" letter-spacing="3" fill="{SOFT}">END OF VOLUME 01 · SUNSET</text>'
            f'<text x="{W-84}" y="{H-22}" text-anchor="end" font-family="{MONO}" font-weight="300" font-size="11" letter-spacing="3" fill="{SOFT}">SEE YOU NEXT CHAPTER</text>'
            f'<g transform="translate({W-70} {H-58})"><rect width="44" height="44" rx="4" fill="none" stroke="{RED}" stroke-width="2.5"/>'
            f'<text x="22" y="31" text-anchor="middle" font-family="{SERIF}" font-weight="300" font-size="15" letter-spacing="1" fill="{RED}">END</text></g>')
    css = (".cl{animation:drift 60s ease-in-out infinite alternate}"
           ".b{animation-duration:80s;animation-direction:alternate-reverse}.c{animation-duration:45s}"
           "@keyframes drift{from{transform:translateX(-30px)}to{transform:translateX(40px)}}"
           ".sun{animation:sink 12s ease-in-out infinite alternate}@keyframes sink{to{transform:translateY(10px)}}"
           ".bird{animation:fly 14s linear infinite}@keyframes fly{0%{transform:translate(-420px,30px);opacity:0}"
           "8%{opacity:1}90%{opacity:1}100%{transform:translate(860px,-40px);opacity:0}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Sunset over the town — clouds drift, code ships.">'
            f'<style>{css}{RM}</style>{defs}{body}</svg>')


if __name__ == "__main__":
    (Path(__file__).parent / "sunset.svg").write_text(build())
    print("sunset.svg written")
