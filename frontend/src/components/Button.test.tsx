import { describe, expect, it, vi } from "vitest";
import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { Button, IconButton, buttonClasses } from "./Button";

describe("Button", () => {
  it("meets the 44px minimum accessible tap target at every size", () => {
    for (const size of ["md", "lg"] as const) {
      const match = buttonClasses({ size }).match(/min-h-\[(\d+)px\]/);
      expect(match, `size "${size}" should set a min-h-[Npx] class`).not.toBeNull();
      expect(Number(match![1])).toBeGreaterThanOrEqual(44);
    }
  });

  it("fires onClick when clicked and not disabled", async () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click me</Button>);
    await userEvent.click(screen.getByRole("button", { name: "Click me" }));
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it("does not fire onClick when disabled", async () => {
    const onClick = vi.fn();
    render(
      <Button onClick={onClick} disabled>
        Click me
      </Button>
    );
    await userEvent.click(screen.getByRole("button", { name: "Click me" }));
    expect(onClick).not.toHaveBeenCalled();
  });
});

describe("IconButton", () => {
  it("is circular and at least 44px square by default", () => {
    render(<IconButton aria-label="test icon">X</IconButton>);
    const btn = screen.getByRole("button", { name: "test icon" });
    expect(btn.className).toContain("rounded-full");
    expect(btn.className).toContain("h-11");
    expect(btn.className).toContain("w-11");
  });

  it("reflects the active state visually via aria-pressed when set", () => {
    render(
      <IconButton aria-label="toggle" aria-pressed active>
        X
      </IconButton>
    );
    expect(screen.getByRole("button", { name: "toggle" })).toHaveAttribute("aria-pressed", "true");
  });
});
