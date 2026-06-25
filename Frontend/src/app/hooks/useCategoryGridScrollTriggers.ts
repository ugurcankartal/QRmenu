import { useEffect, useRef } from "react";
import { useMotionValueEvent, useScroll } from "motion/react";
import { useInView } from "react-intersection-observer";

import { useHeaderScroll } from "../context/HeaderScrollContext";
import type { ActiveCategory } from "../types/categorySelection";
import { isAtProductGridTop } from "../utils/scrollToCategoryNav";

interface UseCategoryGridScrollTriggersOptions {
  categoryKey: ActiveCategory;
  onCategoryEndReached?: () => void;
  onCategoryStartReached?: () => void;
  showCategoryEnd: boolean;
  showCategoryStart: boolean;
  isScrollBlocked?: () => boolean;
}

const RETREAT_COOLDOWN_MS = 600;

export function useCategoryGridScrollTriggers({
  categoryKey,
  onCategoryEndReached,
  onCategoryStartReached,
  showCategoryEnd,
  showCategoryStart,
  isScrollBlocked,
}: UseCategoryGridScrollTriggersOptions) {
  const { headerHeight } = useHeaderScroll();
  const { scrollY } = useScroll();
  const scrollDirectionRef = useRef<"up" | "down">("down");
  const endWasInViewRef = useRef(false);
  const lastRetreatAttemptRef = useRef(0);
  const onEndReachedRef = useRef(onCategoryEndReached);
  const onStartReachedRef = useRef(onCategoryStartReached);
  const isScrollBlockedRef = useRef(isScrollBlocked);

  onEndReachedRef.current = onCategoryEndReached;
  onStartReachedRef.current = onCategoryStartReached;
  isScrollBlockedRef.current = isScrollBlocked;

  useEffect(() => {
    endWasInViewRef.current = false;
    lastRetreatAttemptRef.current = 0;
  }, [categoryKey]);

  useMotionValueEvent(scrollY, "change", (latest) => {
    const previous = scrollY.getPrevious() ?? latest;
    if (latest < previous) {
      scrollDirectionRef.current = "up";
    } else if (latest > previous) {
      scrollDirectionRef.current = "down";
    }
  });

  const { ref: categoryEndRef } = useInView({
    skip: !showCategoryEnd,
    threshold: 0,
    onChange(inView) {
      if (isScrollBlockedRef.current?.()) {
        endWasInViewRef.current = inView;
        return;
      }

      if (
        inView &&
        !endWasInViewRef.current &&
        scrollDirectionRef.current === "down" &&
        window.scrollY > 120
      ) {
        onEndReachedRef.current?.();
      }
      endWasInViewRef.current = inView;
    },
  });

  const tryStartRetreat = () => {
    if (!showCategoryStart || !onStartReachedRef.current) {
      return;
    }
    if (isScrollBlockedRef.current?.()) {
      return;
    }
    if (Date.now() - lastRetreatAttemptRef.current < RETREAT_COOLDOWN_MS) {
      return;
    }
    if (!isAtProductGridTop(headerHeight)) {
      return;
    }

    lastRetreatAttemptRef.current = Date.now();
    onStartReachedRef.current();
  };

  useMotionValueEvent(scrollY, "change", (latest) => {
    if (!showCategoryStart) {
      return;
    }
    const previous = scrollY.getPrevious() ?? latest;
    if (latest < previous - 0.5) {
      tryStartRetreat();
    }
  });

  useEffect(() => {
    if (!showCategoryStart) {
      return;
    }

    const onWheel = (event: WheelEvent) => {
      if (event.deltaY >= 0) {
        return;
      }
      tryStartRetreat();
    };

    window.addEventListener("wheel", onWheel, { passive: true });
    return () => window.removeEventListener("wheel", onWheel);
  }, [headerHeight, showCategoryStart]);

  return { categoryEndRef };
}
