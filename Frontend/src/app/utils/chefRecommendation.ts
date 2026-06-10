import type { ChefRecommendation } from "../types/chefRecommendation";
import type { Product } from "../types/product";

export function getRecommendationProducts(
  recommendation: ChefRecommendation,
): Product[] {
  return [...recommendation.product_links]
    .sort((a, b) => a.order - b.order || a.id - b.id)
    .map((link) => link.product)
    .filter(Boolean);
}

export function getFeaturedProduct(
  recommendation: ChefRecommendation,
): Product | null {
  const products = getRecommendationProducts(recommendation);
  return products[0] ?? null;
}
