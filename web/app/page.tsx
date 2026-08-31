import { promises as fs } from "fs";
import path from "path";
import type { DigestData } from "@/types/digest";
import Masthead from "@/components/Masthead";
import Lead from "@/components/Lead";
import Board from "@/components/Board";
import DeepDive from "@/components/DeepDive";
import TryThis from "@/components/TryThis";
import GapRadar from "@/components/GapRadar";
import Signals from "@/components/Signals";
import Repos from "@/components/Repos";
import CadenceControl from "@/components/CadenceControl";

async function getDigestData(): Promise<DigestData> {
  const filePath = path.join(process.cwd(), "public", "data", "latest.json");
  const raw = await fs.readFile(filePath, "utf-8");
  return JSON.parse(raw);
}

export default async function Home() {
  const data = await getDigestData();

  const topPapers = data.top_papers?.filter((p) => p?.paper?.title) ?? [];
  const gaps = data.implementation_gaps ?? [];
  const signals = data.hn_posts ?? [];
  const repos = data.github_repos ?? [];
  const isDeepDive = data.post_style === "deep-dive" && !!data.deep_dive;

  return (
    <>
      <Masthead
        generatedAt={data.generated_at}
        editionDate={data.edition_date}
        weekNumber={data.week_number}
        postStyle={data.post_style}
        counts={{
          papers: topPapers.length + (data.paper_of_week ? 1 : 0),
          repos: repos.length,
          signals: signals.length,
          gaps: gaps.length,
        }}
      />

      <main className="mx-auto w-full max-w-[76rem] px-5 sm:px-8">
        {data.paper_of_week && <Lead data={data.paper_of_week} soloEdition={isDeepDive} />}

        {isDeepDive && data.deep_dive ? (
          <DeepDive data={data.deep_dive} />
        ) : (
          <Board papers={topPapers} />
        )}

        {data.one_thing_to_try && <TryThis data={data.one_thing_to_try} />}

        <div className="grid gap-x-12 gap-y-10 border-t border-rule py-10 sm:py-14 lg:grid-cols-2">
          <GapRadar papers={gaps} />
          <Signals posts={signals} />
        </div>

        <Repos repos={repos.slice(0, 6)} />

        <CadenceControl current={data.cadence ?? "weekly"} />
      </main>

      <footer className="border-t-2 border-ink">
        <div className="mx-auto flex w-full max-w-[76rem] flex-wrap items-baseline justify-between gap-x-8 gap-y-2 px-5 py-8 sm:px-8">
          <p className="text-[13px] font-semibold">
            ML Research Pulse — rebuilt every day, by itself.
          </p>
          <p className="text-[13px] text-ink-3">
            arXiv · Hacker News · GitHub · summarised by GPT-OSS 120B on Groq
          </p>
        </div>
      </footer>
    </>
  );
}
