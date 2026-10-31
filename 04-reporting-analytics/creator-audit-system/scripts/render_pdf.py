#!/usr/bin/env python3
"""Render an audit report (markdown) to an ALTR-branded PDF.

Usage: python3 scripts/render_pdf.py reports/<handle>-<date>.md [out.pdf]

Pipeline: pandoc (md -> html fragment) -> inject into branded shell with
brand/brand.css (relative images embedded as base64) -> headless Chrome -> PDF.
"""
import base64
import mimetypes
import re
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
BRAND_NAME = "ALTR"

SHELL = """<!DOCTYPE html>
<html><head><meta charset="utf-8"><style>{css}</style></head>
<body>
<section class="cover">
  <div class="wordmark">{wordmark}</div>
  <div class="rule"></div>
  <h1>{title}</h1>
  <div class="handle">{handle}</div>
  <div class="meta">
    <b>Prepared</b> &nbsp;{prepared}<br>
    <b>Prepared by</b> &nbsp;{brand}<br>
    <b>Scope</b> &nbsp;{scope}
  </div>
  <div class="confidential">Confidential &mdash; prepared for the account owner</div>
</section>
<table class="pagewrap">
<thead><tr><td><div class="pagepad-t"></div></td></tr></thead>
<tbody><tr><td><div class="report-body">
{body}
</div></td></tr></tbody>
<tfoot><tr><td><div class="pagepad-b"></div></td></tr></tfoot>
</table>
</body></html>"""

SEV_RE = re.compile(r"\b(CRITICAL|HIGH|MEDIUM|LOW)\b")


def badge(m: re.Match) -> str:
    s = m.group(1)
    return f'<span class="sev sev-{s.lower()}">{s}</span>'


def data_uri(path: Path) -> str:
    mime = mimetypes.guess_type(path.name)[0] or "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()


def embed_images(body: str, base: Path) -> str:
    def sub(m: re.Match) -> str:
        src = m.group(2)
        if src.startswith(("http://", "https://", "data:")):
            return m.group(0)
        p = (base / src).resolve()
        if not p.exists():
            print(f"warning: image not found: {src}", file=sys.stderr)
            return m.group(0)
        return m.group(1) + data_uri(p) + m.group(3)
    return re.sub(r'(<img[^>]*\bsrc=")([^"]+)(")', sub, body)


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_suffix(".pdf")

    md = src.read_text()
    # Cover title/subject come from the report's own H1: "<Title> — <Subject>"
    m = re.search(r"^#\s+(.+?)(?:\s+—\s+(.+))?\s*$", md, re.M)
    raw_title = (m.group(1).strip() if m else "Account Audit")
    handle = (m.group(2).strip() if m and m.group(2) else src.stem.split("-2")[0])
    words = raw_title.split()
    cut = max(1, (len(words) + 1) // 2)
    title = " ".join(words[:cut]) + "<br>" + " ".join(words[cut:]) if len(words) > 1 else raw_title
    m = re.search(r"\*\*Scope:\*\*\s*([^\n]+)", md)
    scope = (m.group(1).split(".")[0].split(";")[0].strip() if m
             else "Public profile, link funnel, recent content review")
    if len(scope) > 70:
        scope = scope[:67].rsplit(" ", 1)[0] + "…"
    m = re.search(r"\*\*Prepared:\*\*\s*(.+)", md)
    prepared = m.group(1).strip() if m else date.today().strftime("%B %d, %Y")

    # The cover page carries title + metadata; strip them from the body
    # (everything from the H1 through the first horizontal rule).
    md = re.sub(r"\A# .*?\n---+\n", "", md, count=1, flags=re.S)

    body = subprocess.run(
        ["pandoc", "-f", "gfm", "-t", "html"],
        input=md, check=True, capture_output=True, text=True,
    ).stdout
    body = SEV_RE.sub(badge, body)
    # Section kickers: "2. Account-Level Findings" -> mono "02 /" above title
    body = re.sub(
        r"(<h2[^>]*>)(\d+)\.\s*",
        lambda m: f'{m.group(1)}<span class="hnum">{int(m.group(2)):02d} /</span>',
        body)
    body = embed_images(body, src.parent)

    css = (ROOT / "brand" / "brand.css").read_text()

    wordmark = f'<span class="wm-text">{BRAND_NAME}</span>'
    for logo in (ROOT / "brand" / "logo-mark.png", ROOT / "brand" / "logo.svg",
                 ROOT / "brand" / "logo.png"):
        if logo.exists():
            wordmark = (f'<img src="{data_uri(logo)}" alt="{BRAND_NAME}">'
                        f'<span class="wm-text">{BRAND_NAME}</span>')
            break

    html = SHELL.format(css=css, body=body, handle=handle, title=title,
                        scope=scope, prepared=prepared, wordmark=wordmark,
                        brand=BRAND_NAME)

    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html)
        tmp = f.name

    subprocess.run(
        [CHROME, "--headless", "--disable-gpu", "--no-pdf-header-footer",
         f"--print-to-pdf={out}", "--virtual-time-budget=6000", f"file://{tmp}"],
        check=True, capture_output=True,
    )
    Path(tmp).unlink()
    print(out)


if __name__ == "__main__":
    main()
