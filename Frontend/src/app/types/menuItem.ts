export interface MenuItem {
  id: string;
  name: string;
  description: string;
  price: number;
  image: string;
  popular?: boolean;
  category: string;
  ingredients?: string[];
  allergens?: string[];
  calories?: number;
}
