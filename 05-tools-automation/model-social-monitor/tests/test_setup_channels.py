import importlib.util
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "setup_channels.py"

# The script exits at import time if telethon is missing; skip these tests then.
telethon_missing = importlib.util.find_spec("telethon") is None


def load_script():
    spec = importlib.util.spec_from_file_location("setup_channels", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


SAMPLE = """\
# Ollie Clients — live configuration.
poll:
  results_limit: 8

models:
  - name: Amber Hayes
    instagram: amber_hazee
    telegram_chat_id: 0

  # a comment that must survive
  - name: Sarah Lloyd
    instagram: saraahlloyd
    telegram_chat_id: 0
"""


@pytest.mark.skipif(telethon_missing, reason="telethon not installed")
def test_set_chat_id_replaces_only_target_model():
    mod = load_script()
    out = mod.set_chat_id_in_yaml(SAMPLE, "Sarah Lloyd", -1009876543210)
    assert "instagram: saraahlloyd\n    telegram_chat_id: -1009876543210" in out
    # Amber's placeholder untouched, comments preserved
    assert "instagram: amber_hazee\n    telegram_chat_id: 0" in out
    assert "# a comment that must survive" in out


@pytest.mark.skipif(telethon_missing, reason="telethon not installed")
def test_set_chat_id_is_not_applied_twice():
    mod = load_script()
    out = mod.set_chat_id_in_yaml(SAMPLE, "Amber Hayes", -100111)
    with pytest.raises(ValueError):
        mod.set_chat_id_in_yaml(out, "Amber Hayes", -100222)


@pytest.mark.skipif(telethon_missing, reason="telethon not installed")
def test_missing_model_raises():
    mod = load_script()
    with pytest.raises(ValueError):
        mod.set_chat_id_in_yaml(SAMPLE, "Nobody", -100333)
