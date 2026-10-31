"""snapstar — ALTR Snapchat verification-readiness audit CLI."""

from __future__ import annotations

import os

import click

from .config import load_config


@click.group()
@click.option("--config", "config_path", default="config.yaml", show_default=True,
              help="Path to config.yaml")
@click.pass_context
def main(ctx: click.Context, config_path: str) -> None:
    """Audit creators' public Snapchat profiles ahead of a verification
    (gold star) application and generate ALTR-branded cleanup reports."""
    ctx.obj = load_config(config_path)


@main.command()
@click.option("--roster", required=True, type=click.Path(exists=True),
              help="CSV with creator_name,snap_username,notes")
@click.option("--output", default="output", show_default=True)
@click.pass_obj
def capture(cfg: dict, roster: str, output: str) -> None:
    """Capture each creator's public Snapchat web profile."""
    from .capture import run_capture

    manifests = run_capture(roster, output, cfg)
    ok = sum(1 for m in manifests if m.status.value == "ok")
    click.echo(f"Captured {ok}/{len(manifests)} profiles OK -> {output}/captures/")


@main.command()
@click.option("--output", default="output", show_default=True)
@click.option("--model", default=None, help="Override the review model")
@click.option("--only", multiple=True, help="Limit to specific username(s)")
@click.option("--force", is_flag=True, help="Re-review creators that already have results")
@click.pass_obj
def review(cfg: dict, output: str, model: str | None, only: tuple[str, ...], force: bool) -> None:
    """Review captured content with Claude against the verification rubric."""
    if model:
        cfg["model"] = model
    if not os.environ.get("ANTHROPIC_API_KEY") and not os.environ.get("ANTHROPIC_AUTH_TOKEN"):
        click.echo("note: ANTHROPIC_API_KEY not set — relying on `ant auth login` profile if present")
    from .review import run_review

    reviews = run_review(output, cfg, only=list(only) or None, force=force)
    click.echo(f"Reviewed {len(reviews)} creators -> {output}/reviews/")


@main.command()
@click.option("--output", default="output", show_default=True)
@click.pass_obj
def report(cfg: dict, output: str) -> None:
    """Generate ALTR-branded PDF reports from review results."""
    from .report import run_report

    pdfs = run_report(output, cfg)
    click.echo(f"Wrote {len(pdfs)} PDFs -> {output}/reports/")


@main.command()
@click.option("--roster", required=True, type=click.Path(exists=True))
@click.option("--output", default="output", show_default=True)
@click.pass_context
def run(ctx: click.Context, roster: str, output: str) -> None:
    """Full pipeline: capture -> review -> report."""
    ctx.invoke(capture, roster=roster, output=output)
    ctx.invoke(review, output=output, model=None, only=(), force=False)
    ctx.invoke(report, output=output)


@main.command()
@click.argument("username")
@click.option("--name", default=None, help="Creator display name (defaults to the username)")
@click.option("--notes", default="", help="Internal notes for this creator")
@click.option("--output", default="output", show_default=True)
@click.option("--model", default=None, help="Override the review model")
@click.option("--force", is_flag=True, help="Redo capture+review even if already audited")
@click.pass_obj
def add(cfg: dict, username: str, name: str | None, notes: str,
        output: str, model: str | None, force: bool) -> None:
    """Audit ONE creator end-to-end: capture -> review -> refresh all reports.

    Example: snapstar add janedoe --name "Jane Doe"
    """
    if model:
        cfg["model"] = model
    username = username.strip().lstrip("@")
    from pathlib import Path

    from .capture import capture_creators
    from .report import run_report
    from .review import run_review

    if (Path(output) / "reviews" / f"{username}.json").exists() and not force:
        raise SystemExit(
            f"@{username} was already audited — use --force to re-capture and "
            "re-review (e.g. after they cleaned up their account)."
        )
    creator = {"snap_username": username, "creator_name": (name or username).strip(),
               "notes": notes}
    manifests = capture_creators([creator], output, cfg)
    if manifests[0].status.value != "ok":
        click.echo(f"warning: capture status = {manifests[0].status.value} "
                   f"({manifests[0].status_detail}) — the report will say 'not audited'")
    run_review(output, cfg, only=[username], force=True)  # capture is fresh
    pdfs = run_report(output, cfg)
    click.echo(f"Done. {len(pdfs)} PDFs refreshed in {output}/reports/ — "
               f"creator report: {creator['creator_name']} - Snapchat Verification Readiness.pdf")


@main.command()
@click.option("--output", default="output-demo", show_default=True)
@click.pass_context
def demo(ctx: click.Context, output: str) -> None:
    """Generate sample data and render the PDFs (no Snapchat, no API calls)."""
    from .demo import build_demo_data

    build_demo_data(output)
    ctx.invoke(report, output=output)


if __name__ == "__main__":
    main()
