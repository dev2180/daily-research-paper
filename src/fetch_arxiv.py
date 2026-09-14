import requests
import time
import xml.etree.ElementTree as ET
import datetime
from typing import Any

ARXIV_API = "http://export.arxiv.org/api/query"
ATOM_NS = "http://www.w3.org/2005/Atom"
ARXIV_NS = "http://arxiv.org/schemas/atom"

CATEGORIES = ["cs.AI", "cs.LG", "stat.ML", "cs.CL", "cs.CV"]

# GitHub Actions runners share IP pools across every workflow using them, so
# export.arxiv.org routinely 429s or times out the very first request of a
# run -- observed on 2026-09-12 (429) and 2026-09-14 (read timeout), both on
# attempt 1 with no retry, which zeroed out the paper count and aborted the
# whole run. Retry like fetch_pwc.py already does.
def _fetch_with_retry(params: dict, attempts: int = 4, timeout: int = 20) -> bytes | None:
    headers = {"User-Agent": "daily-research-paper/1.0 (github.com/dev2180/daily-research-paper)"}
    for attempt in range(attempts):
        try:
            resp = requests.get(ARXIV_API, params=params, headers=headers, timeout=timeout)
            if resp.status_code == 429:
                wait = 5 * (attempt + 1)
                print(f"[fetch_arxiv] 429 rate limited -- waiting {wait}s (attempt {attempt+1}/{attempts})")
                time.sleep(wait)
                continue
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            print(f"[fetch_arxiv] Warning (attempt {attempt+1}/{attempts}): {e}")
            if attempt < attempts - 1:
                time.sleep(5)
    return None


def fetch_arxiv_papers(max_results: int = 30) -> list[dict[str, Any]]:
    query = " OR ".join(f"cat:{c}" for c in CATEGORIES)
    params = {
        "search_query": query,
        "start": 0,
        "max_results": max_results,
        "sortBy": "submittedDate",
        "sortOrder": "descending",
    }

    content = _fetch_with_retry(params)
    if content is None:
        print("[fetch_arxiv] All retries exhausted -- returning no papers")
        return []

    try:
        root = ET.fromstring(content)
    except ET.ParseError as e:
        print(f"[fetch_arxiv] XML parse error: {e}")
        return []

    papers = []
    for entry in root.findall(f"{{{ATOM_NS}}}entry"):
        arxiv_id_url = entry.findtext(f"{{{ATOM_NS}}}id", "")
        arxiv_id = arxiv_id_url.split("/abs/")[-1].strip()

        title = entry.findtext(f"{{{ATOM_NS}}}title", "").replace("\n", " ").strip()
        summary = entry.findtext(f"{{{ATOM_NS}}}summary", "").replace("\n", " ").strip()
        published = entry.findtext(f"{{{ATOM_NS}}}published", "")

        authors = [
            a.findtext(f"{{{ATOM_NS}}}name", "")
            for a in entry.findall(f"{{{ATOM_NS}}}author")[:3]
        ]

        categories = [
            t.get("term", "")
            for t in entry.findall(f"{{{ATOM_NS}}}category")
        ]
        primary_cat = categories[0] if categories else "cs.AI"

        pdf_url = ""
        for link in entry.findall(f"{{{ATOM_NS}}}link"):
            if link.get("title") == "pdf":
                pdf_url = link.get("href", "")

        papers.append({
            "id": arxiv_id,
            "title": title,
            "summary": summary,
            "authors": authors,
            "url": f"https://arxiv.org/abs/{arxiv_id}",
            "pdf_url": pdf_url or f"https://arxiv.org/pdf/{arxiv_id}",
            "category": primary_cat,
            "source": "arxiv",
            "published": published,
        })

    return papers
