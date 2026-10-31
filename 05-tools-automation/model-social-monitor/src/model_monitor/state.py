"""SQLite-backed dedupe / delivery state.

Statuses:
  seeded  — recorded silently (first sight of an account); never sent
  pending — send attempted and failed; will retry until MAX_ATTEMPTS
  sent    — delivered to Telegram
  skipped — Claude judged it not relevant to chatters; never sent or retried
  failed  — gave up after MAX_ATTEMPTS; never retried again
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path

MAX_ATTEMPTS = 3

_SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
  platform   TEXT NOT NULL,
  post_id    TEXT NOT NULL,
  model      TEXT NOT NULL,
  status     TEXT NOT NULL,
  attempts   INTEGER NOT NULL DEFAULT 0,
  first_seen TEXT NOT NULL,
  sent_at    TEXT,
  PRIMARY KEY (platform, post_id)
);
CREATE TABLE IF NOT EXISTS accounts (
  platform  TEXT NOT NULL,
  handle    TEXT NOT NULL,
  seeded_at TEXT NOT NULL,
  PRIMARY KEY (platform, handle)
);
CREATE TABLE IF NOT EXISTS meta (
  key   TEXT PRIMARY KEY,
  value TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


class StateStore:
    def __init__(self, db_path: Path | str):
        db_path = Path(db_path)
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(db_path)
        self._conn.executescript(_SCHEMA)
        # Migration for DBs created before summaries were stored.
        cols = {row[1] for row in self._conn.execute("PRAGMA table_info(posts)")}
        if "summary" not in cols:
            self._conn.execute("ALTER TABLE posts ADD COLUMN summary TEXT")
        self._conn.commit()

    def close(self) -> None:
        self._conn.close()

    # -- accounts ---------------------------------------------------------

    def is_account_seeded(self, platform: str, handle: str) -> bool:
        row = self._conn.execute(
            "SELECT 1 FROM accounts WHERE platform = ? AND handle = ?",
            (platform, handle.lower()),
        ).fetchone()
        return row is not None

    def seed_account(self, platform: str, handle: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO accounts (platform, handle, seeded_at) VALUES (?, ?, ?)",
            (platform, handle.lower(), _now()),
        )
        self._conn.commit()

    # -- posts ------------------------------------------------------------

    def get_post(self, platform: str, post_id: str) -> tuple[str, int] | None:
        """Return (status, attempts) or None if never seen."""
        row = self._conn.execute(
            "SELECT status, attempts FROM posts WHERE platform = ? AND post_id = ?",
            (platform, post_id),
        ).fetchone()
        return (row[0], row[1]) if row else None

    def should_process(self, platform: str, post_id: str) -> bool:
        """True if this post still needs to be sent (new, or pending under the attempts cap)."""
        row = self.get_post(platform, post_id)
        if row is None:
            return True
        status, attempts = row
        return status == "pending" and attempts < MAX_ATTEMPTS

    def record_seeded(self, platform: str, post_id: str, model: str) -> None:
        self._conn.execute(
            "INSERT OR IGNORE INTO posts (platform, post_id, model, status, attempts, first_seen)"
            " VALUES (?, ?, ?, 'seeded', 0, ?)",
            (platform, post_id, model, _now()),
        )
        self._conn.commit()

    def record_skipped(self, platform: str, post_id: str, model: str) -> None:
        """Post was judged not relevant to chatters — never send, never retry."""
        now = _now()
        self._conn.execute(
            "INSERT INTO posts (platform, post_id, model, status, attempts, first_seen)"
            " VALUES (?, ?, ?, 'skipped', 0, ?)"
            " ON CONFLICT (platform, post_id)"
            " DO UPDATE SET status = 'skipped'",
            (platform, post_id, model, now),
        )
        self._conn.commit()

    def mark_sent(
        self, platform: str, post_id: str, model: str, summary: str | None = None
    ) -> None:
        now = _now()
        self._conn.execute(
            "INSERT INTO posts (platform, post_id, model, status, attempts, first_seen,"
            " sent_at, summary)"
            " VALUES (?, ?, ?, 'sent', 0, ?, ?, ?)"
            " ON CONFLICT (platform, post_id)"
            " DO UPDATE SET status = 'sent', sent_at = ?, summary = ?",
            (platform, post_id, model, now, now, summary, now, summary),
        )
        self._conn.commit()

    def recent_summaries(self, model: str, hours: int = 48, limit: int = 8) -> list[str]:
        """Summaries sent for this model in the last couple of days — used so
        Claude can skip a new post showing the same thing as one already
        announced. The window is deliberately short: the same activity
        happening again after a longer gap is news and must go through."""
        cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
        rows = self._conn.execute(
            "SELECT summary FROM posts"
            " WHERE model = ? AND status = 'sent' AND summary IS NOT NULL AND sent_at >= ?"
            " ORDER BY sent_at DESC LIMIT ?",
            (model, cutoff, limit),
        ).fetchall()
        return [row[0] for row in rows]

    def record_failure(self, platform: str, post_id: str, model: str) -> int:
        """Increment the attempt count; flip to 'failed' at MAX_ATTEMPTS. Returns new count."""
        now = _now()
        self._conn.execute(
            "INSERT INTO posts (platform, post_id, model, status, attempts, first_seen)"
            " VALUES (?, ?, ?, 'pending', 1, ?)"
            " ON CONFLICT (platform, post_id)"
            " DO UPDATE SET attempts = attempts + 1",
            (platform, post_id, model, now),
        )
        row = self._conn.execute(
            "SELECT attempts FROM posts WHERE platform = ? AND post_id = ?",
            (platform, post_id),
        ).fetchone()
        attempts = row[0]
        self._conn.execute(
            "UPDATE posts SET status = ? WHERE platform = ? AND post_id = ?",
            ("failed" if attempts >= MAX_ATTEMPTS else "pending", platform, post_id),
        )
        self._conn.commit()
        return attempts

    # -- meta ---------------------------------------------------------------

    def get_meta(self, key: str) -> str | None:
        row = self._conn.execute("SELECT value FROM meta WHERE key = ?", (key,)).fetchone()
        return row[0] if row else None

    def set_meta(self, key: str, value: str) -> None:
        self._conn.execute(
            "INSERT INTO meta (key, value) VALUES (?, ?)"
            " ON CONFLICT (key) DO UPDATE SET value = ?",
            (key, value, value),
        )
        self._conn.commit()
