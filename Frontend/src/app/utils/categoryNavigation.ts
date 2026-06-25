import type { Category } from "../types/category";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";

export function getNextCategoryId(
  categories: Category[],
  current: ActiveCategory,
): number | null {
  if (categories.length === 0) {
    return null;
  }

  if (current === ALL_CATEGORIES) {
    return categories.length > 1 ? categories[1].id : null;
  }

  const index = categories.findIndex((category) => category.id === current);
  if (index === -1) {
    return null;
  }

  if (index >= categories.length - 1) {
    return null;
  }

  return categories[index + 1].id;
}

export function getPreviousCategoryId(
  categories: Category[],
  current: ActiveCategory,
): number | null {
  if (categories.length === 0 || current === ALL_CATEGORIES) {
    return null;
  }

  const index = categories.findIndex((category) => category.id === current);
  if (index <= 0) {
    return null;
  }

  return categories[index - 1].id;
}
