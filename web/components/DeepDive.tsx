import type { DeepDive as DeepDiveData } from "@/types/digest";

const SECTIONS: { key: keyof DeepDiveData; label: string }[] = [
  { key: "problem", label: "The problem" },
  { key: "approach", label: "How it works" },
  { key: "results", label: "What they measured" },
  { key: "limitations", label: "Where it breaks" },
  { key: "what_it_unlocks", label: "What this unlocks" },
];

/* Deep-dive editions carry one paper instead of a board, so the page needs a
   different shape entirely — previously the mode changed a label and nothing
   else, because the summariser returned roundup-shaped data either way. */
export default function DeepDive({ data }: { data: DeepDiveData }) {
  const present = SECTIONS.filter((s) => (data[s.key] ?? "").trim());
  if (!present.length) return null;

  return (
    <section aria-labelledby="deepdive-heading" className="border-b border-rule py-10 sm:py-14">
      <div className="mb-8 flex items-baseline justify-between gap-4">
        <h2
          id="deepdive-heading"
          className="wd-tight text-[clamp(1.6rem,3.4vw,2.25rem)] font-extrabold uppercase leading-none tracking-[-0.02em]"
        >
          The whole edition, one paper
        </h2>
      </div>

      <dl className="grid gap-x-12 gap-y-8 sm:grid-cols-2">
        {present.map(({ key, label }) => (
          <div key={key} className="border-t-2 border-ink pt-4">
            <dt className="text-[13px] font-extrabold uppercase tracking-[0.06em]">
              {label}
            </dt>
            <dd className="pretty mt-2.5 max-w-[62ch] text-[15px] leading-[1.62] text-ink-2">
              {data[key]}
            </dd>
          </div>
        ))}
      </dl>
    </section>
  );
}
