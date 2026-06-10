import {
  API_BASE_URL,
  AUTH_ACCESS_TOKEN_KEY,
  AUTH_REFRESH_TOKEN_KEY,
} from "../config";

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

export function getStoredAccessToken(): string | null {
  return sessionStorage.getItem(AUTH_ACCESS_TOKEN_KEY);
}

export function getStoredRefreshToken(): string | null {
  return sessionStorage.getItem(AUTH_REFRESH_TOKEN_KEY);
}

export function storeAuthTokens(access: string, refresh: string): void {
  sessionStorage.setItem(AUTH_ACCESS_TOKEN_KEY, access);
  sessionStorage.setItem(AUTH_REFRESH_TOKEN_KEY, refresh);
}

export function clearAuthTokens(): void {
  sessionStorage.removeItem(AUTH_ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(AUTH_REFRESH_TOKEN_KEY);
}

let cachedCsrfToken: string | null = null;

export function getCsrfToken(): string | null {
  return cachedCsrfToken ?? getCookie("csrftoken");
}

export function setCsrfToken(token: string): void {
  cachedCsrfToken = token;
}

export async function parseJsonResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) {
    throw new Error(
      response.ok
        ? "Sunucu beklenmeyen bir yanıt döndürdü."
        : `İstek başarısız (${response.status}). API sunucusunun çalıştığından emin olun.`,
    );
  }
  return response.json() as Promise<T>;
}

export async function fetchCsrfToken(): Promise<string> {
  const response = await apiFetch("/auth/csrf/");
  if (!response.ok) {
    throw new Error("CSRF token alınamadı.");
  }
  const data = (await parseJsonResponse<{ csrfToken?: string }>(response)) ?? {};
  const token = data.csrfToken ?? getCookie("csrftoken");
  if (!token) {
    throw new Error("CSRF token alınamadı.");
  }
  setCsrfToken(token);
  return token;
}

export async function apiFetch(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(init.headers);
  const token = getStoredAccessToken();

  if (token && !headers.has("Authorization")) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  return fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers,
    credentials: init.credentials ?? "include",
  });
}

export async function apiFetchWithCsrf(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  const headers = new Headers(init.headers);
  const csrfToken = getCsrfToken();
  if (csrfToken) {
    headers.set("X-CSRFToken", csrfToken);
  }
  if (!headers.has("Content-Type") && init.body) {
    headers.set("Content-Type", "application/json");
  }
  return apiFetch(path, { ...init, headers });
}

export async function refreshAccessToken(): Promise<string | null> {
  if (!getStoredRefreshToken()) {
    return null;
  }

  if (!getCsrfToken()) {
    try {
      await fetchCsrfToken();
    } catch {
      clearAuthTokens();
      return null;
    }
  }

  const refresh = getStoredRefreshToken();
  if (!refresh) {
    return null;
  }

  const response = await apiFetchWithCsrf("/auth/refresh/", {
    method: "POST",
    body: JSON.stringify({ refresh }),
  });

  if (!response.ok) {
    clearAuthTokens();
    return null;
  }

  const data = await parseJsonResponse<{ access?: string; refresh?: string }>(
    response,
  );
  if (!data.access) {
    clearAuthTokens();
    return null;
  }

  storeAuthTokens(data.access, data.refresh ?? refresh);
  return data.access;
}

export async function apiFetchAuthorized(
  path: string,
  init: RequestInit = {},
): Promise<Response> {
  let response = await apiFetch(path, init);
  if (response.status !== 401) {
    return response;
  }

  const newAccess = await refreshAccessToken();
  if (!newAccess) {
    return response;
  }

  const retryHeaders = new Headers(init.headers);
  retryHeaders.set("Authorization", `Bearer ${newAccess}`);
  return apiFetch(path, { ...init, headers: retryHeaders });
}
