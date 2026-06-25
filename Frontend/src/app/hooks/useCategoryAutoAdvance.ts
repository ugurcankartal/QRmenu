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
  CATEGORY_SCROLL_DURATION_MS,
  isSmoothScrolling,
  smoothScrollTo,
} from "../utils/smoothScrollTo";
import {
  getProductGridScrollTarget,
  getRetreatScrollTarget,
  isAtProductGridTop,
} from "../utils/scrollToCategoryNav";

type PendingScroll = "forward" | "retreat" | null;

const TRANSITION_LOCK_MS = CATEGORY_SCROLL_DURATION_MS + 400;

export function useCategoryAutoAdvance(disabled = false) {
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const [rootCategories, setRootCategories] = useState<Category[]>([]);
  const { prepareForCategoryScroll, headerHeight } = useHeaderScroll();
  const advancedFromCategoryRef = useRef<ActiveCategory | null>(null);
  const retreatedFromCategoryRef = useRef<ActiveCategory | null>(null);
  const transitionLockUntilRef = useRef(0);
  const pendingScrollRef = useRef<PendingScroll>(null);
  const retreatFromScrollYRef = useRef(0);

  const lockTransitions = useCallback(() => {
    transitionLockUntilRef.current =
      Date.now() + TRANSITION_LOCK_MS;
  }, []);

  const isScrollBlocked = useCallback(() => {
    return (
      disabled ||
      Date.now() < transitionLockUntilRef.current ||
      isSmoothScrolling()
    );
  }, [disabled]);

  useEffect(() => {
    advancedFromCategoryRef.current = null;
    retreatedFromCategoryRef.current = null;
  }, [selectedCategory]);

  const runPendingScroll = useCallback(() => {
    const pending = pendingScrollRef.current;
    if (!pending) {
      return;
    }

    pendingScrollRef.current = null;

    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        if (pending === "forward") {
          const targetTop = getProductGridScrollTarget(headerHeight);
          prepareForCategoryScroll(targetTop);
          smoothScrollTo(targetTop, lockTransitions);
          return;
        }

        const fromScrollY = retreatFromScrollYRef.current;
        const targetTop = getRetreatScrollTarget(headerHeight, fromScrollY);
        prepareForCategoryScroll(targetTop);
        smoothScrollTo(targetTop, lockTransitions);
      });
    });
  }, [headerHeight, lockTransitions, prepareForCategoryScroll]);

  const onProductsLoadingChange = useCallback(
    (isLoadingProducts: boolean) => {
      if (isLoadingProducts || !pendingScrollRef.current) {
        return;
      }
      runPendingScroll();
    },
    [runPendingScroll],
  );

  const handleRootCategoriesChange = useCallback((roots: Category[]) => {
    setRootCategories(roots);
  }, []);

  const handleCategoryEndReached = useCallback(() => {
    if (isScrollBlocked()) {
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
    pendingScrollRef.current = "forward";
    setSelectedCategory(nextCategoryId);
  }, [
    isScrollBlocked,
    lockTransitions,
    rootCategories,
    selectedCategory,
  ]);

  const handleCategoryStartReached = useCallback(() => {
    if (disabled) {
      return;
    }

    const atGridTop = isAtProductGridTop(headerHeight);
    if (!atGridTop && isScrollBlocked()) {
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
    pendingScrollRef.current = "retreat";
    setSelectedCategory(previousCategoryId);
  }, [
    disabled,
    headerHeight,
    isScrollBlocked,
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
    isScrollBlocked,
  };
}
