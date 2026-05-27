import { useEffect, useMemo, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { QRCodeCanvas } from "qrcode.react";
import { http } from "../api/http";
import { useI18n } from "../i18n/i18n";
import { useAuth } from "../store/auth";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";

type EventDetails = {
  id: number;
  title: string;
  description: string;
  start_dt: string;
  end_dt: string;
  location_name: string | null;
  category_name: string | null;
  organizer_name: string | null;
  status: string;
  participation_mode: string;
  registration_link: string | null;
  free_entry: boolean;
  requires_registration: boolean;
  requires_ticket: boolean;
  capacity: number | null;
  has_qr_code: boolean;
  sponsors: { name: string; logo_path: string | null }[];
  materials: { id: number; filename: string; size_bytes: number }[];
};

function formatRange(startIso: string, endIso: string) {
  const s = new Date(startIso);
  const e = new Date(endIso);
  return `${s.toLocaleString()} -> ${e.toLocaleString()}`;
}

export function EventDetailsPage() {
  const { t } = useI18n();
  const { id } = useParams();
  const { auth } = useAuth();
  const [item, setItem] = useState<EventDetails | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [actionMsg, setActionMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    let cancelled = false;
    setLoading(true);
    setError(null);
    http
      .get(`/events/${id}`)
      .then((res) => {
        if (cancelled) return;
        setItem(res.data);
      })
      .catch((err) => {
        if (cancelled) return;
        setError(err?.response?.data?.detail ?? t("event_failed_default"));
      })
      .finally(() => {
        if (cancelled) return;
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [id, t]);

  const meta = useMemo(() => {
    if (!item) return null;
    return [
      { k: t("label_when"), v: formatRange(item.start_dt, item.end_dt) },
      { k: t("label_where"), v: item.location_name ?? t("value_tba") },
      { k: t("label_organizer"), v: item.organizer_name ?? t("value_dash") },
      { k: t("label_category"), v: item.category_name ?? t("value_dash") }
    ];
  }, [item, t]);

  async function register() {
    if (!id) return;
    setActionMsg(null);
    try {
      const res = await http.post(`/events/${id}/register`);
      setActionMsg(res.data?.message ?? t("event_registered"));
    } catch (err: any) {
      setActionMsg(err?.response?.data?.detail ?? t("event_registration_failed"));
    }
  }

  async function exportIcs() {
    if (!id) return;
    const res = await http.get(`/events/${id}/ics`, { responseType: "text" });
    const blob = new Blob([res.data], { type: "text/calendar" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `event-${id}.ics`;
    a.click();
    URL.revokeObjectURL(url);
  }

  if (loading) {
    return (
      <Card className="p-6">
        <div className="text-sm font-semibold text-black/70 dark:text-white/80">{t("event_loading")}</div>
      </Card>
    );
  }
  if (error) {
    return (
      <Card className="p-6 ring-1 ring-red-200">
        <div className="text-sm font-semibold text-red-700">{t("events_failed_title")}</div>
        <div className="mt-2 text-sm text-red-700/80">{error}</div>
      </Card>
    );
  }
  if (!item || !meta) return null;

  return (
    <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
      <div className="space-y-6">
        <Card className="p-6">
          <div className="flex flex-wrap items-start justify-between gap-4">
            <div className="min-w-0">
              <Link to="/events" className="text-xs font-semibold text-black/50 hover:text-ink dark:text-white/60 dark:hover:text-white">
                ← {t("action_back_to_events")}
              </Link>
              <h1 className="mt-3 text-3xl font-bold tracking-tight text-ink dark:text-white">{item.title}</h1>
              <div className="mt-3 flex flex-wrap gap-2">
                <Badge tone="blue">{item.status}</Badge>
                <Badge tone="neutral">{item.participation_mode}</Badge>
                {item.free_entry ? <Badge>{t("badge_free_entry")}</Badge> : <Badge tone="neutral">{t("badge_paid")}</Badge>}
                {item.requires_registration ? (
                  <Badge tone="amber">{t("badge_registration")}</Badge>
                ) : (
                  <Badge tone="neutral">{t("badge_no_registration")}</Badge>
                )}
              </div>
            </div>
          </div>

          <div className="mt-6 grid gap-3 md:grid-cols-2">
            {meta.map((m) => (
              <div key={m.k} className="rounded-2xl bg-haze p-4 ring-1 ring-black/5 dark:bg-white/5 dark:ring-white/10">
                <div className="text-xs font-semibold text-black/50 dark:text-white/60">{m.k}</div>
                <div className="mt-1 text-sm font-semibold text-ink dark:text-white">{m.v}</div>
              </div>
            ))}
          </div>

          <div className="mt-6">
            <div className="text-xs font-semibold text-black/50 dark:text-white/60">{t("event_about")}</div>
            <p className="mt-2 whitespace-pre-wrap text-sm leading-relaxed text-black/70 dark:text-white/80">
              {item.description || t("event_no_description")}
            </p>
          </div>

          {actionMsg ? (
            <div className="mt-5 rounded-2xl bg-black/5 p-4 text-sm text-black/70 dark:bg-white/10 dark:text-white/80">{actionMsg}</div>
          ) : null}
        </Card>

        <Card className="p-6">
          <div className="flex items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-bold">{t("event_materials")}</h2>
              <p className="mt-1 text-xs text-black/50 dark:text-white/60">{t("event_materials_hint")}</p>
            </div>
          </div>
          {item.materials.length === 0 ? (
            <div className="mt-4 text-sm muted">{t("event_no_materials")}</div>
          ) : (
            <div className="mt-4 space-y-2">
              {item.materials.map((m) => (
                <div
                  key={m.id}
                  className="flex items-center justify-between rounded-2xl border border-black/10 bg-white px-4 py-3 dark:border-white/10 dark:bg-slate-950"
                >
                  <div className="min-w-0">
                    <div className="truncate font-mono text-xs text-ink dark:text-white">{m.filename}</div>
                    <div className="mt-1 text-[11px] text-black/50 dark:text-white/60">{Math.round(m.size_bytes / 1024)} KB</div>
                  </div>
                  <Badge tone="neutral">file</Badge>
                </div>
              ))}
            </div>
          )}
        </Card>

        <Card className="p-6">
          <h2 className="text-lg font-bold">{t("event_sponsors")}</h2>
          {item.sponsors.length === 0 ? (
            <div className="mt-4 text-sm muted">{t("event_no_sponsors")}</div>
          ) : (
            <div className="mt-4 flex flex-wrap gap-2">
              {item.sponsors.map((s) => (
                <Badge key={s.name} tone="neutral">
                  {s.name}
                </Badge>
              ))}
            </div>
          )}
        </Card>
      </div>

      <div className="space-y-6 lg:sticky lg:top-24 lg:self-start">
        <Card className="p-6">
          <h2 className="text-lg font-bold">{t("event_actions")}</h2>
          <div className="mt-4 grid gap-2">
            <Button variant="secondary" onClick={exportIcs}>
              {t("action_export_ics")}
            </Button>
            {auth.role === "STUDENT" && item.requires_registration ? (
              <Button variant="primary" onClick={register}>
                {t("action_register")}
              </Button>
            ) : null}
            {item.registration_link ? (
              <a href={item.registration_link} target="_blank" rel="noreferrer">
                <Button variant="secondary" className="w-full">
                  {t("action_open_registration_link")}
                </Button>
              </a>
            ) : null}
          </div>

          <div className="mt-6 grid gap-2 text-sm text-black/70 dark:text-white/80">
            <div className="flex items-center justify-between rounded-xl bg-black/5 px-3 py-2 dark:bg-white/10">
              <span>{t("event_capacity")}</span>
              <span className="font-semibold text-ink dark:text-white">{item.capacity ?? t("value_dash")}</span>
            </div>
            <div className="flex items-center justify-between rounded-xl bg-black/5 px-3 py-2 dark:bg-white/10">
              <span>{t("event_requires_ticket")}</span>
              <span className="font-semibold text-ink dark:text-white">{item.requires_ticket ? t("yes") : t("no")}</span>
            </div>
          </div>
        </Card>

        {item.has_qr_code ? (
          <Card className="p-6">
            <h2 className="text-lg font-bold">{t("event_qr")}</h2>
            <p className="mt-2 text-xs muted">{t("event_qr_hint")}</p>
            <div className="mt-4 flex justify-center">
              <div className="rounded-2xl bg-white p-4 ring-1 ring-black/10 dark:bg-slate-950 dark:ring-white/10">
                <QRCodeCanvas value={`usv-events:event:${item.id}`} size={170} />
              </div>
            </div>
          </Card>
        ) : null}
      </div>
    </div>
  );
}

