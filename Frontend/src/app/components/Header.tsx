import { motion } from "motion/react";
// import { useState } from "react";
// import { Menu } from "lucide-react";
// import { MobileMenu } from "./MobileMenu";
import { LanguageSwitcher } from "./LanguageSwitcher";
import { useHeaderScroll } from "../context/HeaderScrollContext";
import { useSiteSettings } from "../context/SiteSettingsContext";

export function Header() {
  // const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { isHeaderVisible } = useHeaderScroll();
  const { resolved, isLoading } = useSiteSettings();
  const { siteName, siteTitle, logoUrl } = resolved;

  return (
    <>
      <motion.header
        className="fixed top-0 left-0 right-0 z-50 backdrop-blur-xl bg-charcoal-black/80 border-b border-white/10"
        initial={false}
        animate={{ y: isHeaderVisible ? 0 : "-100%" }}
        transition={{ duration: 0.3, ease: "easeInOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo & Name */}
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full overflow-hidden bg-gradient-to-br from-copper-gold to-deep-red flex items-center justify-center shrink-0">
                {logoUrl ? (
                  <img
                    src={logoUrl}
                    alt={siteName || "Logo"}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <span className="text-white font-bold text-lg">
                    {siteName ? siteName.charAt(0).toUpperCase() : "K"}
                  </span>
                )}
              </div>
              <div>
                <h1 className="text-warm-cream font-semibold text-lg leading-none">
                  {siteName || (isLoading ? "…" : "Kebab House")}
                </h1>
                <p className="text-copper-gold text-xs">
                  {siteTitle || (isLoading ? "…" : "Premium Turkish Cuisine")}
                </p>
              </div>
            </div>

            {/* Desktop Actions */}
            <div className="hidden md:flex items-center gap-4">
              <LanguageSwitcher />
              {/* TODO: Arama — sonra geliştirilecek
              <button className="p-2 rounded-lg bg-dark-graphite/50 text-warm-cream hover:bg-copper-gold/20 transition-colors">
                <Search className="w-5 h-5" />
              </button>
              */}
            </div>

            {/* Mobile Actions */}
            <div className="flex md:hidden items-center gap-2">
              <LanguageSwitcher />
              {/* TODO: Arama — sonra geliştirilecek
              <button className="p-2 rounded-lg text-warm-cream">
                <Search className="w-5 h-5" />
              </button>
              */}
              {/* TODO: Hamburger menü — sonra geliştirilecek
              <button
                onClick={() => setIsMenuOpen(true)}
                className="p-2 rounded-lg text-warm-cream"
              >
                <Menu className="w-6 h-6" />
              </button>
              */}
            </div>
          </div>
        </div>
      </motion.header>

      {/* TODO: Hamburger menü — sonra geliştirilecek
      <MobileMenu isOpen={isMenuOpen} onClose={() => setIsMenuOpen(false)} />
      */}
    </>
  );
}
