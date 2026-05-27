import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { http } from "../../api/http";
import { useI18n } from "../../i18n/i18n";
import { Button } from "../../ui/Button";
import { Card } from "../../ui/Card";

export function SubmitForApprovalPage() {
  const { t } = useI18n();
  const { id } = useParams();
  const nav = useNavigate();
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function submit() {
    if (!id) return;
    setLoading(true);
    setMsg(null);
    try {
      const res = await http.post(`/events/${id}/submit-for-approval`);
      setMsg(t("submitted_status", { status: String(res.data?.status ?? "") }));
      setTimeout(() => nav("/organizer/events"), 700);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl">
      <Card className="p-7">
        <h1 className="text-xl font-black tracking-tight text-ink dark:text-white">{t("submit_title")}</h1>
        <p className="mt-2 text-sm muted">{t("submit_hint")}</p>
        {msg ? <div className="mt-4 rounded-xl bg-black/5 p-3 text-sm text-black/70 dark:bg-white/10 dark:text-white/80">{msg}</div> : null}
        <div className="mt-5">
          <Button className="w-full" onClick={submit} disabled={loading}>
            {loading ? t("submitting") : t("submit")}
          </Button>
        </div>
      </Card>
    </div>
  );
}

