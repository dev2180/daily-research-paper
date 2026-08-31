import type { GithubRepo } from "@/types/digest";

export default function Repos({ repos }: { repos: GithubRepo[] }) {
  const items = repos?.filter((r) => r?.title) ?? [];
  if (!items.length) return null;

  return (
    <section aria-labelledby="repos-heading" className="border-t border-rule py-10 sm:py-14">
      <div className="mb-6 flex items-baseline justify-between gap-4">
        <h2
          id="repos-heading"
          className="wd-tight text-[clamp(1.4rem,3vw,2rem)] font-extrabold uppercase leading-none tracking-[-0.02em]"
        >
          New repos worth a look
        </h2>
        <span className="shrink-0 text-[13px] font-semibold text-ink-3">
          past 7 days
        </span>
      </div>

      <ul className="grid gap-x-10 gap-y-0 sm:grid-cols-2">
        {items.map((r) => {
          const [owner, name] = r.title.split("/");
          return (
            <li key={r.id} className="border-t border-rule py-4">
              <div className="flex items-baseline justify-between gap-4">
                <a
                  href={r.url}
                  target="_blank"
                  rel="noreferrer"
                  className="ulink min-w-0 text-[15px] font-bold"
                >
                  <span className="text-ink-3 font-medium">{owner}/</span>
                  {name ?? r.title}
                </a>
                <span className="tnum shrink-0 text-[13px] font-semibold text-ink-2">
                  {r.stars.toLocaleString()}★
                </span>
              </div>
              <p className="pretty mt-1.5 line-clamp-2 text-[13.5px] leading-snug text-ink-2">
                {r.summary}
              </p>
              {r.language && (
                <p className="mt-1.5 text-[12.5px] font-medium text-ink-3">
                  {r.language}
                </p>
              )}
            </li>
          );
        })}
      </ul>
    </section>
  );
}
