interface MastheadProps {
  generatedAt: string;
  editionDate?: string;
  weekNumber: number;
  postStyle: string;
  counts: { papers: number; repos: number; signals: number; gaps: number };
}

function Stat({ n, label }: { n: number; label: string }) {
  return (
    <span className="inline-flex items-baseline gap-1.5">
      <span className="tnum text-[15px] font-bold">{n}</span>
      <span className="text-[13px] font-medium opacity-70">{label}</span>
    </span>
  );
}

export default function Masthead({
  generatedAt,
  editionDate,
  weekNumber,
  postStyle,
  counts,
}: MastheadProps) {
  const d = new Date(editionDate || generatedAt);
  const stamp = d.toLocaleDateString("en-GB", {
    weekday: "short",
    day: "numeric",
    month: "short",
    year: "numeric",
    timeZone: "UTC",
  });

  return (
    /* Drenched band. The signal colour carries the identity in one move,
       then recedes to marking-only for the rest of the page. */
    <header className="bg-signal text-[oklch(0.17_0.008_118)]">
      <div className="mx-auto w-full max-w-[76rem] px-5 py-7 sm:px-8 sm:py-9">
        <div className="flex flex-wrap items-end justify-between gap-x-8 gap-y-5">
          <div>
            <h1 className="wd-tight text-[clamp(2.5rem,8vw,5rem)] font-extrabold leading-[0.86] tracking-[-0.03em] uppercase">
              ML Research
              <br />
              Pulse
            </h1>
          </div>

          <div className="flex flex-col items-start gap-2 sm:items-end">
            <p className="tnum text-[15px] font-semibold">{stamp}</p>
            <p className="text-[13px] font-medium opacity-70">
              Edition {weekNumber} · {postStyle}
            </p>
          </div>
        </div>

        <div className="mt-7 flex flex-wrap items-baseline gap-x-6 gap-y-2 border-t-2 border-current/25 pt-4">
          <Stat n={counts.papers} label="papers ranked" />
          <Stat n={counts.gaps} label="code gaps" />
          <Stat n={counts.repos} label="repos" />
          <Stat n={counts.signals} label="discussions" />
          <span className="text-[13px] font-medium opacity-70">
            Assembled automatically · arXiv + GPT-OSS 120B
          </span>
        </div>
      </div>
    </header>
  );
}
