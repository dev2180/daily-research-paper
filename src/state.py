import json
import os
import datetime
from typing import Any

STATE_PATH = os.path.join("state", "seen_papers.json")
RETENTION_DAYS = 21


def load_seen(path: str = STATE_PATH) -> dict[str, str]:
    """Map of paper id -> ISO date it was published in a digest."""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return {str(k): str(v) for k, v in data.get("seen", {}).items()}
    except (json.JSONDecodeError, OSError, AttributeError) as e:
        print(f"[state] unreadable ({e}) -- starting fresh")
        return {}


def prune(seen: dict[str, str], days: int = RETENTION_DAYS,
          today: datetime.date | None = None) -> dict[str, str]:
    """Forget entries older than `days` so the file cannot grow without bound."""
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    cutoff = today - datetime.timedelta(days=days)
    kept = {}
    for pid, iso in seen.items():
        try:
            if datetime.date.fromisoformat(iso[:10]) >= cutoff:
                kept[pid] = iso
        except ValueError:
            continue
    return kept


def record(seen: dict[str, str], paper_ids: list[str],
           today: datetime.date | None = None) -> dict[str, str]:
    today = today or datetime.datetime.now(datetime.timezone.utc).date()
    stamp = today.isoformat()
    for pid in paper_ids:
        if pid:
            seen[str(pid)] = stamp
    return seen


def save_seen(seen: dict[str, str], path: str = STATE_PATH) -> None:
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    payload: dict[str, Any] = {
        "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "retention_days": RETENTION_DAYS,
        "seen": dict(sorted(seen.items())),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    print(f"[state] {len(seen)} papers remembered -> {path}")


LAST_RUN_PATH = os.path.join("state", "last_run.json")


def last_edition(path: str = LAST_RUN_PATH) -> str:
    """ISO date of the last edition that completed, or '' if unknown."""
    if not os.path.exists(path):
        return ""
    try:
        with open(path, encoding="utf-8") as f:
            return str(json.load(f).get("last_edition", ""))
    except (json.JSONDecodeError, OSError, AttributeError) as e:
        print(f"[state] last_run unreadable ({e})")
        return ""


def save_last_edition(day: datetime.date | None = None,
                      path: str = LAST_RUN_PATH) -> None:
    """Record that today's edition is done.

    GitHub drops and delays scheduled runs, so the workflow fires on several
    cron slots. This is what stops the extra slots from mailing twice.
    """
    day = day or datetime.datetime.now(datetime.timezone.utc).date()
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump({
            "last_edition": day.isoformat(),
            "updated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }, f, indent=2)
    print(f"[state] edition {day.isoformat()} recorded -> {path}")
