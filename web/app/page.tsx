import { promises as fs } from "fs";
import path from "path";
import type { DigestData } from "@/types/digest";
import Hero from "@/components/Hero";
import PaperOfWeekCard from "@/components/PaperOfWeek";
import TopPapers from "@/components/TopPapers";
import OneThingToTryCard from "@/components/OneThingToTry";
import GithubRepos from "@/components/GithubRepos";

async function getDigestData(): Promise<DigestData> {
  const filePath = path.join(process.cwd(), "public", "data", "latest.json");
  const raw = await fs.readFile(filePath, "utf-8");
  return JSON.parse(raw);
}

export default async function Home() {
  const data = await getDigestData();

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <Hero
        weekNumber={data.week_number}
        postStyle={data.post_style}
        generatedAt={data.generated_at}
      />

      <main className="max-w-4xl mx-auto px-6 py-14 flex flex-col gap-14">

        {data.paper_of_week && <PaperOfWeekCard data={data.paper_of_week} />}

        {data.top_papers?.length > 0 && <TopPapers papers={data.top_papers} />}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {data.one_thing_to_try && <OneThingToTryCard data={data.one_thing_to_try} />}
          {data.github_repos?.length > 0 && <GithubRepos repos={data.github_repos.slice(0, 4)} />}
        </div>
      </main>

      <footer className="border-t py-10 text-center" style={{ borderColor: "var(--border)" }}>
        <p className="text-xs" style={{ color: "var(--text-muted)" }}>
          ML Research Pulse · Automated weekly digest · arXiv + Groq GPT-OSS 120B
        </p>
      </footer>
    </div>
  );
}
