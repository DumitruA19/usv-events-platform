import { useEffect, useState } from "react";
import { http } from "../../api/http";

type UserRow = { id: number; username: string | null; email: string | null; role: string; is_active: boolean };

export function OrganizerManagementPage() {
  const [users, setUsers] = useState<UserRow[]>([]);
  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState<string | null>(null);
  const [meId, setMeId] = useState<number | null>(null);
  const [q, setQ] = useState("");
  const [role, setRole] = useState<string>("");
  const [status, setStatus] = useState<string>("");

  const [username, setUsername] = useState("organizer_new");
  const [password, setPassword] = useState("OrganizerPass!234");

  async function reload() {
    setLoading(true);
    if (meId === null) {
      try {
        const me = await http.get("/auth/me");
        setMeId(me.data?.id ?? null);
      } catch {}
    }
    const res = await http.get("/admin/users");
    setUsers(res.data ?? []);
    setLoading(false);
  }

  useEffect(() => {
    reload();
  }, []);

  async function create() {
    setMsg(null);
    await http.post("/admin/organizers", { username, password });
    setMsg("Organizer created");
    await reload();
  }

  async function deactivate(id: number) {
    setMsg(null);
    await http.patch(`/admin/users/${id}`, { is_active: false });
    setMsg("Utilizator dezactivat");
    await reload();
  }

  async function activate(id: number) {
    setMsg(null);
    await http.patch(`/admin/users/${id}`, { is_active: true });
    setMsg("Utilizator activat");
    await reload();
  }

  async function setUserRole(id: number, nextRole: string) {
    setMsg(null);
    await http.patch(`/admin/users/${id}`, { role: nextRole });
    setMsg("Rol actualizat");
    await reload();
  }

  const filtered = users.filter((u) => {
    const qq = q.trim().toLowerCase();
    const matchQ = !qq || (u.username || "").toLowerCase().includes(qq) || (u.email || "").toLowerCase().includes(qq);
    const matchRole = !role || u.role === role;
    const matchStatus = !status || (status === "active" ? u.is_active : !u.is_active);
    return matchQ && matchRole && matchStatus;
  });

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-black tracking-tight">Utilizatori</h1>
      {msg ? <div className="rounded-xl bg-black/5 p-3 text-sm text-black/70">{msg}</div> : null}

      <div className="rounded-2xl bg-white p-6 shadow-sm ring-1 ring-black/5">
        <h2 className="text-sm font-bold">Creează organizator</h2>
        <div className="mt-3 grid gap-3 md:grid-cols-2">
          <input
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
            placeholder="username"
          />
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
            placeholder="password"
          />
        </div>
        <button onClick={create} className="mt-4 rounded-xl bg-usv-700 px-4 py-2 text-sm font-semibold text-white hover:bg-usv-800">
          Creează
        </button>
      </div>

      <div className="rounded-2xl bg-white p-4 shadow-sm ring-1 ring-black/5">
        {loading ? <div className="p-3 text-sm text-black/60">Loading...</div> : null}
        <div className="mb-3 grid gap-2 md:grid-cols-3">
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            className="rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
            placeholder="Caută după username/email…"
          />
          <select
            value={role}
            onChange={(e) => setRole(e.target.value)}
            className="rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
          >
            <option value="">Toate rolurile</option>
            <option value="STUDENT">Student</option>
            <option value="ORGANIZER">Organizator</option>
            <option value="ADMIN">Admin</option>
          </select>
          <select
            value={status}
            onChange={(e) => setStatus(e.target.value)}
            className="rounded-xl border border-black/10 bg-white px-3 py-2 text-sm outline-none ring-usv-600 focus:ring-2"
          >
            <option value="">Toate statusurile</option>
            <option value="active">Activ</option>
            <option value="inactive">Inactiv</option>
          </select>
        </div>
        <div className="overflow-auto">
          <table className="w-full text-sm">
            <thead className="text-xs text-black/60">
              <tr>
                <th className="py-2 text-left">Username</th>
                <th className="py-2 text-left">Email</th>
                <th className="py-2 text-left">Rol</th>
                <th className="py-2 text-left">Status</th>
                <th className="py-2 text-right"></th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((u) => (
                <tr key={u.id} className="border-t border-black/5">
                  <td className="py-2">{u.username}</td>
                  <td className="py-2">{u.email ?? "-"}</td>
                  <td className="py-2">
                    <select
                      value={u.role}
                      onChange={(e) => setUserRole(u.id, e.target.value)}
                      className="rounded-lg border border-black/10 bg-white px-2 py-1 text-xs font-semibold"
                      disabled={meId === u.id}
                      title={meId === u.id ? "Nu îți poți schimba propriul rol." : ""}
                    >
                      <option value="STUDENT">STUDENT</option>
                      <option value="ORGANIZER">ORGANIZER</option>
                      <option value="ADMIN">ADMIN</option>
                    </select>
                  </td>
                  <td className="py-2">{u.is_active ? "Activ" : "Inactiv"}</td>
                  <td className="py-2 text-right">
                    {u.is_active ? (
                      <button
                        onClick={() => deactivate(u.id)}
                        className="rounded-lg border border-black/10 bg-white px-3 py-1.5 text-xs font-semibold hover:bg-black/5 disabled:opacity-50"
                        disabled={meId === u.id}
                        title={meId === u.id ? "Nu îți poți dezactiva propriul cont." : ""}
                      >
                        Dezactivează
                      </button>
                    ) : (
                      <button onClick={() => activate(u.id)} className="rounded-lg bg-usv-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-usv-800">
                        Activează
                      </button>
                    )}
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

