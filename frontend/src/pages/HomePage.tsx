import { Badge } from "../ui/Badge";
import { ButtonLink } from "../ui/ButtonLink";
import { Card, CardBody, CardHeader } from "../ui/Card";
import { useI18n } from "../i18n/i18n";

export function HomePage() {
  const { t } = useI18n();
  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card className="overflow-hidden">
        <CardHeader>
          <div className="flex flex-wrap items-center gap-2">
            <Badge tone="blue">USV</Badge>
            <Badge tone="neutral">{t("home_platform_badge")}</Badge>
          </div>
          <h1 className="mt-4 text-4xl font-bold tracking-tight text-ink dark:text-white">{t("home_title")}</h1>
          <p className="mt-3 text-sm muted">{t("home_subtitle")}</p>
        </CardHeader>
        <CardBody>
          <div className="flex flex-wrap gap-3">
            <ButtonLink to="/events" variant="primary">
              {t("action_browse_events")}
            </ButtonLink>
            <ButtonLink to="/calendar" variant="secondary">
              {t("action_calendar_view")}
            </ButtonLink>
          </div>

          <div className="mt-6 grid gap-3 sm:grid-cols-2">
            <div className="rounded-2xl bg-haze p-4 ring-1 ring-black/5 dark:bg-white/5 dark:ring-white/10">
              <div className="text-xs font-semibold text-black/60 dark:text-white/70">{t("role_student")}</div>
              <div className="mt-1 text-sm font-bold">{t("home_student_login_google")}</div>
              <div className="mt-2 text-xs muted">{t("home_student_desc")}</div>
            </div>
            <div className="rounded-2xl bg-haze p-4 ring-1 ring-black/5 dark:bg-white/5 dark:ring-white/10">
              <div className="text-xs font-semibold text-black/60 dark:text-white/70">{t("role_organizer")}</div>
              <div className="mt-1 text-sm font-bold">{t("home_organizer_create_submit")}</div>
              <div className="mt-2 text-xs muted">{t("home_organizer_desc")}</div>
            </div>
          </div>
        </CardBody>
      </Card>
      <div className="rounded-3xl bg-gradient-to-br from-usv-900 via-usv-800 to-usv-700 p-8 text-white shadow-lift ring-1 ring-black/5">
        <div className="flex items-start justify-between gap-4">
          <div>
            <h2 className="text-xl font-bold">{t("app_name")}</h2>
            <p className="mt-2 text-sm text-white/80">{t("home_subtitle")}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
