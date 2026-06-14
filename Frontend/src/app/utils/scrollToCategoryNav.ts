import { HEADER_HEIGHT } from "../context/HeaderScrollContext";

const CAMPAIGN_SELECTOR = "[data-campaign-hero]";

export function getCategoryChangeScrollTarget(): number {
  const campaignSection = document.querySelector(CAMPAIGN_SELECTOR);
  if (!campaignSection) {
    return 0;
  }

  const rect = campaignSection.getBoundingClientRect();
  return Math.max(0, rect.bottom + window.scrollY - HEADER_HEIGHT);
}

export function scrollOnCategoryChange(targetTop?: number) {
  const top = targetTop ?? getCategoryChangeScrollTarget();

  if (Math.abs(window.scrollY - top) < 4) {
    return;
  }

  window.scrollTo({
    top,
    behavior: "smooth",
  });
}
