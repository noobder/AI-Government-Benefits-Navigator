import { describe, expect, it } from "vitest";
import { render, screen } from "@testing-library/react";
import EligibilityBadge from "./EligibilityBadge";
import type { EligibilityStatus } from "../types/scheme";

const EXPECTED_LABEL: Record<EligibilityStatus, string> = {
  likely_eligible: "Likely Eligible",
  possibly_eligible: "Possibly Eligible",
  missing_information: "More Information Needed",
  not_matching: "Doesn't Currently Match",
  unable_to_determine: "Unable to Determine",
};

describe("EligibilityBadge", () => {
  for (const [status, label] of Object.entries(EXPECTED_LABEL)) {
    it(`renders the correct label for status "${status}"`, () => {
      render(<EligibilityBadge status={status as EligibilityStatus} />);
      expect(screen.getByText(label)).toBeInTheDocument();
    });
  }

  it("falls back to 'Unable to Determine' for an unrecognized status", () => {
    // @ts-expect-error deliberately passing an invalid status to test the fallback
    render(<EligibilityBadge status="something_unexpected" />);
    expect(screen.getByText("Unable to Determine")).toBeInTheDocument();
  });
});
