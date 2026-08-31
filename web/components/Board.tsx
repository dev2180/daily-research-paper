import type { TopPaper } from "@/types/digest";

function Row({ data, rank, delay }: { data: TopPaper; rank: number; delay: number }) {
  const { paper, tldr, bullets, who_should_read } = data;
  if (!paper?.title) return null;

  return (
    <li
      className="row-in group border-b border-rule last:border-b-0"
      style={{ "--row-delay": `${delay}ms` } as React.CSSProperties}
    >
      <div className="grid gap-x-7 gap-y-3 py-6 sm:grid-cols-[3.5rem_minmax(0,1fr)] sm:py-7">
        <div
          aria-hidden
          className="wd-wide tnum text-[2rem] font-extrabold leading-none tracking-[-0.04em] text-ink-3 transition-colors duration-200 group-hover:text-ink sm:text-[2.6rem]"
        >
          {String(rank).padStart(2, "0")}
        </div>

        <div className="min-w-0">
          <h3 className="balance text-[1.15rem] font-bold leading-[1.22] tracking-[-0.015em] sm:text-[1.3rem]">
            <a href={paper.url} target="_blank" rel="noreferrer" className="ulink">
              {paper.title}
            </a>
          </h3>

          {tldr && (
            <p className="pretty mt-2.5 max-w-[70ch] text-[15px] leading-relaxed text-ink-2">
              {tldr}
            </p>
          )}

          {bullets?.length > 0 && (
            <ul className="mt-4 grid gap-x-8 gap-y-2 sm:grid-cols-2 lg:grid-cols-3">
              {bullets.map((b, i) => (
                <li
                  key={i}
                  className="border-t border-rule pt-2 text-[13.5px] leading-snug text-ink-2"
                >
                  {b}
                </li>
              ))}
            </ul>
          )}

          {who_should_read && (
            <p className="mt-4 text-[13px] font-semibold text-ink-3">
              For {who_should_read.replace(/^For\s+/i, "")}
            </p>
          )}
        </div>
      </div>
    </li>
  );
}

export default function Board({ papers }: { papers: TopPaper[] }) {
  const rows = papers?.filter((p) => p?.paper?.title) ?? [];
  if (!rows.length) return null;

  return (
    <section aria-labelledby="board-heading" className="border-b border-rule py-10 sm:py-14">
      <div className="mb-2 flex items-baseline justify-between gap-4">
        <h2
          id="board-heading"
          className="wd-tight text-[clamp(1.6rem,3.4vw,2.25rem)] font-extrabold uppercase leading-none tracking-[-0.02em]"
        >
          The rest of the board
        </h2>
        <span className="tnum shrink-0 text-[13px] font-semibold text-ink-3">
          {String(rows.length).padStart(2, "0")} papers
        </span>
      </div>

      <ul className="mt-4">
        {rows.map((p, i) => (
          <Row key={p.paper?.id ?? i} data={p} rank={i + 2} delay={i * 70} />
        ))}
      </ul>
    </section>
  );
}
