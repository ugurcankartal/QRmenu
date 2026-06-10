import type { Product } from "./product";

export interface AdisyonItem {
  id: number;
  quantity: number;
  order: number;
  price: string;
  discounted_price: string;
  campaign_rule: number | null;
  campaign_badge: string;
  currency: number | null;
  currency_code: string | null;
  currency_symbol: string | null;
  amount: string;
  total_price: string;
  product: Product;
}

export interface Adisyon {
  id: number;
  session_key: string;
  expires_at: string;
  items: AdisyonItem[];
  product_ids: number[];
  total_price: string;
  discounted_total_price: string;
  currency: number | null;
  currency_code: string | null;
  currency_symbol: string | null;
  updated_at: string;
}
