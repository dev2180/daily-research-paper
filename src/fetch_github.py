import os
import requests
import datetime
from typing import Any

GITHUB_SEARCH_API = "https://api.github.com/search/repositories"

ML_TOPICS = ["machine-learning", "deep-learning", "llm", "transformers", "pytorch", "diffusion-models"]


CODE_LANGUAGES = {
    "Python", "Jupyter Notebook", "C++", "Cuda", "Rust", "Go",
    "TypeScript", "JavaScript", "C", "Julia", "Mojo", "Scala", "Java",
}


def _looks_like_star_farm(repo: dict[str, Any]) -> str | None:
    """Return a reason string if this repo smells manufactured, else None.

    The old query (topic:machine-learning, created in the last 7 days,
    stars>5, sorted by stars) was dominated by freshly created repos holding
    a suspiciously uniform ~55 stars, zero forks, and language HTML.
    """
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    lang = repo.get("language")
    desc = (repo.get("description") or "").strip()

    # Real traction leaves forks behind. Stars without any is the tell.
    if stars >= 25 and forks == 0:
        return f"{stars} stars but 0 forks"
    if lang is not None and lang not in CODE_LANGUAGES:
        return f"language {lang} is not an ML implementation language"
    if len(desc) < 20:
        return "no meaningful description"
    return None


def fetch_github_trending(limit: int = 8, days: int = 30) -> list[dict[str, Any]]:
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()

    query = f"topic:machine-learning created:>{since} stars:>25"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        # Over-fetch so there is something left after filtering.
        "per_page": min(100, max(limit * 6, 30)),
    }

    headers = {"Accept": "application/vnd.github+json"}
    token = os.environ.get("GITHUB_TOKEN", "")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    try:
        resp = requests.get(GITHUB_SEARCH_API, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        items = resp.json().get("items", [])
    except Exception as e:
        print(f"[fetch_github] Warning: {e}")
        return []

    repos = []
    rejected = 0
    for repo in items:
        reason = _looks_like_star_farm(repo)
        if reason:
            rejected += 1
            continue

        repos.append({
            "id": str(repo["id"]),
            "title": repo["full_name"],
            "summary": repo.get("description") or "No description provided.",
            "url": repo["html_url"],
            "stars": repo["stargazers_count"],
            "forks": repo.get("forks_count", 0),
            "language": repo.get("language") or "Unknown",
            "topics": repo.get("topics", []),
            "source": "github",
            "created_at": repo.get("created_at", ""),
        })
        if len(repos) >= limit:
            break

    print(f"[fetch_github] {len(repos)} repos kept, {rejected} filtered as low-signal")
    return repos


def fetch_github_paper_implementations(paper_title: str) -> list[dict[str, Any]]:
    """Check if a given paper already has GitHub implementations."""
    query = f"{paper_title} in:name,description,readme"
    params = {
        "q": query,
        "sort": "stars",
        "order": "desc",
        "per_page": 3,
    }
    headers = {"Accept": "application/vnd.github+json"}

    try:
        resp = requests.get(GITHUB_SEARCH_API, params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("items", [])
    except Exception:
        return []
