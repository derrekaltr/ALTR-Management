from pathlib import Path

from snapstar_review.capture import load_manifests, read_roster
from snapstar_review.demo import write_placeholder_png
from snapstar_review.models import CaptureStatus, Manifest


def test_read_roster_strips_at_and_blanks(tmp_path: Path):
    roster = tmp_path / "roster.csv"
    roster.write_text(
        "creator_name,snap_username,notes\n"
        "Jane Doe,@janedoe,priority\n"
        "No Handle,,skip me\n"
        ",bare.handle,\n"
    )
    rows = read_roster(roster)
    assert len(rows) == 2
    assert rows[0]["snap_username"] == "janedoe"
    assert rows[1]["creator_name"] == "bare.handle"  # falls back to username


def test_manifest_roundtrip_and_loading(tmp_path: Path):
    out = tmp_path / "captures" / "someone"
    out.mkdir(parents=True)
    manifest = Manifest(
        username="someone",
        status=CaptureStatus.NOT_FOUND,
        status_detail="Profile URL returned 404",
    )
    (out / "manifest.json").write_text(manifest.model_dump_json())
    loaded = load_manifests(tmp_path)
    assert len(loaded) == 1
    assert loaded[0].status == CaptureStatus.NOT_FOUND


def test_placeholder_png_is_valid_png(tmp_path: Path):
    path = tmp_path / "x.png"
    write_placeholder_png(path, 20, 10, (0, 0, 0), (255, 255, 255))
    data = path.read_bytes()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")
    assert b"IEND" in data
