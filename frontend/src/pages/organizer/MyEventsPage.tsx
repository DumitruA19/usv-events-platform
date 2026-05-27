import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { http } from "../../api/http";
import { useI18n } from "../../i18n/i18n";
import { useMe } from "../../hooks/useMe";
import { Badge } from "../../ui/Badge";
import { ButtonLink } from "../../ui/ButtonLink";
import { Card } from "../../ui/Card";
import { PageHeader } from "../../ui/PageHeader";

type EventListItem = {
  id: number;
  title: string;
  start_dt: string;
  end_dt: string;
  status: string;
};

export function MyEventsPage() {
  const { t } = useI18n();
  const { me } = useMe();
  const [items, setItems] = useState<EventListItem[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!me) return;
    setLoading(true);
    http
      .get("/events", { params: { organizer_id: me.id, sort_by: "date", sort_dir: "asc" } })
      .then((res) => setItems(res.data.items ?? []))
      .finally(() => setLoading(false));
  }, [me]);

  return (
    <div className="space-y-5">
      <PageHeader
        title={t("organizer_my_events_title")}
        actions={
          <ButtonLink to="/organizer/create" variant="primary">
            {t("nav_create_event")}
          </ButtonLink>
        }
      />

      {loading ? (
        <Card className="p-6">
          <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("loading_generic")}</div>
        </Card>
      ) : null}

      <div className="grid gap-3">
        {items.map((e) => (
          <Card key={e.id} className="p-6">
            <div className="flex items-start justify-between gap-4">
              <Link to={`/events/${e.id}`} className="text-lg font-bold text-ink hover:text-usv-800 dark:text-white dark:hover:text-white/90">
                {e.title}
              </Link>
              <Badge tone="neutral">{e.status}</Badge>
            </div>
            <div className="mt-2 text-xs muted">{new Date(e.start_dt).toLocaleString()}</div>
            <div className="mt-4 flex flex-wrap gap-2 text-xs">
              <ButtonLink variant="secondary" size="sm" to={`/organizer/events/${e.id}/participants`}>
                {t("participants")}
              </ButtonLink>
              <ButtonLink variant="secondary" size="sm" to={`/organizer/events/${e.id}/materials`}>
                {t("materials")}
              </ButtonLink>
              <ButtonLink variant="secondary" size="sm" to={`/organizer/events/${e.id}/edit`}>
                {t("edit")}
              </ButtonLink>
              <ButtonLink variant="primary" size="sm" to={`/organizer/events/${e.id}/submit`}>
                {t("submit")}
              </ButtonLink>
            </div>
          </Card>
        ))}
      </div>
    </div>
  );
}

