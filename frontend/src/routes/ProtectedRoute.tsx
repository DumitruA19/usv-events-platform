import React, { useEffect } from "react";
import { Navigate } from "react-router-dom";
import { useAuth, type Role } from "../store/auth";
import { setAuthToken } from "../api/http";

export function ProtectedRoute({ roles, children }: { roles: Role[]; children: React.ReactNode }) {
  const { auth } = useAuth();

  useEffect(() => {
    setAuthToken(auth.accessToken);
  }, [auth.accessToken]);

  if (!auth.accessToken || !auth.role) return <Navigate to="/" replace />;
  if (!roles.includes(auth.role)) return <Navigate to="/" replace />;
  return <>{children}</>;
}

