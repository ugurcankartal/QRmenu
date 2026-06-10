// Dev server proxies /api/v1 → Django (see vite.config.ts). Same-origin keeps CSRF cookies working.
const DEFAULT_API_BASE = "/api/v1";

export const API_BASE_URL =
  (import.meta.env.VITE_API_BASE_URL as string | undefined)?.replace(/\/$/, "") ||
  DEFAULT_API_BASE;

export const LANGUAGE_STORAGE_KEY = "qrmenu.language";
export const LANGUAGE_USER_PICKED_KEY = "qrmenu.language.user_picked";
export const ADISYON_SESSION_KEY = "qrmenu.adisyon.session";
export const AUTH_ACCESS_TOKEN_KEY = "qrmenu.auth.access";
export const AUTH_REFRESH_TOKEN_KEY = "qrmenu.auth.refresh";
