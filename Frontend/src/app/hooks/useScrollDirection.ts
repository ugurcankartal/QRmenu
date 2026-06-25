import { useEffect, useRef } from "react";

export type ScrollDirection = "up" | "down";

export function useScrollDirectionRef() {
  const directionRef = useRef<ScrollDirection>("down");
  const lastScrollYRef = useRef(0);

  useEffect(() => {
    lastScrollYRef.current = window.scrollY;

    const onScroll = () => {
      const currentScrollY = window.scrollY;
      if (currentScrollY < lastScrollYRef.current) {
        directionRef.current = "up";
      } else if (currentScrollY > lastScrollYRef.current) {
        directionRef.current = "down";
      }
      lastScrollYRef.current = currentScrollY;
    };

    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return directionRef;
}
