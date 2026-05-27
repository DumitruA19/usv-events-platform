import { useEffect, useState } from "react";
import { http } from "../../api/http";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

export function ReportsPage() {
  const [eventsPerMonth, setEventsPerMonth] = useState<any[]>([]);
  const [byOrganizer, setByOrganizer] = useState<any[]>([]);
  const [participation, setParticipation] = useState<any[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([
      http.get("/admin/reports/events-per-month"),
      http.get("/admin/reports/by-organizer"),
      http.get("/admin/reports/participation")
    ]).then(([a, b, c]) => {
      setEventsPerMonth(a.data.items ?? []);
      setByOrganizer(b.data.items ?? []);
      setParticipation(c.data.items ?? []);
    }).catch((e) => {
      setError(e?.response?.data?.detail ?? "Nu s-au putut încărca rapoartele.");
    }).finally(() => {
      setLoading(false);
    });
  }, []);

  async function exportPdf() {
    setMsg(null);
    const res = await http.get("/admin/reports/export-pdf");
    setMsg(`PDF generated at: ${res.data.file_path}`);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <h1 className="text-2xl font-black tracking-tight">Reports</h1>
        <button onClick={exportPdf} className="rounded-xl bg-usv-700 px-4 py-2 text-sm font-semibold text-white hover:bg-usv-800">
          Export PDF
        </button>
      </div>
      {msg ? <div className="rounded-xl bg-black/5 p-3 text-sm text-black/70">{msg}</div> : null}
      {error ? <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div> : null}
      {loading ? <div className="rounded-2xl bg-white p-6 text-sm text-black/70 shadow-sm ring-1 ring-black/5">Se încarcă rapoartele…</div> : null}
      {!loading && !error && !eventsPerMonth.length && !byOrganizer.length && !participation.length ? (
        <div className="rounded-2xl bg-white p-6 text-sm text-black/70 shadow-sm ring-1 ring-black/5">Nu există încă date pentru rapoarte.</div>
      ) : null}

      <div className="grid gap-4 md:grid-cols-2">
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-black/5">
          <h2 className="text-sm font-bold">Events per month</h2>
          <div className="mt-4 h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={eventsPerMonth}>
                <XAxis dataKey="month" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="events" fill="#0b5fe6" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-black/5">
          <h2 className="text-sm font-bold">Events by organizer</h2>
          <div className="mt-4 h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={byOrganizer}>
                <XAxis dataKey="organizer_id" />
                <YAxis />
                <Tooltip />
                <Bar dataKey="events" fill="#0a4bb8" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-black/5">
        <h2 className="text-sm font-bold">Participation</h2>
        <div className="mt-4 h-52">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={participation}>
              <XAxis dataKey="event_id" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="participants" fill="#1c7cff" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

