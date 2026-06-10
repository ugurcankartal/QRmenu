import {
  apiFetchAuthorized,
  apiFetchWithCsrf,
  clearAuthTokens,
  fetchCsrfToken,
  parseJsonResponse,
  storeAuthTokens,
} from "./http";

export interface FrontendAuthUser {
  id: number;
  username: string;
  full_name: string;
  groups: string[];
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: FrontendAuthUser;
}

export async function login(
  username: string,
  password: string,
): Promise<FrontendAuthUser> {
  await fetchCsrfToken();

  const response = await apiFetchWithCsrf("/auth/login/", {
    method: "POST",
    body: JSON.stringify({ username, password }),
  });

  const data = await parseJsonResponse<LoginResponse & { detail?: string }>(
    response,
  );
  if (!response.ok) {
    throw new Error(data.detail ?? "Giriş başarısız.");
  }

  storeAuthTokens(data.access, data.refresh);
  return data.user;
}

export async function fetchCurrentUser(): Promise<FrontendAuthUser | null> {
  const response = await apiFetchAuthorized("/auth/me/");
  if (response.status === 401 || response.status === 403) {
    clearAuthTokens();
    return null;
  }
  if (!response.ok) {
    throw new Error(`Oturum doğrulanamadı (${response.status})`);
  }
  return parseJsonResponse<FrontendAuthUser>(response);
}

export function logout(): void {
  clearAuthTokens();
}
