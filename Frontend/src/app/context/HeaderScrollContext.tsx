import {
  createContext,
  useContext,
  useEffect,
  useRef,
  useState,
  type ReactNode,
} from "react";

const SCROLL_THRESHOLD = 10;
export const HEADER_HEIGHT = 64;

type HeaderScrollContextValue = {
  isHeaderVisible: boolean;
  headerHeight: number;
};

const HeaderScrollContext = createContext<HeaderScrollContextValue>({
  isHeaderVisible: true,
  headerHeight: HEADER_HEIGHT,
});

export function HeaderScrollProvider({ children }: { children: ReactNode }) {
  const [isHeaderVisible, setIsHeaderVisible] = useState(true);
  const lastScrollY = useRef(0);

  useEffect(() => {
    const handleScroll = () => {
      const currentScrollY = window.scrollY;
      const scrollDelta = currentScrollY - lastScrollY.current;

      if (Math.abs(scrollDelta) < SCROLL_THRESHOLD) {
        return;
      }

      if (currentScrollY <= 0) {
        setIsHeaderVisible(true);
      } else if (scrollDelta > 0) {
        setIsHeaderVisible(false);
      } else {
        setIsHeaderVisible(true);
      }

      lastScrollY.current = currentScrollY;
    };

    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <HeaderScrollContext.Provider
      value={{ isHeaderVisible, headerHeight: HEADER_HEIGHT }}
    >
      {children}
    </HeaderScrollContext.Provider>
  );
}

export function useHeaderScroll() {
  return useContext(HeaderScrollContext);
}
