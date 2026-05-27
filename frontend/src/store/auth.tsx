import React, { createContext, useContext, useMemo, useState } from "react";

export type Role = "STUDENT" | "ORGANIZER" | "ADMIN";

export type AuthState = {
  accessToken: string | null;
  refreshToken: string | null;
  role: Role | null;
  username: string | null;
};

type AuthContextValue = {
  auth: AuthState;
  setAuth: (next: AuthState) => void;
  logout: () => void;
};

const AUTH_STORAGE_KEY = "usv_events_auth_v1";

function loadAuth(): AuthState {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY);
    if (!raw) return { accessToken: null, refreshToken: null, role: null, username: null };
    const parsed = JSON.parse(raw) as AuthState;
    return {
      accessToken: parsed.accessToken ?? null,
      refreshToken: parsed.refreshToken ?? null,
      role: parsed.role ?? null,
      username: parsed.username ?? null
    };
  } catch {
    return { accessToken: null, refreshToken: null, role: null, username: null };
  }
}

function persistAuth(auth: AuthState) {
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(auth));
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [auth, setAuthState] = useState<AuthState>(() => loadAuth());

  const value = useMemo<AuthContextValue>(() => {
    return {
      auth,
      setAuth: (next) => {
        setAuthState(next);
        persistAuth(next);
      },
      logout: () => {
        const empty: AuthState = { accessToken: null, refreshToken: null, role: null, username: null };
        setAuthState(empty);
        persistAuth(empty);
      }
    };
  }, [auth]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}

