import datetime
import importlib
import os

from src.config import load_config, should_send_email
from src.state import prune, record
from src.aggregator import _edition
from src.fetch_github import _looks_like_star_farm
from src.fetch_hn import AI_TITLE_RE


def test_all_modules_importable():
    modules = [
        "src.fetch_arxiv",
        "src.fetch_pwc",
        "src.fetch_github",
        "src.fetch_hn",
        "src.aggregator",
        "src.summariser",
        "src.mailer",
        "src.config",
        "src.state",
    ]
    for mod in modules:
        assert importlib.import_module(mod) is not None, f"Failed to import {mod}"


def test_templates_exist():
    # Previously asserted templates/digest.html, which has never existed here.
    assert os.path.exists("templates/email_teaser.html")


def test_main_importable():
    import main
    assert hasattr(main, "main")


# --- cadence -------------------------------------------------------------

SUNDAY = datetime.date(2026, 9, 6)
MONDAY = datetime.date(2026, 9, 7)


def test_weekly_only_emails_on_the_chosen_day():
    cfg = {"cadence": "weekly", "weekly_day": "sunday"}
    assert should_send_email(cfg, SUNDAY)[0] is True
    assert should_send_email(cfg, MONDAY)[0] is False


def test_daily_always_emails_and_paused_never_does():
    assert should_send_email({"cadence": "daily"}, MONDAY)[0] is True
    assert should_send_email({"cadence": "paused"}, SUNDAY)[0] is False


def test_bad_config_falls_back_to_defaults():
    cfg = load_config("does-not-exist.json")
    assert cfg["cadence"] == "weekly"


# --- editions ------------------------------------------------------------

def test_daily_cadence_alternates_every_day():
    styles = [_edition("daily", SUNDAY + datetime.timedelta(days=i))[1] for i in range(4)]
    assert styles[0] != styles[1], "consecutive daily editions must differ"
    assert styles[0] == styles[2]


def test_weekly_cadence_alternates_every_week():
    styles = [_edition("weekly", SUNDAY + datetime.timedelta(weeks=i))[1] for i in range(3)]
    assert styles[0] != styles[1]
    assert styles[0] == styles[2]


# --- cross-run dedup -----------------------------------------------------

def test_prune_drops_stale_and_keeps_recent():
    today = datetime.date(2026, 8, 31)
    kept = prune({"old": "2026-07-01", "new": "2026-08-25"}, days=21, today=today)
    assert kept == {"new": "2026-08-25"}


def test_prune_survives_corrupt_dates():
    assert prune({"x": "not-a-date"}, today=datetime.date(2026, 8, 31)) == {}


def test_record_stamps_new_ids():
    out = record({}, ["2508.111", "2508.222"], today=datetime.date(2026, 8, 31))
    assert out == {"2508.111": "2026-08-31", "2508.222": "2026-08-31"}


# --- source quality filters ---------------------------------------------

def test_star_farm_repos_are_rejected():
    # The real shape seen in production: ~55 stars, zero forks, language HTML.
    spam = {"stargazers_count": 55, "forks_count": 0, "language": "HTML",
            "description": "A machine learning starter template"}
    assert _looks_like_star_farm(spam) is not None


def test_genuine_repo_is_kept():
    good = {"stargazers_count": 239, "forks_count": 205, "language": "Jupyter Notebook",
            "description": "Hands-on labs for AI engineering fundamentals"}
    assert _looks_like_star_farm(good) is None


def test_hn_title_filter_matches_ai_and_rejects_lookalikes():
    assert AI_TITLE_RE.search("GLM-5.3 is now open-weight")
    assert AI_TITLE_RE.search("LLMs could control their host machines")
    assert not AI_TITLE_RE.search("First aid for burns")
    assert not AI_TITLE_RE.search("Get your Windows license refund")
