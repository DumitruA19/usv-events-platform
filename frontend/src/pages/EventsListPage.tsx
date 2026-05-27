import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { http } from "../api/http";
import { useI18n } from "../i18n/i18n";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { Input } from "../ui/Input";
import { PageHeader } from "../ui/PageHeader";

type EventListItem = {
  id: number;
  title: string;
  start_dt: string;
  end_dt: string;
  location_name: string | null;
  category_name: string | null;
  organizer_name: string | null;
  status: string;
  participation_mode: string;
  free_entry: boolean;
  requires_registration: boolean;
  has_qr_code: boolean;
};

function formatRange(startIso: string, endIso: string) {
  const s = new Date(startIso);
  const e = new Date(endIso);
  return `${s.toLocaleString()} -> ${e.toLocaleString()}`;
}

export function EventsListPage() {
  const { t } = useI18n();
  const [items, setItems] = useState<EventListItem[]>([]);
  const [query, setQuery] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    if (!q) return items;
    return items.filter((e) => e.title.toLowerCase().includes(q));
  }, [items, query]);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    http
      .get("/events", { params: { sort_by: "date", sort_dir: "asc" } })
      .then((res) => {
        if (cancelled) return;
        setItems(res.data.items ?? []);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err?.response?.data?.detail ?? t("events_failed_default"));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [t]);

  return (
    <div className="space-y-5">
      <PageHeader
        title={t("page_events_title")}
        subtitle={t("page_events_subtitle")}
        actions={
          <div className="w-full md:w-96">
            <Input
              label={t("events_search_label")}
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={t("events_search_placeholder")}
            />
          </div>
        }
      />

      {loading ? (
        <Card className="p-6">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("events_loading")}</div>
          <div className="mt-2 text-xs text-black/50 dark:text-white/60">{t("events_loading_hint")}</div>
        </Card>
      ) : null}
      {error ? (
        <Card className="p-6 ring-1 ring-red-200">
          <div className="text-sm font-semibold text-red-700">{t("events_failed_title")}</div>
          <div className="mt-2 text-sm text-red-700/80">{error}</div>
        </Card>
      ) : null}

      {!loading && !error && filtered.length === 0 ? (
        <Card className="p-8">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("events_empty_title")}</div>
          <div className="mt-2 text-sm text-black/50 dark:text-white/60">{t("events_empty_hint")}</div>
          <div className="mt-5">
            <Button variant="secondary" onClick={() => setQuery("")}>
              {t("action_clear_search")}
            </Button>
          </div>
        </Card>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        {filtered.map((e) => (
          <Link key={e.id} to={`/events/${e.id}`} className="group">
            <Card className="p-6 transition hover:-translate-y-0.5 hover:shadow-lift">
              <div className="flex items-start justify-between gap-4">
                <div className="min-w-0">
                  <div className="truncate text-lg font-bold text-ink dark:text-white">{e.title}</div>
                  <div className="mt-2 text-xs muted">{formatRange(e.start_dt, e.end_dt)}</div>
                  <div className="mt-2 text-xs muted">
                    {t("label_location")}: {e.location_name ?? t("value_tba")}{" "}
                    <span className="text-black/20 dark:text-white/20">•</span>{" "}
                    {t("label_category")}: {e.category_name ?? t("value_dash")}
                  </div>
                </div>
                <Badge tone="blue">{e.participation_mode}</Badge>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {e.free_entry ? <Badge>{t("badge_free_entry")}</Badge> : null}
                {e.requires_registration ? <Badge tone="amber">{t("badge_registration")}</Badge> : null}
                {e.has_qr_code ? <Badge tone="neutral">QR</Badge> : null}
                <Badge tone="neutral">{e.status}</Badge>
              </div>

              <div className="mt-4 text-xs text-black/45 group-hover:text-black/60 dark:text-white/50 dark:group-hover:text-white/70">
                {t("events_open_details")}
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

