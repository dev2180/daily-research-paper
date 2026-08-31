import json
import os
import datetime
from typing import Any

CONFIG_PATH = "digest_config.json"
VALID_CADENCE = ("daily", "weekly", "paused")
DAYS = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]

DEFAULTS: dict[str, Any] = {"cadence": "weekly", "weekly_day": "sunday"}


def load_config(path: str = CONFIG_PATH) -> dict[str, Any]:
    """Read digest_config.json, falling back to defaults on anything unexpected.

    A malformed config must never take the pipeline down -- it is edited by a
    workflow triggered from a button on a public page.
    """
    cfg = dict(DEFAULTS)
    if not os.path.exists(path):
        print(f"[config] {path} not found -- using defaults {cfg}")
        return cfg

    try:
        with open(path, encoding="utf-8") as f:
            raw = json.load(f)
    except (json.JSONDecodeError, OSError) as e:
        print(f"[config] unreadable ({e}) -- using defaults {cfg}")
        return cfg

    cadence = str(raw.get("cadence", "")).strip().lower()
    if cadence in VALID_CADENCE:
        cfg["cadence"] = cadence
    elif cadence:
        print(f"[config] unknown cadence {cadence!r} -- keeping {cfg['cadence']!r}")

    day = str(raw.get("weekly_day", "")).strip().lower()
    if day in DAYS:
        cfg["weekly_day"] = day
    elif day:
        print(f"[config] unknown weekly_day {day!r} -- keeping {cfg['weekly_day']!r}")

    return cfg


def should_send_email(cfg: dict[str, Any], today: datetime.date | None = None) -> tuple[bool, str]:
    """Decide whether today's run mails the digest. Returns (send, reason)."""
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    cadence = cfg.get("cadence", "weekly")

    if cadence == "paused":
        return False, "cadence is paused"
    if cadence == "daily":
        return True, "cadence is daily"

    want = cfg.get("weekly_day", "sunday")
    actual = DAYS[today.weekday()]
    if actual == want:
        return True, f"weekly, and today is {actual}"
    return False, f"weekly on {want}; today is {actual}"
