import { useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useI18n } from "../i18n/i18n";
import { useAuth } from "../store/auth";
import { Card } from "../ui/Card";
import { setAuthToken } from "../api/http";

function parseHash(hash: string): Record<string, string> {
  const h = hash.startsWith("#") ? hash.slice(1) : hash;
  const out: Record<string, string> = {};
  for (const [k, v] of new URLSearchParams(h).entries()) out[k] = v;
  return out;
}

export function AuthCallbackPage() {
  const { t } = useI18n();
  const nav = useNavigate();
  const loc = useLocation();
  const { setAuth } = useAuth();

  useEffect(() => {
    const params = parseHash(loc.hash || "");
    const accessToken = params.access_token || null;
    const refreshToken = params.refresh_token || null;
    const role = (params.role ? String(params.role).toLowerCase() : null) as any;
    const next = params.next || "/";

    if (!accessToken || !refreshToken || !role) {
      nav("/login/student", { replace: true });
      return;
    }

    setAuth({
      accessToken,
      refreshToken,
      role,
      username: null
    });

    setAuthToken(accessToken);

    // Route by role by default. Only honor `next` when it matches the user's role.
    const roleLower = String(role).toLowerCase();
    const defaultNext = roleLower === "admin" ? "/admin" : roleLower === "organizer" ? "/organizer" : "/student";
    const safeNext = typeof next === "string" && next.startsWith("/") ? next : defaultNext;
    const roleOk =
      (roleLower === "student" && safeNext.startsWith("/student")) ||
      (roleLower === "organizer" && safeNext.startsWith("/organizer")) ||
      (roleLower === "admin" && safeNext.startsWith("/admin"));

    nav(roleOk ? safeNext : defaultNext, { replace: true });
  }, [loc.hash, nav, setAuth]);

  return (
    <div className="mx-auto max-w-lg">
      <Card className="p-7">
        <h1 className="text-2xl font-bold tracking-tight text-ink dark:text-white">{t("auth_signing_in")}</h1>
        <p className="mt-2 text-sm muted">{t("auth_callback_hint")}</p>
      </Card>
    </div>
  );
}

