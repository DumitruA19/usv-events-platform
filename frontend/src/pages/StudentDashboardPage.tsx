import { Link } from "react-router-dom";
import { useI18n } from "../i18n/i18n";
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { PageHeader } from "../ui/PageHeader";

function DashCard(props: { to?: string; kicker: string; title: string; desc: string; tone?: "blue" | "amber" | "neutral" }) {
  const body = (
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
  );
  return props.to ? <Link to={props.to}>{body}</Link> : body;
}

export function StudentDashboardPage() {
  const { t } = useI18n();
  return (
    <div className="space-y-5">
      <PageHeader title={t("dash_student_title")} subtitle={t("dash_student_subtitle")} />

      <div className="grid gap-4 md:grid-cols-3">
        <DashCard to="/events" kicker={t("dash_browse")} title={t("dash_events_list")} desc={t("dash_events_list_desc")} tone="blue" />
        <DashCard to="/calendar" kicker={t("dash_plan")} title={t("dash_calendar")} desc={t("dash_calendar_desc")} tone="amber" />
        <DashCard to="/student/registrations" kicker={t("dash_track")} title={t("dash_my_registrations")} desc={t("dash_my_registrations_desc")} tone="neutral" />
      </div>
    </div>
  );
}
