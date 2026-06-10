import type { ChefRecommendation } from "../types/chefRecommendation";
import { apiFetchAuthorized } from "./http";
function normalizeRecommendations(payload: unknown): ChefRecommendation[] {
  const list = Array.isArray(payload)
    ? payload
    : payload &&
        typeof payload === "object" &&
        Array.isArray((payload as { results?: unknown }).results)
      ? ((payload as { results: ChefRecommendation[] }).results ?? [])
      : [];

  return list;
}

export async function fetchChefRecommendations(
  languageCode: string,
): Promise<ChefRecommendation[]> {
  const params = new URLSearchParams({ lang: languageCode });
  const response = await apiFetchAuthorized(
    `/chef-recommendations/?${params}`,
  );
  if (!response.ok) {
    throw new Error(`Şefin önerileri yüklenemedi (${response.status})`);
  }

  const payload = (await response.json()) as unknown;
  return normalizeRecommendations(payload);
}

export async function fetchChefRecommendationBySlug(
  slug: string,
  languageCode: string,
): Promise<ChefRecommendation | null> {
  const params = new URLSearchParams({ lang: languageCode });
  const response = await apiFetchAuthorized(
    `/chef-recommendations/${encodeURIComponent(slug)}/?${params}`,
  );
  if (response.status === 404) {
    return null;
  }

  if (!response.ok) {
    throw new Error(`Şefin önerisi yüklenemedi (${response.status})`);
  }

  return (await response.json()) as ChefRecommendation;
}
