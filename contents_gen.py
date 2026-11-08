#!/usr/bin/env python3
"""
Contents · Volume 01 — writes contents.svg from your public GitHub repos.

Every public repo is a chapter, in the order you created them.
Every commit is a page, so a chapter's page number is where it starts in the book
of everything you've committed, and the gap to the next chapter is how long it runs.

Run by .github/workflows/profile-stats.yml.  Local test:  python3 contents_gen.py --mock
"""
import datetime as dt
import html
import json
import os
import sys
import urllib.request
from pathlib import Path

PAPER, INK, SOFT, FAINT, RED = "#F2EADB", "#1A1714", "#7A6F62", "#B9AE9C", "#B4432B"
SANS = "'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif"
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"
e = html.escape
SKIP = {"iamshi-vissa"}  # the profile repo itself
MIN_COMMITS = 2          # single-commit repos are left out unless they're a known project (BLURBS)

# Used when a repo has no description on GitHub
BLURBS = {
    "commitrad": "Scores every commit for the risk it needs a bug fix",
    "hakobu": "Universal file converter, 800+ conversion paths",
    "akshara": "Document engineering for DOCX, PDF and PPTX",
    "x-editor": "Local-first desktop IDE with runtime management",
    "docent": "Multi-document Q&A with page-level citations",
    "shashin": "A private photo diary, one photo a day",
    "x-wall": "Scam QR-code and payment-link analyzer",
    "coko": "An animated desk buddy that tracks your day",
}

Q = """query($login:String!){ user(login:$login){
  repositories(ownerAffiliations:OWNER, privacy:PUBLIC, isFork:false, first:100,
               orderBy:{field:CREATED_AT, direction:ASC}){
    nodes{ name description defaultBranchRef{ target{ ... on Commit{ history{ totalCount } } } } } } } }"""


def fetch(user, token):
    req = urllib.request.Request("https://api.github.com/graphql",
                                 data=json.dumps({"query": Q, "variables": {"login": user}}).encode(),
                                 headers={"Authorization": f"bearer {token}", "User-Agent": "contents-page"})
    d = json.load(urllib.request.urlopen(req))
    if "errors" in d:
        raise SystemExit(d["errors"])
    out = []
    for n in d["data"]["user"]["repositories"]["nodes"]:
        ref = n["defaultBranchRef"]
        commits = ref["target"]["history"]["totalCount"] if ref and ref.get("target") else 0
        out.append((n["name"], n["description"] or "", commits))
    return out


def mock():
    return [("Void-Voyager", "", 1), ("CoKo", "", 14), ("Docent", "", 23), ("X-Editor", "", 31), ("X-WALL", "", 12),
            ("Transula", "", 1), ("CommitRad", "", 58), ("Hakobu", "", 41), ("AKSHARA", "", 36), ("Shashin", "", 19)]


def blurb(name, desc):
    t = desc.strip() or BLURBS.get(name.lower(), "")
    return t if len(t) <= 62 else t[:60].rstrip() + "…"


