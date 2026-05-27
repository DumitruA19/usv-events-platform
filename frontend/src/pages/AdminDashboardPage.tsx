import { Link } from "react-router-dom";
import { useI18n } from "../i18n/i18n";
import { Badge } from "../ui/Badge";
import { Card } from "../ui/Card";
import { PageHeader } from "../ui/PageHeader";

function DashCard(props: { to: string; kicker: string; title: string; desc: string; tone?: "blue" | "amber" | "neutral" | "green" }) {
  return (
    <Link to={props.to}>
      <Card className="p-6 transition hover:-translate-y-0.5 hover:shadow-lift">
        <div className="flex items-start justify-between gap-4">
          <div>
            <div className="text-xs font-semibold text-black/50 dark:text-white/60">{props.kicker}</div>
            <div className="mt-1 text-lg font-bold text-ink dark:text-white">{props.title}</div>
          </div>
          <Badge tone={(props.tone as any) ?? "neutral"}>{props.tone ?? "go"}</Badge>
        </div>
        <div className="mt-3 text-sm muted">{props.desc}</div>
      </Card>
    </Link>
  );
}

export function AdminDashboardPage() {
  const { t } = useI18n();
  return (
    <div className="space-y-5">
      <PageHeader title={t("dash_admin_title")} subtitle={t("dash_admin_subtitle")} />

      <div className="grid gap-4 md:grid-cols-3">
        <DashCard to="/admin/pending" kicker={t("dash_moderate")} title={t("dash_pending_approvals")} desc={t("dash_pending_approvals_desc")} tone="amber" />
        <DashCard to="/admin/reports" kicker={t("dash_insights")} title={t("nav_reports")} desc={t("dash_reports_desc")} tone="blue" />
        <DashCard to="/admin/scraping" kicker={t("dash_ingest")} title={t("nav_scraping")} desc={t("dash_scraping_desc")} tone="neutral" />
      </div>

      <Card className="p-6">
        <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("quality_bar")}</div>
        <p className="mt-2 text-sm muted">{t("quality_bar_hint")}</p>
      </Card>
    </div>
  );
}
