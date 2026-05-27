import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { http } from "../api/http";
import { setAuthToken } from "../api/http";
import { useI18n } from "../i18n/i18n";
import { useAuth } from "../store/auth";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Input } from "../ui/Input";

export function OrganizerLoginPage() {
  const { t } = useI18n();
  const nav = useNavigate();
  const { setAuth } = useAuth();
  const [email, setEmail] = useState("iroftei290@gmail.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    setError(null);
    setLoading(true);
    try {
      const res = await http.post("/auth/login", { email, password });
      const role = String(res.data.role || "").toLowerCase();
      setAuth({
        accessToken: res.data.access_token,
        refreshToken: res.data.refresh_token,
        role: role as any,
        username: null
      });
      setAuthToken(res.data.access_token);
      nav("/organizer");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? t("login_failed"));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <Card className="p-7">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="amber">{t("role_organizer")}</Badge>
          <Badge tone="neutral">{t("username")} + {t("password")}</Badge>
        </div>
        <h1 className="mt-4 text-2xl font-bold tracking-tight text-ink dark:text-white">{t("login_organizer_title")}</h1>
        <p className="mt-2 text-sm muted">{t("login_organizer_subtitle")}</p>

        <div className="mt-6 grid gap-3">
          <Input label="Email" value={email} onChange={(e) => setEmail(e.target.value)} data-testid="organizer-email" />
          <Input label={t("password")} type="password" value={password} onChange={(e) => setPassword(e.target.value)} data-testid="organizer-password" />
          {error ? <div className="rounded-2xl bg-red-50 p-4 text-sm text-red-700 ring-1 ring-red-100">{error}</div> : null}
          <Button onClick={submit} disabled={loading} data-testid="organizer-login">
            {loading ? t("action_signing_in") : t("action_sign_in")}
          </Button>
        </div>
      </Card>
    </div>
  );
}

