import os
import sys
import json

# Paper titles carry non-ASCII punctuation (non-breaking hyphens, em dashes).
# On a Windows console that defaults to cp1252 those raise UnicodeEncodeError
# mid-run and kill the pipeline after the digest has already been written.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, ValueError):
        pass

from src.aggregator import aggregate_sources
from src.summariser import rank_and_summarise
from src.mailer import send_digest
from src.config import load_config, should_send_email
from src import state


def _published_ids(digest: dict) -> list[str]:
    """Paper ids this edition actually featured, so later runs can skip them."""
    ids = []
    potw = (digest.get("paper_of_week") or {}).get("paper") or {}
    if potw.get("id"):
        ids.append(str(potw["id"]))
    for tp in digest.get("top_papers") or []:
        pid = (tp.get("paper") or {}).get("id")
        if pid:
            ids.append(str(pid))
    return ids


def main():
    print("=" * 55)
    print("  Daily Research Paper -- Pipeline Starting")
    print("=" * 55)

    dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    web_url = os.getenv("GITHUB_PAGES_URL", "")

    cfg = load_config()
    send, reason = should_send_email(cfg)
    print(f"[config] cadence={cfg['cadence']} (weekly_day={cfg['weekly_day']})")
    print(f"[config] email today? {'YES' if send else 'NO'} -- {reason}\n")

    if dry_run:
        print("[DRY RUN] No email will be sent.\n")

    required_secrets = ["GROQ_API_KEY", "GMAIL_USER", "GMAIL_APP_PASSWORD", "RECIPIENT_EMAIL"]
    missing = [s for s in required_secrets if not os.getenv(s)]
    if missing and not dry_run and send:
        print(f"[ERROR] Missing secrets: {', '.join(missing)}")
        sys.exit(1)
    elif missing:
        print(f"[DRY RUN] Skipping secret check -- missing: {', '.join(missing)}\n")

    # M2: Fetch & aggregate
    seen = state.prune(state.load_seen())
    raw_data = aggregate_sources(
        detect_gaps=True,
        cadence=cfg["cadence"],
        exclude_ids=set(seen),
    )

    print(f"\n{'-' * 55}")
    print(f"  {raw_data['edition_date']} | Week #{raw_data['week_number']} "
          f"| Style: {raw_data['post_style'].upper()}")
    print(f"{'-' * 55}")
    print(f"  Papers found   : {len(raw_data['papers'])}")
    print(f"  GitHub repos   : {len(raw_data['github_repos'])}")
    print(f"  HN posts       : {len(raw_data['hn_posts'])}")
    print(f"  Gap papers     : {len(raw_data['implementation_gaps'])}")
    print(f"  Previously seen: {len(seen)}")
    print(f"{'-' * 55}\n")

    if not raw_data["papers"]:
        print("[ERROR] No papers left after filtering -- nothing to publish.")
        sys.exit(1)

    # M3: Summarise with Groq
    if os.getenv("GROQ_API_KEY"):
        print("[M3] Running Groq summarisation...")
        digest_data = rank_and_summarise(raw_data)
    else:
        print("[M3] Skipping summarisation -- GROQ_API_KEY not set\n")
        digest_data = raw_data

    os.makedirs("output", exist_ok=True)
    with open("output/digest_data.json", "w", encoding="utf-8") as f:
        json.dump(digest_data, f, indent=2, ensure_ascii=False)
    print("Digest data saved to output/digest_data.json\n")

    potw = digest_data.get("paper_of_week") or {}
    paper = potw.get("paper") or {}
    print(f"  Paper of the Week : {paper.get('title', 'N/A')[:65]}")
    print(f"  Headline          : {potw.get('headline', 'N/A')[:65]}")
    print(f"  Excitement score  : {potw.get('excitement_score', 'N/A')}/10")
    one_thing = digest_data.get("one_thing_to_try") or {}
    print(f"  One thing to try  : {one_thing.get('action', 'N/A')[:65]}\n")

    # Remember what we published so the next edition does not repeat it.
    if os.getenv("GROQ_API_KEY"):
        state.save_seen(state.record(seen, _published_ids(digest_data)))

    # M5: Send email
    if dry_run or not send:
        if not send and not dry_run:
            print(f"[SKIP] No email this run -- {reason}.")
            print("[SKIP] The web digest was still rebuilt.")
        else:
            print("[DRY RUN] Skipping email send.")
            print(f"[DRY RUN] Would send to: {os.getenv('RECIPIENT_EMAIL', '<not set>')}")
            print(f"[DRY RUN] Web URL: {web_url or '<not set>'}")

        from jinja2 import Environment, FileSystemLoader, select_autoescape
        env = Environment(
            loader=FileSystemLoader("templates"),
            autoescape=select_autoescape(["html"]),
        )
        import datetime as _dt
        try:
            _stamp = _dt.date.fromisoformat(
                digest_data.get("edition_date", "")).strftime("%d %b %Y")
        except (ValueError, TypeError):
            _stamp = digest_data.get("edition_date", "")
        html = env.get_template("email_teaser.html").render(
            data=digest_data, web_url=web_url, stamp=_stamp
        )
        with open("output/email_preview.html", "w", encoding="utf-8") as f:
            f.write(html)
        print("Email preview saved to output/email_preview.html")
    else:
        print("[M5] Sending email via Gmail SMTP...")
        send_digest(digest_data, web_url=web_url)

    print("\nPipeline complete.")


if __name__ == "__main__":
    main()
