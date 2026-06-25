import { useEffect, useRef } from "react";

import { useHeaderScroll } from "../context/HeaderScrollContext";
import { getProductGridScrollTarget } from "../utils/scrollToCategoryNav";

/** Grid üst scroll hedefiyle piksel toleransı. */
const GRID_TOP_TOLERANCE_PX = 20;

function isAtProductGridTop(headerHeight: number): boolean {
  const gridTop = getProductGridScrollTarget(headerHeight);
  return Math.abs(window.scrollY - gridTop) <= GRID_TOP_TOLERANCE_PX;
}

/** Grid üstündeyken yukarı kaydırma → önceki kategoriye geçiş. */
export function useProductGridTopRetreat(
  onRetreat: (() => void) | undefined,
  enabled: boolean,
) {
  const { headerHeight } = useHeaderScroll();
  const onRetreatRef = useRef(onRetreat);
  const lastScrollYRef = useRef(0);

  onRetreatRef.current = onRetreat;

  useEffect(() => {
    if (!enabled || !onRetreatRef.current) {
      return;
    }

    lastScrollYRef.current = window.scrollY;

    const tryRetreat = () => {
      if (!isAtProductGridTop(headerHeight) || !onRetreatRef.current) {
        return;
      }
      onRetreatRef.current();
    };

    const onScroll = () => {
      const currentScrollY = window.scrollY;
      const delta = currentScrollY - lastScrollYRef.current;
      lastScrollYRef.current = currentScrollY;

      if (delta < 0) {
        tryRetreat();
      }
    };

    const onWheel = (event: WheelEvent) => {
      if (event.deltaY < 0) {
        tryRetreat();
      }
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    window.addEventListener("wheel", onWheel, { passive: true });

    return () => {
      window.removeEventListener("scroll", onScroll);
      window.removeEventListener("wheel", onWheel);
    };
  }, [enabled, headerHeight]);
}

export { isAtProductGridTop, GRID_TOP_TOLERANCE_PX };
