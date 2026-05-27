import { useEffect, useRef, useState } from "react";
import { useLocation } from "react-router-dom";
import { http } from "../api/http";
import { useAuth } from "../store/auth";

type Msg = { role: "user" | "assistant"; content: string };

export function ChatbotWidget() {
  const { auth } = useAuth();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [msgs, setMsgs] = useState<Msg[]>(() => [
    { role: "assistant", content: "Salut! Sunt asistentul platformei. Cu ce te pot ajuta?" }
  ]);
  const endRef = useRef<HTMLDivElement | null>(null);
  const location = useLocation();

  const canUse = Boolean(auth.accessToken && auth.role);
  const page = location.pathname;

  useEffect(() => {
    if (!open) return;
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [open, msgs.length]);

  if (!canUse) return null;

  async function send() {
    const text = input.trim();
    if (!text || loading) return;
    if (text.length > 500) {
      setError("Mesajul este prea lung. Te rog păstrează-l sub 500 de caractere.");
      return;
    }
    setError(null);
    setInput("");
    const nextMsgs: Msg[] = [...msgs, { role: "user", content: text }];
    setMsgs(nextMsgs);
    setLoading(true);
    try {
      const history = nextMsgs.slice(-4);
      const res = await http.post("/ai/chat", { message: text, page, history, session_id: sessionId });
      const reply = String(res.data?.reply ?? "Nu am primit răspuns.");
      const sid = res.data?.session_id ? String(res.data.session_id) : null;
      if (sid && !sessionId) setSessionId(sid);
      setMsgs((prev) => [...prev, { role: "assistant", content: reply }]);
    } catch (e: any) {
      const detail = e?.response?.data?.detail ?? "Asistentul nu este disponibil momentan.";
      setError(detail);
      setMsgs((prev) => [...prev, { role: "assistant", content: detail }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {open ? (
        <div className="w-[min(360px,calc(100vw-24px))] overflow-hidden rounded-3xl border border-black/10 bg-white shadow-lift dark:border-white/10 dark:bg-slate-950">
          <div className="flex items-center justify-between gap-3 border-b border-black/5 px-4 py-3 dark:border-white/10">
            <div className="text-sm font-bold text-ink dark:text-white">Asistent</div>
            <button onClick={() => setOpen(false)} className="rounded-xl bg-black/5 px-3 py-1 text-xs font-semibold dark:bg-white/10">
              Închide
            </button>
          </div>
          <div className="max-h-[360px] overflow-auto px-4 py-3">
            <div className="space-y-2">
              {error ? <div className="rounded-2xl bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div> : null}
              {msgs.map((m, i) => (
                <div
                  key={i}
                  className={[
                    "rounded-2xl px-3 py-2 text-sm",
                    m.role === "user" ? "ml-8 bg-usv-700 text-white" : "mr-8 bg-black/5 text-ink dark:bg-white/10 dark:text-white"
                  ].join(" ")}
                >
                  {m.content}
                </div>
              ))}
              <div ref={endRef} />
            </div>
          </div>
          <div className="flex gap-2 border-t border-black/5 p-3 dark:border-white/10">
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => (e.key === "Enter" ? send() : null)}
              placeholder="Scrie o întrebare…"
              maxLength={500}
              className="w-full rounded-2xl border border-black/10 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-usv-700/30 dark:border-white/10 dark:bg-slate-950 dark:text-white"
              disabled={loading}
            />
            <button
              onClick={send}
              disabled={loading || !input.trim()}
              className="rounded-2xl bg-usv-700 px-4 py-2 text-sm font-semibold text-white disabled:opacity-50"
            >
              {loading ? "..." : "Trimite"}
            </button>
          </div>
        </div>
      ) : (
        <button onClick={() => setOpen(true)} className="rounded-full bg-usv-700 px-4 py-3 text-sm font-semibold text-white shadow-lift">
          Chat
        </button>
      )}
    </div>
  );
}
