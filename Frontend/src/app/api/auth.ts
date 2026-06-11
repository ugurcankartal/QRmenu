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

export interface LoginErrorPayload {
  detail?: string;
  remaining_attempts?: number;
  retry_after_seconds?: number;
  lockout_minutes?: number;
  locked_until?: string;
}

export class LoginError extends Error {
  remainingAttempts?: number;
  retryAfterSeconds?: number;
  lockoutMinutes?: number;
  lockedUntil?: string;
  status: number;

  constructor(message: string, status: number, payload: LoginErrorPayload = {}) {
    super(message);
    this.name = "LoginError";
    this.status = status;
    this.remainingAttempts = payload.remaining_attempts;
    this.retryAfterSeconds = payload.retry_after_seconds;
    this.lockoutMinutes = payload.lockout_minutes;
    this.lockedUntil = payload.locked_until;
  }
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

  const data = await parseJsonResponse<LoginResponse & LoginErrorPayload>(
    response,
  );
  if (!response.ok) {
    throw new LoginError(
      data.detail ?? "Giriş başarısız.",
      response.status,
      data,
    );
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
