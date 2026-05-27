import React, { createContext, useContext, useMemo, useState } from "react";

export type Theme = "light" | "dark";

const THEME_STORAGE_KEY = "usv_events_theme_v1";

function applyTheme(theme: Theme) {
  const root = document.documentElement;
  if (theme === "dark") root.classList.add("dark");
  else root.classList.remove("dark");
}

function loadTheme(): Theme {
  try {
    const raw = localStorage.getItem(THEME_STORAGE_KEY);
    if (raw === "dark") return "dark";
  } catch {
    // ignore
  }
  return "light";
}

type ThemeContextValue = {
  theme: Theme;
  setTheme: (next: Theme) => void;
  toggleTheme: () => void;
};

const ThemeContext = createContext<ThemeContextValue | null>(null);

export function ThemeProvider({ children }: { children: React.ReactNode }) {
  const [theme, setThemeState] = useState<Theme>(() => loadTheme());

  const value = useMemo<ThemeContextValue>(() => {
    return {
      theme,
      setTheme: (next) => {
        setThemeState(next);
        applyTheme(next);
        try {
          localStorage.setItem(THEME_STORAGE_KEY, next);
        } catch {
          // ignore
        }
      },
      toggleTheme: () => {
        const next: Theme = theme === "dark" ? "light" : "dark";
        setThemeState(next);
        applyTheme(next);
        try {
          localStorage.setItem(THEME_STORAGE_KEY, next);
        } catch {
          // ignore
        }
      }
    };
  }, [theme]);

  React.useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) throw new Error("useTheme must be used within ThemeProvider");
  return ctx;
}

