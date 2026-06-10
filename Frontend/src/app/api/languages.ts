import type { Language } from "../types/language";
import { apiFetchAuthorized } from "./http";

function normalizeLanguages(payload: unknown): Language[] {
  const list = Array.isArray(payload)
    ? payload
    : payload &&
        typeof payload === "object" &&
        Array.isArray((payload as { results?: unknown }).results)
      ? ((payload as { results: Language[] }).results ?? [])
      : [];

  return list
    .filter((language) => language.is_active)
    .sort((left, right) => left.sort_order - right.sort_order);
}

export async function fetchLanguages(): Promise<Language[]> {
  const response = await apiFetchAuthorized("/languages/");

  if (!response.ok) {
    throw new Error(`Diller yüklenemedi (${response.status})`);
  }

  const payload = (await response.json()) as unknown;
  return normalizeLanguages(payload);
}
