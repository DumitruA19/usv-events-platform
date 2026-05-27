import React from "react";
import { cn } from "./cn";

type Variant = "primary" | "secondary" | "ghost" | "danger";
type Size = "sm" | "md";

export function Button(
  props: React.ButtonHTMLAttributes<HTMLButtonElement> & {
    variant?: Variant;
    size?: Size;
    leftIcon?: React.ReactNode;
  }
) {
  const { className, variant = "primary", size = "md", leftIcon, children, ...rest } = props;

  const base =
    "inline-flex items-center justify-center gap-2 rounded-xl font-semibold transition focus:outline-none focus-visible:ring-2 focus-visible:ring-usv-500/60 disabled:opacity-60 disabled:pointer-events-none";
  const sizes: Record<Size, string> = {
    sm: "px-3 py-2 text-sm",
    md: "px-4 py-2.5 text-sm"
  };
  const variants: Record<Variant, string> = {
    primary: "bg-ink text-white hover:bg-black shadow-sm dark:bg-white dark:text-slate-950 dark:hover:bg-white/90",
    secondary: "bg-white text-ink ring-1 ring-black/10 hover:bg-black/5 dark:bg-slate-900 dark:text-white dark:ring-white/10 dark:hover:bg-slate-800",
    ghost: "bg-transparent text-ink hover:bg-black/5 dark:text-white dark:hover:bg-white/10",
    danger: "bg-red-600 text-white hover:bg-red-700 dark:bg-red-500 dark:hover:bg-red-600"
  };

  return (
    <button className={cn(base, sizes[size], variants[variant], className)} {...rest}>
      {leftIcon ? <span className="grid place-items-center">{leftIcon}</span> : null}
      {children}
    </button>
  );
}
