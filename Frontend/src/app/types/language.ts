export interface Language {
  id: number;
  code: string;
  name_native: string;
  flag_url: string | null;
  is_active: boolean;
  is_default: boolean;
  sort_order: number;
}
