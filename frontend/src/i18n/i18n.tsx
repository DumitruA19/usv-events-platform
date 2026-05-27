import React, { createContext, useContext, useMemo, useState } from "react";

export type Lang = "ro" | "en";

const LANG_STORAGE_KEY = "usv_events_lang_v1";

const dict = {
  ro: {
    app_name: "USV Events",
    app_tagline: "Hub pentru evenimente universitare",

    nav_section: "Navigare",
    nav_home: "Acasă",
    nav_events: "Evenimente",
    nav_calendar: "Calendar",
    nav_my_registrations: "Înscrierile mele",
    nav_recommendations: "Recomandări",
    nav_my_events: "Evenimentele mele",
    nav_create_event: "Creează eveniment",
    nav_approvals: "Aprobări",
    nav_reports: "Rapoarte",
    nav_scraping: "Scraping",
    nav_users_admin: "Utilizatori",
    nav_events_admin: "Evenimente",
    nav_login: "Autentificare",
    nav_login_student: "Autentificare (Student)",
    nav_login_organizer: "Autentificare (Organizator)",
    nav_login_admin: "Autentificare (Admin)",

    role_student: "Student",
    role_organizer: "Organizator",
    role_admin: "Admin",

    action_sign_in: "Autentificare",
    action_sign_out: "Deconectare",
    action_signing_in: "Se autentifică…",
    action_continue_with_google: "Continuă cu Google",
    action_sign_in_mock: "Autentificare (mock)",
    action_browse_events: "Vezi evenimente",
    action_calendar_view: "Vizualizare calendar",
    action_clear_search: "Golește căutarea",
    action_export_ics: "Exportă ICS",
    action_register: "Înscrie-mă",
    action_open_registration_link: "Deschide linkul de înscriere",
    action_back_to_events: "Înapoi la evenimente",

    theme_light: "Luminos",
    theme_dark: "Întunecat",
    lang_ro: "RO",
    lang_en: "EN",

    common_or: "sau",
    yes: "Da",
    no: "Nu",

    home_platform_badge: "Platformă evenimente",
    home_title: "Găsește, participă și gestionează evenimente universitare.",
    home_subtitle:
      "Un flux simplu pentru studenți, organizatori și administratori. Rulează local cu SQLite și suportă Google OAuth + Calendar când este activat.",
    home_demo_accounts: "Conturi demo",
    home_demo_hint: "Folosește-le când rulezi în modul mock.",
    home_enable_oauth_hint: "Activează OAuth real în `.env` (backend)",
    home_student_login_google: "Autentificare cu Google",
    home_student_desc: "Înscriere într-un click. Dacă Calendar este conectat, adăugăm automat.",
    home_organizer_create_submit: "Creează și trimite",
    home_organizer_desc: "Ciornează evenimente, trimite la aprobare, gestionează participanți și materiale.",

    page_events_title: "Evenimente",
    page_events_subtitle: "Răsfoiește evenimente publicate. Deschide un eveniment pentru ICS sau înscriere (studenți).",
    events_loading: "Se încarcă evenimentele…",
    events_loading_hint: "Se preiau din API.",
    events_failed_title: "Nu s-a putut încărca",
    events_failed_default: "Nu s-au putut încărca evenimentele",
    events_empty_title: "Nu s-au găsit evenimente.",
    events_empty_hint: "Încearcă un alt termen de căutare.",
    events_search_label: "Caută",
    events_search_placeholder: "Caută după titlu...",
    events_open_details: "Deschide detalii",

    label_location: "Locație",
    label_category: "Categorie",
    label_when: "Când",
    label_where: "Unde",
    label_organizer: "Organizator",
    value_tba: "de stabilit",
    value_dash: "-",
    badge_free_entry: "Intrare liberă",
    badge_registration: "Înscriere",
    badge_paid: "Plătit",
    badge_no_registration: "Fără înscriere",

    auth_signing_in: "Se finalizează autentificarea…",
    auth_callback_hint: "Se procesează callback-ul OAuth.",

    login_student_title: "Autentificare",
    login_student_help:
      "Recomandat: Google OAuth real. Pentru demo local, poți folosi și autentificarea mock (doar @{domain}).",
    login_mock_email_label: "Email student (mock)",
    login_failed: "Autentificare eșuată",
    login_notes: "Note",
    login_notes_oauth: "OAuth real necesită `.env` în backend cu `INTEGRATIONS_MODE=real` și credențiale Google.",
    login_notes_calendar: "Evenimentele din Calendar se adaugă la înscriere doar dacă ai acordat scopurile Calendar.",
    login_organizer_title: "Autentificare organizator",
    login_organizer_subtitle: "Creează evenimente, încarcă materiale și trimite la aprobare.",
    login_admin_title: "Autentificare admin",
    login_admin_subtitle: "Aprobă evenimente, gestionează organizatori și exportă rapoarte.",
    username: "Utilizator",
    password: "Parolă",

    dash_student_title: "Panou student",
    dash_student_subtitle: "Acțiuni rapide pentru a răsfoi, a te înscrie și a-ți urmări programul.",
    dash_browse: "Răsfoiește",
    dash_plan: "Planifică",
    dash_track: "Urmărește",
    dash_events_list: "Lista de evenimente",
    dash_events_list_desc: "Caută și deschide detalii despre evenimente.",
    dash_calendar: "Calendar",
    dash_calendar_desc: "Vizualizare lunară a evenimentelor viitoare.",
    dash_my_registrations: "Înscrierile mele",
    dash_my_registrations_desc: "Vezi unde te-ai înscris și biletele.",

    dash_organizer_title: "Panou organizator",
    dash_organizer_subtitle: "Creează evenimente, gestionează conținut și urmărește participarea.",
    dash_manage: "Gestionează",
    dash_create: "Creează",
    dash_discover: "Descoperă",
    dash_public_events: "Evenimente publice",
    dash_public_events_desc: "Vezi cum apare conținutul tău public.",
    dash_new_event: "Eveniment nou",
    dash_new_event_desc: "Pornește o ciornă nouă și trimite la aprobare.",
    dash_my_events_desc: "Ciorne, trimiteri și evenimente publicate.",
    tip: "Sfat",
    tip_organizer_workflow:
      "Flux complet: creează un eveniment, trimite la aprobare, apoi autentifică-te ca admin pentru aprobare.",

    dash_admin_title: "Panou admin",
    dash_admin_subtitle: "Aprobă conținut, exportă rapoarte și gestionează organizatori.",
    dash_moderate: "Moderează",
    dash_insights: "Analize",
    dash_ingest: "Import",
    dash_pending_approvals: "Aprobări în așteptare",
    dash_pending_approvals_desc: "Revizuiește și publică evenimente.",
    dash_reports_desc: "Exportă CSV/PDF și revizuiește activitatea.",
    dash_scraping_desc: "Revizuiește ciornele și transformă-le în evenimente.",
    quality_bar: "Standard de calitate",
    quality_bar_hint:
      "Păstrează titlurile clare, setează orele corect și verifică locațiile. Studenții se bazează pe acestea pentru sincronizare.",

    event_loading: "Se încarcă evenimentul…",
    event_failed_default: "Nu s-a putut încărca evenimentul",
    event_about: "Despre",
    event_no_description: "Nu există descriere.",
    event_materials: "Materiale",
    event_materials_hint: "Fișiere atașate acestui eveniment.",
    event_no_materials: "Nu există materiale încărcate.",
    event_sponsors: "Sponsori",
    event_no_sponsors: "Fără sponsori.",
    event_actions: "Acțiuni",
    event_capacity: "Capacitate",
    event_requires_ticket: "Necesită bilet",
    event_qr: "QR eveniment",
    event_qr_hint: "QR local (demo). QR-ul biletului se generează la înscriere.",
    event_registered: "Înscris",
    event_registration_failed: "Înscriere eșuată",

    calendar_title: "Calendar",
    calendar_subtitle: "Vizualizare lunară a evenimentelor viitoare.",
    calendar_prev: "Înapoi",
    calendar_next: "Înainte",
    dow_mon: "Lun",
    dow_tue: "Mar",
    dow_wed: "Mie",
    dow_thu: "Joi",
    dow_fri: "Vin",
    dow_sat: "Sâm",
    dow_sun: "Dum",
    calendar_more: "+{n} mai multe",

    regs_title: "Înscrierile mele",
    regs_subtitle: "Înscrierile curente și biletele (dacă sunt activate).",
    regs_loading: "Se încarcă…",
    regs_failed_default: "Nu s-au putut încărca înscrierile",
    error_title: "Eroare",
    regs_empty_title: "Nu ai încă înscrieri.",
    regs_empty_hint: "Răsfoiește evenimente și înscrie-te din pagina de detalii:",
    ticket_payload: "Payload bilet",
    loading_generic: "Se încarcă…",

    organizer_my_events_title: "Evenimentele mele",
    participants: "Participanți",
    materials: "Materiale",
    edit: "Editează",
    submit: "Trimite",
    submit_title: "Trimite evenimentul la aprobare",
    submit_hint: "Adminii trebuie să aprobe evenimentele înainte de publicare.",
    submitting: "Se trimite…",
    submitted_status: "Trimis. Status: {status}",

    reco_title: "Recomandări",
    reco_subtitle: "Recomandări locale bazate pe activitatea ta.",
    reco_hint: "Acestea sunt euristici de bază pentru build-ul demo. Le poți înlocui ulterior cu un sistem real.",
    reco_empty_title: "Nu există recomandări încă.",
    reco_empty_hint: "Înscrie-te sau marchează evenimente ca favorite mai întâi.",

    footer_left: "USV University Events Management Platform",
    footer_right: "Build demo local (mocks implicit)"
  },
  en: {
    app_name: "USV Events",
    app_tagline: "University events hub",

    nav_section: "Navigation",
    nav_home: "Home",
    nav_events: "Events",
    nav_calendar: "Calendar",
    nav_my_registrations: "My registrations",
    nav_recommendations: "Recommendations",
    nav_my_events: "My events",
    nav_create_event: "Create event",
    nav_approvals: "Approvals",
    nav_reports: "Reports",
    nav_scraping: "Scraping",
    nav_users_admin: "Users",
    nav_events_admin: "Events",
    nav_login: "Sign in",
    nav_login_student: "Login (Student)",
    nav_login_organizer: "Login (Organizer)",
    nav_login_admin: "Login (Admin)",

    role_student: "Student",
    role_organizer: "Organizer",
    role_admin: "Admin",

    action_sign_in: "Sign in",
    action_sign_out: "Logout",
    action_signing_in: "Signing in…",
    action_continue_with_google: "Continue with Google",
    action_sign_in_mock: "Sign in (mock)",
    action_browse_events: "Browse events",
    action_calendar_view: "Calendar view",
    action_clear_search: "Clear search",
    action_export_ics: "Export ICS",
    action_register: "Register",
    action_open_registration_link: "Open registration link",
    action_back_to_events: "Back to events",

    theme_light: "Light",
    theme_dark: "Dark",
    lang_ro: "RO",
    lang_en: "EN",

    common_or: "or",
    yes: "Yes",
    no: "No",

    home_platform_badge: "Events platform",
    home_title: "Find, join, and manage university events.",
    home_subtitle:
      "A clean workflow for students, organizers, and admins. Runs locally with SQLite and supports Google OAuth + Calendar when enabled.",
    home_demo_accounts: "Demo accounts",
    home_demo_hint: "Use these when running in mock mode.",
    home_enable_oauth_hint: "Enable real OAuth in backend `.env`",
    home_student_login_google: "Login with Google",
    home_student_desc: "Register in one click. If Calendar is connected, we add it automatically.",
    home_organizer_create_submit: "Create and submit",
    home_organizer_desc: "Draft events, submit for approval, manage participants and materials.",

    page_events_title: "Events",
    page_events_subtitle: "Browse published events. Open an event to export an ICS or register (students).",
    events_loading: "Loading events…",
    events_loading_hint: "Fetching from API.",
    events_failed_title: "Failed to load",
    events_failed_default: "Failed to load events",
    events_empty_title: "No events found.",
    events_empty_hint: "Try a different search term.",
    events_search_label: "Search",
    events_search_placeholder: "Search by title...",
    events_open_details: "Open details",

    label_location: "Location",
    label_category: "Category",
    label_when: "When",
    label_where: "Where",
    label_organizer: "Organizer",
    value_tba: "TBA",
    value_dash: "-",
    badge_free_entry: "Free entry",
    badge_registration: "Registration",
    badge_paid: "Paid",
    badge_no_registration: "No registration",

    auth_signing_in: "Signing you in…",
    auth_callback_hint: "Completing OAuth callback.",

    login_student_title: "Sign in",
    login_student_help:
      "Recommended: real Google OAuth. For local demo, you can also use the mock login (restricted to @{domain}).",
    login_mock_email_label: "Mock student email",
    login_failed: "Login failed",
    login_notes: "Notes",
    login_notes_oauth: "Real OAuth requires backend `.env` with `INTEGRATIONS_MODE=real` and Google credentials.",
    login_notes_calendar: "Calendar events are added on registration only if your Google account granted Calendar scope.",
    login_organizer_title: "Organizer login",
    login_organizer_subtitle: "Create events, upload materials, and submit for approval.",
    login_admin_title: "Admin login",
    login_admin_subtitle: "Approve events, manage organizers, and export reports.",
    username: "Username",
    password: "Password",

    dash_student_title: "Student dashboard",
    dash_student_subtitle: "Quick actions for browsing, registering, and keeping track of your schedule.",
    dash_browse: "Browse",
    dash_plan: "Plan",
    dash_track: "Track",
    dash_events_list: "Events list",
    dash_events_list_desc: "Search and open event details.",
    dash_calendar: "Calendar",
    dash_calendar_desc: "Month view of upcoming events.",
    dash_my_registrations: "My registrations",
    dash_my_registrations_desc: "See what you joined and your tickets.",

    dash_organizer_title: "Organizer dashboard",
    dash_organizer_subtitle: "Create events, manage content, and track attendance.",
    dash_manage: "Manage",
    dash_create: "Create",
    dash_discover: "Discover",
    dash_public_events: "Public events",
    dash_public_events_desc: "See how your content appears publicly.",
    dash_new_event: "New event",
    dash_new_event_desc: "Start a new draft and submit it for approval.",
    dash_my_events_desc: "Drafts, submissions, and published events.",
    tip: "Tip",
    tip_organizer_workflow: "Complete workflow: create an event, submit for approval, then log in as admin to approve it.",

    dash_admin_title: "Admin dashboard",
    dash_admin_subtitle: "Approve content, export reports, and manage organizers.",
    dash_moderate: "Moderate",
    dash_insights: "Insights",
    dash_ingest: "Ingest",
    dash_pending_approvals: "Pending approvals",
    dash_pending_approvals_desc: "Review and publish events.",
    dash_reports_desc: "Export CSV/PDF and review system activity.",
    dash_scraping_desc: "Review scraped drafts and turn them into events.",
    quality_bar: "Quality bar",
    quality_bar_hint: "Keep titles clear, set correct times, and verify locations. Students rely on these for calendar sync.",

    event_loading: "Loading event…",
    event_failed_default: "Failed to load event",
    event_about: "About",
    event_no_description: "No description provided.",
    event_materials: "Materials",
    event_materials_hint: "Files attached to this event.",
    event_no_materials: "No materials uploaded.",
    event_sponsors: "Sponsors",
    event_no_sponsors: "No sponsors.",
    event_actions: "Actions",
    event_capacity: "Capacity",
    event_requires_ticket: "Requires ticket",
    event_qr: "Event QR",
    event_qr_hint: "Local QR (demo). Ticket QR is generated per registration.",
    event_registered: "Registered",
    event_registration_failed: "Registration failed",

    calendar_title: "Calendar",
    calendar_subtitle: "A month view of upcoming events.",
    calendar_prev: "Prev",
    calendar_next: "Next",
    dow_mon: "Mon",
    dow_tue: "Tue",
    dow_wed: "Wed",
    dow_thu: "Thu",
    dow_fri: "Fri",
    dow_sat: "Sat",
    dow_sun: "Sun",
    calendar_more: "+{n} more",

    regs_title: "My registrations",
    regs_subtitle: "Your current registrations and ticket payloads (if enabled).",
    regs_loading: "Loading…",
    regs_failed_default: "Failed to load registrations",
    error_title: "Error",
    regs_empty_title: "No registrations yet.",
    regs_empty_hint: "Browse events and register from the event details page:",
    ticket_payload: "Ticket payload",
    loading_generic: "Loading…",

    organizer_my_events_title: "My events",
    participants: "Participants",
    materials: "Materials",
    edit: "Edit",
    submit: "Submit",
    submit_title: "Submit event for approval",
    submit_hint: "Admins must approve events before publication.",
    submitting: "Submitting…",
    submitted_status: "Submitted. Status: {status}",

    reco_title: "Recommendations",
    reco_subtitle: "Local-only recommendations based on your activity.",
    reco_hint: "These are basic heuristics intended for the demo build. You can replace this later with a real recommender.",
    reco_empty_title: "No recommendations yet.",
    reco_empty_hint: "Register or favorite some events first.",

    footer_left: "USV University Events Management Platform",
    footer_right: "Local demo build (mocks by default)"
  }
} as const;

type Dict = typeof dict.ro;
export type I18nKey = keyof Dict;

function loadLang(): Lang {
  try {
    const raw = localStorage.getItem(LANG_STORAGE_KEY);
    if (raw === "en") return "en";
  } catch {
    // ignore
  }
  return "ro";
}

type I18nContextValue = {
  lang: Lang;
  setLang: (next: Lang) => void;
  t: (key: I18nKey, vars?: Record<string, string>) => string;
};

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: React.ReactNode }) {
  const [lang, setLangState] = useState<Lang>(() => loadLang());

  const value = useMemo<I18nContextValue>(() => {
    const t = (key: I18nKey, vars?: Record<string, string>) => {
      const template = (dict as any)[lang][key] ?? (dict as any).ro[key] ?? String(key);
      if (!vars) return String(template);
      return String(template).replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? `{${name}}`);
    };
    return {
      lang,
      setLang: (next) => {
        setLangState(next);
        try {
          localStorage.setItem(LANG_STORAGE_KEY, next);
        } catch {
          // ignore
        }
      },
      t
    };
  }, [lang]);

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const ctx = useContext(I18nContext);
  if (!ctx) throw new Error("useI18n must be used within I18nProvider");
  return ctx;
}
