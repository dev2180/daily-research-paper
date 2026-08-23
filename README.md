# ML Research Pulse ⚡

> Fully automated weekly AI/ML research digest delivered to your inbox every Sunday at 8 PM IST — and published as a web page on GitHub Pages. Zero paid services.

## What You Get

Every week, a beautiful digest with:

- 🏆 **Paper of the Week** — ranked by novelty, applicability & community impact
- 📚 **Top 5 Papers** — 3-bullet summaries ranked for ML practitioners
- 🔍 **Implementation Gap Radar** — hot papers with no GitHub code yet (your opportunity)
- 🔥 **Trending ML Repos** — top new GitHub repos in ML this week
- 💡 **One Thing To Try** — one concrete hands-on experiment for the week
- 🌐 **Web digest page** — auto-published to GitHub Pages, shareable with the community

Posts alternate between **roundup** (top 5 papers) and **deep-dive** (one paper, fully analysed) every other week.

---

## Web Hosting

https://varunb1996.github.io/ml-research-pulse


## Stack

| Component | Tool | Cost |
|---|---|---|
| Scheduling | GitHub Actions (cron) | Free |
| Papers | arXiv Export API | Free |
| Trending repos | GitHub Search API | Free |
| Community posts | Hacker News Algolia API | Free |
| AI Summarisation | **Groq — GPT-OSS 120B** | Free (14,400 req/day) |
| Email delivery | Gmail SMTP | Free |
| Web hosting | GitHub Pages | Free |
| **Total** | | **$0/year** |

---

## One-Time Setup (< 10 minutes)

### 1. Get a Groq API Key (free)
1. Go to [console.groq.com](https://console.groq.com) and sign up
2. Click **API Keys → Create API Key** → copy it

### 2. Get a Gmail App Password (free)
1. Go to **myaccount.google.com → Security → 2-Step Verification** (must be enabled)
2. Search **App Passwords** → create one for Mail
3. Copy the 16-character password

### 3. Add GitHub Secrets
Go to your repo → **Settings → Secrets and variables → Actions → New repository secret**

| Secret | Value |
|---|---|
| `GROQ_API_KEY` | Your Groq API key |
| `GMAIL_USER` | Your Gmail address |
| `GMAIL_APP_PASSWORD` | 16-char app password from step 2 |
| `RECIPIENT_EMAIL` | Where to send the digest |

### 4. Enable GitHub Pages
Go to **Settings → Pages → Source → Deploy from branch → `gh-pages`**

### 5. Test it
Go to **Actions → ML Research Pulse — Weekly Digest → Run workflow**

That's it. Every Sunday at 8 PM IST — papers fetched, summarised by GPT-OSS 120B, web page published, email sent.

---

## Local Development

```bash
# Install Python deps
pip install -r requirements.txt

# Run pipeline (dry run — no email sent)
export GROQ_API_KEY=your_key_here
python main.py

# Inspect email preview
open output/email_preview.html

# Run web app locally
cd web && npm install && npm run dev
# → http://localhost:3000
```

---

## Project Structure

```
ml-research-pulse/
├── .github/workflows/
│   └── weekly_digest.yml     # GitHub Actions — cron + full pipeline
├── src/
│   ├── fetch_arxiv.py        # arXiv Export API (cs.AI, cs.LG, stat.ML, cs.CL, cs.CV)
│   ├── fetch_pwc.py          # Semantic Scholar API
│   ├── fetch_github.py       # GitHub Search API — trending ML repos
│   ├── fetch_hn.py           # Hacker News Algolia API
│   ├── aggregator.py         # Merge, dedup, implementation gap detector
│   ├── summariser.py         # Groq GPT-OSS 120B — rank + summarise (1 API call)
│   └── mailer.py             # Gmail SMTP delivery
├── templates/
│   └── email_teaser.html     # Jinja2 HTML email template
├── web/                      # Next.js + Tailwind digest web app
│   ├── app/                  # App Router pages
│   ├── components/           # Hero, PaperOfWeek, TopPapers, etc.
│   └── public/data/          # latest.json injected by pipeline
├── main.py                   # Pipeline orchestrator
└── requirements.txt
```

---

## How It Works

```
GitHub Actions (cron: Sun 14:30 UTC = 8 PM IST)
  │
  ├── python main.py
  │     ├── fetch: arXiv + Semantic Scholar + GitHub + HN
  │     ├── summarise: Groq GPT-OSS 120B (single batched prompt)
  │     └── save: output/digest_data.json
  │
  ├── cp digest_data.json → web/public/data/latest.json
  ├── npm run build → web/out/ (static export)
  ├── deploy web/out/ → gh-pages branch → GitHub Pages
  └── send HTML email via Gmail SMTP
```
