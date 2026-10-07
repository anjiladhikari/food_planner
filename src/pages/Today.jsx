import { useEffect, useState } from "react";
import MealCard from "../components/MealCard.jsx";
import { deductInventoryItem } from "../lib/inventory.js";
import {
  SHEETS,
  getTodayIndex,
  getWeekdayName,
  mealLines,
  useSheet,
} from "../lib/sheets.js";
import {
  getMealCompletions,
  completeMeal,
} from "../lib/meals.js";

const MEAL_BUTTON =
  "rounded-full border px-2 py-1 text-[11px] font-medium transition-all duration-150 sm:px-2.5 sm:py-0.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/40 focus-visible:ring-offset-2 focus-visible:ring-offset-cream sm:text-[13px] ";

const MEAL_BUTTON_DONE =
  "cursor-default border-olive/40 bg-olive/10 text-olive";

const MEAL_BUTTON_TODO =
  "cursor-pointer border-line bg-surface text-muted hover:border-ink/40 hover:bg-ink/5 hover:text-ink active:translate-y-0 motion-safe:hover:-translate-y-px";

const NAV_BUTTON =
  "shrink-0 cursor-pointer rounded-full border border-line bg-surface px-2 py-1 text-[11px] font-medium sm:px-2.5 sm:py-0.5 transition-all duration-150 hover:border-ink hover:bg-ink hover:text-cream hover:shadow-md hover:shadow-black/30 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ink/40 focus-visible:ring-offset-2 focus-visible:ring-offset-cream active:translate-y-0 motion-safe:hover:-translate-y-px sm:text-[13px]";

