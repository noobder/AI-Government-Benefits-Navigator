import { describe, expect, it } from "vitest";
import en from "./en.json";
import hi from "./hi.json";
import ta from "./ta.json";

/** Recursively flattens a nested translation object into dotted key paths,
 * e.g. { common: { nav: { home: "..." } } } -> ["common.nav.home"]. */
function flattenKeys(obj: Record<string, unknown>, prefix = ""): string[] {
  return Object.entries(obj).flatMap(([key, value]) => {
    const path = prefix ? `${prefix}.${key}` : key;
    if (value && typeof value === "object" && !Array.isArray(value)) {
      return flattenKeys(value as Record<string, unknown>, path);
    }
    return [path];
  });
}

describe("locale files stay in sync", () => {
  const enKeys = new Set(flattenKeys(en));
  const hiKeys = new Set(flattenKeys(hi));
  const taKeys = new Set(flattenKeys(ta));

  it("Hindi has every key English has", () => {
    const missing = [...enKeys].filter((k) => !hiKeys.has(k));
    expect(missing).toEqual([]);
  });

  it("Tamil has every key English has", () => {
    const missing = [...enKeys].filter((k) => !taKeys.has(k));
    expect(missing).toEqual([]);
  });

  it("Hindi has no stray keys English doesn't have", () => {
    const extra = [...hiKeys].filter((k) => !enKeys.has(k));
    expect(extra).toEqual([]);
  });

  it("Tamil has no stray keys English doesn't have", () => {
    const extra = [...taKeys].filter((k) => !enKeys.has(k));
    expect(extra).toEqual([]);
  });

  it("no translation value is an empty string", () => {
    for (const [name, locale] of [
      ["en", en],
      ["hi", hi],
      ["ta", ta],
    ] as const) {
      const empties = flattenKeys(locale).filter((path) => {
        const value = path.split(".").reduce<any>((acc, part) => acc?.[part], locale);
        return typeof value === "string" && value.trim() === "";
      });
      expect(empties, `${name} has empty-string values at: ${empties.join(", ")}`).toEqual([]);
    }
  });
});
