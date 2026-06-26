import {
  createContext,
  useCallback,
  useContext,
  useRef,
  useState,
  type ReactNode,
  type RefObject,
} from "react";

import { useHeaderScroll } from "./HeaderScrollContext";
import {
  refreshScrollTriggers,
  smoothScrollElement,
} from "../utils/gsapScroll";

const SCROLL_TOP_TOLERANCE_PX = 4;

/** Sticky kategori şeridi yaklaşık yüksekliği (px). */
export const CATEGORY_NAV_HEIGHT = 72;

export interface CategoryScrollContextValue {
  scrollContainerRef: RefObject<HTMLDivElement | null>;
  scrollContainerReady: number;
  setScrollContainerNode: (node: HTMLDivElement | null) => void;
  scrollToTop: (smooth?: boolean) => void;
  scrollToBottom: (smooth?: boolean) => void;
  scrollToBottomAfterLayout: (smooth?: boolean) => void;
  isScrollAtTop: () => boolean;
}

const CategoryScrollContext = createContext<CategoryScrollContextValue | null>(
  null,
);

export function CategoryScrollProvider({
  children,
}: {
  children: ReactNode;
}) {
  const scrollContainerRef = useRef<HTMLDivElement>(null);
  const [scrollContainerReady, setScrollContainerReady] = useState(0);

  const setScrollContainerNode = useCallback((node: HTMLDivElement | null) => {
    scrollContainerRef.current = node;
    if (node) {
      setScrollContainerReady((value) => value + 1);
    }
  }, []);

  const scrollToTop = useCallback((smooth = true) => {
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }

    if (!smooth || container.scrollTop <= SCROLL_TOP_TOLERANCE_PX) {
      container.scrollTop = 0;
      refreshScrollTriggers();
      return;
    }

    smoothScrollElement(container, 0, () => {
      refreshScrollTriggers();
    });
  }, []);

  const scrollToBottom = useCallback((smooth = true) => {
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }

    const target = Math.max(0, container.scrollHeight - container.clientHeight);

    if (!smooth || Math.abs(container.scrollTop - target) <= SCROLL_TOP_TOLERANCE_PX) {
      container.scrollTop = target;
      refreshScrollTriggers();
      return;
    }

    smoothScrollElement(container, target, () => {
      refreshScrollTriggers();
    });
  }, []);

  const scrollToBottomAfterLayout = useCallback((_smooth = false) => {
    const container = scrollContainerRef.current;
    if (!container) {
      return;
    }

    const content = container.querySelector("[data-product-grid]");
    const apply = () => {
      container.scrollTop = Math.max(
        0,
        container.scrollHeight - container.clientHeight,
      );
    };

    apply();

    let frameCount = 0;
    const maxFrames = 16;
    let observer: ResizeObserver | null = null;

    const finish = () => {
      observer?.disconnect();
      refreshScrollTriggers();
    };

    const tick = () => {
      apply();
      frameCount += 1;
      if (frameCount < maxFrames) {
        requestAnimationFrame(tick);
      } else {
        finish();
      }
    };

    observer = new ResizeObserver(() => {
      apply();
    });
    observer.observe(container);
    if (content instanceof HTMLElement) {
      observer.observe(content);
    }

    requestAnimationFrame(tick);

    window.setTimeout(() => {
      apply();
      finish();
    }, 400);
  }, []);

  const isScrollAtTop = useCallback(() => {
    const container = scrollContainerRef.current;
    if (!container) {
      return true;
    }
    return container.scrollTop <= SCROLL_TOP_TOLERANCE_PX;
  }, []);

  return (
    <CategoryScrollContext.Provider
      value={{
        scrollContainerRef,
        scrollContainerReady,
        setScrollContainerNode,
        scrollToTop,
        scrollToBottom,
        scrollToBottomAfterLayout,
        isScrollAtTop,
      }}
    >
      {children}
    </CategoryScrollContext.Provider>
  );
}

export function CategoryScrollViewport({
  children,
  panelHeight,
}: {
  children: ReactNode;
  panelHeight: string;
}) {
  const { setScrollContainerNode } = useCategoryScroll();

  return (
    <div
      ref={setScrollContainerNode}
      data-category-menu-scroll
      className="scrollbar-hide min-h-0 touch-pan-y overflow-x-hidden overflow-y-auto overscroll-y-contain [-webkit-overflow-scrolling:touch]"
      style={{ height: panelHeight, maxHeight: panelHeight }}
    >
      {children}
    </div>
  );
}

export function useCategoryScroll() {
  const context = useContext(CategoryScrollContext);
  if (!context) {
    throw new Error("useCategoryScroll must be used within CategoryScrollProvider");
  }
  return context;
}

export function useOptionalCategoryScroll() {
  return useContext(CategoryScrollContext);
}

/** Görünür scroll alanı yüksekliği (dvh) — içerik bundan uzunsa panel içinde kayar. */
const PANEL_VIEWPORT_VH = 100;

export function useCategoryPanelHeight() {
  const { headerHeight } = useHeaderScroll();
  return `calc(${PANEL_VIEWPORT_VH}dvh - ${headerHeight + CATEGORY_NAV_HEIGHT}px)`;
}
