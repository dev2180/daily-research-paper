import type { OneThingToTry } from "@/types/digest";

export default function TryThis({ data }: { data: OneThingToTry }) {
  const { action, why, time_estimate, difficulty } = data;
  if (!action) return null;

  return (
    /* Deliberately the only inverted block on the page: it is the one
       thing here you are meant to act on rather than read. */
    <section
      aria-labelledby="try-heading"
      className="my-10 bg-ink px-5 py-10 text-surface sm:my-14 sm:px-10 sm:py-12"
    >
      <div className="grid gap-x-12 gap-y-6 lg:grid-cols-[minmax(0,1fr)_16rem]">
        <div className="min-w-0">
          <h2
            id="try-heading"
            className="wd-tight text-[13px] font-extrabold uppercase tracking-[0.1em] opacity-60"
          >
            Do this today
          </h2>
          <p className="balance mt-4 text-[clamp(1.35rem,3vw,2rem)] font-bold leading-[1.14] tracking-[-0.02em]">
            {action}
          </p>
          {why && (
            <p className="pretty mt-4 max-w-[60ch] text-[15px] leading-relaxed opacity-75">
              {why}
            </p>
          )}
        </div>

        <dl className="flex gap-10 self-end lg:flex-col lg:gap-5">
          {time_estimate && (
            <div>
              <dt className="text-[12px] font-semibold uppercase tracking-[0.08em] opacity-75">
                Time
              </dt>
              <dd className="tnum mt-1 text-[1.1rem] font-bold">{time_estimate}</dd>
            </div>
          )}
          {difficulty && (
            <div>
              <dt className="text-[12px] font-semibold uppercase tracking-[0.08em] opacity-75">
                Level
              </dt>
              <dd className="mt-1 text-[1.1rem] font-bold capitalize">{difficulty}</dd>
            </div>
          )}
        </dl>
      </div>
    </section>
  );
}
