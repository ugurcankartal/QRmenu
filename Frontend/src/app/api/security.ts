import { ADISYON_SESSION_KEY, API_BASE_URL } from "../config";
import { getStoredAccessToken } from "./http";

function getStoredAdisyonSessionKey(): string | null {
  try {
    return localStorage.getItem(ADISYON_SESSION_KEY);
  } catch {
    return null;
  }
}

export function logPageVisit(pathname: string, search: string): void {
  const path = pathname || "/";
  const params = new URLSearchParams({ path });
  if (search && search !== "?") {
    params.set("search", search.startsWith("?") ? search.slice(1) : search);
  }
  if (typeof document !== "undefined" && document.referrer) {
    params.set("referrer", document.referrer);
  }

  const url = `${API_BASE_URL}/security/page-visit/?${params.toString()}`;
  const headers: HeadersInit = {};
  const token = getStoredAccessToken();
  if (token) {
    headers.Authorization = `Bearer ${token}`;
  }
  const sessionKey = getStoredAdisyonSessionKey();
  if (sessionKey) {
    headers["X-Session-Key"] = sessionKey;
  }

  void fetch(url, {
    method: "GET",
    credentials: "include",
    keepalive: true,
    headers,
  });
}
