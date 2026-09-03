import type { Cadence } from "@/types/digest";

const REPO = process.env.NEXT_PUBLIC_REPO_SLUG || "dev2180/daily-research-paper";

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

/* GitHub delays and sometimes drops scheduled runs, so there has to be a way
   to force today's send by hand. Same mechanism as the cadence buttons: the
   digest workflow itself listens for this issue, checks the author is the
   repo owner, runs, then closes it. */
const SEND_NOW_URL =
  `https://github.com/${REPO}/issues/new` +
  `?title=${encodeURIComponent("send: now")}` +
  `&labels=${encodeURIComponent("digest-send")}` +
  `&body=${encodeURIComponent(
    [
      "Rebuild the digest and email it now.",
      "",
      "Submitting this issue runs the digest workflow immediately, then closes",
      "this issue. Only the repository owner can trigger it.",
    ].join("\n"),
  )}`;

const ACTIONS_URL = `https://github.com/${REPO}/actions/workflows/weekly_digest.yml`;

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

      <div className="mt-8 border-t-2 border-ink pt-6">
        <div className="flex flex-wrap items-baseline justify-between gap-x-8 gap-y-3">
          <div className="min-w-0">
            <h3 className="text-[1.05rem] font-bold leading-snug">
              Today&rsquo;s email never arrived?
            </h3>
            <p className="pretty mt-1.5 max-w-[52ch] text-[14px] leading-relaxed text-ink-2">
              Scheduled runs are best-effort and can be delayed or skipped. This
              rebuilds the board and sends it right now.
            </p>
          </div>
          <a
            href={SEND_NOW_URL}
            target="_blank"
            rel="noreferrer"
            className="cadence-option shrink-0 border-2 px-6 py-3 text-[15px] font-bold no-underline"
          >
            Send it now &rarr;
          </a>
        </div>
      </div>

      <p className="pretty mt-6 max-w-[68ch] text-[13.5px] leading-relaxed text-ink-3">
        Both controls open a prefilled issue on{" "}
        <a
          href={`https://github.com/${REPO}`}
          target="_blank"
          rel="noreferrer"
          className="ulink font-semibold"
        >
          {REPO}
        </a>
        . Submit it and a workflow does the rest, then closes the issue. Only
        the repository owner can trigger either one. A cadence change shows on
        the page after the next build. You can also run it straight from{" "}
        <a
          href={ACTIONS_URL}
          target="_blank"
          rel="noreferrer"
          className="ulink font-semibold"
        >
          the Actions tab
        </a>
        .
      </p>
    </section>
  );
}
