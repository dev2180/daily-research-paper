export interface Paper {
  id: string
  title: string
  summary: string
  authors: string[]
  url: string
  pdf_url: string
  category: string
  source: string
  published: string
}

export interface PaperOfWeek {
  index: number
  headline: string
  summary: string
  key_takeaway: string
  excitement_score: number
  paper: Paper
}

export interface TopPaper {
  index: number
  tldr: string
  bullets: string[]
  who_should_read: string
  paper: Paper
}

export interface OneThingToTry {
  action: string
  why: string
  time_estimate: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
}

export interface GithubRepo {
  id: string
  title: string
  summary: string
  url: string
  stars: number
  language: string
  topics: string[]
  source: string
  created_at: string
}

export interface HNPost {
  id: string
  title: string
  url: string
  hn_url: string
  points: number
  comments: number
  author: string
  source: string
}

export type Cadence = 'daily' | 'weekly' | 'paused'

export interface DeepDive {
  problem: string
  approach: string
  results: string
  limitations: string
  what_it_unlocks: string
}

export interface DigestData {
  post_style: 'roundup' | 'deep-dive'
  week_number: number
  edition_date: string
  cadence: Cadence
  generated_at: string
  paper_of_week: PaperOfWeek
  top_papers: TopPaper[]
  deep_dive: DeepDive | null
  one_thing_to_try: OneThingToTry
  github_repos: GithubRepo[]
  hn_posts: HNPost[]
  implementation_gaps: Paper[]
}