export default function Today({ user, onRequireLogin }) {
  const { rows, error, loading } = useSheet(SHEETS.plan);
  const [offset, setOffset] = useState(0);
  const [completed, setCompleted] = useState([]);

  function getDate(offset) {
    const date = new Date();
    date.setDate(date.getDate() + offset);

    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, "0");
    const day = String(date.getDate()).padStart(2, "0");

    return `${year}-${month}-${day}`;
  }

  useEffect(() => {
    getMealCompletions(getDate(offset))
      .then((data) =>
        setCompleted(data.map((item) => item.meal_type))
      )
      .catch(console.error);
  }, [offset]);

  function parseFood(line) {
    const match = line.match(
      /^(\d+(?:\.\d+)?)\s*(g|ml)?\s*(.+)$/i
    );

    if (!match) return null;

    const amount = Number(match[1]);

    let foodName = match[3]
      .replace(/\(dry\)/gi, "")
      .replace(/\(in springwater\)/gi, "")
      .trim();

    // Match names used in inventory
    if (/boiled eggs?/i.test(foodName)) foodName = "Eggs";
    if (/lite milk/i.test(foodName)) foodName = "Milk";

    return {
      foodName,
      amount,
    };
  }

  async function handleComplete(mealType) {
    if (!user) {
      onRequireLogin();
      return;
    }

    if (completed.includes(mealType)) return;

    try {
      let mealText = "";

      // row[0] = Day
      // row[1] = Weekday
      // row[2] = Breakfast
      // row[3] = Lunch
      // row[4] = Dinner
      // row[5] = Nutrition
      if (mealType === "breakfast") mealText = row[2];
      if (mealType === "lunch") mealText = row[3];
      if (mealType === "dinner") mealText = row[4];

      const foods = mealLines(mealText);

      for (const line of foods) {
        const food = parseFood(line);

        if (food) {
          await deductInventoryItem(
            food.foodName,
            food.amount
          );
        }
      }

      await completeMeal(getDate(offset), mealType);

      setCompleted((current) => [
        ...current,
        mealType,
      ]);
    } catch (error) {
      console.error(error);
    }
  }

  if (loading) {
    return (
      <p className="py-16 text-center text-muted">
        Loading food plan…
      </p>
    );
  }

  if (error || !rows.length) {
    return (
      <p className="py-16 text-center text-muted">
        Could not load the food plan.
      </p>
    );
  }

  // getTodayIndex now finds today's row using the Weekday column.
  const index =
    (getTodayIndex(rows) + offset) % rows.length;

  const row = rows[index];

  const previousRow =
    rows[(index - 1 + rows.length) % rows.length];

  const nextRow =
    rows[(index + 1) % rows.length];

  return (
    <>
      <div className="flex flex-wrap items-center gap-x-2 gap-y-1.5 sm:gap-x-3">
        <button
          type="button"
          onClick={() =>
            setOffset((value) => (value + 6) % 7)
          }
          className={NAV_BUTTON}
        >
          ← {previousRow[0]}
        </button>

        <div className="flex shrink-0 items-baseline gap-2 sm:border-r sm:border-line sm:pr-3">
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-clay sm:text-[11px]">
            {getWeekdayName(offset)} ·
          </p>

          <h2 className="font-display text-base leading-tight tracking-tight sm:text-lg">
            {row[0]}
          </h2>
        </div>

        <div className="order-last flex w-full flex-wrap items-center gap-1 sm:order-none sm:w-auto sm:gap-1.5">
          <span className="group relative inline-flex">
            <button
              type="button"
              onClick={() =>
                handleComplete("breakfast")
              }
              disabled={completed.includes("breakfast")}
              className={
                MEAL_BUTTON +
                (completed.includes("breakfast")
                  ? MEAL_BUTTON_DONE
                  : MEAL_BUTTON_TODO)
              }
            >
              {completed.includes("breakfast")
                ? "✓ Breakfast"
                : "Breakfast"}
            </button>

            {!completed.includes("breakfast") && (
              <span
                role="tooltip"
                className="pointer-events-none absolute left-1/2 top-full z-30 mt-2 hidden w-52 -translate-x-1/2 rounded-lg border border-line bg-surface px-3 py-2 text-[11px] leading-snug text-muted shadow-md shadow-black/30 sm:group-focus-within:block sm:group-hover:block"
              >
                Have you finished breakfast? Click only
                after you have eaten it.
              </span>
            )}
          </span>

          <span className="group relative inline-flex">
            <button
              type="button"
              onClick={() =>
                handleComplete("lunch")
              }
              disabled={completed.includes("lunch")}
              className={
                MEAL_BUTTON +
                (completed.includes("lunch")
                  ? MEAL_BUTTON_DONE
                  : MEAL_BUTTON_TODO)
              }
            >
              {completed.includes("lunch")
                ? "✓ Lunch"
                : "Lunch"}
            </button>

            {!completed.includes("lunch") && (
              <span
                role="tooltip"
                className="pointer-events-none absolute left-1/2 top-full z-30 mt-2 hidden w-52 -translate-x-1/2 rounded-lg border border-line bg-surface px-3 py-2 text-[11px] leading-snug text-muted shadow-md shadow-black/30 sm:group-focus-within:block sm:group-hover:block"
              >
                Have you finished lunch? Click only after
                you have eaten it.
              </span>
            )}
          </span>

          <span className="group relative inline-flex">
            <button
              type="button"
              onClick={() =>
                handleComplete("dinner")
              }
              disabled={completed.includes("dinner")}
              className={
                MEAL_BUTTON +
                (completed.includes("dinner")
                  ? MEAL_BUTTON_DONE
                  : MEAL_BUTTON_TODO)
              }
            >
              {completed.includes("dinner")
                ? "✓ Dinner"
                : "Dinner"}
            </button>

            {!completed.includes("dinner") && (
              <span
                role="tooltip"
                className="pointer-events-none absolute left-1/2 top-full z-30 mt-2 hidden w-52 -translate-x-1/2 rounded-lg border border-line bg-surface px-3 py-2 text-[11px] leading-snug text-muted shadow-md shadow-black/30 sm:group-focus-within:block sm:group-hover:block"
              >
                Have you finished dinner? Click only after
                you have eaten it.
              </span>
            )}
          </span>
        </div>

        <button
          type="button"
          onClick={() =>
            setOffset((value) => (value + 1) % 7)
          }
          className={"ml-auto " + NAV_BUTTON}
        >
          {nextRow[0]} →
        </button>
      </div>

      <div className="mt-4 space-y-2.5 sm:mt-8 sm:space-y-4">
        <MealCard
          accent="breakfast"
          title="Breakfast"
          time="8–9 AM"
          items={mealLines(row[2])}
        />

        <MealCard
          accent="lunch"
          title="Lunch"
          time="1–3 PM"
          items={mealLines(row[3])}
        />

        <MealCard
          accent="dinner"
          title="Dinner"
          time="6–7 PM"
          items={mealLines(row[4])}
        />

        <MealCard
          accent="nutrition"
          title="Daily Nutrition & Cost"
          items={mealLines(row[5])}
        />
      </div>
    </>
  );
}