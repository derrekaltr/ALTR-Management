"""CLI entry point.

Usage:
  python -m model_monitor check [--dry-run] [--force] [--model NAME]
  python -m model_monitor seed  [--model NAME]
  python -m model_monitor send-test [--model NAME]
"""

from __future__ import annotations

import argparse
import fcntl
import logging
import logging.handlers
import sys
from pathlib import Path

from .config import ConfigError, load_config
from .pipeline import run_cycle, send_test_messages
from .state import StateStore

REPO_ROOT = Path(__file__).resolve().parents[2]

log = logging.getLogger("model_monitor")


def _setup_logging(level: str) -> None:
    logs_dir = REPO_ROOT / "logs"
    logs_dir.mkdir(exist_ok=True)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")

    file_handler = logging.handlers.RotatingFileHandler(
        logs_dir / "monitor.log", maxBytes=2_000_000, backupCount=3
    )
    file_handler.setFormatter(fmt)
    stream_handler = logging.StreamHandler(sys.stderr)
    stream_handler.setFormatter(fmt)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))
    root.addHandler(file_handler)
    root.addHandler(stream_handler)
    # keep third-party HTTP logging quiet unless debugging
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)


def _acquire_lock() -> object | None:
    """Prevent overlapping runs (slow Apify run vs. 15-min schedule)."""
    data_dir = REPO_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    lock_file = open(data_dir / "monitor.lock", "w")
    try:
        fcntl.flock(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return None
    return lock_file  # keep the handle alive for the process lifetime


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="model_monitor")
    parser.add_argument("--config", type=Path, help="path to models.yaml (default: config/models.yaml)")
    sub = parser.add_subparsers(dest="command", required=True)

    check = sub.add_parser("check", help="fetch new posts and send updates (the scheduled command)")
    check.add_argument("--dry-run", action="store_true",
                       help="run the full pipeline but print updates instead of sending; writes no state")
    check.add_argument("--force", action="store_true",
                       help="treat each account's latest post as new (end-to-end test)")
    check.add_argument("--model", help="limit to one model by name, e.g. --model 'Amber Hayes'")

    seed = sub.add_parser("seed", help="record current posts silently without sending anything")
    seed.add_argument("--model", help="limit to one model by name")

    test = sub.add_parser("send-test", help="post a connectivity test message to every channel")
    test.add_argument("--model", help="limit to one model by name")

    args = parser.parse_args(argv)

    try:
        config = load_config(REPO_ROOT, args.config)
    except ConfigError as exc:
        print(f"Configuration problem:\n{exc}", file=sys.stderr)
        return 2

    _setup_logging(config.log_level)

    if args.command == "send-test":
        failures = send_test_messages(config, args.model)
        return 1 if failures else 0

    lock = _acquire_lock()
    if lock is None:
        log.info("another run is already in progress; exiting")
        return 0

    store = StateStore(config.state_db_path)
    try:
        summary = run_cycle(
            config,
            store,
            force=(args.command == "check" and args.force),
            dry_run=(args.command == "check" and args.dry_run),
            seed_only=(args.command == "seed"),
            only_model=args.model,
        )
    finally:
        store.close()

    log.info("cycle done: %s", summary.one_liner())
    if summary.all_platforms_failed:
        log.error("every platform failed this cycle")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
