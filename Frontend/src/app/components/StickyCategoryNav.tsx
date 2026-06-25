import { useRef } from "react";
import { motion } from "motion/react";
import { CategoryNav } from "./CategoryNav";
import { useHeaderScroll } from "../context/HeaderScrollContext";
import {
  getCategoryChangeScrollTarget,
  scrollOnCategoryChange,
} from "../utils/scrollToCategoryNav";
import type { Category } from "../types/category";
import type { ActiveCategory } from "../types/categorySelection";
import type { Product } from "../types/product";

interface StickyCategoryNavProps {
  selectedCategory?: ActiveCategory;
  onCategoryChange?: (category: ActiveCategory) => void;
  onCategoriesLoaded?: (categories: Category[]) => void;
  onRootCategoriesChange?: (categories: Category[]) => void;
  products?: Product[];
}

export function StickyCategoryNav({
  selectedCategory,
  onCategoryChange,
  onCategoriesLoaded,
  onRootCategoriesChange,
  products,
}: StickyCategoryNavProps) {
  const previousCategory = useRef<ActiveCategory | undefined>(undefined);
  const { isHeaderVisible, headerHeight, prepareForCategoryScroll, isHeaderMotionInstant } =
    useHeaderScroll();
  const stickyTransition = isHeaderMotionInstant
    ? { duration: 0 }
    : { duration: 0.3, ease: "easeInOut" as const };

  const handleCategoryChange = (category: ActiveCategory) => {
    const isUserChange =
      previousCategory.current !== undefined &&
      previousCategory.current !== category;
    previousCategory.current = category;

    onCategoryChange?.(category);

    if (isUserChange) {
      const targetTop = getCategoryChangeScrollTarget();
      prepareForCategoryScroll(targetTop);
      scrollOnCategoryChange(targetTop);
    }
  };

  return (
    <motion.div
      className="sticky z-30"
      animate={{ top: isHeaderVisible ? headerHeight : 0 }}
      transition={stickyTransition}
    >
      <CategoryNav
        selectedCategory={selectedCategory}
        onCategoryChange={handleCategoryChange}
        onCategoriesLoaded={onCategoriesLoaded}
        onRootCategoriesChange={onRootCategoriesChange}
        products={products}
      />
    </motion.div>
  );
}
