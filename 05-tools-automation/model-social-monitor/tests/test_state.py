from model_monitor.state import MAX_ATTEMPTS, StateStore


def make_store(tmp_path):
    return StateStore(tmp_path / "state.db")


def test_new_post_should_process(tmp_path):
    store = make_store(tmp_path)
    assert store.should_process("instagram", "p1")


def test_sent_post_not_reprocessed(tmp_path):
    store = make_store(tmp_path)
    store.mark_sent("instagram", "p1", "Amber Hayes")
    assert not store.should_process("instagram", "p1")
    assert store.get_post("instagram", "p1")[0] == "sent"


def test_seeded_post_never_sent(tmp_path):
    store = make_store(tmp_path)
    store.record_seeded("instagram", "p1", "Amber Hayes")
    assert not store.should_process("instagram", "p1")


def test_seeding_is_idempotent_and_does_not_downgrade(tmp_path):
    store = make_store(tmp_path)
    store.mark_sent("instagram", "p1", "Amber Hayes")
    store.record_seeded("instagram", "p1", "Amber Hayes")
    assert store.get_post("instagram", "p1")[0] == "sent"


def test_account_seeding(tmp_path):
    store = make_store(tmp_path)
    assert not store.is_account_seeded("tiktok", "vale.rae")
    store.seed_account("tiktok", "Vale.Rae")
    assert store.is_account_seeded("tiktok", "vale.rae")
    assert store.is_account_seeded("tiktok", "VALE.RAE")


def test_failure_retries_until_cap(tmp_path):
    store = make_store(tmp_path)
    for i in range(1, MAX_ATTEMPTS):
        assert store.record_failure("tiktok", "v1", "Vale Rae") == i
        assert store.should_process("tiktok", "v1"), f"should retry after attempt {i}"

    assert store.record_failure("tiktok", "v1", "Vale Rae") == MAX_ATTEMPTS
    assert not store.should_process("tiktok", "v1")
    assert store.get_post("tiktok", "v1") == ("failed", MAX_ATTEMPTS)


def test_failure_then_success(tmp_path):
    store = make_store(tmp_path)
    store.record_failure("instagram", "p1", "Sarah H")
    store.mark_sent("instagram", "p1", "Sarah H")
    assert store.get_post("instagram", "p1")[0] == "sent"
    assert not store.should_process("instagram", "p1")


def test_skipped_post_never_retried(tmp_path):
    store = make_store(tmp_path)
    store.record_skipped("instagram_story", "s1", "Amber Hayes")
    assert not store.should_process("instagram_story", "s1")
    assert store.get_post("instagram_story", "s1")[0] == "skipped"


def test_meta_roundtrip(tmp_path):
    store = make_store(tmp_path)
    assert store.get_meta("last_story_fetch") is None
    store.set_meta("last_story_fetch", "2026-09-26T10:00:00+00:00")
    assert store.get_meta("last_story_fetch") == "2026-09-26T10:00:00+00:00"
    store.set_meta("last_story_fetch", "2026-09-26T11:00:00+00:00")
    assert store.get_meta("last_story_fetch") == "2026-09-26T11:00:00+00:00"


def test_platforms_do_not_collide(tmp_path):
    store = make_store(tmp_path)
    store.mark_sent("instagram", "same-id", "Amber Hayes")
    assert store.should_process("tiktok", "same-id")


def test_recent_summaries_only_sent_posts_for_that_model(tmp_path):
    store = make_store(tmp_path)
    store.mark_sent("instagram_story", "s1", "Lauren Blake", "Lauren got flowers.")
    store.mark_sent("instagram", "p1", "Lauren Blake", "Lauren at the gym.")
    store.mark_sent("instagram", "p2", "Lauren Blake", None)  # legacy row, no summary
    store.mark_sent("instagram", "p3", "Valerae", "Valerae at the beach.")
    store.record_seeded("instagram", "p4", "Lauren Blake")
    store.record_skipped("instagram", "p5", "Lauren Blake")

    summaries = store.recent_summaries("Lauren Blake")
    assert sorted(summaries) == ["Lauren at the gym.", "Lauren got flowers."]
    assert store.recent_summaries("Valerae") == ["Valerae at the beach."]


def test_summary_column_migration(tmp_path):
    import sqlite3

    db = tmp_path / "old.db"
    conn = sqlite3.connect(db)
    conn.executescript(
        "CREATE TABLE posts (platform TEXT NOT NULL, post_id TEXT NOT NULL,"
        " model TEXT NOT NULL, status TEXT NOT NULL, attempts INTEGER NOT NULL DEFAULT 0,"
        " first_seen TEXT NOT NULL, sent_at TEXT, PRIMARY KEY (platform, post_id));"
    )
    conn.commit()
    conn.close()

    store = StateStore(db)  # must add the summary column without complaint
    store.mark_sent("instagram", "p1", "Lauren Blake", "Lauren got flowers.")
    assert store.recent_summaries("Lauren Blake") == ["Lauren got flowers."]
