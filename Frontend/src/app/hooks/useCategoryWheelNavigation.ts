import { useEffect, useRef } from "react";

import { useCategoryScroll } from "../context/CategoryScrollContext";
import type { Category } from "../types/category";
import type { ActiveCategory } from "../types/categorySelection";
import {
  isAtScrollBottom,
  isAtScrollTop,
  resolveCategoryPanelBoundaryAction,
  scrollPageBy,
  TOUCH_SWIPE_THRESHOLD_PX,
  type CategoryPanelBoundaryContext,
} from "../utils/categoryPanelBoundary";

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

function applyBoundaryAction(
  action: ReturnType<typeof resolveCategoryPanelBoundaryAction>,
  event: Event | null,
  onAdvance: () => void,
  onRetreat: () => void,
): boolean {
  switch (action.type) {
    case "native":
      return false;
    case "block":
      event?.preventDefault();
      event?.stopPropagation();
      return true;
    case "advance":
      event?.preventDefault();
      event?.stopPropagation();
      onAdvance();
      return true;
    case "retreat":
      event?.preventDefault();
      event?.stopPropagation();
      onRetreat();
      return true;
    case "scroll-page":
      event?.preventDefault();
      scrollPageBy(action.deltaY);
      return true;
    default:
      return false;
  }
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
  const contextRef = useRef<CategoryPanelBoundaryContext>({
    disabled,
    isLoading,
    isScrollBlocked,
    rootCategories,
    selectedCategory,
    hasMore,
    isLoadingMore,
  });

  onAdvanceRef.current = onAdvance;
  onRetreatRef.current = onRetreat;
  isScrollBlockedRef.current = isScrollBlocked;
  contextRef.current = {
    disabled,
    isLoading,
    isScrollBlocked: isScrollBlockedRef.current,
    rootCategories,
    selectedCategory,
    hasMore,
    isLoadingMore,
  };

  useEffect(() => {
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }

    const getContext = () => ({
      ...contextRef.current,
      isScrollBlocked: isScrollBlockedRef.current,
    });

    const handleWheel = (event: WheelEvent) => {
      const action = resolveCategoryPanelBoundaryAction(
        event.deltaY,
        container,
        getContext(),
      );
      applyBoundaryAction(action, event, onAdvanceRef.current, onRetreatRef.current);
    };

    let touchStartY = 0;
    let touchLastY = 0;
    let boundaryGestureHandled = false;

    const handleTouchStart = (event: TouchEvent) => {
      if (event.touches.length !== 1) {
        return;
      }
      touchStartY = event.touches[0].clientY;
      touchLastY = touchStartY;
      boundaryGestureHandled = false;
    };

    const handleTouchMove = (event: TouchEvent) => {
      if (event.touches.length !== 1) {
        return;
      }

      const currentY = event.touches[0].clientY;
      const deltaY = touchLastY - currentY;
      touchLastY = currentY;

      if (deltaY === 0) {
        return;
      }

      const action = resolveCategoryPanelBoundaryAction(
        deltaY,
        container,
        getContext(),
      );

      if (action.type === "advance" || action.type === "retreat") {
        event.preventDefault();
        return;
      }

      applyBoundaryAction(
        action,
        event,
        onAdvanceRef.current,
        onRetreatRef.current,
      );
    };

    const handleTouchEnd = (event: TouchEvent) => {
      if (boundaryGestureHandled || event.changedTouches.length !== 1) {
        return;
      }

      const endY = event.changedTouches[0].clientY;
      const totalDeltaY = touchStartY - endY;

      if (Math.abs(totalDeltaY) < TOUCH_SWIPE_THRESHOLD_PX) {
        return;
      }

      const atTop = isAtScrollTop(container);
      const atBottom = isAtScrollBottom(container);

      if (totalDeltaY > 0 && !atBottom) {
        return;
      }
      if (totalDeltaY < 0 && !atTop) {
        return;
      }

      const action = resolveCategoryPanelBoundaryAction(
        totalDeltaY,
        container,
        getContext(),
      );

      if (action.type === "advance" || action.type === "retreat") {
        boundaryGestureHandled = applyBoundaryAction(
          action,
          event,
          onAdvanceRef.current,
          onRetreatRef.current,
        );
      }
    };

    container.addEventListener("wheel", handleWheel, { passive: false });
    container.addEventListener("touchstart", handleTouchStart, {
      passive: true,
    });
    container.addEventListener("touchmove", handleTouchMove, { passive: false });
    container.addEventListener("touchend", handleTouchEnd, { passive: false });
    container.addEventListener("touchcancel", handleTouchEnd, { passive: false });

    return () => {
      container.removeEventListener("wheel", handleWheel);
      container.removeEventListener("touchstart", handleTouchStart);
      container.removeEventListener("touchmove", handleTouchMove);
      container.removeEventListener("touchend", handleTouchEnd);
      container.removeEventListener("touchcancel", handleTouchEnd);
    };
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
