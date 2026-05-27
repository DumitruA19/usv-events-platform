import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { http } from "../api/http";
import { useI18n } from "../i18n/i18n";
import { Badge } from "../ui/Badge";
import { Button } from "../ui/Button";
import { Card } from "../ui/Card";
import { PageHeader } from "../ui/PageHeader";

type CalendarEvent = { id: number; title: string; start_dt: string; end_dt: string };

function startOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth(), 1);
}
function endOfMonth(date: Date) {
  return new Date(date.getFullYear(), date.getMonth() + 1, 0);
}

export function CalendarPage() {
  const { t } = useI18n();
  const [cursor, setCursor] = useState(() => new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);

  useEffect(() => {
    http.get("/events/calendar").then((res) => setEvents(res.data.items ?? []));
  }, []);

  const grid = useMemo(() => {
    const start = startOfMonth(cursor);
    const end = endOfMonth(cursor);
    const firstDow = (start.getDay() + 6) % 7; // Mon=0
    const daysInMonth = end.getDate();
    const cells: Array<{ date: Date | null }> = [];
    for (let i = 0; i < firstDow; i++) cells.push({ date: null });
    for (let d = 1; d <= daysInMonth; d++) cells.push({ date: new Date(cursor.getFullYear(), cursor.getMonth(), d) });
    while (cells.length % 7 !== 0) cells.push({ date: null });
    return cells;
  }, [cursor]);

  const monthLabel = cursor.toLocaleString(undefined, { month: "long", year: "numeric" });

  function inSameDay(e: CalendarEvent, day: Date) {
    const s = new Date(e.start_dt);
    return s.getFullYear() === day.getFullYear() && s.getMonth() === day.getMonth() && s.getDate() === day.getDate();
  }

  return (
    <div className="space-y-5">
      <PageHeader
        title={t("calendar_title")}
        subtitle={t("calendar_subtitle")}
        actions={
          <div className="flex items-center gap-2">
            <Button variant="secondary" size="sm" onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() - 1, 1))}>
              {t("calendar_prev")}
            </Button>
            <div className="rounded-xl bg-white px-4 py-2 text-sm font-bold ring-1 ring-black/10 dark:bg-slate-950 dark:text-white dark:ring-white/10">{monthLabel}</div>
            <Button variant="secondary" size="sm" onClick={() => setCursor(new Date(cursor.getFullYear(), cursor.getMonth() + 1, 1))}>
              {t("calendar_next")}
            </Button>
          </div>
        }
      />

      <div className="grid grid-cols-7 gap-2 text-xs font-semibold text-black/50 dark:text-white/60">
        {[t("dow_mon"), t("dow_tue"), t("dow_wed"), t("dow_thu"), t("dow_fri"), t("dow_sat"), t("dow_sun")].map((d) => (
          <div key={d} className="px-2">
            {d}
          </div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-2">
        {grid.map((cell, idx) => {
          const dayEvents = cell.date ? events.filter((e) => inSameDay(e, cell.date!)) : [];
          return (
            <Card key={idx} className="min-h-28 p-3">
              <div className="flex items-center justify-between">
                <div className="text-xs font-bold text-black/60 dark:text-white/70">{cell.date ? cell.date.getDate() : ""}</div>
                {dayEvents.length ? <Badge tone="blue">{dayEvents.length}</Badge> : null}
              </div>
              <div className="mt-3 space-y-1">
                {dayEvents.slice(0, 3).map((e) => (
                  <Link
                    key={e.id}
                    to={`/events/${e.id}`}
                    className="block truncate rounded-xl bg-usv-700/10 px-3 py-2 text-[11px] font-semibold text-usv-900 hover:bg-usv-700/15"
                    title={e.title}
                  >
                    {e.title}
                  </Link>
                ))}
                {dayEvents.length > 3 ? (
                  <div className="text-[11px] text-black/50 dark:text-white/60">{t("calendar_more", { n: String(dayEvents.length - 3) })}</div>
                ) : null}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}
