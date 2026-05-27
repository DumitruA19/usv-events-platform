import { Link } from "react-router-dom";
import { useI18n } from "../i18n/i18n";
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { PageHeader } from "../ui/PageHeader";

function DashCard(props: { to: string; kicker: string; title: string; desc: string; tone?: "blue" | "amber" | "neutral" }) {
  return (
    <Link to={props.to}>
      <Card className="p-6 transition hover:-translate-y-0.5 hover:shadow-lift">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs font-semibold text-black/50 dark:text-white/60">{props.kicker}</div>
            <div className="mt-1 text-lg font-bold text-ink dark:text-white">{props.title}</div>
          </div>
          <Badge tone={props.tone ?? "neutral"}>{props.tone ?? "go"}</Badge>
        </div>
        <div className="mt-3 text-sm muted">{props.desc}</div>
      </Card>
    </Link>
  );
}

export function OrganizerDashboardPage() {
  const { t } = useI18n();
  return (
    <div className="space-y-5">
      <PageHeader title={t("dash_organizer_title")} subtitle={t("dash_organizer_subtitle")} />

      <div className="grid gap-4 md:grid-cols-3">
        <DashCard to="/organizer/events" kicker={t("dash_manage")} title={t("nav_my_events")} desc={t("dash_my_events_desc")} tone="blue" />
        <DashCard to="/organizer/create" kicker={t("dash_create")} title={t("dash_new_event")} desc={t("dash_new_event_desc")} tone="amber" />
        <DashCard to="/events" kicker={t("dash_discover")} title={t("dash_public_events")} desc={t("dash_public_events_desc")} tone="neutral" />
      </div>

      <Card className="p-6">
        <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("tip")}</div>
        <p className="mt-2 text-sm muted">{t("tip_organizer_workflow")}</p>
      </Card>
    </div>
  );
}
