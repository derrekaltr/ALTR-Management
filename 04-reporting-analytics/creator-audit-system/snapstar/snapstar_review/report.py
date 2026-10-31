"""Render ALTR-branded PDF reports from review results.

HTML is rendered with Jinja2, then printed to PDF with Playwright's Chromium
(same dependency as the capture stage — no extra PDF toolchain needed).
"""

from __future__ import annotations

import base64
import datetime
from pathlib import Path
from typing import Any

from jinja2 import Environment, FileSystemLoader, select_autoescape
from playwright.sync_api import sync_playwright

from .models import CATEGORY_LABELS, CaptureStatus, CreatorReview, Severity
from .review import load_reviews
from .rubric import READINESS_LABELS, readiness_level, weighted_score

TEMPLATES_DIR = Path(__file__).parent / "templates"
ASSETS_DIR = Path("assets")

MEDIA_TYPES = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".svg": "image/svg+xml",
}

FOOTER_TEMPLATE = """
<div style="width:100%; font-size:8px; color:#8a8a8a; padding:0 14mm;
            display:flex; justify-content:space-between;
            font-family:Helvetica,Arial,sans-serif;">
  <span>ALTR &middot; Confidential &mdash; prepared for the creator named herein</span>
  <span>Page <span class="pageNumber"></span> of <span class="totalPages"></span></span>
</div>
"""


def _data_uri(path: Path) -> str:
    media_type = MEDIA_TYPES.get(path.suffix.lower())
    if not media_type or not path.is_file():
        return ""
    data = base64.standard_b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{media_type};base64,{data}"


def brand_assets() -> dict[str, str]:
    """Wordmark + mark data URIs from assets/ (altr-logo.* overrides the
    wordmark if the team drops in an alternative)."""
    wordmark = ""
    for name in ("altr-logo.svg", "altr-logo.png", "altr-wordmark.png"):
        wordmark = _data_uri(ASSETS_DIR / name)
        if wordmark:
            break
    return {
        "wordmark_uri": wordmark,
        "mark_uri": _data_uri(ASSETS_DIR / "altr-mark.png"),
    }


def _jinja_env() -> Environment:
    env = Environment(
        loader=FileSystemLoader(TEMPLATES_DIR),
        autoescape=select_autoescape(["html"]),
    )
    env.globals["category_label"] = lambda c: CATEGORY_LABELS.get(c, str(c))
    return env


def _creator_context(
    review: CreatorReview, output_dir: Path, cfg: dict[str, Any]
) -> dict[str, Any]:
    captures_dir = output_dir / "captures" / review.username
    level = readiness_level(review, cfg["scoring"])
    flagged = review.flagged_items()
    findings = []
    for item in flagged:
        image_uri = ""
        if item.image_path:
            image_uri = _data_uri(captures_dir / item.image_path)
        findings.append({"item": item, "image_uri": image_uri})
    return {
        "review": review,
        "styles": (TEMPLATES_DIR / "styles.css").read_text(),
        **brand_assets(),
        "prepared_by": cfg["report"]["prepared_by"],
        "contact": cfg["report"].get("contact", ""),
        "date": datetime.date.today().strftime("%B %d, %Y"),
        "readiness_key": level,
        "readiness": READINESS_LABELS[level],
        "score": weighted_score(review, cfg["scoring"]),
        "counts": review.severity_counts(),
        "findings": findings,
        "clean_count": sum(
            1 for i in review.items if i.review.severity == Severity.CLEAN
        ),
        "not_audited": review.status != CaptureStatus.OK,
        "Severity": Severity,
    }


def _html_to_pdf(page, html: str, pdf_path: Path) -> None:
    page.set_content(html, wait_until="load")
    page.pdf(
        path=str(pdf_path),
        format="Letter",
        print_background=True,
        display_header_footer=True,
        header_template="<span></span>",
        footer_template=FOOTER_TEMPLATE,
        margin={"top": "14mm", "bottom": "16mm", "left": "0", "right": "0"},
    )


def run_report(output_dir: str | Path, cfg: dict[str, Any]) -> list[Path]:
    output_dir = Path(output_dir)
    reviews = load_reviews(output_dir)
    if not reviews:
        raise SystemExit(
            f"No reviews found under {output_dir}/reviews — run `snapstar review` first."
        )
    env = _jinja_env()
    creator_template = env.get_template("creator_report.html.j2")
    roster_template = env.get_template("roster_summary.html.j2")
    reports_dir = output_dir / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    pdfs: list[Path] = []
    roster_rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        for review in reviews:
            context = _creator_context(review, output_dir, cfg)
            html = creator_template.render(**context)
            pdf_path = (
                reports_dir
                / f"{review.creator_name} - Snapchat Verification Readiness.pdf"
            )
            print(f"[report] {pdf_path.name}", flush=True)
            _html_to_pdf(page, html, pdf_path)
            pdfs.append(pdf_path)
            roster_rows.append(context)

        roster_html = roster_template.render(
            rows=roster_rows,
            styles=(TEMPLATES_DIR / "styles.css").read_text(),
            **brand_assets(),
            prepared_by=cfg["report"]["prepared_by"],
            date=datetime.date.today().strftime("%B %d, %Y"),
        )
        roster_pdf = reports_dir / "ALTR Roster - Verification Readiness Overview.pdf"
        print(f"[report] {roster_pdf.name}", flush=True)
        _html_to_pdf(page, roster_html, roster_pdf)
        pdfs.append(roster_pdf)
        browser.close()
    return pdfs
