import { useCallback, useEffect, useRef, useState } from "react";

import { useHeaderScroll } from "../context/HeaderScrollContext";
import type { Category } from "../types/category";
import {
  getNextCategoryId,
  getPreviousCategoryId,
} from "../utils/categoryNavigation";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";
import {
  getProductGridScrollTarget,
  scrollToRetreatTarget,
} from "../utils/scrollToCategoryNav";
import { isAtProductGridTop } from "./useProductGridTopRetreat";

const TRANSITION_LOCK_MS = 1200;

export function useCategoryAutoAdvance(disabled = false) {
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const [rootCategories, setRootCategories] = useState<Category[]>([]);
  const { prepareForCategoryScroll, headerHeight } = useHeaderScroll();
  const advancedFromCategoryRef = useRef<ActiveCategory | null>(null);
  const retreatedFromCategoryRef = useRef<ActiveCategory | null>(null);
  const transitionLockUntilRef = useRef(0);
  const pendingReverseScrollRef = useRef(false);
  const retreatFromScrollYRef = useRef(0);

  const lockTransitions = useCallback(() => {
    transitionLockUntilRef.current = Date.now() + TRANSITION_LOCK_MS;
  }, []);

  const isTransitionLocked = useCallback(() => {
    return Date.now() < transitionLockUntilRef.current;
  }, []);

  useEffect(() => {
    advancedFromCategoryRef.current = null;
    retreatedFromCategoryRef.current = null;
  }, [selectedCategory]);

  const onProductsLoadingChange = useCallback(
    (isLoadingProducts: boolean) => {
      if (!pendingReverseScrollRef.current || isLoadingProducts) {
        return;
      }

      pendingReverseScrollRef.current = false;
      const fromScrollY = retreatFromScrollYRef.current;
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          prepareForCategoryScroll(
            getProductGridScrollTarget(headerHeight),
          );
          scrollToRetreatTarget(fromScrollY, headerHeight);
        });
      });
    },
    [headerHeight, prepareForCategoryScroll],
  );

  const handleRootCategoriesChange = useCallback((roots: Category[]) => {
    setRootCategories(roots);
  }, []);

  const handleCategoryEndReached = useCallback(() => {
    if (disabled || isTransitionLocked()) {
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
    lockTransitions();
    setSelectedCategory(nextCategoryId);

    requestAnimationFrame(() => {
      const targetTop = getProductGridScrollTarget(headerHeight);
      prepareForCategoryScroll(targetTop);
      window.scrollTo({ top: targetTop, behavior: "auto" });
    });
  }, [
    disabled,
    headerHeight,
    isTransitionLocked,
    lockTransitions,
    prepareForCategoryScroll,
    rootCategories,
    selectedCategory,
  ]);

  const handleCategoryStartReached = useCallback(() => {
    if (disabled) {
      return;
    }

    const atGridTop = isAtProductGridTop(headerHeight);
    if (!atGridTop && isTransitionLocked()) {
      return;
    }

    if (retreatedFromCategoryRef.current === selectedCategory) {
      return;
    }

    const previousCategoryId = getPreviousCategoryId(
      rootCategories,
      selectedCategory,
    );
    if (previousCategoryId === null) {
      return;
    }

    retreatedFromCategoryRef.current = selectedCategory;
    lockTransitions();
    retreatFromScrollYRef.current = window.scrollY;
    pendingReverseScrollRef.current = true;
    setSelectedCategory(previousCategoryId);
  }, [
    disabled,
    headerHeight,
    isTransitionLocked,
    lockTransitions,
    rootCategories,
    selectedCategory,
  ]);

  return {
    selectedCategory,
    setSelectedCategory,
    handleRootCategoriesChange,
    handleCategoryEndReached,
    handleCategoryStartReached,
    onProductsLoadingChange,
  };
}
