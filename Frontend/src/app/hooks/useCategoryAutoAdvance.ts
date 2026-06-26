import { useCallback, useEffect, useRef, useState } from "react";

import { useCategoryScroll } from "../context/CategoryScrollContext";
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
} from "../utils/gsapScroll";

export type CategoryScrollIntent = "forward" | "retreat" | null;

const TRANSITION_LOCK_MS = CATEGORY_SCROLL_DURATION_MS + 400;

function resolveScrollIntent(
  categories: Category[],
  from: ActiveCategory,
  to: ActiveCategory,
): CategoryScrollIntent {
  if (categories.length === 0 || from === to) {
    return null;
  }

  const fromIndex =
    from === ALL_CATEGORIES
      ? -1
      : categories.findIndex((item) => item.id === from);
  const toIndex = categories.findIndex((item) => item.id === to);

  if (toIndex === -1) {
    return null;
  }

  if (fromIndex === -1 || toIndex > fromIndex) {
    return "forward";
  }

  if (toIndex < fromIndex) {
    return "retreat";
  }

  return null;
}

export function useCategoryAutoAdvance(disabled = false) {
  const [selectedCategory, setSelectedCategoryState] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const [scrollIntent, setScrollIntent] = useState<CategoryScrollIntent>(null);
  const [rootCategories, setRootCategories] = useState<Category[]>([]);
  const { isScrollAtTop } = useCategoryScroll();
  const advancedFromCategoryRef = useRef<ActiveCategory | null>(null);
  const retreatedFromCategoryRef = useRef<ActiveCategory | null>(null);
  const transitionLockUntilRef = useRef(0);

  const lockTransitions = useCallback(() => {
    transitionLockUntilRef.current = Date.now() + TRANSITION_LOCK_MS;
  }, []);

  const isScrollBlocked = useCallback(() => {
    return (
      disabled ||
      Date.now() < transitionLockUntilRef.current ||
      isSmoothScrolling()
    );
  }, [disabled]);

  const clearScrollIntent = useCallback(() => {
    setScrollIntent(null);
  }, []);

  useEffect(() => {
    advancedFromCategoryRef.current = null;
    retreatedFromCategoryRef.current = null;
  }, [selectedCategory]);

  const changeCategory = useCallback(
    (category: ActiveCategory, intent: CategoryScrollIntent) => {
      if (category === selectedCategory) {
        return;
      }

      if (intent) {
        setScrollIntent(intent);
      }

      setSelectedCategoryState(category);
    },
    [selectedCategory],
  );

  const handleRootCategoriesChange = useCallback((roots: Category[]) => {
    setRootCategories(roots);
  }, []);

  const selectCategory = useCallback(
    (category: ActiveCategory) => {
      if (category === selectedCategory) {
        return;
      }

      const intent = resolveScrollIntent(
        rootCategories,
        selectedCategory,
        category,
      );
      changeCategory(category, intent);
    },
    [changeCategory, rootCategories, selectedCategory],
  );

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
    changeCategory(nextCategoryId, "forward");
  }, [
    changeCategory,
    isScrollBlocked,
    lockTransitions,
    rootCategories,
    selectedCategory,
  ]);

  const handleCategoryStartReached = useCallback(() => {
    if (disabled) {
      return;
    }

    if (!isScrollAtTop() && isScrollBlocked()) {
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
    changeCategory(previousCategoryId, "retreat");
  }, [
    changeCategory,
    disabled,
    isScrollAtTop,
    isScrollBlocked,
    lockTransitions,
    rootCategories,
    selectedCategory,
  ]);

  return {
    selectedCategory,
    setSelectedCategory: selectCategory,
    scrollIntent,
    clearScrollIntent,
    lockTransitions,
    handleRootCategoriesChange,
    handleCategoryEndReached,
    handleCategoryStartReached,
    isScrollBlocked,
  };
}
