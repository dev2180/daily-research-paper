import os
import json
import time
from groq import Groq
from typing import Any

MODEL = "openai/gpt-oss-120b"

PERSONA = (
    "You are writing for Dev Sharma, a researcher. "
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

ROUNDUP_SCHEMA = """{
  "paper_of_week": {
    "index": <1-based index of best paper>,
    "headline": "<punchy 10-word sentence capturing the breakthrough>",
    "summary": "<3 short paragraphs: what problem, key insight, why practitioners care>",
    "key_takeaway": "<one actionable sentence>",
    "excitement_score": <integer 1-10>
  },
  "top_papers": [
    {
      "index": <1-based index>,
      "tldr": "<core idea in max 20 words>",
      "bullets": ["<contribution 1>", "<contribution 2>", "<contribution 3>"],
      "who_should_read": "<e.g. NLP engineers>"
    }
  ],
  "one_thing_to_try": {
    "action": "<exactly what to do, max 20 words>",
    "why": "<one sentence on why this matters now>",
    "time_estimate": "<e.g. 2-3 hours>",
    "difficulty": "<beginner|intermediate|advanced>"
  },
  "deep_dive": null
}

top_papers must have exactly 5 entries, all different from paper_of_week."""

DEEP_DIVE_SCHEMA = """{
  "paper_of_week": {
    "index": <1-based index of the single most interesting paper>,
    "headline": "<punchy 10-word sentence capturing the breakthrough>",
    "summary": "<2 short paragraphs framing the work>",
    "key_takeaway": "<one actionable sentence>",
    "excitement_score": <integer 1-10>
  },
  "top_papers": [],
  "deep_dive": {
    "problem": "<the concrete problem, 2-3 sentences>",
    "approach": "<how the method actually works, 3-4 sentences, specific about mechanism>",
    "results": "<what they measured and what it showed, with numbers where given>",
    "limitations": "<where it breaks down or what is unproven, 2-3 sentences>",
    "what_it_unlocks": "<what a practitioner can build with this now, 2-3 sentences>"
  },
  "one_thing_to_try": {
    "action": "<exactly what to do, max 20 words>",
    "why": "<one sentence on why this matters now>",
    "time_estimate": "<e.g. 2-3 hours>",
    "difficulty": "<beginner|intermediate|advanced>"
  }
}

top_papers MUST be an empty array. deep_dive MUST be fully populated -- this is
the whole edition, so go deeper than an abstract would."""


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

    # The schema itself has to change with the mode. Previously both modes were
    # sent the same schema (deep_dive: null, exactly 5 top_papers), so a
    # "deep-dive" edition produced an identical roundup with a different label.
    deep = post_style == "deep-dive"
    mode_instruction = (
        "This is a DEEP-DIVE edition. Pick the single most interesting paper and "
        "analyse it properly. Do not summarise the others."
        if deep else
        "This is a ROUNDUP edition. Pick the 6 best papers."
    )
    schema = DEEP_DIVE_SCHEMA if deep else ROUNDUP_SCHEMA

    prompt = f"""{PERSONA}

{mode_instruction}

PAPERS:
{paper_list}

TRENDING GITHUB REPOS:
{repo_list}

Return a single valid JSON object with this exact structure:
{schema}

Return raw JSON only. No markdown, no explanation, no preamble."""

    print(f"[summariser] Sending {post_style} prompt to Groq (GPT-OSS 120B)...")
    raw = _call(client, prompt)

    try:
        result = _parse_json(raw)
    except json.JSONDecodeError as e:
        print(f"[summariser] JSON parse error: {e}")
        print(f"Raw snippet:\n{raw[:400]}")
        raise

    idx_map = {i + 1: p for i, p in enumerate(papers)}
    potw_idx = result["paper_of_week"]["index"]
    result["paper_of_week"]["paper"] = idx_map.get(potw_idx, papers[0])

    for entry in result.get("top_papers", []) or []:
        entry["paper"] = idx_map.get(entry.get("index", 0), {})

    if deep and not result.get("deep_dive"):
        print("[summariser] WARNING: deep-dive edition returned no deep_dive block")

    return result


def rank_and_summarise(raw_data: dict) -> dict:
    client = _client()
    digest = run_full_digest(raw_data, client)

    return {
        "post_style": raw_data.get("post_style", "roundup"),
        "week_number": raw_data.get("week_number", 1),
        "edition_date": raw_data.get("edition_date", ""),
        "cadence": raw_data.get("cadence", "weekly"),
        "generated_at": raw_data.get("generated_at", ""),
        "paper_of_week": digest.get("paper_of_week"),
        "top_papers": digest.get("top_papers", []),
        "deep_dive": digest.get("deep_dive"),
        "one_thing_to_try": digest.get("one_thing_to_try"),
        "github_repos": raw_data.get("github_repos", []),
        "hn_posts": raw_data.get("hn_posts", []),
        "implementation_gaps": raw_data.get("implementation_gaps", []),
    }
