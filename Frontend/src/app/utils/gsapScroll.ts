import gsap from "gsap";
import { ScrollToPlugin } from "gsap/ScrollToPlugin";
import { ScrollTrigger } from "gsap/ScrollTrigger";

const SCROLL_DURATION_S = 0.55;

let pluginsRegistered = false;
let activeTween: gsap.core.Tween | null = null;
let scrolling = false;

export function ensureGsapScrollPlugins(): void {
  if (pluginsRegistered) {
    return;
  }
  gsap.registerPlugin(ScrollTrigger, ScrollToPlugin);
  pluginsRegistered = true;
}

export function isSmoothScrolling(): boolean {
  return scrolling;
}

export function refreshScrollTriggers(): void {
  ensureGsapScrollPlugins();
  ScrollTrigger.refresh();
}

export function smoothScrollTo(
  targetTop: number,
  onComplete?: () => void,
): void {
  ensureGsapScrollPlugins();

  const clampedTarget = Math.max(0, targetTop);
  const start = window.scrollY;

  if (Math.abs(start - clampedTarget) < 2) {
    onComplete?.();
    return;
  }

  activeTween?.kill();
  scrolling = true;

  activeTween = gsap.to(window, {
    duration: SCROLL_DURATION_S,
    ease: "power2.inOut",
    scrollTo: { y: clampedTarget, autoKill: false },
    onComplete: () => {
      scrolling = false;
      activeTween = null;
      ScrollTrigger.refresh();
      onComplete?.();
    },
  });
}

export function smoothScrollElement(
  element: HTMLElement,
  targetTop: number,
  onComplete?: () => void,
): void {
  ensureGsapScrollPlugins();

  const maxScroll = Math.max(0, element.scrollHeight - element.clientHeight);
  const clampedTarget = Math.min(maxScroll, Math.max(0, targetTop));

  if (Math.abs(element.scrollTop - clampedTarget) < 2) {
    onComplete?.();
    return;
  }

  activeTween?.kill();
  scrolling = true;

  activeTween = gsap.to(element, {
    duration: SCROLL_DURATION_S,
    ease: "power2.inOut",
    scrollTo: { y: clampedTarget, autoKill: false },
    onComplete: () => {
      scrolling = false;
      activeTween = null;
      ScrollTrigger.refresh();
      onComplete?.();
    },
  });
}

export const CATEGORY_SCROLL_DURATION_MS = Math.round(SCROLL_DURATION_S * 1000);

export { ScrollTrigger };
