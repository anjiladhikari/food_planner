import { useState } from "react";
import MealCard from "../components/MealCard.jsx";
import {
  SHEETS,
  dayLabel,
  getTodayIndex,
  mealLines,
  useSheet,
} from "../lib/sheets.js";

export default function Week() {
  const { rows, error, loading } = useSheet(SHEETS.plan);
  const [startOffset, setStartOffset] = useState(0);

  if (loading) {
    return (
      <p className="py-16 text-center text-muted">
        Loading weekly plan…
      </p>
    );
  }

  if (error || !rows.length) {
    return (
      <p className="py-16 text-center text-muted">
        Could not load the weekly plan.
      </p>
    );
  }

  // Weekday is now stored in row[1],
  // so getTodayIndex finds today's row from the sheet itself.
  const todayIndex = getTodayIndex(rows);

  const rowFor = (offset) =>
    rows[(todayIndex + offset) % rows.length];

  const allOffsets = [0, 1, 2, 3, 4, 5, 6];

  const visibleOffsets = [0, 1, 2, 3].map(
    (i) => (startOffset + i) % 7
  );

  return (
    <>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1.5 sm:gap-x-4">
        <h2 className="shrink-0 font-display text-lg leading-tight tracking-tight sm:border-r sm:border-line sm:pr-4 sm:text-2xl">
          Weekly Plan
        </h2>

        <div className="flex min-w-0 flex-1 flex-wrap gap-1 sm:gap-2">
          {allOffsets.map((offset) => {
            const isActive = offset === startOffset;

            return (
              <button
                key={offset}
                type="button"
                onClick={() => setStartOffset(offset)}
                className={
                  "cursor-pointer rounded-full border px-2 py-1 text-[11px] font-medium transition-all duration-150 sm:px-3 sm:py-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/40 focus-visible:ring-offset-2 focus-visible:ring-offset-cream active:translate-y-0 motion-safe:hover:-translate-y-px sm:text-[13px] " +
                  (isActive
                    ? "border-ink bg-ink text-cream"
                    : "border-line bg-surface text-muted hover:border-ink/40 hover:bg-ink/5 hover:text-ink")
                }
              >
                {rowFor(offset)[0]}
              </button>
            );
          })}
        </div>
      </div>

      <div className="mt-3 grid grid-cols-4 gap-1 sm:mt-6 sm:gap-4">
        {visibleOffsets.map((offset) => {
          const row = rowFor(offset);

          return (
            <div
              key={offset}
              className={
                "row-span-5 grid min-w-0 grid-rows-subgrid gap-y-2 rounded-xl border bg-surface p-2 sm:gap-y-4 sm:rounded-2xl sm:p-5 " +
                (offset === startOffset
                  ? "border-ink/25"
                  : "border-line")
              }
            >
              <div className="min-w-0">
                <p className="text-[9px] leading-tight font-semibold uppercase tracking-[0.08em] break-words text-clay sm:text-[11px] sm:tracking-[0.14em]">
                  {dayLabel(offset)}
                </p>

                <h3 className="mt-0.5 font-display text-sm sm:text-xl">
                  {row[0]}
                </h3>
              </div>

              <MealCard
                compact
                accent="breakfast"
                title="Breakfast"
                items={mealLines(row[2])}
              />

              <MealCard
                compact
                accent="lunch"
                title="Lunch"
                items={mealLines(row[3])}
              />

              <MealCard
                compact
                accent="dinner"
                title="Dinner"
                items={mealLines(row[4])}
              />

              <MealCard
                compact
                accent="nutrition"
                title="Nutrition"
                items={mealLines(row[5])}
              />
            </div>
          );
        })}
      </div>
    </>
  );
}