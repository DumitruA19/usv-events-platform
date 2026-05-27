import axios from "axios";

const baseURL = import.meta.env.VITE_API_URL || import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export const http = axios.create({
  baseURL
});

export function setAuthToken(token: string | null) {
  if (token) {
    http.defaults.headers.common.Authorization = `Bearer ${token}`;
  } else {
    delete http.defaults.headers.common.Authorization;
  }
}

