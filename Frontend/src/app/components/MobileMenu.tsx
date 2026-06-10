import { motion, AnimatePresence } from "motion/react";
import { X, Home, UtensilsCrossed, Heart, Info, Globe, Phone, MapPin } from "lucide-react";
import { useNavigate, useLocation } from "react-router";

interface MobileMenuProps {
  isOpen: boolean;
  onClose: () => void;
}

export function MobileMenu({ isOpen, onClose }: MobileMenuProps) {
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    { icon: Home, label: "Home", path: "/" },
    { icon: UtensilsCrossed, label: "Menu", path: "/menu" },
    { icon: Heart, label: "Favorites", path: "/adisyon" },
    { icon: Info, label: "About", path: "/about" },
  ];

  const handleNavigate = (path: string) => {
    navigate(path);
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Menu Drawer */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 bottom-0 w-full max-w-sm bg-gradient-to-b from-dark-graphite to-charcoal-black z-50 shadow-2xl"
          >
            <div className="flex flex-col h-full">
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-white/10">
                <div>
                  <h2 className="text-warm-cream text-2xl font-semibold">Menu</h2>
                  <p className="text-copper-gold text-sm">Premium Turkish Cuisine</p>
                </div>
                <button
                  onClick={onClose}
                  className="p-2 rounded-full bg-white/5 text-warm-cream hover:bg-white/10 transition-colors"
                >
                  <X className="w-6 h-6" />
                </button>
              </div>

              {/* Navigation Items */}
              <nav className="flex-1 p-6 space-y-2">
                {menuItems.map((item, index) => {
                  const Icon = item.icon;
                  const isActive = location.pathname === item.path;

                  return (
                    <motion.button
                      key={item.path}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      onClick={() => handleNavigate(item.path)}
                      className={`w-full flex items-center gap-4 p-4 rounded-xl transition-all ${
                        isActive
                          ? "bg-copper-gold text-charcoal-black"
                          : "text-warm-cream hover:bg-white/5"
                      }`}
                    >
                      <Icon className="w-6 h-6" />
                      <span className="text-lg font-medium">{item.label}</span>
                    </motion.button>
                  );
                })}
              </nav>

              {/* Footer Info */}
              <div className="p-6 border-t border-white/10 space-y-3">
                <div className="flex items-center gap-3 text-warm-cream/70">
                  <Globe className="w-5 h-5 text-copper-gold" />
                  <span className="text-sm">English / Türkçe</span>
                </div>
                <div className="flex items-center gap-3 text-warm-cream/70">
                  <Phone className="w-5 h-5 text-copper-gold" />
                  <span className="text-sm">+90 555 123 4567</span>
                </div>
                <div className="flex items-center gap-3 text-warm-cream/70">
                  <MapPin className="w-5 h-5 text-copper-gold" />
                  <span className="text-sm">Istanbul, Turkey</span>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
