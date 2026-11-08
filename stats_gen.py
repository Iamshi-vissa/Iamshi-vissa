#!/usr/bin/env python3
"""
Writes stats.svg, languages.svg and contributions.svg from your real GitHub data.
Run by .github/workflows/profile-stats.yml (daily + on demand) — no third-party
image services, so nothing can fail to load.

Local use:  GH_TOKEN=<token> GH_USER=Iamshi-vissa python3 stats_gen.py
            python3 stats_gen.py --placeholder   (writes "syncing" cards)
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request
from pathlib import Path

INK, PAPER, SOFT, LINE = "#0A0A0A", "#FAFAFA", "#9A9A9A", "#4D4D4D"
MONO = "'IBM Plex Mono','SFMono-Regular',Consolas,'Liberation Mono',monospace"
SERIF = "Georgia,'Times New Roman',serif"
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
e = html.escape
OUT = Path(__file__).parent
DASH = ' stroke-dasharray="8 6"'

Q = """query($login:String!){ user(login:$login){
  followers{totalCount}
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false, first:100){
    totalCount nodes{ stargazerCount languages(first:10, orderBy:{field:SIZE,direction:DESC}){ edges{ size node{name} } } } }
  contributionsCollection{ totalCommitContributions totalPullRequestContributions totalIssueContributions
    contributionCalendar{ totalContributions weeks{ contributionDays{ contributionCount date } } } } } }"""


def fetch(user, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": Q, "variables": {"login": user}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "profile-stats"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        raise SystemExit(d["errors"])
    u = d["data"]["user"]
    cc = u["contributionsCollection"]
    days = [x for w in cc["contributionCalendar"]["weeks"] for x in w["contributionDays"]]
    langs = {}
    for r in u["repositories"]["nodes"]:
        for ed in r["languages"]["edges"]:
            langs[ed["node"]["name"]] = langs.get(ed["node"]["name"], 0) + ed["size"]
    # streaks
    cur = best = run = 0
    for i, x in enumerate(days):
        run = run + 1 if x["contributionCount"] else 0
        best = max(best, run)
    for x in reversed(days):
        if x["contributionCount"]:
            cur += 1
        elif cur == 0 and x is days[-1]:
            continue  # today not committed yet doesn't break the streak
        else:
            break
    return {
        "Contributions": cc["contributionCalendar"]["totalContributions"],
        "Commits": cc["totalCommitContributions"],
        "Pull requests": cc["totalPullRequestContributions"],
        "Stars": sum(r["stargazerCount"] for r in u["repositories"]["nodes"]),
        "Repos": u["repositories"]["totalCount"],
        "Streak": cur, "Best streak": best,
        "langs": sorted(langs.items(), key=lambda kv: -kv[1])[:6],
        "days": [(x["date"], x["contributionCount"]) for x in days],
    }


def svg(w, h, body, label, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}"><style>{style}{RM}</style>{body}</svg>')


def odometer(value, x, y, size, delay):
    """React Bits CountUp / Saisei AnimatedNumber as rolling digit reels."""
    s = str(value)
    cw = size * 0.62
    out = []
    for i, ch in enumerate(s):
        cx = x + i * cw
        d = int(ch)
        col = "".join(f'<text x="{cx:.1f}" y="{y + k*size*1.2:.1f}">{k}</text>' for k in range(10))
        out.append(f'<g clip-path="url(#reel)"><g class="reel" style="--to:-{d*size*1.2:.1f}px;animation-delay:{delay + i*.08:.2f}s">{col}</g></g>')
    return "".join(out)


def stats_svg(d, placeholder):
    keys = ["Contributions", "Commits", "Pull requests", "Stars", "Streak"]
    W, H = 1200, 190
    cw = (W - 48) / len(keys)
    parts = []
    for i, k in enumerate(keys):
        x = 24 + i * cw
        parts.append(f'<rect x="{x:.0f}" y="24" width="{cw-12:.0f}" height="{H-48}" fill="#111" stroke="{LINE}" '
                     f'stroke-width="1.5"{DASH if placeholder else ""}/>'
                     f'<text x="{x+22:.0f}" y="58" font-size="12" letter-spacing="2" fill="{SOFT}">{e(k.upper())}</text>')
        if placeholder:
            parts.append(f'<text x="{x+22:.0f}" y="118" font-size="44" font-weight="700" fill="{LINE}">—</text>')
        else:
            parts.append(f'<g font-size="44" font-weight="700" fill="{PAPER}">{odometer(d[k], x+22, 118, 44, .2+i*.15)}</g>')
        sub = "days in a row" if k == "Streak" else ("last 12 months" if k in ("Contributions", "Commits", "Pull requests") else "across public repos")
        if k == "Streak" and not placeholder:
            sub = f"best: {d['Best streak']} days"
        parts.append(f'<text x="{x+22:.0f}" y="146" font-size="12" fill="{SOFT}">{e(sub)}</text>')
    tag = "SYNCING — RUN THE ACTION" if placeholder else f"UPDATED {dt.date.today():%d %b %Y}".upper()
    body = (f'<defs><clipPath id="reel" clipPathUnits="userSpaceOnUse"><rect x="0" y="78" width="{W}" height="52"/></clipPath></defs>'
            f'<rect width="{W}" height="{H}" fill="{INK}"/><g font-family="{MONO}">{"".join(parts)}'
            f'<text x="{W-24}" y="{H-6}" text-anchor="end" font-size="11" letter-spacing="2" fill="{LINE}">{tag}</text></g>')
    css = ".reel{animation:reel 1.6s cubic-bezier(.2,.8,.2,1) both}@keyframes reel{from{transform:translateY(0)}to{transform:translateY(var(--to))}}"
    return svg(W, H, body, "GitHub stats", css)


PATTERNS = """<pattern id="p0" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#FAFAFA"/></pattern>
<pattern id="p1" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect width="6" height="6" fill="#0A0A0A"/><rect width="3" height="6" fill="#FAFAFA"/></pattern>
<pattern id="p2" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#0A0A0A"/><circle cx="3" cy="3" r="1.6" fill="#FAFAFA"/></pattern>
<pattern id="p3" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#0A0A0A"/><rect width="6" height="2" fill="#FAFAFA"/></pattern>
<pattern id="p4" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><rect width="6" height="6" fill="#0A0A0A"/><rect width="1.5" height="6" fill="#FAFAFA"/></pattern>
<pattern id="p5" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#9A9A9A"/></pattern>"""


