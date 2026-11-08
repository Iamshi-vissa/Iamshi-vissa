#!/usr/bin/env python3
"""
Autumn leaves · The maple tree — writes maple.svg from your GitHub contribution calendar.

Each leaf is one day you contributed.
  · last 30 days  → still on the branches, in maple red
  · older months  → fallen, one ink pile per month on the ground
  · leaf tone     → outline (1–2 contributions) · screentone (3–5) · solid ink (6+)
Fallen leaves return to the roots.

Run by .github/workflows/profile-stats.yml.  Local test:  python3 maple_gen.py --mock
"""
import datetime as dt
import hashlib
import json
import math
import os
import random
import sys
import urllib.request
from pathlib import Path

PAPER, PAPER2, INK, SOFT, RED = "#F2EADB", "#E7DCC6", "#1A1714", "#7A6F62", "#B4432B"
MONO = "'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif"
SERIF = MONO
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
W, H = 1200, 600
GROUND = 470
TRUNK_X = 330

LEAF = ("M0,-10 L1.5,-6 L5,-7.5 L4,-3.5 L9,-4 L6.5,-0.5 L8.5,2 L3,2 L3.5,5 L0.5,3 L0.5,9 L-0.5,9 "
        "L-0.5,3 L-3.5,5 L-3,2 L-8.5,2 L-6.5,-0.5 L-9,-4 L-4,-3.5 L-5,-7.5 L-1.5,-6 Z")

Q = """query($login:String!){ user(login:$login){ contributionsCollection{ contributionCalendar{
  totalContributions weeks{ contributionDays{ contributionCount date } } } } } }"""


