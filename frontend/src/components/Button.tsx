import { forwardRef } from "react";
import type { ButtonHTMLAttributes, AnchorHTMLAttributes, ReactNode } from "react";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "md" | "lg";

const VARIANT_CLASSES: Record<Variant, string> = {
  primary: "bg-brand-700 text-white hover:bg-brand-800 border border-transparent",
  secondary: "bg-[var(--surface)] text-[var(--ink)] border border-[var(--line-strong)] hover:bg-[var(--surface-2)]",
  ghost: "bg-transparent text-[var(--ink)] border border-transparent hover:bg-[var(--surface-2)]",
  danger: "bg-[var(--danger)] text-white border border-transparent hover:brightness-95",
};

// Every size meets the 44px minimum accessible tap target (WCAG 2.5.5).
const SIZE_CLASSES: Record<Size, string> = {
  md: "min-h-[44px] px-4 py-2.5 text-sm gap-2 rounded-xl",
  lg: "min-h-[56px] px-6 py-3.5 text-base gap-2.5 rounded-xl",
};

const BASE =
  "inline-flex items-center justify-center font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed select-none";

interface CommonProps {
  variant?: Variant;
  size?: Size;
  icon?: ReactNode;
  fullWidth?: boolean;
  children?: ReactNode;
}

export function buttonClasses({
  variant = "primary",
  size = "md",
  fullWidth = false,
}: { variant?: Variant; size?: Size; fullWidth?: boolean } = {}) {
  return `${BASE} ${VARIANT_CLASSES[variant]} ${SIZE_CLASSES[size]} ${fullWidth ? "w-full" : ""}`;
}

type ButtonProps = CommonProps & ButtonHTMLAttributes<HTMLButtonElement>;

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = "primary", size = "md", icon, fullWidth, className = "", children, ...rest },
  ref
) {
  return (
    <button ref={ref} className={`${buttonClasses({ variant, size, fullWidth })} ${className}`} {...rest}>
      {icon}
      {children}
    </button>
  );
});

// For places that need button styling on an <a>/<Link> (react-router Link
// forwards extra props to an <a>, so this covers both).
type LinkButtonProps = CommonProps & AnchorHTMLAttributes<HTMLAnchorElement>;

export const LinkButton = forwardRef<HTMLAnchorElement, LinkButtonProps>(function LinkButton(
  { variant = "primary", size = "md", icon, fullWidth, className = "", children, ...rest },
  ref
) {
  return (
    <a ref={ref} className={`${buttonClasses({ variant, size, fullWidth })} ${className}`} {...rest}>
      {icon}
      {children}
    </a>
  );
});

// Square icon-only button (toggles, mic, etc.) — same 44/56px minimums, circular.
const ICON_SIZE_CLASSES: Record<Size, string> = {
  md: "h-11 w-11 rounded-full text-lg",
  lg: "h-14 w-14 rounded-full text-2xl",
};

interface IconButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
  active?: boolean;
}

export const IconButton = forwardRef<HTMLButtonElement, IconButtonProps>(function IconButton(
  { variant = "secondary", size = "md", active = false, className = "", children, ...rest },
  ref
) {
  return (
    <button
      ref={ref}
      className={`${BASE} ${ICON_SIZE_CLASSES[size]} ${
        active ? "border-2 border-[var(--brand)] bg-[var(--brand-weak)] text-[var(--brand)]" : VARIANT_CLASSES[variant]
      } ${className}`}
      {...rest}
    >
      {children}
    </button>
  );
});
