import "@testing-library/jest-dom/vitest";
import { beforeAll } from "vitest";
import i18n from "../i18n";

beforeAll(async () => {
  // Ensure i18next is initialized (and settled on English) before any test
  // that renders a component using useTranslation() runs.
  await i18n.changeLanguage("en");
});
