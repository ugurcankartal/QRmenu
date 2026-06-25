import { useEffect, useState } from "react";
import { motion } from "motion/react";

import {
  fetchCategories,
  getRootCategories,
  getRootCategoriesForProducts,
} from "../api/categories";
import type { Product } from "../types/product";
import { useLanguage } from "../context/LanguageContext";
import type { Category } from "../types/category";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";

interface CategoryNavProps {
  selectedCategory?: ActiveCategory;
  onCategoryChange?: (category: ActiveCategory) => void;
  onCategoriesLoaded?: (categories: Category[]) => void;
  onRootCategoriesChange?: (categories: Category[]) => void;
  products?: Product[];
}

export function CategoryNav({
  selectedCategory: selectedCategoryProp,
  onCategoryChange,
  onCategoriesLoaded,
  onRootCategoriesChange,
  products,
}: CategoryNavProps) {
  const { languageCode } = useLanguage();
  const [allCategories, setAllCategories] = useState<Category[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [internalCategory, setInternalCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const [isLoading, setIsLoading] = useState(true);

  const isControlled = selectedCategoryProp !== undefined;
  const activeCategory = isControlled ? selectedCategoryProp : internalCategory;

  const setActiveCategory = (category: ActiveCategory) => {
    if (!isControlled) {
      setInternalCategory(category);
    }
    onCategoryChange?.(category);
  };

  useEffect(() => {
    let cancelled = false;

    async function loadCategories() {
      setIsLoading(true);
      try {
        const data = await fetchCategories(languageCode);
        if (!cancelled) {
          setAllCategories(data);
          if (!isControlled) {
            setInternalCategory(ALL_CATEGORIES);
          }
        }
      } catch {
        if (!cancelled) {
          setAllCategories([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadCategories();

    return () => {
      cancelled = true;
    };
  }, [languageCode]);

  useEffect(() => {
    const roots =
      products && products.length > 0
        ? getRootCategoriesForProducts(allCategories, products)
        : getRootCategories(allCategories);

    setCategories(roots);
    onCategoriesLoaded?.(allCategories);
    onRootCategoriesChange?.(roots);

    if (roots.length > 0 && activeCategory === ALL_CATEGORIES) {
      setActiveCategory(roots[0].id);
    }
  }, [allCategories, products, activeCategory]);

  if (isLoading) {
    return (
      <div className="border-b border-white/10 bg-dark-graphite/95 backdrop-blur-xl">
        <div className="flex gap-2 overflow-x-auto px-4 py-4 scrollbar-hide">
          {Array.from({ length: 5 }).map((_, index) => (
            <div
              key={index}
              className="h-10 w-24 flex-shrink-0 animate-pulse rounded-full bg-white/10"
            />
          ))}
        </div>
      </div>
    );
  }

  if (categories.length === 0) {
    return null;
  }

  return (
    <div className="border-b border-white/10 bg-dark-graphite/95 backdrop-blur-xl">
      <div
        className="flex gap-2 overflow-x-auto px-4 py-4 scrollbar-hide"
        style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
      >
        {categories.map((category) => {
          const isActive = activeCategory === category.id;
          return (
            <button
              key={category.id}
              type="button"
              onClick={() => setActiveCategory(category.id)}
              className="relative flex-shrink-0 rounded-full px-6 py-2.5 transition-all"
            >
              {isActive && (
                <motion.div
                  layoutId="categoryIndicator"
                  className="absolute inset-0 rounded-full bg-copper-gold"
                  transition={{ type: "spring", damping: 20, stiffness: 300 }}
                />
              )}
              <span
                className={`relative z-10 whitespace-nowrap text-sm font-medium transition-colors ${
                  isActive ? "text-charcoal-black" : "text-warm-cream/70"
                }`}
              >
                {category.name}
              </span>
            </button>
          );
        })}
      </div>
    </div>
  );
}
