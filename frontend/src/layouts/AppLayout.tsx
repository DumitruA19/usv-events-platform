import { Outlet, Link, NavLink } from "react-router-dom";
import { useAuth } from "../store/auth";
import { useI18n } from "../i18n/i18n";
import { useTheme } from "../theme/theme";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { ButtonLink } from "../ui/ButtonLink";
import { ChatbotWidget } from "../components/ChatbotWidget";

type NavItem = { to: string; label: string; roles?: Array<"STUDENT" | "ORGANIZER" | "ADMIN"> };

export function AppLayout() {
  const { auth, logout } = useAuth();
  const { t, lang, setLang } = useI18n();
  const { theme, toggleTheme } = useTheme();
  const role = auth.role;
  const NAV: NavItem[] = [
    { to: "/events", label: t("nav_events") },
    { to: "/calendar", label: t("nav_calendar") },
    { to: "/student/registrations", label: t("nav_my_registrations"), roles: ["STUDENT"] },
    { to: "/student/recommendations", label: t("nav_recommendations"), roles: ["STUDENT"] },
    { to: "/organizer/events", label: t("nav_my_events"), roles: ["ORGANIZER"] },
    { to: "/organizer/create", label: t("nav_create_event"), roles: ["ORGANIZER"] },
    { to: "/admin/organizers", label: t("nav_users_admin"), roles: ["ADMIN"] },
    { to: "/admin/events", label: t("nav_events_admin"), roles: ["ADMIN"] },
    { to: "/admin/pending", label: t("nav_approvals"), roles: ["ADMIN"] },
    { to: "/admin/reports", label: t("nav_reports"), roles: ["ADMIN"] },
    { to: "/admin/scraping", label: t("nav_scraping"), roles: ["ADMIN"] }
  ];
  const navItems = NAV.filter((i) => !i.roles || (role ? i.roles.includes(role) : false));
  const navTestId = (to: string) => `nav-${to.replace(/^\//, "").replace(/\//g, "-") || "home"}`;

  const mobilePrimary: NavItem[] = [
    { to: "/", label: t("nav_home") },
    { to: "/events", label: t("nav_events") },
    { to: "/calendar", label: t("nav_calendar") },
    role === "STUDENT" ? { to: "/student", label: t("role_student") } : null,
    role === "ORGANIZER" ? { to: "/organizer", label: t("role_organizer") } : null,
    role === "ADMIN" ? { to: "/admin", label: t("role_admin") } : null,
    !role ? { to: "/login/student", label: t("nav_login") } : null,
  ].filter(Boolean) as NavItem[];

  return (
    <div className="min-h-screen">
      <header className="sticky top-0 z-30 border-b border-black/5 bg-white/70 backdrop-blur dark:border-white/10 dark:bg-slate-950/70">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-4">
          <div className="flex items-center gap-4">
            <Link to="/" className="group inline-flex items-center gap-3">
              <span className="grid h-9 w-9 place-items-center rounded-2xl bg-usv-700 text-sm font-black text-white shadow-sm ring-1 ring-black/5">
                U
              </span>
              <div className="leading-tight">
                <div className="font-display text-sm font-bold tracking-tight text-ink group-hover:text-usv-900 dark:text-white dark:group-hover:text-white/90">{t("app_name")}</div>
                <div className="text-[11px] text-black/50 dark:text-white/60">{t("app_tagline")}</div>
              </div>
            </Link>
          </div>

          <div className="flex items-center gap-2">
            {role ? <Badge tone="blue">{role}</Badge> : null}
            <Button size="sm" variant="ghost" onClick={() => setLang(lang === "ro" ? "en" : "ro")} data-testid="lang-toggle">
              {lang === "ro" ? t("lang_ro") : t("lang_en")}
            </Button>
            <Button size="sm" variant="ghost" onClick={toggleTheme} data-testid="theme-toggle">
              {theme === "dark" ? t("theme_dark") : t("theme_light")}
            </Button>
            {auth.accessToken ? (
              <Button size="sm" variant="secondary" onClick={logout}>
                {t("action_sign_out")}
              </Button>
            ) : (
              <div className="flex items-center gap-2">
                <div className="md:hidden">
                  <ButtonLink to="/login/student" size="sm" variant="primary">
                    {t("action_sign_in")}
                  </ButtonLink>
                </div>
                <div className="hidden items-center gap-2 md:flex">
                  <ButtonLink to="/login/student" size="sm" variant="secondary">
                    {t("role_student")}
                  </ButtonLink>
                  <ButtonLink to="/login/organizer" size="sm" variant="secondary">
                    {t("role_organizer")}
                  </ButtonLink>
                  <ButtonLink to="/login/admin" size="sm" variant="primary">
                    {t("role_admin")}
                  </ButtonLink>
              </div>
              </div>
            )}
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-6xl gap-6 px-4 py-8 md:grid-cols-[240px_1fr]">
        <aside className="hidden md:block">
          <div className="surface p-3">
            <div className="px-3 py-2 text-xs font-semibold text-black/50 dark:text-white/60">{t("nav_section")}</div>
            <nav className="mt-1 space-y-1">
              {navItems.map((i) => (
                <NavLink
                  key={i.to}
                  to={i.to}
                  data-testid={navTestId(i.to)}
                  className={({ isActive }) =>
                    [
                      "block rounded-xl px-3 py-2 text-sm font-semibold",
                      isActive
                        ? "bg-usv-700/10 text-usv-900 dark:bg-white/10 dark:text-white"
                        : "text-black/70 hover:bg-black/5 hover:text-ink dark:text-white/80 dark:hover:bg-white/10 dark:hover:text-white"
                    ].join(" ")
                  }
                >
                  {i.label}
                </NavLink>
              ))}
              {!role ? (
                <>
                  <NavLink
                    to="/login/student"
                    className={({ isActive }) =>
                      [
                        "block rounded-xl px-3 py-2 text-sm font-semibold",
                        isActive
                          ? "bg-usv-700/10 text-usv-900 dark:bg-white/10 dark:text-white"
                          : "text-black/70 hover:bg-black/5 hover:text-ink dark:text-white/80 dark:hover:bg-white/10 dark:hover:text-white"
                      ].join(" ")
                    }
                  >
                    {t("nav_login_student")}
                  </NavLink>
                  <NavLink
                    to="/login/organizer"
                    className={({ isActive }) =>
                      [
                        "block rounded-xl px-3 py-2 text-sm font-semibold",
                        isActive
                          ? "bg-usv-700/10 text-usv-900 dark:bg-white/10 dark:text-white"
                          : "text-black/70 hover:bg-black/5 hover:text-ink dark:text-white/80 dark:hover:bg-white/10 dark:hover:text-white"
                      ].join(" ")
                    }
                  >
                    {t("nav_login_organizer")}
                  </NavLink>
                  <NavLink
                    to="/login/admin"
                    className={({ isActive }) =>
                      [
                        "block rounded-xl px-3 py-2 text-sm font-semibold",
                        isActive
                          ? "bg-usv-700/10 text-usv-900 dark:bg-white/10 dark:text-white"
                          : "text-black/70 hover:bg-black/5 hover:text-ink dark:text-white/80 dark:hover:bg-white/10 dark:hover:text-white"
                      ].join(" ")
                    }
                  >
                    {t("nav_login_admin")}
                  </NavLink>
                </>
              ) : null}
            </nav>
          </div>

          <div className="mt-4 rounded-3xl bg-gradient-to-br from-usv-900 to-usv-700 p-5 text-white shadow-lift ring-1 ring-black/5">
            <div className="text-sm font-bold">Tip</div>
            <p className="mt-2 text-sm text-white/85">Use the Events page to browse, then open an event to export an ICS or register.</p>
            <div className="mt-4 text-[11px] text-white/70">Use role-based areas after sign-in to manage registrations, events, approvals, and reports.</div>
          </div>
        </aside>

        <main>
          <Outlet />
        </main>
      </div>

      <div className="md:hidden">
        <nav className="fixed bottom-3 left-1/2 z-40 w-[min(560px,calc(100%-24px))] -translate-x-1/2 rounded-3xl bg-white/80 p-2 shadow-lift ring-1 ring-black/5 backdrop-blur">
          <div className="grid grid-cols-4 gap-1">
            {mobilePrimary.slice(0, 4).map((i) => (
              <NavLink
                key={i.to}
                to={i.to}
                className={({ isActive }) =>
                  [
                    "rounded-2xl px-3 py-2 text-center text-xs font-semibold",
                    isActive ? "bg-usv-700/10 text-usv-900" : "text-black/70 hover:bg-black/5"
                  ].join(" ")
                }
              >
                {i.label}
              </NavLink>
            ))}
          </div>
        </nav>
        <div className="h-20" />
      </div>

      <footer className="border-t border-black/5 bg-white/60 backdrop-blur dark:border-white/10 dark:bg-slate-950/60">
        <div className="mx-auto flex max-w-6xl flex-col gap-2 px-4 py-6 text-xs text-black/60 dark:text-white/70 md:flex-row md:items-center md:justify-between">
          <span>{t("footer_left")}</span>
          <span>{t("footer_right")}</span>
        </div>
      </footer>

      {auth.accessToken ? <ChatbotWidget /> : null}
    </div>
  );
}
