#!/usr/bin/env python3
"""Profile README (v4) — same layout as syedhaamidk/syedhaamidk, content from Iamshi-vissa's repos.
Run `python3 build.py`; upload everything it writes. stats.svg is refreshed by the Action."""
import html
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).parent
e = html.escape
MONO = "'Helvetica Neue',Helvetica,Arial,'Segoe UI',sans-serif"
RM = "@media (prefers-reduced-motion: reduce){*{animation:none!important}}"

USER, NAME, EMAIL = "Iamshi-vissa", "Vamshi", "iamshi725@gmail.com"
LINKEDIN = "https://www.linkedin.com/in/vamshi-bharath-3a1a4b348/"
ROLE = "SOFTWARE DEVELOPER"
SUB = "Training models · designing digital assets · shipping software"
TYPING = ["Teaching Machines · Designing Assets", "Loss Goes Down, Pixels Stay Sharp", "Software Developer · Code Meets Craft"]


def svg(w, h, body, label, style=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{e(label)}"><style>{style}{RM}</style>{body}</svg>')


def typing():
    """Self-hosted version of readme-typing-svg: type, hold, erase, next line."""
    W, H, size = 720, 50, 22
    cw = size * 0.5
    per, n = 6.0, len(TYPING)
    T = per * n
    css, body = [], [f'<rect width="{W}" height="{H}" fill="#000"/>']
    for i, line in enumerate(TYPING):
        L = len(line)
        w = L * cw
        x = (W - w) / 2
        a = i / n * 100
        s = 100 / n
        k = lambda f: a + s * f
        css.append(
            f".m{i}{{transform-box:fill-box;transform-origin:left;animation:m{i} {T}s steps(1) infinite}}"
            f"@keyframes m{i}{{0%{{transform:scaleX(0)}}" +
            "".join(f"{k(.40*j/L):.3f}%{{transform:scaleX({j/L:.3f})}}" for j in range(1, L + 1)) +
            "".join(f"{k(.78 + .18*j/L):.3f}%{{transform:scaleX({(L-j)/L:.3f})}}" for j in range(1, L + 1)) +
            "100%{transform:scaleX(0)}}"
            f".c{i}{{animation:c{i} {T}s steps(1) infinite}}"
            f"@keyframes c{i}{{0%{{opacity:0}}{k(0):.3f}%{{opacity:1;transform:translateX(0)}}" +
            "".join(f"{k(.40*j/L):.3f}%{{opacity:1;transform:translateX({j*cw:.1f}px)}}" for j in range(1, L + 1)) +
            "".join(f"{k(.78 + .18*j/L):.3f}%{{opacity:1;transform:translateX({(L-j)*cw:.1f}px)}}" for j in range(1, L + 1)) +
            f"{k(1):.3f}%{{opacity:0}}100%{{opacity:0}}}}")
        body.append(f'<clipPath id="k{i}"><rect class="m{i}" x="{x:.1f}" y="0" width="{w:.1f}" height="{H}"/></clipPath>'
                    f'<text x="{x:.1f}" y="33" textLength="{w:.1f}" font-family="{MONO}" font-weight="300" letter-spacing="0.5" font-size="{size}" fill="#FFF" clip-path="url(#k{i})">{e(line)}</text>'
                    f'<rect class="c{i}" x="{x+1:.1f}" y="13" width="2" height="26" fill="#FFF" opacity="0"/>')
    return svg(W, H, "".join(body), " · ".join(TYPING), "".join(css))


def rule():
    return svg(1200, 2, '<rect width="1200" height="2" fill="#FFF"/>', "")


def wave():
    W, H = 1200, 90
    d = (f"M0 {H} L0 40 C 150 10, 300 10, 450 38 S 750 70, 900 40 S 1100 10, 1200 30 L1200 {H} Z")
    d2 = (f"M0 {H} L0 55 C 200 30, 350 70, 600 52 S 950 25, 1200 50 L1200 {H} Z")
    return svg(W, H, f'<path d="{d2}" fill="#FFF" fill-opacity=".35"/><path class="w" d="{d}" fill="#FFF"/>', "",
               ".w{animation:w 6s ease-in-out infinite alternate}@keyframes w{to{transform:translateX(-40px)}}")


def badge(label, logo="", url=""):
    img = (f'<img src="https://img.shields.io/badge/{quote(label).replace("-", "--")}-000000?style=flat-square'
           f'{"&logo=" + logo + "&logoColor=FFFFFF" if logo else ""}" alt="{e(label)}" />')
    return f'<a href="{url}">{img}</a>' if url else img


STACK = [("Python", "python", "https://www.python.org/"), ("TypeScript", "typescript", "https://www.typescriptlang.org/"),
         ("React", "react", "https://react.dev/"), ("Next.js", "nextdotjs", "https://nextjs.org/"),
         ("FastAPI", "fastapi", "https://fastapi.tiangolo.com/"), ("Rust", "rust", "https://www.rust-lang.org/"),
         ("Tauri", "tauri", "https://tauri.app/"), ("Electron", "electron", "https://www.electronjs.org/"),
         ("PostgreSQL", "postgresql", "https://www.postgresql.org/"), ("Supabase", "supabase", "https://supabase.com/"),
         ("Redis", "redis", "https://redis.io/"), ("Docker", "docker", "https://www.docker.com/"),
         ("Tailwind", "tailwindcss", "https://tailwindcss.com/"), ("DuckDB", "duckdb", "https://duckdb.org/")]

ARCS = [  # repo, title, one line, stack
    ("CommitRad", "CommitRad", "Scores every commit — even unpushed ones — for the risk it needs a bug fix, and says why. LightGBM trained on 27,384 commits.", "Python · LightGBM · DuckDB · FastAPI · React"),
    ("Hakobu", "Hakobu", "Universal file converter: detects a file's real type from its bytes. ~50 formats, 800+ paths, sandboxed workers.", "FastAPI · Redis/RQ · Next.js · Docker"),
    ("AKSHARA", "AKSHARA", "Document engineering platform to create, inspect and validate DOCX, PDF and PPTX, with immutable versioned storage.", "FastAPI · PostgreSQL · Redis · React"),
    ("X-Editor", "X-Editor", "Local-first desktop IDE with built-in runtime management for Node, Python and Rust.", "Rust · Tauri v2 · React · Monaco"),
    ("Docent", "Docent", "Multi-document Q&amp;A that answers only from your files, citing file and page.", "Python · FAISS · FastAPI · Next.js"),
    ("Shashin", "Shashin", "A private photo diary — one photo a day, visible only to friends, collected into weekly albums.", "React · TypeScript · Supabase"),
    ("X-WALL", "X-WALL", "Scam QR-code and payment-link analyzer: see where a code really sends you before you pay.", "FastAPI · OpenCV · React"),
    ("CoKo", "CoKo", "An animated desk buddy that tracks your sessions, focus and battery — and reacts to them.", "Electron · JavaScript"),
]


def readme():
    gh = f"https://github.com/{USER}"
    arcs = "\n".join(
        f'    <tr>\n      <td><a href="{gh}/{r}"><strong>{t}</strong></a></td>\n      <td>{d}<br /><sub><code>{s}</code></sub></td>\n    </tr>'
        for r, t, d, s in ARCS)
    return f"""<div align="center">

  <a href="{gh}">
    <img src="hero-panel.jpg" alt="Manga panel banner for {NAME}" width="100%" />
  </a>

  <br /><br />

  <img src="profile.jpg" alt="{NAME} profile picture" width="180" />

  <h1>{NAME}</h1>
  <p><strong>{ROLE}</strong><br />{SUB}</p>

  <br />

  <img src="typing.svg" alt="{e(' · '.join(TYPING))}" />

  <br /><br />

  <img src="https://img.shields.io/badge/CHAPTER-01%20%2F%20PROFILE-000000?style=flat-square&labelColor=FFFFFF&color=000000&logoColor=FFFFFF" alt="Chapter one: profile" />

  <br /><br />

  {badge("GitHub", "github", gh)}
  {badge("LinkedIn", "linkedin", LINKEDIN)}
  {badge("Email", "gmail", "mailto:" + EMAIL)}

</div>

<br />

<div align="center">
  <img src="rule.svg" width="100%" alt="" />
</div>

## `01` // The character

I build complete products — **Python services** behind **TypeScript interfaces**, and desktop apps in **Rust** or **Electron** when the browser isn't enough. Lately my work leans into **ML on real data** and **pipelines that stay safe with untrusted input**.

<table>
  <tr>
    <td width="33%" align="center">
      <strong>◇ FULL-STACK</strong><br /><br />
      FastAPI services, Redis workers,<br />Postgres &amp; React frontends.
    </td>
    <td width="33%" align="center">
      <strong>// ML &amp; DATA</strong><br /><br />
      Risk models on git history,<br />retrieval over documents.
    </td>
    <td width="33%" align="center">
      <strong>+ DESKTOP &amp; TOOLS</strong><br /><br />
      Rust/Tauri IDE, Electron apps,<br />CLIs &amp; git hooks.
    </td>
  </tr>
</table>

> **CURRENT ARC**<br />
> Shipping CommitRad, Hakobu and AKSHARA — one careful layer at a time.

<br />

## `02` // The toolkit

<div align="center">
  {chr(10).join("  " + badge(*s) for s in STACK).strip()}
</div>

<table>
  <thead>
    <tr>
      <th>Layer</th>
      <th>Tools &amp; focus</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td><strong>Build</strong></td>
      <td>Python · FastAPI · TypeScript · React · Next.js · Vite</td>
    </tr>
    <tr>
      <td><strong>Store &amp; run</strong></td>
      <td>PostgreSQL · Supabase · Redis / RQ · DuckDB · Docker</td>
    </tr>
    <tr>
      <td><strong>Model</strong></td>
      <td>LightGBM · pandas · FAISS · sentence-transformers · OpenCV</td>
    </tr>
    <tr>
      <td><strong>Ship native</strong></td>
      <td>Rust · Tauri v2 · Electron · Monaco</td>
    </tr>
  </tbody>
</table>

<br />

## `03` // Story arcs

<table>
  <thead>
    <tr>
      <th>Project</th>
      <th>What it does</th>
    </tr>
  </thead>
  <tbody>
{arcs}
  </tbody>
</table>

<br />

## `04` // GitHub pulse

<div align="center">
  <img src="maple.svg" width="100%" alt="Autumn leaves — a maple tree where each leaf is a day of contributions" />
</div>

<br />

## `05` // Behind the panels

<details>
<summary>✦ A few things I enjoy making</summary>

- Tools that read the signals already sitting in your data — like risk hiding in git history.
- Pipelines that treat every input as untrusted and still feel instant.
- Desktop apps that feel native, not like a web page in a frame.
- Small companions and diaries that make a day a little nicer.

</details>

> **CREDO**<br />
> Every bug is a plot twist. Every fix is a new chapter.

<br />

## `06` // Next page

<div align="center">
  {badge("Explore my GitHub", "github", gh + "?tab=repositories")}
  {badge("Let's connect", "linkedin", LINKEDIN)}
  {badge("Say hello", "gmail", "mailto:" + EMAIL)}
</div>

<br />

<div align="center">
  <img src="sunset.svg" width="100%" alt="Sunset over the town — clouds drift, code ships." />
</div>
"""


if __name__ == "__main__":
    (ROOT / "typing.svg").write_text(typing())
    (ROOT / "rule.svg").write_text(rule())
    (ROOT / "README.md").write_text(readme())
    print("built")
