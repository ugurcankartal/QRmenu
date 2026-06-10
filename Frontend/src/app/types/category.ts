export interface Category {
  id: number;
  name: string;
  title: string;
  slug: string;
  description: string;
  image_url: string | null;
  parent: number | null;
  children: number[];
  order: number;
  level: number;
}
