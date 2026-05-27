import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { http } from "../../api/http";

type FormState = {
  title: string;
  description: string;
  start_dt: string;
  end_dt: string;
  requires_registration: boolean;
  requires_ticket: boolean;
  free_entry: boolean;
  capacity: number | null;
  registration_deadline: string | null;
};

function isoLocal(dt: Date) {
  const pad = (n: number) => String(n).padStart(2, "0");
  return `${dt.getFullYear()}-${pad(dt.getMonth() + 1)}-${pad(dt.getDate())}T${pad(dt.getHours())}:${pad(dt.getMinutes())}`;
}

export function EventFormPage() {
  const { id } = useParams();
  const nav = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [form, setForm] = useState<FormState>(() => {
    const start = new Date();
    const end = new Date(Date.now() + 2 * 60 * 60 * 1000);
    return {
      title: "",
      description: "",
      start_dt: isoLocal(start),
      end_dt: isoLocal(end),
      requires_registration: true,
      requires_ticket: true,
      free_entry: true,
      capacity: 30,
      registration_deadline: isoLocal(new Date(Date.now() + 24 * 60 * 60 * 1000))
    };
  });

  useEffect(() => {
    if (!id) return;
    setLoading(true);
    http
      .get(`/events/${id}`)
      .then((res) => {
        const e = res.data;
        setForm({
          title: e.title,
          description: e.description ?? "",
          start_dt: isoLocal(new Date(e.start_dt)),
          end_dt: isoLocal(new Date(e.end_dt)),
          requires_registration: !!e.requires_registration,
          requires_ticket: !!e.requires_ticket,
          free_entry: !!e.free_entry,
          capacity: e.capacity ?? null,
          registration_deadline: e.registration_deadline ? isoLocal(new Date(e.registration_deadline)) : null
        });
      })
      .finally(() => setLoading(false));
  }, [id]);

  async function submit() {
    setError(null);
    setLoading(true);
    try {
      const payload: any = {
        title: form.title,
        description: form.description,
        start_dt: new Date(form.start_dt).toISOString(),
        end_dt: new Date(form.end_dt).toISOString(),
        requires_registration: form.requires_registration,
        requires_ticket: form.requires_ticket,
        free_entry: form.free_entry,
        capacity: form.capacity,
        registration_deadline: form.registration_deadline ? new Date(form.registration_deadline).toISOString() : null,
        has_qr_code: true
      };
      if (id) {
        await http.put(`/events/${id}`, payload);
      } else {
        await http.post(`/events`, payload);
      }
      nav("/organizer/events");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Save failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-2xl rounded-2xl bg-white p-6 shadow-sm ring-1 ring-black/5">
      <h1 className="text-xl font-black tracking-tight">{id ? "Edit event" : "Create event"}</h1>
      {loading ? <div className="mt-3 text-sm text-black/60">Loading...</div> : null}
      <label className="mt-5 block text-xs font-semibold text-black/60">Title</label>
      <input
        value={form.title}
        onChange={(e) => setForm((s) => ({ ...s, title: e.target.value }))}
        className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
      />
      <label className="mt-4 block text-xs font-semibold text-black/60">Description</label>
      <textarea
        value={form.description}
        onChange={(e) => setForm((s) => ({ ...s, description: e.target.value }))}
        className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
        rows={5}
      />
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div>
          <label className="block text-xs font-semibold text-black/60">Start</label>
          <input
            type="datetime-local"
            value={form.start_dt}
            onChange={(e) => setForm((s) => ({ ...s, start_dt: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-black/60">End</label>
          <input
            type="datetime-local"
            value={form.end_dt}
            onChange={(e) => setForm((s) => ({ ...s, end_dt: e.target.value }))}
            className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
          />
        </div>
      </div>
      <div className="mt-4 grid gap-3 md:grid-cols-2">
        <div>
          <label className="block text-xs font-semibold text-black/60">Capacity</label>
          <input
            type="number"
            value={form.capacity ?? ""}
            onChange={(e) => setForm((s) => ({ ...s, capacity: e.target.value ? Number(e.target.value) : null }))}
            className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
          />
        </div>
        <div>
          <label className="block text-xs font-semibold text-black/60">Registration deadline</label>
          <input
            type="datetime-local"
            value={form.registration_deadline ?? ""}
            onChange={(e) => setForm((s) => ({ ...s, registration_deadline: e.target.value || null }))}
            className="mt-1 w-full rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
          />
        </div>
      </div>

      <div className="mt-5 flex flex-wrap gap-4 text-sm">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={form.requires_registration}
            onChange={(e) => setForm((s) => ({ ...s, requires_registration: e.target.checked }))}
          />
          Requires registration
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={form.requires_ticket}
            onChange={(e) => setForm((s) => ({ ...s, requires_ticket: e.target.checked }))}
          />
          Requires ticket
        </label>
        <label className="flex items-center gap-2">
          <input type="checkbox" checked={form.free_entry} onChange={(e) => setForm((s) => ({ ...s, free_entry: e.target.checked }))} />
          Free entry
        </label>
      </div>

      {error ? <div className="mt-4 rounded-xl bg-red-50 p-3 text-sm text-red-700 ring-1 ring-red-100">{error}</div> : null}
      <button
        onClick={submit}
        disabled={loading}
        className="mt-6 w-full rounded-xl bg-usv-700 px-4 py-2 text-sm font-semibold text-white hover:bg-usv-800 disabled:opacity-60"
      >
        {loading ? "Saving..." : "Save"}
      </button>
    </div>
  );
}

