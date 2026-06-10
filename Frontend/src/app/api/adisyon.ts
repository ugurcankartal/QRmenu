import { ADISYON_SESSION_KEY } from "../config";
import type { Adisyon } from "../types/adisyon";
import { apiFetchAuthorized } from "./http";

const SESSION_HEADER = "X-Session-Key";

function getStoredSessionKey(): string | null {
  try {
    return localStorage.getItem(ADISYON_SESSION_KEY);
  } catch {
    return null;
  }
}

function storeSessionKey(key: string) {
  try {
    localStorage.setItem(ADISYON_SESSION_KEY, key);
  } catch {
    // ignore storage errors
  }
}

async function adisyonRequest(
  path: string,
  languageCode: string,
  options: RequestInit = {},
): Promise<Adisyon> {
  const headers = new Headers(options.headers);

  if (options.body) {
    headers.set("Content-Type", "application/json");
  }

  const sessionKey = getStoredSessionKey();
  if (sessionKey) {
    headers.set(SESSION_HEADER, sessionKey);
  }

  const params = new URLSearchParams({ lang: languageCode });
  const response = await apiFetchAuthorized(`${path}?${params}`, {
    ...options,
    headers,
  });

  const headerKey = response.headers.get(SESSION_HEADER);
  if (headerKey) {
    storeSessionKey(headerKey);
  }

  if (!response.ok) {
    throw new Error(`Adisyon isteği başarısız (${response.status})`);
  }

  const data = (await response.json()) as Adisyon;
  if (data.session_key) {
    storeSessionKey(data.session_key);
  }

  return data;
}

export async function fetchAdisyon(languageCode: string): Promise<Adisyon> {
  return adisyonRequest("/adisyon/", languageCode);
}

export async function toggleAdisyonProduct(
  productId: number,
  languageCode: string,
): Promise<Adisyon & { added?: boolean }> {
  return adisyonRequest("/adisyon/toggle/", languageCode, {
    method: "POST",
    body: JSON.stringify({ product_id: productId }),
  });
}

export async function updateAdisyonItemQuantity(
  itemId: number,
  quantity: number,
  languageCode: string,
): Promise<Adisyon> {
  return adisyonRequest(`/adisyon/items/${itemId}/`, languageCode, {
    method: "PATCH",
    body: JSON.stringify({ quantity }),
  });
}

export async function removeAdisyonItem(
  itemId: number,
  languageCode: string,
): Promise<Adisyon> {
  return adisyonRequest(`/adisyon/items/${itemId}/`, languageCode, {
    method: "DELETE",
  });
}
