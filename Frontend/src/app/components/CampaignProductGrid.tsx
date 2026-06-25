import { type RefObject, useEffect, useRef } from "react";
import { motion } from "motion/react";

import { useScrollDirectionRef } from "../hooks/useScrollDirection";
import { useI18n } from "../context/I18nContext";
import type { Product } from "../types/product";
import { mapProductToMenuItem } from "../utils/mapProductToMenuItem";
import { MenuCard } from "./MenuCard";

interface CampaignProductGridProps {
  products: Product[];
  isLoading?: boolean;
  isLoadingMore?: boolean;
  hasMore?: boolean;
  loadMoreRef?: RefObject<HTMLDivElement | null>;
  emptyMessage?: string;
  onCategoryEndReached?: () => void;
  onCategoryStartReached?: () => void;
}

/** Son ürün kartlarından sonra kategori geçişi öncesi boş kaydırma alanı. */
const CATEGORY_END_SCROLL_BUFFER_CLASS =
  "mt-12 min-h-[min(58vh,30rem)] sm:min-h-[min(52vh,32rem)]";

/** İlk ürün kartlarından önce önceki kategoriye geçiş için boş kaydırma alanı. */
const CATEGORY_START_SCROLL_BUFFER_CLASS =
  "mb-12 min-h-[min(58vh,30rem)] sm:min-h-[min(52vh,32rem)]";

function useCategoryEdgeTrigger(
  onReached: (() => void) | undefined,
  enabled: boolean,
  direction: "up" | "down",
) {
  const ref = useRef<HTMLDivElement>(null);
  const onReachedRef = useRef(onReached);
  const wasIntersectingRef = useRef(false);
  const scrollDirectionRef = useScrollDirectionRef();

  onReachedRef.current = onReached;

  useEffect(() => {
    const node = ref.current;
    if (!node || !enabled || !onReachedRef.current) {
      return;
    }

    const observer = new IntersectionObserver(
      ([entry]) => {
        const isIntersecting = Boolean(entry?.isIntersecting);
        const scrolledDown = window.scrollY > 120;
        const matchesDirection = scrollDirectionRef.current === direction;

        if (
          isIntersecting &&
          !wasIntersectingRef.current &&
          scrolledDown &&
          matchesDirection &&
          onReachedRef.current
        ) {
          onReachedRef.current();
        }

        wasIntersectingRef.current = isIntersecting;
      },
      { rootMargin: "0px 0px 0px 0px", threshold: 0 },
    );

    observer.observe(node);
    return () => observer.disconnect();
  }, [direction, enabled, scrollDirectionRef]);

  return ref;
}

export function CampaignProductGrid({
  products,
  isLoading = false,
  isLoadingMore = false,
  hasMore = false,
  loadMoreRef,
  emptyMessage,
  onCategoryEndReached,
  onCategoryStartReached,
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
  const categoryEndRef = useCategoryEdgeTrigger(
    onCategoryEndReached,
    showCategoryEnd,
    "down",
  );
  const categoryStartRef = useCategoryEdgeTrigger(
    onCategoryStartReached,
    showCategoryStart,
    "up",
  );

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
    <section data-product-grid className="px-4 py-8">
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
          <>
            {showCategoryStart ? (
              <div
                className={`${CATEGORY_START_SCROLL_BUFFER_CLASS} flex flex-col justify-start`}
                aria-hidden
              >
                <div ref={categoryStartRef} className="h-px w-full" />
              </div>
            ) : null}

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {items.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: Math.min(index, 5) * 0.05 }}
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
                className={`${CATEGORY_END_SCROLL_BUFFER_CLASS} flex flex-col justify-end`}
                aria-hidden
              >
                <div ref={categoryEndRef} className="h-px w-full" />
              </div>
            ) : null}
          </>
        )}
      </div>
    </section>
  );
}
