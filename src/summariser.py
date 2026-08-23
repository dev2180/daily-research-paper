import os
import json
import time
from groq import Groq
from typing import Any

MODEL = "openai/gpt-oss-120b"

PERSONA = (
    "You are writing for Varun Bukka, an AI/ML engineer and builder. "
    "Tone: sharp, insightful, practitioner-first. No hype, no fluff. "
    "Assume the reader has a strong ML background."
)


def _client() -> Groq:
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY not set")
    return Groq(api_key=api_key)


def _call(client: Groq, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=2048,
                response_format={"type": "json_object"},
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            msg = str(e)
            if "429" in msg or "rate" in msg.lower():
                wait = 10 * (attempt + 1)
                print(f"[summariser] Rate limited — waiting {wait}s (attempt {attempt+1}/{retries})...")
                time.sleep(wait)
            else:
                raise
    raise RuntimeError(f"Groq call failed after {retries} retries")


def _parse_json(raw: str) -> Any:
    cleaned = raw.strip()
    for fence in ["```json", "```"]:
        if cleaned.startswith(fence):
            cleaned = cleaned[len(fence):]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return json.loads(cleaned.strip())


def run_full_digest(raw_data: dict, client: Groq) -> dict:
    papers = raw_data.get("papers", [])[:10]
    repos = raw_data.get("github_repos", [])[:3]
    post_style = raw_data.get("post_style", "roundup")

    paper_list = "\n".join(
        f"{i+1}. TITLE: {p['title']}\n   ABSTRACT: {p['summary'][:150]}"
        for i, p in enumerate(papers)
    )
    repo_list = "\n".join(
        f"- {r['title']} ({r['stars']} stars): {r['summary'][:80]}"
        for r in repos
    )

    mode_instruction = (
        "This is a ROUNDUP week. Pick the 6 best papers."
        if post_style == "roundup"
        else "This is a DEEP-DIVE week. Pick the single most interesting paper."
    )

    prompt = f"""{PERSONA}

{mode_instruction}

PAPERS:
{paper_list}

TRENDING GITHUB REPOS:
{repo_list}

Return a single valid JSON object with this exact structure:
{{
  "paper_of_week": {{
    "index": <1-based index of best paper>,
    "headline": "<punchy 10-word sentence capturing the breakthrough>",
    "summary": "<3 short paragraphs: what problem, key insight, why practitioners care>",
    "key_takeaway": "<one actionable sentence>",
    "excitement_score": <integer 1-10>
  }},
  "top_papers": [
    {{
      "index": <1-based index>,
      "tldr": "<core idea in max 20 words>",
      "bullets": ["<contribution 1>", "<contribution 2>", "<contribution 3>"],
      "who_should_read": "<e.g. NLP engineers>"
    }}
  ],
  "one_thing_to_try": {{
    "action": "<exactly what to do, max 20 words>",
    "why": "<one sentence on why this matters now>",
    "time_estimate": "<e.g. 2-3 hours>",
    "difficulty": "<beginner|intermediate|advanced>"
  }},
  "deep_dive": null
}}

top_papers must have exactly 5 entries, all different from paper_of_week.
Return raw JSON only. No markdown, no explanation, no preamble."""

    print("[summariser] Sending prompt to Groq (GPT-OSS 120B)...")
    raw = _call(client, prompt)

    try:
        result = _parse_json(raw)
    except json.JSONDecodeError as e:
        print(f"[summariser] JSON parse error: {e}\nRaw snippet:\n{raw[:400]}")
        raise

    idx_map = {i + 1: p for i, p in enumerate(papers)}
    potw_idx = result["paper_of_week"]["index"]
    result["paper_of_week"]["paper"] = idx_map.get(potw_idx, papers[0])

    for entry in result.get("top_papers", []):
        entry["paper"] = idx_map.get(entry.get("index", 0), {})

    return result


def rank_and_summarise(raw_data: dict) -> dict:
    client = _client()
    digest = run_full_digest(raw_data, client)

    return {
        "post_style": raw_data.get("post_style", "roundup"),
        "week_number": raw_data.get("week_number", 1),
        "generated_at": raw_data.get("generated_at", ""),
        "paper_of_week": digest.get("paper_of_week"),
        "top_papers": digest.get("top_papers", []),
        "deep_dive": digest.get("deep_dive"),
        "one_thing_to_try": digest.get("one_thing_to_try"),
        "github_repos": raw_data.get("github_repos", []),
        "hn_posts": raw_data.get("hn_posts", []),
        "implementation_gaps": raw_data.get("implementation_gaps", []),
    }