def languages_svg(d, placeholder):
    W, H = 1200, 250
    langs = d["langs"] if not placeholder else [("—", 1)]
    total = sum(v for _, v in langs) or 1
    parts = []
    bx, bw, by = 24, W - 48, 70
    # stacked bar (Saisei: carried by pattern, not hue)
    x = bx
    for i, (n, v) in enumerate(langs):
        w = bw * v / total
        fill = f"url(#p{i})" if not placeholder else "none"
        parts.append(f'<rect class="grow" style="animation-delay:{.2+i*.12:.2f}s" x="{x:.1f}" y="{by}" width="{w:.1f}" height="26" fill="{fill}" stroke="{INK}" stroke-width="2"/>')
        x += w
    parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="26" fill="none" stroke="{PAPER if not placeholder else LINE}" stroke-width="1.5"'
                 f'{DASH if placeholder else ""}/>')
    # legend
    for i, (n, v) in enumerate(langs if not placeholder else []):
        lx = bx + (i % 3) * 390
        ly = 140 + (i // 3) * 44
        parts.append(f'<g class="up" style="animation-delay:{.6+i*.08:.2f}s"><rect x="{lx}" y="{ly-16}" width="20" height="20" fill="url(#p{i})" stroke="{PAPER}"/>'
                     f'<text x="{lx+32}" y="{ly}" font-size="16" fill="{PAPER}">{e(n)}</text>'
                     f'<text x="{lx+330}" y="{ly}" text-anchor="end" font-size="16" fill="{SOFT}">{v/total*100:.1f}%</text></g>')
    if placeholder:
        parts.append(f'<text x="{W/2}" y="170" text-anchor="middle" font-size="13" letter-spacing="2" fill="{LINE}">SYNCING — RUN THE ACTION</text>')
    body = (f'<defs>{PATTERNS}</defs><rect width="{W}" height="{H}" fill="{INK}"/><g font-family="{MONO}">'
            f'<text x="24" y="44" font-size="12" letter-spacing="3" fill="{SOFT}">LANGUAGES · BY BYTES IN PUBLIC REPOS</text>{"".join(parts)}</g>')
    css = (".grow{animation:grow .9s cubic-bezier(.2,.8,.2,1) both;transform-box:fill-box;transform-origin:left}"
           "@keyframes grow{from{transform:scaleX(0)}to{transform:none}}"
           ".up{animation:up .6s ease-out both}@keyframes up{from{opacity:0;transform:translateY(10px)}to{opacity:1;transform:none}}")
    return svg(W, H, body, "Most used languages", css)


def contributions_svg(d, placeholder):
    W, H = 1200, 230
    days = d["days"] if not placeholder else []
    if placeholder:
        start = dt.date.today() - dt.timedelta(days=364)
        days = [((start + dt.timedelta(days=i)).isoformat(), 0) for i in range(365)]
    mx = max([c for _, c in days] + [1])
    s, g = 16, 4
    first = dt.date.fromisoformat(days[0][0])
    off = (first.weekday() + 1) % 7  # Sunday-first rows like GitHub
    cols = (len(days) + off + 6) // 7
    x0 = (W - cols * (s + g)) / 2
    cells = []
    for i, (date, c) in enumerate(days):
        k = i + off
        col, row = divmod(k, 7)
        lvl = 0 if c == 0 else min(4, 1 + int(3 * c / mx))
        op = [0.07, 0.3, 0.55, 0.8, 1][lvl]
        dash = ' stroke="#4D4D4D" stroke-dasharray="2 2"' if placeholder else ""
        cells.append(f'<rect class="c" style="animation-delay:{(col+row)*0.012:.3f}s" x="{x0+col*(s+g):.0f}" y="{50+row*(s+g)}" '
                     f'width="{s}" height="{s}" fill="{PAPER}" fill-opacity="{op}"{dash}><title>{date}: {c}</title></rect>')
    total = sum(c for _, c in days)
    head = "SYNCING — RUN THE ACTION" if placeholder else f"{total} CONTRIBUTIONS · LAST 12 MONTHS"
    legend = "".join(f'<rect x="{W-64-5*22+i*22}" y="{H-24}" width="16" height="16" fill="{PAPER}" fill-opacity="{o}"/>'
                     for i, o in enumerate([0.07, 0.3, 0.55, 0.8, 1]))
    body = (f'<rect width="{W}" height="{H}" fill="{INK}"/><g font-family="{MONO}">'
            f'<text x="24" y="32" font-size="12" letter-spacing="3" fill="{SOFT}">{head}</text>{"".join(cells)}'
            f'<text x="{W-64-5*22-10}" y="{H-11}" text-anchor="end" font-size="11" fill="{SOFT}">less</text>{legend}'
            f'<text x="{W-58}" y="{H-11}" font-size="11" fill="{SOFT}">more</text>'
            f'<text x="24" y="{H-11}" font-size="11" letter-spacing="2" fill="{LINE}">EACH SQUARE IS A PANEL</text></g>')
    css = ".c{animation:c .5s ease-out both}@keyframes c{from{opacity:0;transform:scale(.3)}to{opacity:1;transform:none}}.c{transform-box:fill-box;transform-origin:center}"
    return svg(W, H, body, "Contribution heatmap", css)


def main():
    placeholder = "--placeholder" in sys.argv
    if "--mock" in sys.argv:
        import random
        random.seed(3)
        start = dt.date.today() - dt.timedelta(days=364)
        days = [((start + dt.timedelta(days=i)).isoformat(), random.choice([0, 0, 1, 2, 3, 5, 8])) for i in range(365)]
        d = {"Contributions": 812, "Commits": 640, "Pull requests": 37, "Stars": 54, "Repos": 21, "Streak": 12, "Best streak": 31,
             "langs": [("JavaScript", 50), ("TypeScript", 20), ("Python", 12), ("CSS", 9), ("HTML", 6), ("Java", 3)], "days": days}
    elif placeholder:
        d = {}
    else:
        d = fetch(os.environ.get("GH_USER", "Iamshi-vissa"), os.environ["GH_TOKEN"])
    (OUT / "stats.svg").write_text(stats_svg(d, placeholder))
    (OUT / "languages.svg").write_text(languages_svg(d, placeholder))
    (OUT / "contributions.svg").write_text(contributions_svg(d, placeholder))
    print("stats written", "(placeholder)" if placeholder else "")


if __name__ == "__main__":
    main()
