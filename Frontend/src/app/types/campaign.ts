import type { Product } from "./product";

export interface Campaign {
  id: number;
  name: string;
  slug: string;
  description: string;
  badge: string;
  image_url: string | null;
  is_active: boolean;
  priority: number;
  product_ids: number[];
  products: Product[];
}
