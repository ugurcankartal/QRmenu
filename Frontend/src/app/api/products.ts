import type { Product } from "../types/product";
import { apiFetchAuthorized } from "./http";

function extractPage(payload: unknown): {
  items: Product[];
  hasMore: boolean;
} {
  if (Array.isArray(payload)) {
    return { items: payload, hasMore: false };
  }

  if (payload && typeof payload === "object") {
    const page = payload as {
      results?: Product[];
      next?: string | null;
    };
    return {
      items: page.results ?? [],
      hasMore: Boolean(page.next),
    };
  }

  return { items: [], hasMore: false };
}

export async function fetchProducts(languageCode: string): Promise<Product[]> {
  const allProducts: Product[] = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const params = new URLSearchParams({
      lang: languageCode,
      available: "1",
      page: String(page),
    });
    const response = await apiFetchAuthorized(`/products/?${params}`);

    if (!response.ok) {
      throw new Error(`Ürünler yüklenemedi (${response.status})`);
    }

    const payload = (await response.json()) as unknown;
    const { items, hasMore: nextPage } = extractPage(payload);
    allProducts.push(...items);
    hasMore = nextPage;
    page += 1;
  }

  return allProducts;
}
