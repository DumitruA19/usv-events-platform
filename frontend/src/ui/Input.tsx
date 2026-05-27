import React from "react";
import { cn } from "./cn";

export function Input(
  props: React.InputHTMLAttributes<HTMLInputElement> & {
    label?: string;
    hint?: string;
    error?: string | null;
  }
) {
  const { className, label, hint, error, id, ...rest } = props;
  const inputId = id || React.useId();

  return (
    <div>
      {label ? (
        <label htmlFor={inputId} className="text-xs font-semibold text-black/60">
          {label}
        </label>
      ) : null}
      <input
        id={inputId}
        className={cn(
          "mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2.5 text-sm outline-none dark:border-white/10 dark:bg-slate-950 dark:text-white",
          "focus:border-usv-400 focus:ring-2 focus:ring-usv-500/25",
          error ? "border-red-300 focus:border-red-400 focus:ring-red-200" : "",
          className
        )}
        {...rest}
      />
      {error ? <div className="mt-2 text-xs font-semibold text-red-700">{error}</div> : null}
      {!error && hint ? <div className="mt-2 text-xs text-black/50">{hint}</div> : null}
    </div>
  );
}
