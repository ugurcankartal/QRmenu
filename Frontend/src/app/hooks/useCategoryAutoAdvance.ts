import { useCallback, useEffect, useRef, useState } from "react";

import { useHeaderScroll } from "../context/HeaderScrollContext";
import type { Category } from "../types/category";
import { getNextCategoryId } from "../utils/categoryNavigation";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";
import {
  getProductGridScrollTarget,
  scrollToProductGrid,
} from "../utils/scrollToCategoryNav";

export function useCategoryAutoAdvance(disabled = false) {
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const [rootCategories, setRootCategories] = useState<Category[]>([]);
  const { prepareForCategoryScroll, headerHeight } = useHeaderScroll();
  const advancedFromCategoryRef = useRef<ActiveCategory | null>(null);

  useEffect(() => {
    advancedFromCategoryRef.current = null;
  }, [selectedCategory]);

  const handleRootCategoriesChange = useCallback((roots: Category[]) => {
    setRootCategories(roots);
  }, []);

  const handleCategoryEndReached = useCallback(() => {
    if (disabled) {
      return;
    }

    if (advancedFromCategoryRef.current === selectedCategory) {
      return;
    }

    const nextCategoryId = getNextCategoryId(rootCategories, selectedCategory);
    if (nextCategoryId === null) {
      return;
    }

    advancedFromCategoryRef.current = selectedCategory;
    setSelectedCategory(nextCategoryId);

    requestAnimationFrame(() => {
      const targetTop = getProductGridScrollTarget(headerHeight);
      prepareForCategoryScroll(targetTop);
      scrollToProductGrid(targetTop);
    });
  }, [
    disabled,
    headerHeight,
    prepareForCategoryScroll,
    rootCategories,
    selectedCategory,
  ]);

  return {
    selectedCategory,
    setSelectedCategory,
    handleRootCategoriesChange,
    handleCategoryEndReached,
  };
}
