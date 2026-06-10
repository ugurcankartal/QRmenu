import type { Product } from "./product";

export interface ChefRecommendationProductLink {
  id: number;
  order: number;
  product: Product;
}

export interface ChefRecommendation {
  id: number;
  title: string;
  summary: string;
  slug: string;
  description: string;
  image_url: string | null;
  product_links: ChefRecommendationProductLink[];
}
