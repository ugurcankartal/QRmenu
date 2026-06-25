import { useEffect, useRef } from "react";
import { useMotionValueEvent, useScroll } from "motion/react";
import { useInView } from "react-intersection-observer";

import { useHeaderScroll } from "../context/HeaderScrollContext";
import { isAtProductGridTop } from "../utils/scrollToCategoryNav";

interface UseCategoryGridScrollTriggersOptions {
  onCategoryEndReached?: () => void;
  onCategoryStartReached?: () => void;
  showCategoryEnd: boolean;
  showCategoryStart: boolean;
}

export function useCategoryGridScrollTriggers({
  onCategoryEndReached,
  onCategoryStartReached,
  showCategoryEnd,
  showCategoryStart,
}: UseCategoryGridScrollTriggersOptions) {
  const { headerHeight } = useHeaderScroll();
  const { scrollY } = useScroll();
  const scrollDirectionRef = useRef<"up" | "down">("down");
  const endWasInViewRef = useRef(false);
  const onEndReachedRef = useRef(onCategoryEndReached);
  const onStartReachedRef = useRef(onCategoryStartReached);

  onEndReachedRef.current = onCategoryEndReached;
  onStartReachedRef.current = onCategoryStartReached;

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
    if (!isAtProductGridTop(headerHeight)) {
      return;
    }
    onStartReachedRef.current();
  };

  useMotionValueEvent(scrollY, "change", (latest) => {
    if (!showCategoryStart) {
      return;
    }
    const previous = scrollY.getPrevious() ?? latest;
    if (latest < previous) {
      tryStartRetreat();
    }
  });

  useEffect(() => {
    if (!showCategoryStart) {
      return;
    }

    const onWheel = (event: WheelEvent) => {
      if (event.deltaY < 0) {
        tryStartRetreat();
      }
    };

    window.addEventListener("wheel", onWheel, { passive: true });
    return () => window.removeEventListener("wheel", onWheel);
  }, [headerHeight, showCategoryStart]);

  return { categoryEndRef };
}
