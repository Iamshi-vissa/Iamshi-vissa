#!/usr/bin/env python3
"""Writes moon.svg from the contribution calendar. Test locally: python3 moon_gen.py --mock 5 9"""
import datetime as dt
import json
import os
import random
import sys
import urllib.request
from pathlib import Path

PAPER, NIGHT, INK, SOFT, FAINT, RED = "#F2EADB", "#1B1916", "#1A1714", "#7A6F62", "#B9AE9C", "#B4432B"
SANS = "'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif"
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
W, H = 1200, 440
PX, PY, PW, PH = 40, 40, 740, 360          # night panel
CX, CY, R = PX + 470, PY + 150, 96         # the moon

Q = """query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
  weeks{ contributionDays{ contributionCount date } } } } } }"""


def fetch(user, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": Q, "variables": {"login": user}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "autumn-moon"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        raise SystemExit(d["errors"])
    weeks = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(x["date"], x["contributionCount"]) for w in weeks for x in w["contributionDays"]]


def streaks(days):
    best = run = 0
    for _, c in days:
        run = run + 1 if c else 0
        best = max(best, run)
    cur = 0
    seq = [c for _, c in days]
    if seq and seq[-1] == 0:      # today isn't over yet: don't break the streak for it
        seq = seq[:-1]
    for c in reversed(seq):
        if not c:
            break
        cur += 1
    return cur, best


def phase_name(f):
    if f <= 0:
        return "NEW MOON"
    if f < .45:
        return "WAXING CRESCENT"
    if f < .55:
        return "FIRST QUARTER"
    if f < 1:
        return "WAXING GIBBOUS"
    return "FULL MOON"


def lit_path(f):
    """Illuminated part of a waxing moon (lit on the right), f = lit fraction 0..1."""
    if f <= 0:
        return ""
    if f >= 1:
        return f"M{CX},{CY-R} A{R},{R} 0 1 1 {CX},{CY+R} A{R},{R} 0 1 1 {CX},{CY-R} Z"
    rx = R * abs(1 - 2 * f)
    sweep = 0 if f < .5 else 1
    return f"M{CX},{CY-R} A{R},{R} 0 0 1 {CX},{CY+R} A{rx:.1f},{R} 0 0 {sweep} {CX},{CY-R} Z"


def grass():
    """Pampas grass (susuki), the plant set out for moon-viewing — ink on ink, barely there."""
    r = random.Random(5)
    out = []
    base = PY + PH
    for i in range(16):
        x = PX + 30 + i * 22 + r.uniform(-6, 6)
        h = r.uniform(70, 150)
        lean = r.uniform(18, 50)
        tip = (x + lean, base - h)
        out.append(f'<path d="M{x:.0f} {base} Q {x + lean*.2:.0f} {base - h*.6:.0f} {tip[0]:.0f} {tip[1]:.0f}" stroke="{PAPER}" '
                   f'stroke-opacity=".28" stroke-width="1.4" fill="none"/>')
        if i % 2 == 0:  # plume
            out.append(f'<g class="sway" style="animation-delay:-{i*.4:.1f}s;transform-origin:{x:.0f}px {base}px">'
                       + "".join(f'<path d="M{tip[0]:.0f} {tip[1]:.0f} q {6+k*3} {8+k*5} {14+k*4} {10+k*7}" stroke="{PAPER}" '
                                 f'stroke-opacity=".22" stroke-width="1" fill="none"/>' for k in range(4)) + '</g>')
    return "".join(out)


def stars():
    r = random.Random(9)
    s = []
    for i in range(46):
        x, y = r.uniform(PX + 14, PX + PW - 14), r.uniform(PY + 12, PY + 210)
        if (x - CX) ** 2 + (y - CY) ** 2 < (R + 30) ** 2:
            continue
        s.append(f'<circle class="tw" style="animation-delay:-{r.uniform(0, 4):.1f}s" cx="{x:.0f}" cy="{y:.0f}" '
                 f'r="{r.choice([.7, .9, 1.2]):.1f}" fill="{PAPER}" fill-opacity=".55"/>')
    return "".join(s)


def cloud(y, x0, w, delay, dur):
    return (f'<g class="cl" style="animation-delay:-{delay}s;animation-duration:{dur}s">'
            f'<path d="M{x0} {y} h{w}" stroke="{NIGHT}" stroke-width="9" stroke-linecap="round"/>'
            f'<path d="M{x0} {y} h{w}" stroke="{PAPER}" stroke-opacity=".5" stroke-width="1.2" stroke-linecap="round"/>'
            f'<path d="M{x0+40} {y+9} h{w*.6:.0f}" stroke="{NIGHT}" stroke-width="7" stroke-linecap="round"/>'
            f'<path d="M{x0+40} {y+9} h{w*.6:.0f}" stroke="{PAPER}" stroke-opacity=".35" stroke-width="1" stroke-linecap="round"/></g>')


