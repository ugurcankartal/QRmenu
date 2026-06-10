import { apiFetchAuthorized } from "./http";

export interface I18nBundleResponse {
  language: string | null;
  strings: Record<string, string>;
}

export async function fetchI18nBundle(lang?: string): Promise<I18nBundleResponse> {
  const params = new URLSearchParams();
  if (lang) {
    params.set("lang", lang);
  }

  const query = params.toString();
  const response = await apiFetchAuthorized(
    `/bundle/${query ? `?${query}` : ""}`,
  );

  if (!response.ok) {
    throw new Error(`UI çevirileri yüklenemedi (${response.status})`);
  }

  return response.json() as Promise<I18nBundleResponse>;
}
