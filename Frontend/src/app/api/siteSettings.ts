import type { SiteSettings } from "../types/siteSettings";
import { apiFetchAuthorized } from "./http";

export async function fetchSiteSettings(
  languageCode?: string,
): Promise<SiteSettings | null> {
  const params = new URLSearchParams();
  if (languageCode) {
    params.set("lang", languageCode);
  }
  const query = params.toString();
  const response = await apiFetchAuthorized(
    `/settings/${query ? `?${query}` : ""}`,
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Site ayarları yüklenemedi (${response.status})`);
  }

  return response.json() as Promise<SiteSettings>;
}
