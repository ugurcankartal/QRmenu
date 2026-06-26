import type { Category } from "../types/category";
import {
  isFirstRootCategory,
  isLastRootCategory,
} from "./categoryNavigation";
import type { ActiveCategory } from "../types/categorySelection";

export const SCROLL_EDGE_TOLERANCE_PX = 2;
export const TOUCH_SWIPE_THRESHOLD_PX = 52;

export type CategoryPanelBoundaryAction =
  | { type: "native" }
  | { type: "block" }
  | { type: "advance" }
  | { type: "retreat" }
  | { type: "scroll-page"; deltaY: number };

export interface CategoryPanelBoundaryContext {
  disabled?: boolean;
  isLoading?: boolean;
  isScrollBlocked?: () => boolean;
  rootCategories: Category[];
  selectedCategory: ActiveCategory;
  hasMore?: boolean;
  isLoadingMore?: boolean;
}

export function isAtScrollTop(container: HTMLElement): boolean {
  return container.scrollTop <= SCROLL_EDGE_TOLERANCE_PX;
}

export function isAtScrollBottom(container: HTMLElement): boolean {
  return (
    container.scrollTop + container.clientHeight >=
    container.scrollHeight - SCROLL_EDGE_TOLERANCE_PX
  );
}

export function canScrollInternally(container: HTMLElement): boolean {
  return (
    container.scrollHeight >
    container.clientHeight + SCROLL_EDGE_TOLERANCE_PX
  );
}

/** deltaY > 0: aşağı / içerik yukarı kayar (tekerlek aşağı, parmak yukarı). */
export function resolveCategoryPanelBoundaryAction(
  deltaY: number,
  container: HTMLElement,
  context: CategoryPanelBoundaryContext,
): CategoryPanelBoundaryAction {
  if (context.disabled || deltaY === 0) {
    return { type: "native" };
  }

  const scrollable = canScrollInternally(container);
  const atTop = isAtScrollTop(container);
  const atBottom = isAtScrollBottom(container);
  const isFirstCategory = isFirstRootCategory(
    context.rootCategories,
    context.selectedCategory,
  );
  const isLastCategory = isLastRootCategory(
    context.rootCategories,
    context.selectedCategory,
  );
  const isMiddleCategory = !isFirstCategory && !isLastCategory;

  if (scrollable) {
    if (deltaY > 0 && !atBottom) {
      return { type: "native" };
    }
    if (deltaY < 0 && !atTop) {
      return { type: "native" };
    }
  }

  if (context.isLoading || context.isScrollBlocked?.()) {
    return isMiddleCategory ? { type: "block" } : { type: "native" };
  }

  if (deltaY > 0) {
    if (context.hasMore || context.isLoadingMore) {
      return { type: "block" };
    }

    if (isMiddleCategory || !isLastCategory) {
      return { type: "advance" };
    }

    if (isLastCategory && (atBottom || !scrollable)) {
      return { type: "scroll-page", deltaY };
    }

    return { type: "native" };
  }

  if (isMiddleCategory || !isFirstCategory) {
    return { type: "retreat" };
  }

  if (isFirstCategory && (atTop || !scrollable)) {
    return { type: "scroll-page", deltaY };
  }

  return { type: "native" };
}

export function scrollPageBy(deltaY: number): void {
  window.scrollBy({ top: deltaY, behavior: "auto" });
}
