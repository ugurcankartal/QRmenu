import { type RefObject, useLayoutEffect, useRef } from "react";

import { useHeaderScroll } from "../context/HeaderScrollContext";
import type { ActiveCategory } from "../types/categorySelection";
import {
  ScrollTrigger,
  ensureGsapScrollPlugins,
  refreshScrollTriggers,
} from "../utils/gsapScroll";

/** Sticky kategori şeridi yaklaşık yüksekliği (px). */
const STICKY_CATEGORY_NAV_HEIGHT = 72;

interface UseGsapCategoryScrollTriggersOptions {
  categoryKey: ActiveCategory;
  gridRef: RefObject<HTMLElement | null>;
  endRef: RefObject<HTMLElement | null>;
  onCategoryEndReached?: () => void;
  onCategoryStartReached?: () => void;
  showCategoryEnd: boolean;
  showCategoryStart: boolean;
  isScrollBlocked?: () => boolean;
  /** İçerik yüksekliği değişince ScrollTrigger yenilenir. */
  layoutKey: string;
}

export function useGsapCategoryScrollTriggers({
  categoryKey,
  gridRef,
  endRef,
  onCategoryEndReached,
  onCategoryStartReached,
  showCategoryEnd,
  showCategoryStart,
  isScrollBlocked,
  layoutKey,
}: UseGsapCategoryScrollTriggersOptions) {
  const { headerHeight } = useHeaderScroll();
  const triggersRef = useRef<ScrollTrigger[]>([]);
  const onEndReachedRef = useRef(onCategoryEndReached);
  const onStartReachedRef = useRef(onCategoryStartReached);
  const isScrollBlockedRef = useRef(isScrollBlocked);

  onEndReachedRef.current = onCategoryEndReached;
  onStartReachedRef.current = onCategoryStartReached;
  isScrollBlockedRef.current = isScrollBlocked;

  useLayoutEffect(() => {
    ensureGsapScrollPlugins();

    triggersRef.current.forEach((trigger) => trigger.kill());
    triggersRef.current = [];

    const grid = gridRef.current;
    const end = endRef.current;
    const gridTopOffset = headerHeight + STICKY_CATEGORY_NAV_HEIGHT;

    if (showCategoryEnd && end) {
      const forwardTrigger = ScrollTrigger.create({
        trigger: end,
        start: "top 92%",
        onEnter: (self) => {
          if (isScrollBlockedRef.current?.()) {
            return;
          }
          if (self.direction !== 1 || window.scrollY < 120) {
            return;
          }
          onEndReachedRef.current?.();
        },
      });
      triggersRef.current.push(forwardTrigger);
    }

    if (showCategoryStart && grid) {
      const backwardTrigger = ScrollTrigger.create({
        trigger: grid,
        start: `top top+=${gridTopOffset}`,
        onLeaveBack: (self) => {
          if (isScrollBlockedRef.current?.()) {
            return;
          }
          if (self.direction !== -1) {
            return;
          }
          onStartReachedRef.current?.();
        },
      });
      triggersRef.current.push(backwardTrigger);
    }

    refreshScrollTriggers();

    return () => {
      triggersRef.current.forEach((trigger) => trigger.kill());
      triggersRef.current = [];
    };
  }, [
    categoryKey,
    endRef,
    gridRef,
    headerHeight,
    showCategoryEnd,
    showCategoryStart,
  ]);

  useLayoutEffect(() => {
    refreshScrollTriggers();
  }, [layoutKey, categoryKey]);
}
