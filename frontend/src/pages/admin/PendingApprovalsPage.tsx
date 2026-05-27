import { useEffect, useState } from "react";
import { http } from "../../api/http";

type Pending = { id: number; title: string; organizer_id: number; start_dt: string; status: string };

export function PendingApprovalsPage() {
  const [items, setItems] = useState<Pending[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);

  async function reload() {
    setLoading(true);
    const res = await http.get("/admin/events/pending");
    setItems(res.data.items ?? []);
    setLoading(false);
  }

  useEffect(() => {
    reload();
  }, []);

  async function approve(id: number) {
    setMsg(null);
    await http.post(`/events/${id}/approve`);
    setMsg(`Approved event ${id}`);
    await reload();
  }
  async function reject(id: number) {
    const reason = window.prompt("Motiv respingere (obligatoriu):");
    if (!reason || reason.trim().length < 3) return;
    setMsg(null);
    await http.post(`/admin/events/${id}/reject`, { reason: reason.trim() });
    setMsg(`Eveniment respins (#${id}).`);
    await reload();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black tracking-tight">Aprobări în așteptare</h1>
      {msg ? <div className="rounded-xl bg-black/5 p-3 text-sm text-black/70">{msg}</div> : null}
      {loading ? <div className="rounded-xl bg-white p-4 ring-1 ring-black/5">Loading...</div> : null}
      <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-black/5">
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-black/60">
              <tr>
                <th className="py-2 text-left">Title</th>
                <th className="py-2 text-left">Organizer</th>
                <th className="py-2 text-left">Start</th>
                <th className="py-2 text-right">Actions</th>
              </tr>
            </thead>
            <tbody>
              {items.map((e) => (
                <tr key={e.id} className="border-t border-black/5">
                  <td className="py-2">{e.title}</td>
                  <td className="py-2">{e.organizer_id}</td>
                  <td className="py-2">{new Date(e.start_dt).toLocaleString()}</td>
                  <td className="py-2 text-right space-x-2">
                    <button onClick={() => approve(e.id)} className="rounded-lg bg-usv-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-usv-800">
                      Approve
                    </button>
                    <button onClick={() => reject(e.id)} className="rounded-lg border border-black/10 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-black/5">
                      Reject
                    </button>
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

