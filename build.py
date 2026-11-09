#!/usr/bin/env python3
"""Profile README (v4) — same layout as syedhaamidk/syedhaamidk, content from Iamshi-vissa's repos.
Run `python3 build.py`; upload everything it writes. stats.svg is refreshed by the Action."""
import base64
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
SUB = "Training models · designing digital assets · building software"
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


LI_MARK = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><rect width="24" height="24" rx="3" fill="#FFF"/>'
           '<rect x="5" y="9.5" width="3" height="9.5" fill="#000"/><circle cx="6.5" cy="6.3" r="1.8" fill="#000"/>'
           '<path d="M10 9.5h2.9v1.4c.5-.9 1.6-1.6 3.1-1.6 2.6 0 3.5 1.6 3.5 4.3V19h-3v-4.8c0-1.3-.3-2.2-1.5-2.2s-2 .9-2 2.3V19h-3z" fill="#000"/></svg>')
LI_LOGO = "data:image/svg+xml;base64," + base64.b64encode(LI_MARK.encode()).decode()


def badge(label, logo="", url=""):
    img = (f'<img src="https://img.shields.io/badge/{quote(label).replace("-", "--")}-000000?style=flat-square'
           f'{("&logo=" + quote(LI_LOGO, safe="") if logo == "linkedin" else "&logo=" + logo + "&logoColor=FFFFFF") if logo else ""}" alt="{e(label)}" />')
    return f'<a href="{url}">{img}</a>' if url else img


STACK = [("Python", "python", "https://www.python.org/"), ("TypeScript", "typescript", "https://www.typescriptlang.org/"),
         ("React", "react", "https://react.dev/"), ("Next.js", "nextdotjs", "https://nextjs.org/"),
         ("FastAPI", "fastapi", "https://fastapi.tiangolo.com/"), ("Rust", "rust", "https://www.rust-lang.org/"),
         ("Tailwind CSS", "tailwindcss", "https://tailwindcss.com/"), ("Docker", "docker", "https://www.docker.com/")]

def readme():
    gh = f"https://github.com/{USER}"
    return f"""<div align="center">

  <a href="{gh}">
    <img src="banner.jpg" alt="Banner for {NAME}" width="100%" />
  </a>

  <br />

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

I build software that learns and looks good doing it — models trained on real data, digital assets designed with care, and the code that brings them together. I enjoy working where machine learning meets visual craft, turning rough ideas into things people want to come back to.

<table>
  <tr>
    <td width="33%" align="center">
      <strong>◇ MODELS</strong><br /><br />
      Training, evaluation<br />&amp; retrieval on real data.
    </td>
    <td width="33%" align="center">
      <strong>// DESIGN</strong><br /><br />
      Digital assets, interfaces<br />&amp; quiet motion.
    </td>
    <td width="33%" align="center">
      <strong>+ SOFTWARE</strong><br /><br />
      Full-stack products,<br />desktop apps &amp; tooling.
    </td>
  </tr>
</table>

> **CURRENT ARC**<br />
> Teaching models to see what matters, and designing what people see.

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
      <td><strong>Train</strong></td>
      <td>Python · LightGBM · pandas · sentence-transformers · FAISS · OpenCV</td>
    </tr>
    <tr>
      <td><strong>Shape</strong></td>
      <td>Digital assets · interfaces · motion · Tailwind · responsive interaction design</td>
    </tr>
    <tr>
      <td><strong>Build</strong></td>
      <td>TypeScript · React · Next.js · FastAPI · Rust · Tauri · Docker</td>
    </tr>
  </tbody>
</table>

<br />

## `03` // Autumn moon

<div align="center">
  <img src="moon.svg" width="100%" alt="Autumn moon: the moon waxes with my current commit streak and is full only when it matches my longest" />
</div>

<br />

## `04` // Next page

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
