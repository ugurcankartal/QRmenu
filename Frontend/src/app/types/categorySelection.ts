export const ALL_CATEGORIES = "all" as const;

export type ActiveCategory = typeof ALL_CATEGORIES | number;
