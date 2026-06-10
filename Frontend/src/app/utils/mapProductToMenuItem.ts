import type { MenuItem } from "../types/menuItem";
import type { Product } from "../types/product";
import { normalizeStringList } from "./normalizeStringList";

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080";

export function mapProductToMenuItem(product: Product): MenuItem {
  return {
    id: String(product.id),
    name: product.name,
    description: product.description,
    price: Number(product.price),
    image: product.image_url || FALLBACK_IMAGE,
    popular: product.is_popular,
    category: product.category_name,
    ingredients: normalizeStringList(product.ingredients),
    allergens: normalizeStringList(product.allergens),
    calories: product.calories ?? undefined,
  };
}
