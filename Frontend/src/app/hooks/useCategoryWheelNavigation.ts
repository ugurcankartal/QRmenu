import { useEffect, useRef } from "react";

import { useCategoryScroll } from "../context/CategoryScrollContext";
import type { Category } from "../types/category";
import {
  isFirstRootCategory,
  isLastRootCategory,
} from "../utils/categoryNavigation";
import type { ActiveCategory } from "../types/categorySelection";

const SCROLL_EDGE_TOLERANCE_PX = 2;

interface UseCategoryWheelNavigationOptions {
  disabled?: boolean;
  isScrollBlocked?: () => boolean;
  rootCategories: Category[];
  selectedCategory: ActiveCategory;
  hasMore?: boolean;
  isLoadingMore?: boolean;
  isLoading?: boolean;
  onAdvance: () => void;
  onRetreat: () => void;
}

function isAtScrollTop(container: HTMLElement): boolean {
  return container.scrollTop <= SCROLL_EDGE_TOLERANCE_PX;
}

function isAtScrollBottom(container: HTMLElement): boolean {
  return (
    container.scrollTop + container.clientHeight >=
    container.scrollHeight - SCROLL_EDGE_TOLERANCE_PX
  );
}

function canScrollInternally(container: HTMLElement): boolean {
  return (
    container.scrollHeight >
    container.clientHeight + SCROLL_EDGE_TOLERANCE_PX
  );
}

function scrollPageBy(deltaY: number): void {
  window.scrollBy({ top: deltaY, behavior: "auto" });
}

export function useCategoryWheelNavigation({
  disabled = false,
  isScrollBlocked,
  rootCategories,
  selectedCategory,
  hasMore = false,
  isLoadingMore = false,
  isLoading = false,
  onAdvance,
  onRetreat,
}: UseCategoryWheelNavigationOptions) {
  const { scrollContainerRef, scrollContainerReady } = useCategoryScroll();
  const onAdvanceRef = useRef(onAdvance);
  const onRetreatRef = useRef(onRetreat);
  const isScrollBlockedRef = useRef(isScrollBlocked);

  onAdvanceRef.current = onAdvance;
  onRetreatRef.current = onRetreat;
  isScrollBlockedRef.current = isScrollBlocked;

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }

    const handleWheel = (event: WheelEvent) => {
      if (disabled) {
        return;
      }

      const { deltaY } = event;
      if (deltaY === 0) {
        return;
      }

      const scrollable = canScrollInternally(container);
      const atTop = isAtScrollTop(container);
      const atBottom = isAtScrollBottom(container);
      const isFirstCategory = isFirstRootCategory(
        rootCategories,
        selectedCategory,
      );
      const isLastCategory = isLastRootCategory(
        rootCategories,
        selectedCategory,
      );
      const isMiddleCategory = !isFirstCategory && !isLastCategory;

      if (scrollable) {
        if (deltaY > 0 && !atBottom) {
          return;
        }
        if (deltaY < 0 && !atTop) {
          return;
        }
      }

      if (isLoading || isScrollBlockedRef.current?.()) {
        if (isMiddleCategory) {
          event.preventDefault();
          event.stopPropagation();
        }
        return;
      }

      if (deltaY > 0) {
        if (hasMore || isLoadingMore) {
          event.preventDefault();
          event.stopPropagation();
          return;
        }

        if (isMiddleCategory || !isLastCategory) {
          event.preventDefault();
          event.stopPropagation();
          onAdvanceRef.current();
          return;
        }

        if (isLastCategory && (atBottom || !scrollable)) {
          event.preventDefault();
          scrollPageBy(deltaY);
        }
        return;
      }

      if (isMiddleCategory || !isFirstCategory) {
        event.preventDefault();
        event.stopPropagation();
        onRetreatRef.current();
        return;
      }

      if (isFirstCategory && (atTop || !scrollable)) {
        event.preventDefault();
        scrollPageBy(deltaY);
      }
    };

    container.addEventListener("wheel", handleWheel, { passive: false });
    return () => container.removeEventListener("wheel", handleWheel);
  }, [
    disabled,
    hasMore,
    isLoading,
    isLoadingMore,
    rootCategories,
    scrollContainerReady,
    scrollContainerRef,
    selectedCategory,
  ]);
}
