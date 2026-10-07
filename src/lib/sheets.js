import { useEffect, useState } from "react";

export const SHEET_ID = "1QwwTSwh7imbzvkHXPvvtZ5awNyf41r_aMnQUsLFivAY";

export const SHEETS = {
  plan: "food plan",
  shopping: "cooking links and which food",
  cooking: "how to cook",
};

// One in-memory entry per sheet, kept for the whole page session.
// The promise itself is cached so concurrent callers share a single fetch.
const cache = {};

export function getSheet(sheetName) {
  if (cache[sheetName]) {
    return cache[sheetName];
  }

  const url =
    `https://docs.google.com/spreadsheets/d/${SHEET_ID}/gviz/tq` +
    `?tqx=out:json&sheet=${encodeURIComponent(sheetName)}`;

  const request = fetch(url)
    .then((response) => response.text())
    .then((text) => {
      const data = JSON.parse(text.substring(47, text.length - 2));

      return data.table.rows
        .map((row) => row.c.map((cell) => cell?.v ?? ""))
        .filter((row) => {
          const first = String(row[0]).trim();

          return first && first !== "Day" && first !== "Food Item";
        });
    })
    .catch((error) => {
      // Let a failed sheet be retried later instead of caching the failure.
      delete cache[sheetName];
      throw error;
    });

  cache[sheetName] = request;

  return request;
}

export function useSheet(sheetName) {
  const [rows, setRows] = useState(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let active = true;

    setError(false);

    getSheet(sheetName)
      .then((data) => active && setRows(data))
      .catch((err) => {
        console.error(err);
        if (active) setError(true);
      });

    return () => {
      active = false;
    };
  }, [sheetName]);

  return { rows, error, loading: !rows && !error };
}

// A sheet cell holds one meal as newline separated "+ item" lines.
export function mealLines(text) {
  if (!text) return [];

  return String(text)
    .split("\n")
    .map((item) => item.replace(/^[+•]\s*/, "").trim())
    .filter(Boolean);
}

// The foods the meal plan actually names, parsed the same way a completed
// meal is when it is deducted from inventory. Unique and alphabetical.
export function planFoodNames(rows) {
  const names = new Set();

  (rows || []).forEach((row) => {
    // Weekday is now row[1].
    // Meals are breakfast=row[2], lunch=row[3], dinner=row[4].
    [2, 3, 4].forEach((column) => {
      mealLines(row[column]).forEach((line) => {
        const match = line.match(
          /^(\d+(?:\.\d+)?)\s*(g|ml)?\s*(.+)$/i
        );

        if (!match) return;

        let name = match[3]
          .replace(/\(dry\)/gi, "")
          .replace(/\(in springwater\)/gi, "")
          .trim();

        if (/boiled eggs?/i.test(name)) name = "Eggs";
        if (/lite milk/i.test(name)) name = "Milk";

        // "Rolled Oats + 15g Chia" is two foods, not one item.
        name.split(/\s*\+\s*/).forEach((part) => {
          const food = part
            .replace(/^\d+(?:\.\d+)?\s*(g|ml)?\s*/i, "")
            .trim();

          if (food) names.add(food);
        });
      });
    });
  });

  return [...names].sort((a, b) => a.localeCompare(b));
}

// Find today's meal-plan row using the Weekday column in Google Sheets.
// This keeps the mapping data-driven instead of hardcoding Day 1 = Monday.
export function getTodayIndex(rows) {
  const today = getWeekdayName(0).toLowerCase();

  const index = (rows || []).findIndex(
    (row) => String(row[1]).trim().toLowerCase() === today
  );

  return index >= 0 ? index : 0;
}

export function getWeekdayName(offset = 0) {
  const date = new Date();

  date.setDate(date.getDate() + offset);

  return date.toLocaleDateString("en-AU", {
    weekday: "long",
  });
}

export function dayLabel(offset) {
  if (offset === 0) {
    return `Today · ${getWeekdayName(0)}`;
  }

  if (offset === 1) {
    return `Tomorrow · ${getWeekdayName(1)}`;
  }

  return getWeekdayName(offset);
}