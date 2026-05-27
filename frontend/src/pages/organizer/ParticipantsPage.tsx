import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { http } from "../../api/http";

type Participant = {
  student_id: number;
  email: string | null;
  status: string;
  registered_at: string;
  ticket_qr_payload: string | null;
};

export function ParticipantsPage() {
  const { id } = useParams();
  const [items, setItems] = useState<Participant[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    http
      .get(`/events/${id}/participants`)
      .then((res) => setItems(res.data ?? []))
      .finally(() => setLoading(false));
  }, [id]);

  async function exportCsv() {
    if (!id) return;
    const res = await http.get(`/events/${id}/participants/export`, { responseType: "text" });
    const blob = new Blob([res.data], { type: "text/csv" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `participants-${id}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

  async function checkIn(qr_payload: string) {
    if (!id) return;
    setMsg(null);
    const res = await http.post(`/events/${id}/check-in`, { qr_payload });
    setMsg(res.data?.message ?? "Checked in");
    const updated = await http.get(`/events/${id}/participants`);
    setItems(updated.data ?? []);
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <h1 className="text-2xl font-black tracking-tight">Participants</h1>
        <button onClick={exportCsv} className="rounded-xl border border-black/10 bg-white px-4 py-2 text-sm font-semibold hover:bg-black/5">
          Export CSV
        </button>
      </div>
      {msg ? <div className="rounded-xl bg-black/5 p-3 text-sm text-black/70">{msg}</div> : null}
      {loading ? <div className="rounded-xl bg-white p-4 ring-1 ring-black/5">Loading...</div> : null}
      <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-black/5">
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-black/60">
              <tr>
                <th className="py-2 text-left">Student</th>
                <th className="py-2 text-left">Status</th>
                <th className="py-2 text-left">Registered</th>
                <th className="py-2 text-left">Ticket</th>
                <th className="py-2 text-right"></th>
              </tr>
            </thead>
            <tbody>
              {items.map((p) => (
                <tr key={p.student_id} className="border-t border-black/5">
                  <td className="py-2">{p.email ?? p.student_id}</td>
                  <td className="py-2">{p.status}</td>
                  <td className="py-2">{new Date(p.registered_at).toLocaleString()}</td>
                  <td className="py-2 font-mono text-xs">{p.ticket_qr_payload ?? "—"}</td>
                  <td className="py-2 text-right">
                    {p.ticket_qr_payload && p.status !== "CHECKED_IN" ? (
                      <button
                        onClick={() => checkIn(p.ticket_qr_payload!)}
                        className="rounded-lg bg-usv-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-usv-800"
                      >
                        Check-in
                      </button>
                    ) : null}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

