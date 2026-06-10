import { Receipt, Sparkles } from "lucide-react";
import { motion } from "motion/react";
import { useState } from "react";

import { useAdisyon } from "../context/AdisyonContext";
import { useI18n } from "../context/I18nContext";
import type { MenuItem } from "../types/menuItem";
import { ProductDetailModal } from "./ProductDetailModal";

interface MenuCardProps {
  item: MenuItem;
}

export function MenuCard({ item }: MenuCardProps) {
  const { t } = useI18n();
  const { isInAdisyon, toggleProduct, togglingProductIds } = useAdisyon();
  const [isModalOpen, setIsModalOpen] = useState(false);

  const productId = Number(item.id);
  const inAdisyon = isInAdisyon(productId);
  const isToggling = togglingProductIds.has(productId);

  return (
    <>
      <motion.div
        whileHover={{ y: -4 }}
        onClick={() => setIsModalOpen(true)}
        className="group relative rounded-2xl overflow-hidden bg-gradient-to-b from-dark-graphite/70 to-dark-graphite/50 backdrop-blur-md border border-white/10 shadow-xl hover:shadow-2xl hover:shadow-copper-gold/10 transition-all cursor-pointer"
      >
        {/* Image */}
        <div className="relative aspect-[4/3] overflow-hidden">
          <img
            src={item.image}
            alt={item.name}
            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
          />
          <div className="absolute inset-0 bg-gradient-to-t from-charcoal-black/80 via-charcoal-black/20 to-transparent" />

          {/* Popular Badge */}
          {item.popular && (
            <div className="absolute top-3 left-3 flex items-center gap-1.5 px-3 py-1.5 bg-deep-red/90 backdrop-blur-sm rounded-full">
              <Sparkles className="w-3.5 h-3.5 text-white" />
              <span className="text-white text-xs font-medium">
                {t("about.popular", "Popular")}
              </span>
            </div>
          )}

          {/* Adisyon Button */}
          <button
            type="button"
            aria-label={t("footer-nav.adisyon", "Adisyon")}
            disabled={isToggling}
            onClick={(e) => {
              e.stopPropagation();
              void toggleProduct(productId);
            }}
            className="absolute top-3 right-3 p-2.5 rounded-full bg-charcoal-black/60 backdrop-blur-sm hover:bg-charcoal-black/80 transition-colors disabled:opacity-60"
          >
            <Receipt
              className={`w-5 h-5 transition-colors ${
                inAdisyon ? "text-copper-gold" : "text-white"
              }`}
            />
          </button>
        </div>

        {/* Content */}
        <div className="p-5">
          <h3 className="text-warm-cream text-lg font-semibold mb-4 group-hover:text-copper-gold transition-colors">
            {item.name}
          </h3>
          <div className="flex items-center justify-between">
            <span className="text-copper-gold text-xl font-semibold">
              ₺{item.price}
            </span>
            <span className="text-warm-cream/50 text-xs uppercase tracking-wider">
              {item.category}
            </span>
          </div>
        </div>
      </motion.div>

      <ProductDetailModal
        item={item}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}
