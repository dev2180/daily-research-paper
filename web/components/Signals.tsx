import type { HNPost } from "@/types/digest";

export default function Signals({ posts }: { posts: HNPost[] }) {
  const items = posts?.filter((p) => p?.title) ?? [];
  if (!items.length) return null;

  return (
    <section aria-labelledby="signals-heading">
      <h2
        id="signals-heading"
        className="wd-tight text-[1.4rem] font-extrabold uppercase leading-none tracking-[-0.015em]"
      >
        What they argued about
      </h2>
      <p className="mt-2.5 max-w-[46ch] text-[14px] leading-relaxed text-ink-2">
        The AI threads that drew a crowd on Hacker News.
      </p>

      <ul className="mt-5 border-t border-rule">
        {items.map((p) => (
          <li key={p.id} className="border-b border-rule py-4">
            <a
              href={p.url || p.hn_url}
              target="_blank"
              rel="noreferrer"
              className="ulink balance text-[15px] font-semibold leading-snug"
            >
              {p.title}
            </a>
            <p className="tnum mt-1.5 text-[13px] text-ink-3">
              {p.points} points
              {typeof p.comments === "number" && (
                <>
                  {" · "}
                  <a
                    href={p.hn_url}
                    target="_blank"
                    rel="noreferrer"
                    className="ulink font-semibold"
                  >
                    {p.comments} comments
                  </a>
                </>
              )}
            </p>
          </li>
        ))}
      </ul>
    </section>
  );
}
