import requests
import time
from typing import Any

# Semantic Scholar API — free, no key required, reliable
S2_API = "https://api.semanticscholar.org/graph/v1/paper/search"
S2_FIELDS = "paperId,title,abstract,authors,year,publicationDate,openAccessPdf,citationCount,externalIds"

AI_QUERIES = ["large language model", "diffusion model", "reinforcement learning", "vision transformer"]


def fetch_pwc_trending(limit: int = 10) -> list[dict[str, Any]]:
    """Fetch recent highly-cited AI papers via Semantic Scholar (replaces PwC API)."""
    papers = []
    seen_ids = set()

    # Was AI_QUERIES[:2], capping the whole fallback pool at ~14 candidates.
    # On 2026-09-14 arXiv failed AND this returned 0 new results -- everything
    # it had was already in the 21-day "seen" window. Querying all four terms
    # widens the pool so one bad arXiv day doesn't also empty this out.
    for query in AI_QUERIES:
        params = {
            "query": query,
            "fields": S2_FIELDS,
            # Was limit // 2 + 2, sized for exactly 2 queries splitting the
            # target -- with 4 queries now, that undercounted per query and
            # the len(papers) >= limit break below often stopped after query
            # 1, defeating the point of querying more terms. Flat per-query
            # cap instead; the final papers[:limit] slice still bounds output.
            "limit": 8,
            "sort": "citationCount:desc",
        }
        headers = {"User-Agent": "ml-research-pulse/1.0"}
        data = None
        for attempt in range(3):
            try:
                resp = requests.get(S2_API, params=params, headers=headers, timeout=12)
                if resp.status_code == 429:
                    wait = 5 * (attempt + 1)
                    # Was silent -- when every query hit this branch (observed
                    # while debugging the arXiv outages) the run logged
                    # "0 papers" with zero indication why.
                    print(f"[fetch_s2] 429 for '{query}' -- waiting {wait}s (attempt {attempt+1}/3)")
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                data = resp.json()
                break
            except Exception as e:
                print(f"[fetch_s2] Warning for '{query}' (attempt {attempt+1}): {e}")
                time.sleep(3)
        if not data:
            continue

        for item in data.get("data", []):
            pid = item.get("paperId", "")
            if not pid or pid in seen_ids:
                continue
            seen_ids.add(pid)

            arxiv_id = (item.get("externalIds") or {}).get("ArXiv", "")
            pdf_url = (item.get("openAccessPdf") or {}).get("url", "")
            authors = [a.get("name", "") for a in (item.get("authors") or [])[:3]]

            papers.append({
                "id": arxiv_id or pid,
                "title": item.get("title", "").strip(),
                "summary": (item.get("abstract") or "").strip(),
                "authors": authors,
                "url": f"https://arxiv.org/abs/{arxiv_id}" if arxiv_id else f"https://www.semanticscholar.org/paper/{pid}",
                "pdf_url": pdf_url,
                "category": "Semantic Scholar",
                "source": "semantic_scholar",
                "citations": item.get("citationCount", 0),
                "published": item.get("publicationDate", ""),
                "has_code": bool(arxiv_id),
                "github_url": "",
            })

        if len(papers) >= limit:
            break

    return papers[:limit]
