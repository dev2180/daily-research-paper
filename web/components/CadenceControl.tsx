import type { Cadence } from "@/types/digest";

const REPO = process.env.NEXT_PUBLIC_REPO_SLUG || "dev2180/ml-research-pulse";

const OPTIONS: { value: Cadence; label: string; detail: string }[] = [
  { value: "daily", label: "Every day", detail: "Every morning, 8 AM IST" },
  { value: "weekly", label: "Once a week", detail: "Sundays, 8 AM IST" },
  { value: "paused", label: "Pause email", detail: "Page keeps updating" },
];

/* This page is a static export on GitHub Pages: no backend, and no token can
   live in a public bundle. So the control does the one thing a static page
   legitimately can — it opens a prefilled issue against the repo, which a
   workflow reads, validates against the repo owner, and commits to
   digest_config.json. The pipeline reads that file on its next run. */
function issueUrl(value: Cadence): string {
  const title = `cadence: ${value}`;
  const body = [
    `Set the digest email cadence to **${value}**.`,
    "",
    "Submitting this issue triggers the `set-cadence` workflow, which updates",
    "`digest_config.json` on `main` and closes this issue. Only the repository",
    "owner can change the setting.",
  ].join("\n");
  return (
    `https://github.com/${REPO}/issues/new` +
    `?title=${encodeURIComponent(title)}` +
    `&labels=${encodeURIComponent("digest-cadence")}` +
    `&body=${encodeURIComponent(body)}`
  );
}

export default function CadenceControl({ current }: { current: Cadence }) {
  return (
    <section aria-labelledby="cadence-heading" className="border-t border-rule py-10 sm:py-14">
      <h2
        id="cadence-heading"
        className="wd-tight text-[clamp(1.4rem,3vw,2rem)] font-extrabold uppercase leading-none tracking-[-0.02em]"
      >
        How often should this land in your inbox?
      </h2>
      <p className="pretty mt-3 max-w-[60ch] text-[15px] leading-relaxed text-ink-2">
        The board rebuilds every day either way. This only changes the email.
      </p>

      <ul className="mt-7 grid gap-3 sm:grid-cols-3">
        {OPTIONS.map((opt) => {
          const active = opt.value === current;
          return (
            <li key={opt.value}>
              <a
                href={issueUrl(opt.value)}
                target="_blank"
                rel="noreferrer"
                aria-current={active ? "true" : undefined}
                className="cadence-option group block h-full border-2 px-5 py-4 no-underline"
              >
                <span className="flex items-baseline justify-between gap-3">
                  <span className="text-[16px] font-bold">{opt.label}</span>
                  {active && (
                    <span className="text-[11px] font-extrabold uppercase tracking-[0.08em]">
                      Current
                    </span>
                  )}
                </span>
                <span className="cadence-detail mt-1 block text-[13.5px]">
                  {opt.detail}
                </span>
                {!active && (
                  <span className="mt-3 block text-[13px] font-bold">
                    Switch to this &rarr;
                  </span>
                )}
              </a>
            </li>
          );
        })}
      </ul>

      <p className="pretty mt-5 max-w-[68ch] text-[13.5px] leading-relaxed text-ink-3">
        Choosing an option opens a prefilled issue on{" "}
        <a
          href={`https://github.com/${REPO}`}
          target="_blank"
          rel="noreferrer"
          className="ulink font-semibold"
        >
          {REPO}
        </a>
        . Submit it and a workflow commits the change, then closes the issue.
        Only the repository owner can change the setting, and the page shows the
        new value after the next daily build.
      </p>
    </section>
  );
}
