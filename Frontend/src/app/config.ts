// Dev: Vite proxy (/api/v1 → Django). Prod: Nginx ayni origin uzerinden proxy eder.
const DEFAULT_API_BASE = "/api/v1";

export const API_BASE_URL = import.meta.env.PROD
  ? DEFAULT_API_BASE
  : (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
    DEFAULT_API_BASE;

export const LANGUAGE_STORAGE_KEY = "qrmenu.language";
export const LANGUAGE_USER_PICKED_KEY = "qrmenu.language.user_picked";
export const ADISYON_SESSION_KEY = "qrmenu.adisyon.session";
export const AUTH_ACCESS_TOKEN_KEY = "qrmenu.auth.access";
export const AUTH_REFRESH_TOKEN_KEY = "qrmenu.auth.refresh";
