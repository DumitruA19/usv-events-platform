import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { http } from "../../api/http";
import { useI18n } from "../../i18n/i18n";
import { Badge } from "../../ui/Badge";
import { Card } from "../../ui/Card";
import { PageHeader } from "../../ui/PageHeader";

type MyRegistration = {
  event_id: number;
  title: string;
  start_dt: string;
  status: string;
  ticket_qr_payload: string | null;
};

export function MyRegistrationsPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<MyRegistration[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    http
      .get("/students/me/registrations")
      .then((res) => setItems(res.data.items ?? []))
      .catch((err) => setError(err?.response?.data?.detail ?? t("regs_failed_default")))
      .finally(() => setLoading(false));
  }, [t]);

  return (
    <div className="space-y-5">
      <PageHeader title={t("regs_title")} subtitle={t("regs_subtitle")} />

      {loading ? (
        <Card className="p-6">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("regs_loading")}</div>
        </Card>
      ) : null}
      {error ? (
        <Card className="p-6 ring-1 ring-red-200">
          <div className="text-sm font-semibold text-red-700">{t("error_title")}</div>
          <div className="mt-2 text-sm text-red-700/80">{error}</div>
        </Card>
      ) : null}

      {!loading && !error && items.length === 0 ? (
        <Card className="p-8">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("regs_empty_title")}</div>
          <div className="mt-2 text-sm muted">
            {t("regs_empty_hint")}{" "}
            <Link to="/events" className="font-semibold text-usv-900 hover:underline dark:text-usv-100">
              {t("nav_events")}
            </Link>
          </div>
        </Card>
      ) : null}

      <div className="grid gap-3">
        {items.map((r) => (
          <Card key={`${r.event_id}:${r.status}`} className="p-6">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0">
                <Link to={`/events/${r.event_id}`} className="truncate text-lg font-bold text-ink hover:text-usv-900 dark:text-white dark:hover:text-white/90">
                  {r.title}
                </Link>
                <div className="mt-2 text-xs muted">{new Date(r.start_dt).toLocaleString()}</div>
              </div>
              <Badge tone="neutral">{r.status}</Badge>
            </div>
            {r.ticket_qr_payload ? (
              <div className="mt-4 rounded-2xl bg-black/5 p-4 text-xs text-black/70 dark:bg-white/10 dark:text-white/80">
                {t("ticket_payload")}: <span className="font-mono">{r.ticket_qr_payload}</span>
              </div>
            ) : null}
          </Card>
        ))}
      </div>
    </div>
  );
}