def build(days, user="Iamshi-vissa"):
    cur, best = streaks(days) if days else (0, 0)
    f = min(cur / best, 1) if best else 0
    name = phase_name(f)
    lit = lit_path(f)
    litclip = f'<path d="{lit}"/>' if lit else ""

    moon = (f'<circle cx="{CX}" cy="{CY}" r="{R+26}" fill="url(#halo)" opacity="{.25 + .6*f:.2f}"/>'
            f'<circle cx="{CX}" cy="{CY}" r="{R}" fill="url(#tone)" stroke="{PAPER}" stroke-opacity=".35" stroke-width="1"/>'
            + (f'<path class="lit" d="{lit}" fill="{PAPER}"/>' if lit else "") +
            f'<g clip-path="url(#litC)" fill="{FAINT}" fill-opacity=".35">'
            f'<circle cx="{CX+28}" cy="{CY-26}" r="20"/><circle cx="{CX+48}" cy="{CY+18}" r="13"/>'
            f'<circle cx="{CX-10}" cy="{CY+34}" r="16"/><circle cx="{CX-38}" cy="{CY-12}" r="11"/></g>')

    night = (f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="{NIGHT}"/>'
             f'<g clip-path="url(#panel)">{stars()}{moon}'
             f'{cloud(CY+30, CX-260, 300, 0, 70)}{cloud(CY-60, CX+20, 220, 30, 90)}{cloud(PY+60, PX+60, 160, 50, 110)}'
             f'{grass()}</g>'
             f'<rect x="{PX}" y="{PY}" width="{PW}" height="{PH}" fill="none" stroke="{INK}" stroke-width="3"/>')

    tx = PX + PW + 56
    pct = round(f * 100)
    text = (f'<text x="{tx}" y="{PY+22}" font-size="12" letter-spacing="4" fill="{SOFT}">AUTUMN MOON</text>'
            f'<text x="{tx-2}" y="{PY+76}" font-size="40" font-weight="200" fill="{INK}">{name.title()}</text>'
            f'<rect class="rule" x="{tx}" y="{PY+96}" width="90" height="2" fill="{RED}"/>'
            f'<text x="{tx}" y="{PY+150}" font-size="12" letter-spacing="3" fill="{SOFT}">CURRENT STREAK</text>'
            f'<text x="{tx}" y="{PY+190}" font-size="36" font-weight="200" fill="{INK}">{cur}<tspan font-size="15" fill="{SOFT}"> {"day" if cur == 1 else "days"}</tspan></text>'
            f'<text x="{tx+190}" y="{PY+150}" font-size="12" letter-spacing="3" fill="{SOFT}">LONGEST</text>'
            f'<text x="{tx+190}" y="{PY+190}" font-size="36" font-weight="200" fill="{INK}">{best}<tspan font-size="15" fill="{SOFT}"> {"day" if best == 1 else "days"}</tspan></text>'
            f'<rect x="{tx}" y="{PY+222}" width="320" height="3" fill="{FAINT}" fill-opacity=".5"/>'
            f'<rect class="bar" x="{tx}" y="{PY+222}" width="{320*f:.0f}" height="3" fill="{INK}"/>'
            f'<text x="{tx}" y="{PY+248}" font-size="11.5" letter-spacing="2" fill="{SOFT}">{pct}% LIT</text>'
            f'<text x="{tx}" y="{PY+PH-34}" font-size="15" font-weight="300" font-style="italic" fill="{INK}">The moon only fills when the streak does.</text>'
            f'<text x="{tx}" y="{PY+PH-10}" font-size="11" letter-spacing="2" fill="{FAINT}">'
            + f'UPDATED {dt.date.today():%d %b %Y}'.upper() + '</text>')

    defs = (f'<defs><pattern id="tone" width="5" height="5" patternUnits="userSpaceOnUse"><rect width="5" height="5" fill="{NIGHT}"/>'
            f'<circle cx="2.5" cy="2.5" r=".8" fill="{PAPER}" fill-opacity=".22"/></pattern>'
            f'<radialGradient id="halo"><stop offset=".6" stop-color="{PAPER}" stop-opacity=".35"/><stop offset="1" stop-color="{PAPER}" stop-opacity="0"/></radialGradient>'
            f'<clipPath id="panel"><rect x="{PX}" y="{PY}" width="{PW}" height="{PH}"/></clipPath>'
            f'<clipPath id="litC">{litclip}</clipPath></defs>')
    css = (".cl{animation:cl 80s linear infinite}@keyframes cl{from{transform:translateX(-420px)}to{transform:translateX(620px)}}"
           ".tw{animation:tw 4s ease-in-out infinite alternate}@keyframes tw{to{fill-opacity:.12}}"
           ".sway{animation:sway 6s ease-in-out infinite alternate}@keyframes sway{to{transform:rotate(3deg)}}"
           ".lit{animation:glow 1.6s ease-out both}@keyframes glow{from{opacity:0}}"
           ".rule,.bar{transform-box:fill-box;transform-origin:left;animation:grow 1.2s ease-out .3s both}@keyframes grow{from{transform:scaleX(0)}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Autumn moon: {name.lower()}, current streak {cur} days, longest {best} days.">'
            f'<style>{css}{RM}</style>{defs}<rect width="{W}" height="{H}" fill="{PAPER}"/>'
            f'<g font-family="{SANS}">{night}{text}</g></svg>')


def mock(cur=4, best=9):
    end = dt.date.today()
    d = [((end - dt.timedelta(days=364 - i)).isoformat(), 0) for i in range(365)]
    for i in range(100, 100 + best):
        d[i] = (d[i][0], 2)
    for i in range(364 - cur, 364):
        d[i] = (d[i][0], 1)
    return d


if __name__ == "__main__":
    if "--mock" in sys.argv:
        a = sys.argv[sys.argv.index("--mock") + 1:sys.argv.index("--mock") + 3]
        svg = build(mock(*map(int, a)) if len(a) == 2 and all(x.isdigit() for x in a) else mock())
    else:
        svg = build(fetch(os.environ.get("GH_USER", "Iamshi-vissa"), os.environ["GH_TOKEN"]))
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else Path(__file__).parent / "moon.svg"
    Path(out).write_text(svg)
    print("moon.svg written")
