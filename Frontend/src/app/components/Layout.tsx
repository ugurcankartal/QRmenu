import { useEffect } from "react";
import { Outlet, useLocation } from "react-router";
import { motion } from "motion/react";
import { Header } from "./Header";
import { BottomNav } from "./BottomNav";
import {
  HeaderScrollProvider,
  useHeaderScroll,
  HEADER_HEIGHT,
} from "../context/HeaderScrollContext";
import { LanguageProvider } from "../context/LanguageContext";
import { I18nProvider } from "../context/I18nContext";
import { SiteSettingsProvider } from "../context/SiteSettingsContext";
import { AdisyonProvider } from "../context/AdisyonContext";

function ScrollToTop() {
  const { pathname } = useLocation();

  useEffect(() => {
    window.scrollTo(0, 0);
  }, [pathname]);

  return null;
}

function LayoutContent() {
  const { isHeaderVisible, isHeaderMotionInstant } = useHeaderScroll();
  const layoutTransition = isHeaderMotionInstant
    ? { duration: 0 }
    : { duration: 0.3, ease: "easeInOut" as const };

  return (
    <div className="min-h-screen flex flex-col">
      <ScrollToTop />
      <Header />
      <motion.main
        className="flex-1 pb-20"
        initial={false}
        animate={{ paddingTop: isHeaderVisible ? HEADER_HEIGHT : 0 }}
        transition={layoutTransition}
      >
        <Outlet />
      </motion.main>
      <BottomNav />
    </div>
  );
}

export function Layout() {
  return (
    <LanguageProvider>
      <I18nProvider>
        <SiteSettingsProvider>
          <AdisyonProvider>
            <HeaderScrollProvider>
              <LayoutContent />
            </HeaderScrollProvider>
          </AdisyonProvider>
        </SiteSettingsProvider>
      </I18nProvider>
    </LanguageProvider>
  );
}
