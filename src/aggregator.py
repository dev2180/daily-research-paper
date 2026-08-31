import datetime
from typing import Any

from src.fetch_arxiv import fetch_arxiv_papers
from src.fetch_pwc import fetch_pwc_trending
from src.fetch_github import fetch_github_trending, fetch_github_paper_implementations
from src.fetch_hn import fetch_hn_ai_posts


def _deduplicate_papers(papers: list[dict]) -> list[dict]:
    seen_titles = set()
    seen_ids = set()
    unique = []
    for p in papers:
        title_key = p["title"].lower()[:60]
        pid = p.get("id", "")
        if title_key in seen_titles or (pid and pid in seen_ids):
            continue
        seen_titles.add(title_key)
        if pid:
            seen_ids.add(pid)
        unique.append(p)
    return unique


def _detect_implementation_gaps(papers: list[dict], top_n: int = 5) -> list[dict]:
    """Find hot papers that have no or very few GitHub implementations."""
    gap_papers = []
    for paper in papers[:top_n * 2]:
        if paper.get("source") == "pwc" and paper.get("has_code"):
            continue
        impls = fetch_github_paper_implementations(paper["title"])
        paper["github_implementations"] = len(impls)
        paper["implementation_gap"] = len(impls) == 0
        if paper["implementation_gap"]:
            gap_papers.append(paper)
        if len(gap_papers) >= top_n:
            break
    return gap_papers


def _edition(cadence: str, today: datetime.date) -> tuple[int, str]:
    """(week_number, post_style) for this edition.

    post_style previously alternated on the ISO week, so with a daily cadence
    every edition in a week would carry the same style. Alternate per edition:
    by day-of-year when daily, by ISO week when weekly.
    """
    week = today.isocalendar().week
    counter = today.timetuple().tm_yday if cadence == "daily" else week
    return week, ("roundup" if counter % 2 == 0 else "deep-dive")


def aggregate_sources(detect_gaps: bool = True, cadence: str = "weekly",
                      exclude_ids: set[str] | None = None) -> dict[str, Any]:
    exclude_ids = exclude_ids or set()

    print("[aggregator] Fetching arXiv papers...")
    arxiv_papers = fetch_arxiv_papers(max_results=30)

    print("[aggregator] Fetching Semantic Scholar trending papers...")
    pwc_papers = fetch_pwc_trending(limit=10)

    print("[aggregator] Fetching GitHub trending repos...")
    github_repos = fetch_github_trending(limit=8)

    print("[aggregator] Fetching Hacker News AI posts...")
    hn_posts = fetch_hn_ai_posts(min_points=50, limit=8)

    all_papers = _deduplicate_papers(arxiv_papers + pwc_papers)
    print(f"[aggregator] {len(all_papers)} unique papers after dedup "
          f"({len(arxiv_papers)} arXiv + {len(pwc_papers)} Semantic Scholar)")

    # Dedup ACROSS runs too, or a daily cadence re-features the same paper on
    # consecutive days. exclude_ids holds what previous digests published.
    if exclude_ids:
        before = len(all_papers)
        all_papers = [p for p in all_papers if str(p.get("id", "")) not in exclude_ids]
        skipped = before - len(all_papers)
        if skipped:
            print(f"[aggregator] {skipped} papers skipped -- already featured recently")

    gap_papers = []
    if detect_gaps and all_papers:
        print("[aggregator] Running implementation gap detector...")
        gap_papers = _detect_implementation_gaps(all_papers, top_n=3)
        print(f"[aggregator] Found {len(gap_papers)} papers with no GitHub implementation")

    today = datetime.datetime.now(datetime.timezone.utc).date()
    week_num, post_style = _edition(cadence, today)

    return {
        "papers": all_papers,
        "github_repos": github_repos,
        "hn_posts": hn_posts,
        "implementation_gaps": gap_papers,
        "post_style": post_style,
        "week_number": week_num,
        "edition_date": today.isoformat(),
        "cadence": cadence,
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    }
