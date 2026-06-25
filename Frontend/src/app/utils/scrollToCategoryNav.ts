import { HEADER_HEIGHT } from "../context/HeaderScrollContext";
import { smoothScrollTo } from "./smoothScrollTo";

const CAMPAIGN_SELECTOR = "[data-campaign-hero]";
const PRODUCT_GRID_SELECTOR = "[data-product-grid]";

/** Sticky kategori şeridi yaklaşık yüksekliği (px). */
const STICKY_CATEGORY_NAV_HEIGHT = 72;

/** Grid üst scroll hedefiyle piksel toleransı. */
export const GRID_TOP_TOLERANCE_PX = 20;

export function getCategoryChangeScrollTarget(): number {
  const campaignSection = document.querySelector(CAMPAIGN_SELECTOR);
  if (!campaignSection) {
    return 0;
  }

  const rect = campaignSection.getBoundingClientRect();
  return Math.max(0, rect.bottom + window.scrollY - HEADER_HEIGHT);
}

export function getProductGridScrollTarget(
  headerHeight = HEADER_HEIGHT,
): number {
  const grid = document.querySelector(PRODUCT_GRID_SELECTOR);
  if (!grid) {
    return getCategoryChangeScrollTarget();
  }

  const rect = grid.getBoundingClientRect();
  const offset = headerHeight + STICKY_CATEGORY_NAV_HEIGHT;
  return Math.max(0, rect.top + window.scrollY - offset);
}

export function isAtProductGridTop(headerHeight = HEADER_HEIGHT): boolean {
  const gridTop = getProductGridScrollTarget(headerHeight);
  return Math.abs(window.scrollY - gridTop) <= GRID_TOP_TOLERANCE_PX;
}

export function scrollOnCategoryChange(targetTop?: number) {
  smoothScrollTo(targetTop ?? getCategoryChangeScrollTarget());
}

export function scrollToProductGrid(targetTop?: number) {
  smoothScrollTo(targetTop ?? getProductGridScrollTarget());
}

export function getProductGridBottomScrollTarget(
  headerHeight = HEADER_HEIGHT,
): number {
  const grid = document.querySelector(PRODUCT_GRID_SELECTOR);
  if (!grid) {
    return getProductGridScrollTarget(headerHeight);
  }

  const endBuffer = grid.querySelector("[data-category-end-buffer]");
  const bottomElement = endBuffer ?? grid;
  const rect = bottomElement.getBoundingClientRect();
  const bottomDoc = rect.bottom + window.scrollY;
  const bottomPadding = 96;
  return Math.max(0, bottomDoc - window.innerHeight + bottomPadding);
}

/** Önceki kategoriye dönüşte her zaman aşağı yönlü scroll hedefi. */
export function getRetreatScrollTarget(
  headerHeight = HEADER_HEIGHT,
  minScrollY = window.scrollY,
): number {
  const MIN_DOWN_SCROLL_PX = 120;
  const gridBottomTarget = getProductGridBottomScrollTarget(headerHeight);
  return Math.max(gridBottomTarget, minScrollY + MIN_DOWN_SCROLL_PX);
}

export function scrollToRetreatTarget(
  minScrollY: number,
  headerHeight = HEADER_HEIGHT,
) {
  smoothScrollTo(getRetreatScrollTarget(headerHeight, minScrollY));
}
