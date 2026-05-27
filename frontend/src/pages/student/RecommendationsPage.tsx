import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { http } from "../../api/http";
import { useI18n } from "../../i18n/i18n";
import { Badge } from "../../ui/Badge";
import { Card } from "../../ui/Card";
import { PageHeader } from "../../ui/PageHeader";

type RecItem = { event_id: number; title: string; start_dt: string; reason: string };

export function RecommendationsPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<RecItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    setLoading(true);
    http
      .get("/students/me/recommendations")
      .then((res) => setItems(res.data.items ?? []))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="space-y-5">
      <PageHeader title={t("reco_title")} subtitle={t("reco_subtitle")} />

      <Card className="p-6">
        <div className="text-sm muted">{t("reco_hint")}</div>
      </Card>

      {loading ? (
        <Card className="p-6">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("regs_loading")}</div>
        </Card>
      ) : null}

      {!loading && items.length === 0 ? (
        <Card className="p-8">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("reco_empty_title")}</div>
          <div className="mt-2 text-sm muted">{t("reco_empty_hint")}</div>
        </Card>
      ) : null}

      <div className="grid gap-3">
        {items.map((r) => (
          <Link key={r.event_id} to={`/events/${r.event_id}`}>
            <Card className="p-6 transition hover:-translate-y-0.5 hover:shadow-lift">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="truncate text-lg font-bold text-ink dark:text-white">{r.title}</div>
                  <div className="mt-2 text-sm muted">{r.reason}</div>
                </div>
                <Badge tone="blue">{new Date(r.start_dt).toLocaleDateString()}</Badge>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

