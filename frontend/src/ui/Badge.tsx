import React from "react";
import { cn } from "./cn";

export function Badge(
  props: React.HTMLAttributes<HTMLSpanElement> & { tone?: "blue" | "neutral" | "green" | "amber" }
) {
  const { className, tone = "neutral", ...rest } = props;
  const tones: Record<string, string> = {
    blue: "bg-usv-700/10 text-usv-900 ring-usv-700/15 dark:bg-usv-400/15 dark:text-usv-100 dark:ring-usv-300/20",
    neutral: "bg-black/5 text-black/70 ring-black/10 dark:bg-white/10 dark:text-white/80 dark:ring-white/15",
    green: "bg-emerald-600/10 text-emerald-900 ring-emerald-600/15 dark:bg-emerald-400/15 dark:text-emerald-50 dark:ring-emerald-300/20",
    amber: "bg-amber-500/15 text-amber-900 ring-amber-500/20 dark:bg-amber-300/15 dark:text-amber-50 dark:ring-amber-200/20"
  };
  return (
    <span className={cn("inline-flex items-center rounded-full px-3 py-1 text-[11px] font-semibold ring-1", tones[tone], className)} {...rest} />
  );
}
