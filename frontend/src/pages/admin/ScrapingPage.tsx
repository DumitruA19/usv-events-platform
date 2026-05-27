import { useEffect, useState } from "react";
import { http } from "../../api/http";
import { useAuth } from "../../store/auth";
import { useMe } from "../../hooks/useMe";

type Draft = {
  id: number;
  source: string;
  status: string;
  source_url: string | null;
  image_url: string | null;
  rejection_reason: string | null;
  title: string;
  start_dt: string;
  end_dt: string;
  location_text: string | null;
  category_text: string | null;
};

export function ScrapingPage() {
  const { auth } = useAuth();
  const { me, loading: meLoading } = useMe();
  const [items, setItems] = useState<Draft[]>([]);
  const [msg, setMsg] = useState<string | null>(null);
  const [url, setUrl] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    if (!auth.accessToken) {
      setLoading(false);
      setError("Trebuie să fii autentificat pentru a accesa această secțiune.");
      return;
    }
    if (me && me.role !== "ADMIN") {
      setLoading(false);
      setError("Nu ai drepturi de administrator pentru această secțiune.");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const res = await http.get("/ai/scrape/results");
      setItems(res.data ?? []);
    } catch (e: any) {
      if (e?.response?.status === 401) {
        setError("Trebuie să fii autentificat pentru a accesa această secțiune.");
      } else if (e?.response?.status === 403) {
        setError("Nu ai drepturi de administrator pentru această secțiune.");
      } else {
        setError(e?.response?.data?.detail ?? "Nu s-au putut încărca rezultatele scraping.");
      }
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    if (meLoading) return;
    reload();
  }, [auth.accessToken, me?.role, meLoading]);

  async function runScrape() {
    setMsg(null);
    const res = await http.post("/ai/scrape/run", { url: url.trim() ? url.trim() : null });
    setMsg(`Rulare completă: ${res.data.created} noi, ${res.data.duplicates} duplicate, ${res.data.errors} erori.`);
    await reload();
  }

  async function approve(id: number) {
    setMsg(null);
    const res = await http.post(`/ai/scrape/results/${id}/approve`);
    setMsg(`Draft approved into event ${res.data.event_id}`);
    await reload();
  }

  async function reject(id: number) {
    setMsg(null);
    await http.post(`/ai/scrape/results/${id}/reject`);
    setMsg("Draft respins");
    await reload();
  }

  async function addSource() {
    const u = url.trim();
    if (!u) return;
    if (!auth.accessToken) {
      setError("Trebuie să fii autentificat pentru a accesa această secțiune.");
      return;
    }
    setMsg(null);
    await http.post("/ai/scrape/sources", { url: u });
    setMsg("Sursa a fost salvată. Apasă „Rulează scraping” pentru import.");
  }

  return (
    <div className="space-y-4">
      <div className="flex items-end justify-between">
        <h1 className="text-2xl font-black tracking-tight">Evenimente importate (AI)</h1>
      </div>
      {msg ? <div className="rounded-xl bg-black/5 p-3 text-sm text-black/70">{msg}</div> : null}
      {error ? <div className="rounded-xl bg-red-50 p-3 text-sm text-red-700 ring-1 ring-red-200">{error}</div> : null}

      <div className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-black/5">
        <div className="text-sm font-bold">Sursă URL</div>
        <div className="mt-2 flex gap-2">
          <input
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            placeholder="https://..."
            className="w-full rounded-xl border border-black/10 px-3 py-2 text-sm"
          />
          <button onClick={addSource} className="rounded-xl border border-black/10 bg-white px-4 py-2 text-sm font-semibold hover:bg-black/5">
            Salvează
          </button>
          <button onClick={runScrape} className="rounded-xl bg-usv-700 px-4 py-2 text-sm font-semibold text-white hover:bg-usv-800">
            Rulează scraping
          </button>
        </div>
      </div>

      <div className="grid gap-3">
        {loading ? <div className="rounded-2xl bg-white p-5 text-sm text-black/70 shadow-sm ring-1 ring-black/5">Se încarcă rezultatele…</div> : null}
        {!loading && !items.length ? <div className="rounded-2xl bg-white p-5 text-sm text-black/70 shadow-sm ring-1 ring-black/5">Nu există încă drafturi importate.</div> : null}
        {items.map((d) => (
          <div key={d.id} className="rounded-2xl bg-white p-5 shadow-sm ring-1 ring-black/5">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-lg font-bold">{d.title}</div>
                <div className="mt-1 text-xs text-black/60">
                  {new Date(d.start_dt).toLocaleString()} → {new Date(d.end_dt).toLocaleString()}
                </div>
                <div className="mt-1 text-xs text-black/60">
                  {d.location_text ?? "—"} · {d.category_text ?? "—"} · {d.source}
                </div>
                {d.source_url ? <a href={d.source_url} target="_blank" rel="noreferrer" className="mt-2 block text-xs text-usv-700 underline">Sursă</a> : null}
                {d.rejection_reason ? <div className="mt-1 text-xs text-red-700">{d.rejection_reason}</div> : null}
              </div>
              <span className="rounded-full bg-black/5 px-3 py-1 text-xs font-semibold">{d.status}</span>
            </div>
            <div className="mt-4 flex gap-2 text-xs">
              <button onClick={() => approve(d.id)} className="rounded-lg bg-usv-700 px-3 py-2 font-semibold text-white hover:bg-usv-800">
                Approve
              </button>
              <button onClick={() => reject(d.id)} className="rounded-lg border border-black/10 bg-white px-3 py-2 font-semibold hover:bg-black/5">
                Reject
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