def build(repos, user="Iamshi-vissa"):
    chapters = [(n, d, c) for n, d, c in repos
                if n.lower() not in SKIP and c > 0 and (c >= MIN_COMMITS or n.lower() in BLURBS or d.strip())]
    W = 1200
    top, rh = 70, 62
    H = top + (len(chapters) + 1) * rh + 96
    lx = 380            # chapter column
    rx = W - 64         # page-number column (right aligned)
    parts = []

    # left column: the half-title page
    parts.append(f'<text x="64" y="{top+28}" font-size="12" letter-spacing="4" fill="{SOFT}">VOLUME 01</text>'
                 f'<text x="60" y="{top+92}" font-size="62" font-weight="200" letter-spacing="1" fill="{INK}">Contents</text>'
                 f'<rect class="rule" x="64" y="{top+118}" width="120" height="2" fill="{RED}"/>'
                 f'<text x="64" y="{top+152}" font-size="15" font-weight="300" fill="{INK}">Vamshi</text>'
                 f'<text x="64" y="{top+174}" font-size="12" font-weight="300" letter-spacing="1" fill="{SOFT}">@{e(user)}</text>')
    parts.append(f'<line x1="{lx-48}" y1="{top}" x2="{lx-48}" y2="{H-70}" stroke="{FAINT}"/>')

    page = 1
    for i, (name, desc, commits) in enumerate(chapters):
        y = top + i * rh
        d = f"animation-delay:{.15 + i*.09:.2f}s"
        title_w = sum(14.5 if ch.isupper() else 11 for ch in name)
        lead_x1, lead_x2 = lx + 64 + title_w + 16, rx - len(str(page)) * 11.5 - 14
        parts.append(f'<g class="row" style="{d}">'
                     f'<text x="{lx}" y="{y+26}" font-size="14" font-weight="300" letter-spacing="2" fill="{SOFT}">{i+1:02d}</text>'
                     f'<text x="{lx+64}" y="{y+26}" font-size="21" font-weight="300" fill="{INK}">{e(name)}</text>'
                     f'<text x="{lx+64}" y="{y+48}" font-size="12.5" font-weight="300" fill="{SOFT}">{e(blurb(name, desc))}</text>'
                     f'<line class="lead" style="{d}" x1="{lead_x1:.0f}" y1="{y+22}" x2="{lead_x2}" y2="{y+22}" stroke="{FAINT}" '
                     f'stroke-width="2" stroke-dasharray="1.5 6" stroke-linecap="round"/>'
                     f'<text x="{rx}" y="{y+26}" text-anchor="end" font-size="19" font-weight="300" fill="{INK}">{page}</text>'
                     f'</g>')
        page += commits

    # the next chapter hasn't been written yet: it starts on the next commit
    y = top + len(chapters) * rh
    parts.append(f'<g class="row" style="animation-delay:{.2 + len(chapters)*.09:.2f}s">'
                 f'<text x="{lx}" y="{y+26}" font-size="14" font-weight="300" letter-spacing="2" fill="{RED}">{len(chapters)+1:02d}</text>'
                 f'<text x="{lx+64}" y="{y+26}" font-size="21" font-weight="300" font-style="italic" fill="{RED}">To be continued</text>'
                 f'<line x1="{lx+64+190}" y1="{y+22}" x2="{rx - len(str(page)) * 11.5 - 14:.0f}" y2="{y+22}" stroke="{RED}" stroke-opacity=".5" stroke-width="2" '
                 f'stroke-dasharray="1.5 6" stroke-linecap="round"/>'
                 f'<text x="{rx}" y="{y+26}" text-anchor="end" font-size="19" font-weight="300" fill="{RED}">{page}</text>'
                 f'<rect class="caret" x="{rx+8}" y="{y+8}" width="2" height="22" fill="{RED}"/></g>')

    # colophon
    parts.append(f'<line x1="64" y1="{H-62}" x2="{W-64}" y2="{H-62}" stroke="{FAINT}"/>'
                 f'<text x="64" y="{H-34}" font-size="11" font-weight="300" letter-spacing="3" fill="{SOFT}">'
                 f'{len(chapters)} CHAPTERS · {page-1} PAGES SO FAR</text>'
                 f'<text x="{W-64}" y="{H-34}" text-anchor="end" font-size="11" font-weight="300" letter-spacing="3" fill="{FAINT}">'
                 + f'ONE PAGE PER COMMIT · {dt.date.today():%d %b %Y}'.upper() + '</text>')

    css = (".row{animation:row .7s ease-out both}@keyframes row{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}"
           ".lead{stroke-dashoffset:600;animation:lead 1.6s ease-out both}@keyframes lead{from{stroke-dashoffset:600}to{stroke-dashoffset:0}}"
           ".rule{transform-box:fill-box;transform-origin:left;animation:rule 1s ease-out .2s both}@keyframes rule{from{transform:scaleX(0)}}"
           ".caret{animation:caret 1.1s steps(1) infinite}@keyframes caret{50%{opacity:0}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" '
            f'aria-label="Contents, volume 01: {len(chapters)} chapters, one page per commit.">'
            f'<style>{css}{RM}</style>'
            f'<rect width="{W}" height="{H}" fill="{PAPER}"/>'
            f'<rect x="20" y="20" width="{W-40}" height="{H-40}" fill="none" stroke="{INK}" stroke-width="4"/>'
            f'<g font-family="{SANS}">{"".join(parts)}</g></svg>')


if __name__ == "__main__":
    if "--mock" in sys.argv:
        svg = build(mock())
    else:
        svg = build(fetch(os.environ.get("GH_USER", "Iamshi-vissa"), os.environ["GH_TOKEN"]),
                    os.environ.get("GH_USER", "Iamshi-vissa"))
    out = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else Path(__file__).parent / "contents.svg"
    Path(out).write_text(svg)
    print("contents.svg written")
