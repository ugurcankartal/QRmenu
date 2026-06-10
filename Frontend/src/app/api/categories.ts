import type { Category } from "../types/category";
import { ALL_CATEGORIES, type ActiveCategory } from "../types/categorySelection";
import type { Product } from "../types/product";
import { apiFetchAuthorized } from "./http";

function normalizeCategories(payload: unknown): Category[] {
  const list = Array.isArray(payload)
    ? payload
    : payload &&
        typeof payload === "object" &&
        Array.isArray((payload as { results?: unknown }).results)
      ? ((payload as { results: Category[] }).results ?? [])
      : [];

  return list;
}

export async function fetchCategories(languageCode: string): Promise<Category[]> {
  const params = new URLSearchParams({ lang: languageCode });
  const response = await apiFetchAuthorized(`/categories/?${params}`);

  if (!response.ok) {
    throw new Error(`Kategoriler yüklenemedi (${response.status})`);
  }

  const payload = (await response.json()) as unknown;
  return normalizeCategories(payload);
}

export function getRootCategories(categories: Category[]): Category[] {
  return categories
    .filter((category) => category.parent === null)
    .sort((left, right) => left.order - right.order || left.id - right.id);
}

function getRootCategoryId(
  categories: Category[],
  categoryId: number,
): number | null {
  const byId = new Map(categories.map((category) => [category.id, category]));
  let current = byId.get(categoryId);

  if (!current) {
    return null;
  }

  while (current.parent !== null) {
    const parent = byId.get(current.parent);
    if (!parent) {
      break;
    }
    current = parent;
  }

  return current.id;
}

export function getRootCategoriesForProducts(
  categories: Category[],
  products: Product[],
): Category[] {
  const rootIds = new Set<number>();

  for (const product of products) {
    const rootId = getRootCategoryId(categories, product.category);
    if (rootId !== null) {
      rootIds.add(rootId);
    }
  }

  return getRootCategories(categories).filter((category) =>
    rootIds.has(category.id),
  );
}

export function getCategorySubtreeIds(
  categories: Category[],
  rootId: number,
): Set<number> {
  const childrenByParent = new Map<number, number[]>();

  for (const category of categories) {
    if (category.parent === null) {
      continue;
    }
    const siblings = childrenByParent.get(category.parent) ?? [];
    siblings.push(category.id);
    childrenByParent.set(category.parent, siblings);
  }

  const ids = new Set<number>([rootId]);
  const stack = [rootId];

  while (stack.length > 0) {
    const currentId = stack.pop()!;
    for (const childId of childrenByParent.get(currentId) ?? []) {
      if (!ids.has(childId)) {
        ids.add(childId);
        stack.push(childId);
      }
    }
  }

  return ids;
}

export function filterProductsByCategory(
  products: Product[],
  categories: Category[],
  activeCategory: ActiveCategory,
): Product[] {
  if (activeCategory === ALL_CATEGORIES) {
    return products;
  }

  const allowedCategoryIds = getCategorySubtreeIds(categories, activeCategory);
  return products.filter((product) => allowedCategoryIds.has(product.category));
}
