import { HEADER_HEIGHT } from "../context/HeaderScrollContext";
import { smoothScrollTo } from "./gsapScroll";

const CAMPAIGN_SELECTOR = "[data-campaign-hero]";
const PRODUCT_GRID_SELECTOR = "[data-product-grid]";

/** Sticky kategori şeridi yaklaşık yüksekliği (px). */
const STICKY_CATEGORY_NAV_HEIGHT = 72;

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

export function scrollOnCategoryChange(targetTop?: number) {
  smoothScrollTo(targetTop ?? getCategoryChangeScrollTarget());
}

export function scrollToProductGrid(targetTop?: number) {
  smoothScrollTo(targetTop ?? getProductGridScrollTarget());
}
