import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App";
import { AuthProvider } from "./store/auth";
import { setAuthToken } from "./api/http";
import { I18nProvider } from "./i18n/i18n";
import { ThemeProvider } from "./theme/theme";
import "./styles.css";

try {
  const raw = localStorage.getItem("usv_events_auth_v1");
  if (raw) {
    const parsed = JSON.parse(raw) as { accessToken?: string | null };
    setAuthToken(parsed.accessToken ?? null);
  }
} catch {
  setAuthToken(null);
}

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <ThemeProvider>
      <I18nProvider>
        <AuthProvider>
          <BrowserRouter>
            <App />
          </BrowserRouter>
        </AuthProvider>
      </I18nProvider>
    </ThemeProvider>
  </React.StrictMode>
);
