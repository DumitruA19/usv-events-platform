import { useEffect, useMemo, useState } from "react";
import { http } from "../../api/http";

type Row = { id: number; title: string; organizer_id: number; start_dt: string; end_dt: string; status: string };

export function EventsManagementPage() {
  const [items, setItems] = useState<Row[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [q, setQ] = useState("");
  const [status, setStatus] = useState<string>("");

  async function reload() {
    setLoading(true);
    try {
      const res = await http.get("/admin/events", { params: { q: q.trim() || null, statuses: null } });
      let list: Row[] = res.data.items ?? [];
      if (status) list = list.filter((e) => e.status === status);
      setItems(list);
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    reload();
  }, []);

  const filtered = useMemo(() => {
    const qq = q.trim().toLowerCase();
    if (!qq) return items;
    return items.filter((e) => e.title.toLowerCase().includes(qq));
  }, [items, q]);

  async function approve(id: number) {
    setMsg(null);
    await http.post(`/events/${id}/approve`);
    setMsg(`Eveniment aprobat (#${id}).`);
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

  async function cancel(id: number) {
    const reason = window.prompt("Motiv anulare (obligatoriu):");
    if (!reason || reason.trim().length < 3) return;
    setMsg(null);
    await http.post(`/admin/events/${id}/cancel`, { reason: reason.trim() });
    setMsg(`Eveniment anulat (#${id}).`);
    await reload();
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-col gap-3 md:flex-row md:items-end md:justify-between">
        <div>
          <h1 className="text-2xl font-black tracking-tight">Evenimente</h1>
          <div className="mt-1 text-sm text-black/60">Listă completă + acțiuni admin (aprobare/respingere/anulare).</div>
        </div>
        <div className="flex flex-col gap-2 md:flex-row">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Caută după titlu…"
            className="w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2 md:w-72"
          />
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2 md:w-56"
          >
            <option value="">Toate statusurile</option>
            <option value="DRAFT">DRAFT</option>
            <option value="PENDING_APPROVAL">PENDING</option>
            <option value="PUBLISHED">PUBLISHED</option>
            <option value="REJECTED">REJECTED</option>
            <option value="CANCELLED">CANCELLED</option>
          </select>
          <button onClick={reload} className="rounded-xl bg-usv-700 px-4 py-2 text-sm font-semibold text-white hover:bg-usv-800">
            Reîncarcă
          </button>
        </div>
      </div>

      {msg ? <div className="rounded-xl bg-black/5 p-3 text-sm text-black/70">{msg}</div> : null}
      {loading ? <div className="rounded-xl bg-white p-4 ring-1 ring-black/5">Se încarcă…</div> : null}

      <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-black/5">
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-black/60">
              <tr>
                <th className="py-2 text-left">Titlu</th>
                <th className="py-2 text-left">Organizator</th>
                <th className="py-2 text-left">Start</th>
                <th className="py-2 text-left">Status</th>
                <th className="py-2 text-right">Acțiuni</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((e) => (
                <tr key={e.id} className="border-t border-black/5">
                  <td className="py-2">{e.title}</td>
                  <td className="py-2">#{e.organizer_id}</td>
                  <td className="py-2">{new Date(e.start_dt).toLocaleString()}</td>
                  <td className="py-2">{e.status}</td>
                  <td className="py-2 text-right space-x-2">
                    {e.status === "PENDING_APPROVAL" ? (
                      <button onClick={() => approve(e.id)} className="rounded-lg bg-usv-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-usv-800">
                        Aprobă
                      </button>
                    ) : null}
                    {e.status === "PENDING_APPROVAL" ? (
                      <button onClick={() => reject(e.id)} className="rounded-lg border border-black/10 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-black/5">
                        Respinge
                      </button>
                    ) : null}
                    {e.status !== "CANCELLED" ? (
                      <button onClick={() => cancel(e.id)} className="rounded-lg border border-black/10 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-black/5">
                        Anulează
                      </button>
                    ) : null}
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && !loading ? (
                <tr>
                  <td colSpan={5} className="py-6 text-center text-sm text-black/50">
                    Nu există evenimente.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

