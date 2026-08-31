import re
import requests
import datetime
from typing import Any

HN_SEARCH_API = "https://hn.algolia.com/api/v1/search"

# Algolia scores a multi-word query as a conjunction, so the previous single
# query ("AI machine learning LLM transformer neural") matched almost nothing.
# Query each term separately and merge the results.
AI_QUERIES = [
    "LLM",
    "AI",
    "GPT",
    "diffusion model",
    "machine learning",
    "neural network",
    "open weights model",
]

SKIP_PREFIXES = ("ask hn", "show hn", "tell hn")

# Algolia falls back to relevance ranking, so a high-scoring story surfaces on
# a weak keyword match: a Nitter cease-and-desist and a Xiaomi CPU review both
# came back for "LLM". Require an AI term in the title itself.
AI_TERMS = [
    r"ai",
    r"llms?",
    r"gpts?",
    r"claude", r"gemini", r"llama", r"mistral", r"deepseek", r"qwen",
    r"glm", r"grok", r"openai", r"anthropic", r"deepmind", r"hugging ?face",
    r"machine[- ]learning", r"deep[- ]learning", r"neural",
    r"transformers?", r"diffusion", r"embeddings?",
    r"fine[- ]?tun\w*", r"inference", r"agentic", r"chatbots?",
    r"open[- ]weights?", r"foundation model", r"language model",
    r"reasoning model", r"benchmark\w*",
]
AI_TITLE_RE = re.compile(r"\b(" + "|".join(AI_TERMS) + r")\b", re.IGNORECASE)


def fetch_hn_ai_posts(min_points: int = 50, limit: int = 8) -> list[dict[str, Any]]:
    since_ts = int(
        (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=7)).timestamp()
    )

    posts: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_urls: set[str] = set()

    for query in AI_QUERIES:
        params = {
            "query": query,
            "tags": "story",
            "hitsPerPage": 20,
            # min_points and the 7-day window were previously computed and then
            # never sent to the API, so neither filter was ever applied.
            "numericFilters": f"points>={min_points},created_at_i>{since_ts}",
        }
        try:
            resp = requests.get(HN_SEARCH_API, params=params, timeout=10)
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
        except Exception as e:
            print(f"[fetch_hn] Warning for {query!r}: {e}")
            continue

        for hit in hits:
            oid = str(hit.get("objectID", ""))
            title = (hit.get("title") or "").strip()
            if not oid or not title or oid in seen_ids:
                continue
            if title.lower().startswith(SKIP_PREFIXES):
                continue
            if not AI_TITLE_RE.search(title):
                continue

            url = hit.get("url") or f"https://news.ycombinator.com/item?id={oid}"
            if url in seen_urls:
                continue

            seen_ids.add(oid)
            seen_urls.add(url)
            posts.append({
                "id": oid,
                "title": title,
                "summary": "",
                "url": url,
                "hn_url": f"https://news.ycombinator.com/item?id={oid}",
                "points": hit.get("points", 0),
                "comments": hit.get("num_comments", 0),
                "author": hit.get("author", ""),
                "source": "hackernews",
                "created_at": hit.get("created_at", ""),
            })

    posts.sort(key=lambda p: p["points"], reverse=True)
    print(f"[fetch_hn] {len(posts)} AI stories >={min_points} points in the last 7d")
    return posts[:limit]
