import { useEffect, useState } from "react";
import { http } from "../api/http";
import { useAuth } from "../store/auth";

export type Me = { id: number; email: string | null; username: string | null; role: string };

export function useMe() {
  const { auth } = useAuth();
  const [me, setMe] = useState<Me | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!auth.accessToken) {
      setMe(null);
      return;
    }
    setLoading(true);
    http
      .get("/auth/me")
      .then((res) => setMe(res.data))
      .finally(() => setLoading(false));
  }, [auth.accessToken]);

  return { me, loading };
}

