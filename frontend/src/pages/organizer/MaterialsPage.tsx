import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { http } from "../../api/http";

type Material = { id: number; filename: string; size_bytes: number };

export function MaterialsPage() {
  const { id } = useParams();
  const [items, setItems] = useState<Material[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function reload() {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const res = await http.get(`/events/${id}/materials`);
      setItems(res.data.items ?? []);
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Failed to load materials");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => {
    reload();
  }, [id]);

  async function upload(files: FileList | null) {
    if (!id || !files || files.length === 0) return;
    const form = new FormData();
    Array.from(files).forEach((f) => form.append("files", f));
    await http.post(`/events/${id}/materials`, form, { headers: { "Content-Type": "multipart/form-data" } });
    await reload();
  }

  async function remove(materialId: number) {
    await http.delete(`/materials/${materialId}`);
    await reload();
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black tracking-tight">Materials</h1>
      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-black/5">
        <label className="block text-xs font-semibold text-black/60">Upload files</label>
        <input type="file" multiple className="mt-2 block w-full text-sm" onChange={(e) => upload(e.target.files)} />
        {error ? <div className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700 ring-1 ring-red-100">{error}</div> : null}
      </div>

      {loading ? <div className="rounded-xl bg-white p-4 ring-1 ring-black/5">Loading...</div> : null}
      <div className="grid gap-3">
        {items.map((m) => (
          <div key={m.id} className="flex items-center justify-between rounded-2xl bg-white p-5 shadow-sm ring-1 ring-black/5">
            <div>
              <div className="font-mono text-xs">{m.filename}</div>
              <div className="mt-1 text-xs text-black/50">{Math.round(m.size_bytes / 1024)} KB</div>
            </div>
            <button onClick={() => remove(m.id)} className="rounded-lg border border-black/10 bg-white px-3 py-2 text-xs font-semibold hover:bg-black/5">
              Delete
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}

