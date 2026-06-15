import type { Product } from "../types/product";
import { apiFetchAuthorized } from "./http";

export interface FetchProductsPageOptions {
  languageCode: string;
  page?: number;
  pageSize?: number;
  categoryId?: number;
  search?: string;
}

export interface ProductsPageResult {
  items: Product[];
  hasMore: boolean;
  totalCount: number | null;
}

function extractPage(payload: unknown): ProductsPageResult {
  if (Array.isArray(payload)) {
    return {
      items: payload,
      hasMore: false,
      totalCount: payload.length,
    };
  }

  if (payload && typeof payload === "object") {
    const page = payload as {
      results?: Product[];
      next?: string | null;
      count?: number;
    };
    return {
      items: page.results ?? [],
      hasMore: Boolean(page.next),
      totalCount: typeof page.count === "number" ? page.count : null,
    };
  }

  return { items: [], hasMore: false, totalCount: 0 };
}

export async function fetchProductsPage(
  options: FetchProductsPageOptions,
): Promise<ProductsPageResult> {
  const params = new URLSearchParams({
    lang: options.languageCode,
    available: "1",
    page: String(options.page ?? 1),
  });

  if (options.pageSize) {
    params.set("page_size", String(options.pageSize));
  }
  if (options.categoryId) {
    params.set("category", String(options.categoryId));
  }
  if (options.search) {
    params.set("q", options.search);
  }

  const response = await apiFetchAuthorized(`/products/?${params}`);

  if (!response.ok) {
    throw new Error(`Ürünler yüklenemedi (${response.status})`);
  }

  const payload = (await response.json()) as unknown;
  return extractPage(payload);
}

export async function fetchProducts(languageCode: string): Promise<Product[]> {
  const allProducts: Product[] = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const { items, hasMore: nextPage } = await fetchProductsPage({
      languageCode,
      page,
      pageSize: 30,
    });
    allProducts.push(...items);
    hasMore = nextPage;
    page += 1;
  }

  return allProducts;
}
