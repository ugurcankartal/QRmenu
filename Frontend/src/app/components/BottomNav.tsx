import { Home, UtensilsCrossed, Receipt, Info } from "lucide-react";
import { useNavigate, useLocation } from "react-router";
import { motion } from "motion/react";

import { useAdisyon } from "../context/AdisyonContext";
import { useI18n } from "../context/I18nContext";

export function BottomNav() {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useI18n();
  const { lineItemCount } = useAdisyon();

  const navItems = [
    { icon: Home, labelKey: "footer-nav.home", fallback: "Home", path: "/" },
    {
      icon: UtensilsCrossed,
      labelKey: "footer-nav.menu",
      fallback: "Menu",
      path: "/menu",
    },
    {
      icon: Receipt,
      labelKey: "footer-nav.adisyon",
      fallback: "Favorites",
      path: "/adisyon",
    },
    {
      icon: Info,
      labelKey: "footer-nav.about",
      fallback: "About",
      path: "/about",
    },
  ];

  return (
    <nav className="fixed bottom-0 left-0 right-0 z-40 bg-dark-graphite/95 backdrop-blur-xl border-t border-white/10">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex items-center justify-around h-16">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = location.pathname === item.path;
            const showAdisyonBadge = item.path === "/adisyon" && lineItemCount > 0;
            const badgeLabel = lineItemCount > 99 ? "99+" : String(lineItemCount);

            return (
              <button
                key={item.path}
                onClick={() => navigate(item.path)}
                className="relative flex flex-col items-center justify-center flex-1 h-full"
              >
                {isActive && (
                  <motion.div
                    layoutId="bottomNavIndicator"
                    className="absolute top-0 left-1/2 -translate-x-1/2 w-12 h-1 bg-copper-gold rounded-b-full"
                    transition={{ type: "spring", damping: 20, stiffness: 300 }}
                  />
                )}
                <div className="relative mb-1">
                  <Icon
                    className={`w-6 h-6 transition-colors ${
                      isActive ? "text-copper-gold" : "text-warm-cream/60"
                    }`}
                  />
                  {showAdisyonBadge ? (
                    <span
                      aria-label={`${badgeLabel} ${t("footer-nav.adisyon", "Adisyon")}`}
                      className="absolute -right-2 -top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-deep-red px-1 text-[10px] font-bold leading-none text-white"
                    >
                      {badgeLabel}
                    </span>
                  ) : null}
                </div>
                <span
                  className={`text-xs transition-colors ${
                    isActive ? "text-copper-gold font-medium" : "text-warm-cream/60"
                  }`}
                >
                  {t(item.labelKey, item.fallback)}
                </span>
              </button>
            );
          })}
        </div>
      </div>
    </nav>
  );
}