def fetch(user, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": Q, "variables": {"login": user}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "maple-tree"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        raise SystemExit(d["errors"])
    weeks = d["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(x["date"], x["contributionCount"]) for w in weeks for x in w["contributionDays"]]


def mock():
    r = random.Random(4)
    end = dt.date.today()
    return [((end - dt.timedelta(days=364 - i)).isoformat(),
             r.choice([0, 0, 0, 1, 2, 3, 4, 6, 9])) for i in range(365)]


# ── tree ─────────────────────────────────────────────────────────────
def grow():
    r = random.Random(1709)  # fixed: the tree's shape never changes, only its leaves
    paths, tips = [], []

    def branch(x, y, ang, ln, wd, depth, delay):
        bend = r.uniform(-.25, .25)
        x2 = x + ln * math.cos(ang)
        y2 = y + ln * math.sin(ang)
        cx = (x + x2) / 2 + ln * .18 * math.cos(ang + math.pi / 2) * bend * 4
        cy = (y + y2) / 2 + ln * .18 * math.sin(ang + math.pi / 2) * bend * 4
        paths.append((f"M{x:.1f},{y:.1f} Q{cx:.1f},{cy:.1f} {x2:.1f},{y2:.1f}", wd, delay, ln))
        if depth == 0 or ln < 9:
            tips.append((x2, y2))
            return
        n = 3 if depth > 4 and r.random() < .35 else 2
        spread = r.uniform(.32, .55)
        for k in range(n):
            a = ang + spread * (k - (n - 1) / 2) * 1.6 + r.uniform(-.12, .12)
            branch(x2, y2, a, ln * r.uniform(.66, .8), wd * .64, depth - 1, delay + .12)

    # trunk: a slightly leaning, tapering stroke, then the crown
    branch(TRUNK_X, GROUND + 4, -math.pi / 2 - .06, 120, 26, 7, 0)
    return paths, tips


def leaf(x, y, s, rot, tone, extra=""):
    fill = {"red": RED, "ink": INK, "tone": "url(#tone)", "line": PAPER}[tone]
    stroke = RED if tone == "red" else INK
    return (f'<g transform="translate({x:.1f} {y:.1f}) rotate({rot:.0f}) scale({s:.2f})"><g{extra}>'
            f'<path d="{LEAF}" fill="{fill}" stroke="{stroke}" stroke-width="{1.1/s:.2f}" stroke-linejoin="round"/></g></g>')


def tone_of(c):
    return "line" if c <= 2 else ("tone" if c <= 5 else "ink")


def build(days, placeholder=False):
    today = dt.date.fromisoformat(days[-1][0]) if days else dt.date.today()
    cut = today - dt.timedelta(days=29)
    recent = [(d, c) for d, c in days if c and dt.date.fromisoformat(d) >= cut]
    older = [(d, c) for d, c in days if c and dt.date.fromisoformat(d) < cut]
    total = sum(c for _, c in days)
    active = sum(1 for _, c in days if c)

    paths, tips = grow()
    out = []

    # paper, sky screentone, panel border
    out.append(f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
               f'<rect x="20" y="20" width="{W-40}" height="{GROUND-20}" fill="url(#sky)"/>')

    # roots + ground brush line
    out.append(f'<path d="M24 {GROUND} C 300 {GROUND-3}, 700 {GROUND+3}, {W-24} {GROUND-1}" stroke="{INK}" stroke-width="3" fill="none"/>')
    for i in range(14):
        x = 30 + i * 85 + (i * 37) % 23
        out.append(f'<path d="M{x} {GROUND+12} q 14 -3 28 0" stroke="{INK}" stroke-width="1" fill="none" opacity=".45"/>')

    # branches (drawn on, trunk first)
    for d, wd, delay, ln in paths:
        out.append(f'<path class="br" style="animation-delay:{delay:.2f}s;stroke-dasharray:{ln*1.3:.0f};stroke-dashoffset:{ln*1.3:.0f}" '
                   f'd="{d}" stroke="{INK}" stroke-width="{max(wd,1.1):.1f}" stroke-linecap="round" fill="none"/>')

    # leaves on the branches: last 30 days
    for d, c in recent:
        h = int(hashlib.md5(d.encode()).hexdigest(), 16)
        tx, ty = tips[h % len(tips)]
        r = random.Random(h)
        s = .9 + min(c, 12) * .06
        out.append(leaf(tx + r.uniform(-9, 9), ty + r.uniform(-9, 9), s, r.uniform(-40, 40), "red",
                        f' class="lf" style="animation-delay:{1.3 + (h % 60) / 60:.2f}s"'))

    # fallen piles: one per month, oldest → newest, right of the tree
    months = {}
    for d, c in older:
        k = d[:7]
        months.setdefault(k, []).append((d, c))
    order = sorted(months)[-11:]
    slots = [(today.replace(day=1) - dt.timedelta(days=31 * i)).strftime("%Y-%m") for i in range(11, 0, -1)]
    slots = sorted(set(slots) | set(order))[-11:]
    px0, pstep = 590, 50
    for i, k in enumerate(slots):
        cx = px0 + i * pstep
        pile = months.get(k, [])
        for j, (d, c) in enumerate(sorted(pile, key=lambda t: t[1])):
            r = random.Random(d)
            row = j // 5
            spread = max(19 - row * 3, 5)
            out.append(leaf(cx + r.uniform(-spread, spread), GROUND - 6 - row * 5 - r.uniform(0, 3), .72, r.uniform(0, 360), tone_of(c),
                            f' class="pl" style="animation-delay:{.4 + i*.08 + j*.01:.2f}s"'))
        label = dt.date.fromisoformat(k + "-01").strftime("%b").upper()
        out.append(f'<text x="{cx}" y="{GROUND+34}" text-anchor="middle" font-family="{MONO}" font-weight="300" font-size="11" fill="{SOFT}">{label}</text>'
                   f'<text x="{cx}" y="{GROUND+50}" text-anchor="middle" font-family="{MONO}" font-weight="300" font-size="10" fill="{SOFT}" opacity=".7">{len(pile)}</text>')

    # leaves still falling (loop)
    for i in range(5):
        tx, ty = tips[(i * 29 + 7) % len(tips)]
        dx = 120 + i * 95
        out.append(f'<g class="fall f{i}" style="--dx:{dx}px;--dy:{GROUND - ty - 10:.0f}px;animation-delay:{2.5 + i*1.7:.1f}s">'
                   f'{leaf(tx, ty, 1, 0, "red")}</g>')

    # title, idiom, captions
    out.append(f'<text x="{W-48}" y="66" text-anchor="end" font-family="{SERIF}" font-weight="300" font-size="30" letter-spacing="6" fill="{INK}">AUTUMN LEAVES</text>'
               f'<text x="{W-48}" y="90" text-anchor="end" font-family="{MONO}" font-weight="300" font-size="12" letter-spacing="3" fill="{SOFT}">A YEAR OF WORK, ONE LEAF A DAY</text>')
    out.append(f'<text transform="translate(58 {GROUND-20}) rotate(-90)" font-family="{MONO}" font-weight="300" font-size="12" letter-spacing="4" fill="{SOFT}">FALLEN LEAVES RETURN TO THE ROOTS</text>')
    cap = ("THE FIRST SEASON IS STILL GROWING — RUN THE ACTION" if placeholder else
           f"{active} LEAVES · {total} CONTRIBUTIONS · LAST 12 MONTHS")
    out.append(f'<text x="44" y="{H-56}" font-family="{MONO}" font-weight="300" font-size="12" letter-spacing="3" fill="{INK}">{cap}</text>'
               f'<text x="44" y="{H-36}" font-family="{MONO}" font-weight="300" font-size="10.5" letter-spacing="2" fill="{SOFT}">'
               f'EACH LEAF IS A DAY I SHIPPED · RED STILL HANGS · INK HAS FALLEN</text>')
    # seal
    out.append(f'<g transform="translate({W-96} {H-96})"><rect width="50" height="50" rx="4" fill="none" stroke="{RED}" stroke-width="2.5"/>'
               f'<text x="25" y="34" text-anchor="middle" font-family="{SERIF}" font-weight="300" font-size="26" fill="{RED}">V</text></g>'
               f'<text x="{W-108}" y="{H-52}" text-anchor="end" font-family="{MONO}" font-weight="300" font-size="10" letter-spacing="2" fill="{SOFT}">'
               + f'{today:%d %b %Y}'.upper() + '</text>')
    # manga panel frame
    out.append(f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="{INK}" stroke-width="4"/>')

    defs = (f'<defs><pattern id="tone" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="4" fill="{PAPER}"/>'
            f'<circle cx="2" cy="2" r="1" fill="{INK}"/></pattern>'
            f'<pattern id="dot" width="7" height="7" patternUnits="userSpaceOnUse"><circle cx="3.5" cy="3.5" r=".9" fill="{INK}" fill-opacity=".16"/></pattern>'
            f'<linearGradient id="fadeS" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stop-color="#fff"/><stop offset=".55" stop-color="#fff" stop-opacity="0"/></linearGradient>'
            f'<mask id="skyM"><rect width="{W}" height="{H}" fill="url(#fadeS)"/></mask>'
            f'<pattern id="skyP" width="{W}" height="{H}" patternUnits="userSpaceOnUse"><rect width="{W}" height="{H}" fill="url(#dot)" mask="url(#skyM)"/></pattern></defs>')
    defs = defs.replace('fill="url(#sky)"', 'fill="url(#skyP)"')
    css = (".br{animation:br 1.1s ease-out both}@keyframes br{to{stroke-dashoffset:0}}"
           ".lf{animation:lf .6s cubic-bezier(.3,1.6,.5,1) both;transform-box:fill-box;transform-origin:center}"
           "@keyframes lf{from{opacity:0;transform:scale(.2)}}"
           ".pl{animation:pl .5s ease-out both}@keyframes pl{from{opacity:0;transform:translateY(-14px)}}"
           ".fall{opacity:0;animation:fall 7s ease-in infinite}"
           "@keyframes fall{0%{opacity:0;transform:translate(0,0) rotate(0)}6%{opacity:1}"
           "30%{transform:translate(calc(var(--dx)*.25),calc(var(--dy)*.3)) rotate(80deg)}"
           "55%{transform:translate(calc(var(--dx)*.6),calc(var(--dy)*.6)) rotate(-30deg)}"
           "85%{opacity:1}100%{opacity:0;transform:translate(var(--dx),var(--dy)) rotate(160deg)}}")
    body = "".join(out).replace('fill="url(#sky)"', 'fill="url(#skyP)"')
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="A maple tree: each leaf is a day of contributions. {active} days, {total} contributions in the last year.">'
            f'<style>{css}{RM}</style>{defs}{body}</svg>')


if __name__ == "__main__":
    if "--mock" in sys.argv:
        svg = build(mock())
    elif "--placeholder" in sys.argv:
        svg = build([], placeholder=True)
    else:
        svg = build(fetch(os.environ.get("GH_USER", "Iamshi-vissa"), os.environ["GH_TOKEN"]))
    Path(sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else Path(__file__).parent / "maple.svg").write_text(svg)
    print("maple.svg written")
