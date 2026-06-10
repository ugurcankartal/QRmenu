import type { Campaign } from "../types/campaign";
import { apiFetchAuthorized } from "./http";

function normalizeCampaigns(payload: unknown): Campaign[] {
  const list = Array.isArray(payload)
    ? payload
    : payload &&
        typeof payload === "object" &&
        Array.isArray((payload as { results?: unknown }).results)
      ? ((payload as { results: Campaign[] }).results ?? [])
      : [];

  return list;
}

export async function fetchActiveCampaigns(
  languageCode: string,
): Promise<Campaign[]> {
  const params = new URLSearchParams({
    active: "1",
    lang: languageCode,
  });
  const response = await apiFetchAuthorized(`/campaigns/?${params}`);

  if (!response.ok) {
    throw new Error(`Kampanyalar yüklenemedi (${response.status})`);
  }

  const payload = (await response.json()) as unknown;
  return normalizeCampaigns(payload);
}

export async function fetchCampaignBySlug(
  slug: string,
  languageCode: string,
): Promise<Campaign | null> {
  const params = new URLSearchParams({ lang: languageCode });
  const response = await apiFetchAuthorized(
    `/campaigns/${encodeURIComponent(slug)}/?${params}`,
  );

  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Kampanya yüklenemedi (${response.status})`);
  }

  return (await response.json()) as Campaign;
}
