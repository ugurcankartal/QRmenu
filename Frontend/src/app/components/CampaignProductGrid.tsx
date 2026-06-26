import { type RefObject, useRef } from "react";
import { motion } from "motion/react";

import { useGsapCategoryScrollTriggers } from "../hooks/useGsapCategoryScrollTriggers";
import { useI18n } from "../context/I18nContext";
import type { ActiveCategory } from "../types/categorySelection";
import type { Product } from "../types/product";
import { mapProductToMenuItem } from "../utils/mapProductToMenuItem";
import { MenuCard } from "./MenuCard";

interface CampaignProductGridProps {
  categoryKey: ActiveCategory;
  products: Product[];
  isLoading?: boolean;
  isLoadingMore?: boolean;
  hasMore?: boolean;
  loadMoreRef?: RefObject<HTMLDivElement | null>;
  emptyMessage?: string;
  onCategoryEndReached?: () => void;
  onCategoryStartReached?: () => void;
  isScrollBlocked?: () => boolean;
}

/** Son ürün kartlarından sonra kategori geçişi öncesi boş kaydırma alanı. */
const CATEGORY_END_SCROLL_BUFFER_CLASS =
  "mt-12 min-h-[min(58vh,30rem)] sm:min-h-[min(52vh,32rem)]";

export function CampaignProductGrid({
  categoryKey,
  products,
  isLoading = false,
  isLoadingMore = false,
  hasMore = false,
  loadMoreRef,
  emptyMessage,
  onCategoryEndReached,
  onCategoryStartReached,
  isScrollBlocked,
}: CampaignProductGridProps) {
  const { t } = useI18n();
  const items = products.map(mapProductToMenuItem);
  const resolvedEmptyMessage =
    emptyMessage ??
    t(
      "about.no-dishes-found-in-this-category",
      "No dishes found in this category.",
    );
  const showCategoryEnd =
    !isLoading &&
    !isLoadingMore &&
    !hasMore &&
    products.length > 0 &&
    Boolean(onCategoryEndReached);
  const showCategoryStart =
    !isLoading && products.length > 0 && Boolean(onCategoryStartReached);

  const gridRef = useRef<HTMLElement>(null);
  const endRef = useRef<HTMLDivElement>(null);

  useGsapCategoryScrollTriggers({
    categoryKey,
    gridRef,
    endRef,
    onCategoryEndReached,
    onCategoryStartReached,
    showCategoryEnd,
    showCategoryStart,
    isScrollBlocked,
    layoutKey: `${categoryKey}:${products.length}:${hasMore}:${isLoadingMore}`,
  });

  if (!isLoading && items.length === 0) {
    return (
      <section data-product-grid className="px-4 py-8">
        <div className="mx-auto max-w-7xl py-20 text-center">
          <p className="text-lg text-warm-cream/60">{resolvedEmptyMessage}</p>
        </div>
      </section>
    );
  }

  return (
    <section ref={gridRef} data-product-grid className="px-4 py-8">
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
          <motion.div
            key={String(categoryKey)}
            initial={{ opacity: 0.35 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
          >
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    delay: Math.min(index, 5) * 0.04,
                    duration: 0.35,
                    ease: [0.32, 0.72, 0, 1],
                  }}
                >
                  <MenuCard item={item} />
                </motion.div>
              ))}
            </div>

            {isLoadingMore ? (
              <div className="mt-6 grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
                {Array.from({ length: 3 }).map((_, index) => (
                  <div
                    key={`loading-more-${index}`}
                    className="aspect-[4/3] animate-pulse rounded-2xl bg-dark-graphite/50"
                  />
                ))}
              </div>
            ) : null}

            {hasMore ? (
              <div ref={loadMoreRef} className="h-8 w-full" aria-hidden />
            ) : null}

            {showCategoryEnd ? (
              <div
                data-category-end-buffer
                className={`${CATEGORY_END_SCROLL_BUFFER_CLASS} flex flex-col justify-end`}
                aria-hidden
              >
                <div ref={endRef} className="h-px w-full" />
              </div>
            ) : null}
          </motion.div>
        )}
      </div>
    </section>
  );
}
