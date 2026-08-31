import { ArrowUpRight } from "lucide-react";
import type { PaperOfWeek } from "@/types/digest";

export default function Lead({ data, soloEdition = false }: { data: PaperOfWeek; soloEdition?: boolean }) {
  const { paper, headline, summary, key_takeaway, excitement_score } = data;

  const paras = summary
    ?.split(/\n\n|\n(?=[A-Z])/)
    .map((p) => p.trim())
    .filter(Boolean) ?? [];

  const authors = paper.authors?.slice(0, 3).join(", ");

  return (
    <section aria-labelledby="lead-heading" className="border-b border-rule py-10 sm:py-14">
      <div className="grid gap-x-10 gap-y-7 lg:grid-cols-[7.5rem_minmax(0,1fr)]">
        {/* Rank is the design. Position 01 is the whole point of the page. */}
        <div className="flex items-start gap-4 lg:block">
          <div
            aria-hidden
            className="wd-wide tnum text-[clamp(3.5rem,9vw,6rem)] font-extrabold leading-[0.78] tracking-[-0.045em]"
          >
            01
          </div>
          <p className="mt-0 max-w-[8rem] pt-2 text-[13px] font-semibold uppercase leading-tight tracking-[0.04em] text-ink-2 lg:mt-3 lg:pt-0">
            {soloEdition ? "The" : "Read this"}
            <br />
            {soloEdition ? "whole edition" : "one first"}
          </p>
        </div>

        <div className="min-w-0">
          <h2
            id="lead-heading"
            className="balance text-[clamp(1.75rem,4.2vw,3rem)] font-bold leading-[1.06] tracking-[-0.025em]"
          >
            {headline}
          </h2>

          <p className="pretty mt-4 max-w-[62ch] text-[15px] font-medium leading-relaxed text-ink-2">
            {paper.title}
          </p>

          <p className="mt-2 text-[14px] text-ink-3">
            {authors}
            {paper.authors?.length > 3 ? " et al." : ""}
            {paper.category ? ` · ${paper.category}` : ""}
            <span className="tnum"> · {excitement_score}/10 signal</span>
          </p>

          {key_takeaway && (
            <p className="mt-7 max-w-[54ch] text-[clamp(1.05rem,2vw,1.3rem)] font-semibold leading-snug">
              <span className="marked">{key_takeaway}</span>
            </p>
          )}

          {paras.length > 0 && (
            <div className="mt-7 max-w-[68ch] space-y-4">
              {paras.map((p, i) => (
                <p key={i} className="pretty text-[15.5px] leading-[1.62] text-ink-2">
                  {p}
                </p>
              ))}
            </div>
          )}

          <div className="mt-8 flex flex-wrap items-center gap-x-7 gap-y-3">
            <a
              href={paper.url}
              target="_blank"
              rel="noreferrer"
              className="ulink inline-flex items-center gap-1.5 text-[15px] font-bold"
            >
              Read the paper
              <ArrowUpRight size={16} strokeWidth={2.5} aria-hidden />
            </a>
            {paper.pdf_url && (
              <a
                href={paper.pdf_url}
                target="_blank"
                rel="noreferrer"
                className="ulink inline-flex items-center gap-1.5 text-[15px] font-semibold text-ink-2"
              >
                PDF
                <ArrowUpRight size={15} strokeWidth={2.5} aria-hidden />
              </a>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
