import { useLocation } from "react-router-dom";
import { useI18n } from "../i18n/i18n";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

export function StudentLoginPage() {
  const { t } = useI18n();
  const loc = useLocation();
  const apiBase = import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";
  const error = new URLSearchParams(loc.search).get("error");

  function signInWithGoogle() {
    window.location.href = `${apiBase}/auth/google/start?next=${encodeURIComponent("/student")}`;
  }

  return (
    <div className="mx-auto max-w-xl space-y-4">
      <Card className="p-7">
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="blue">{t("role_student")}</Badge>
          <Badge tone="neutral">OAuth</Badge>
        </div>
        <h1 className="mt-4 text-2xl font-bold tracking-tight text-ink dark:text-white">{t("login_student_title")}</h1>
        <p className="mt-2 text-sm muted">{t("login_student_help", { domain: "student.usv.ro" })}</p>

        <div className="mt-6 grid gap-3">
          <Button variant="primary" onClick={signInWithGoogle}>
            {t("action_continue_with_google")}
          </Button>
        </div>
        {error ? <p className="mt-4 text-sm text-red-600">OAuth error: {error}</p> : null}
      </Card>

      <Card className="p-6">
        <div className="text-xs font-semibold text-black/50 dark:text-white/60">{t("login_notes")}</div>
        <ul className="mt-3 space-y-2 text-sm muted">
          <li>{t("login_notes_oauth")}</li>
          <li>{t("login_notes_calendar")}</li>
        </ul>
      </Card>
    </div>
  );
}
