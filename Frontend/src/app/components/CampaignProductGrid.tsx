import { motion } from "motion/react";

import { useI18n } from "../context/I18nContext";
import type { Product } from "../types/product";
import { mapProductToMenuItem } from "../utils/mapProductToMenuItem";
import { MenuCard } from "./MenuCard";

interface CampaignProductGridProps {
  products: Product[];
  isLoading?: boolean;
}

export function CampaignProductGrid({
  products,
  isLoading = false,
}: CampaignProductGridProps) {
  const { t } = useI18n();
  const items = products.map(mapProductToMenuItem);

  if (!isLoading && items.length === 0) {
    return (
      <section className="px-4 py-8">
        <div className="mx-auto max-w-7xl py-20 text-center">
          <p className="text-lg text-warm-cream/60">
            {t(
              "about.no-dishes-found-in-this-category",
              "No dishes found in this category.",
            )}
          </p>
        </div>
      </section>
    );
  }

  return (
    <section className="px-4 py-8">
      <div className="mx-auto max-w-7xl">
        {isLoading ? (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div
                key={index}
                className="aspect-[4/3] animate-pulse rounded-2xl bg-dark-graphite/50"
              />
            ))}
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
            {items.map((item, index) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <MenuCard item={item} />
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
}
