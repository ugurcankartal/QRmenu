import { motion } from "motion/react";
import { CategoryNav } from "./CategoryNav";
import { useHeaderScroll } from "../context/HeaderScrollContext";
import type { Category } from "../types/category";
import type { ActiveCategory } from "../types/categorySelection";
import type { Product } from "../types/product";

interface StickyCategoryNavProps {
  selectedCategory?: ActiveCategory;
  onCategoryChange?: (category: ActiveCategory) => void;
  onCategoriesLoaded?: (categories: Category[]) => void;
  products?: Product[];
}

export function StickyCategoryNav({
  selectedCategory,
  onCategoryChange,
  onCategoriesLoaded,
  products,
}: StickyCategoryNavProps) {
  const { isHeaderVisible, headerHeight } = useHeaderScroll();

  return (
    <motion.div
      className="sticky z-30"
      animate={{ top: isHeaderVisible ? headerHeight : 0 }}
      transition={{ duration: 0.3, ease: "easeInOut" }}
    >
      <CategoryNav
        selectedCategory={selectedCategory}
        onCategoryChange={onCategoryChange}
        onCategoriesLoaded={onCategoriesLoaded}
        products={products}
      />
    </motion.div>
  );
}
