import { ArrowUpRight } from "lucide-react";
import type { Paper } from "@/types/digest";

/* The pipeline searches GitHub for an implementation of every hot paper.
   Papers that come back with nothing are the interesting ones — that is
   an unclaimed build. It was being computed and then discarded. */
export default function GapRadar({ papers }: { papers: Paper[] }) {
  const gaps = papers?.filter((p) => p?.title) ?? [];

  return (
    <section aria-labelledby="gap-heading">
      <h2
        id="gap-heading"
        className="wd-tight text-[1.4rem] font-extrabold uppercase leading-none tracking-[-0.015em]"
      >
        No code yet
      </h2>
      <p className="mt-2.5 max-w-[46ch] text-[14px] leading-relaxed text-ink-2">
        Papers with no implementation on GitHub. An unclaimed build.
      </p>

      {gaps.length === 0 ? (
        <p className="mt-5 border-t border-rule pt-5 text-[14px] leading-relaxed text-ink-3">
          Nothing open this time — every paper checked already has code in the
          wild.
        </p>
      ) : (
        <ul className="mt-5 border-t border-rule">
          {gaps.map((p) => (
            <li key={p.id} className="border-b border-rule py-4">
              <a
                href={p.url}
                target="_blank"
                rel="noreferrer"
                className="ulink group inline-flex items-start gap-1.5 text-[15px] font-semibold leading-snug"
              >
                <span className="balance">{p.title}</span>
                <ArrowUpRight
                  size={15}
                  strokeWidth={2.5}
                  className="mt-1 shrink-0"
                  aria-hidden
                />
              </a>
              {p.category && (
                <p className="mt-1.5 text-[13px] text-ink-3">{p.category}</p>
              )}
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
