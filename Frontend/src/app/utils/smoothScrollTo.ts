import { animate } from "motion/react";

const SCROLL_DURATION_S = 0.55;
const SCROLL_EASE: [number, number, number, number] = [0.32, 0.72, 0, 1];

let activeAnimation: { stop: () => void } | null = null;
let scrolling = false;

export function isSmoothScrolling(): boolean {
  return scrolling;
}

export function smoothScrollTo(
  targetTop: number,
  onComplete?: () => void,
): void {
  const clampedTarget = Math.max(0, targetTop);
  const start = window.scrollY;

  if (Math.abs(start - clampedTarget) < 2) {
    onComplete?.();
    return;
  }

  activeAnimation?.stop();
  scrolling = true;

  activeAnimation = animate(start, clampedTarget, {
    duration: SCROLL_DURATION_S,
    ease: SCROLL_EASE,
    onUpdate: (value) => {
      window.scrollTo(0, value);
    },
    onComplete: () => {
      scrolling = false;
      activeAnimation = null;
      onComplete?.();
    },
  });
}

export const CATEGORY_SCROLL_DURATION_MS = Math.round(SCROLL_DURATION_S * 1000);
