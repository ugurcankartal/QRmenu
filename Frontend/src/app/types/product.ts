export interface Product {
  id: number;
  name: string;
  slug: string;
  description: string;
  ingredients: string[];
  allergens: string[];
  price: string;
  currency_code: string | null;
  currency_symbol: string | null;
  image_url: string | null;
  is_available: boolean;
  is_popular: boolean;
  is_popular_choice: boolean;
  calories: number | null;
  prep_time: number | null;
  category: number;
  category_name: string;
}
