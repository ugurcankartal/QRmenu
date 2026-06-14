import { Drawer } from "vaul";
import { X, Receipt, Flame, Info } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";

import { useAdisyon } from "../context/AdisyonContext";
import { useI18n } from "../context/I18nContext";
import type { MenuItem } from "../types/menuItem";
import { normalizeStringList } from "../utils/normalizeStringList";

interface ProductDetailModalProps {
  item: MenuItem;
  isOpen: boolean;
  onClose: () => void;
}

export function ProductDetailModal({ item, isOpen, onClose }: ProductDetailModalProps) {
  const { t } = useI18n();
  const { isInAdisyon, toggleProduct, togglingProductIds } = useAdisyon();
  const [isImageFullscreen, setIsImageFullscreen] = useState(false);
  const isImageFullscreenRef = useRef(false);

  const productId = Number(item.id);
  const inAdisyon = isInAdisyon(productId);
  const isToggling = togglingProductIds.has(productId);

  useEffect(() => {
    isImageFullscreenRef.current = isImageFullscreen;
  }, [isImageFullscreen]);

  useEffect(() => {
    if (!isOpen) {
      setIsImageFullscreen(false);
    }
  }, [isOpen]);

  useEffect(() => {
    if (!isImageFullscreen) return;

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key !== "Escape") return;

      event.preventDefault();
      event.stopPropagation();
      setIsImageFullscreen(false);
    };

    window.addEventListener("keydown", onKeyDown, true);
    return () => window.removeEventListener("keydown", onKeyDown, true);
  }, [isImageFullscreen]);

  const closeFullscreen = () => setIsImageFullscreen(false);

  const handleDrawerOpenChange = (open: boolean) => {
    if (open) return;

    if (isImageFullscreenRef.current) {
      closeFullscreen();
      return;
    }

    onClose();
  };

  const fullscreenOverlay =
    isImageFullscreen && typeof document !== "undefined"
      ? createPortal(
          <div
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/95 p-4"
            onClick={closeFullscreen}
            role="dialog"
            aria-modal="true"
            aria-label={item.name}
          >
            <button
              type="button"
              onClick={closeFullscreen}
              className="absolute right-4 top-4 z-10 rounded-full bg-charcoal-black/70 p-2.5 backdrop-blur-sm transition-colors hover:bg-charcoal-black/90"
              aria-label="Close"
            >
              <X className="h-6 w-6 text-white" />
            </button>
            <img
              src={item.image}
              alt={item.name}
              className="max-h-full max-w-full object-contain"
              onClick={(event) => event.stopPropagation()}
            />
          </div>,
          document.body,
        )
      : null;

  const ingredients = normalizeStringList(item.ingredients);
  const allergens = normalizeStringList(item.allergens);
  const hasIngredients = ingredients.length > 0;
  const hasAllergens = allergens.length > 0;
  const hasCalories = item.calories != null;
  const hasNutritionInfo = hasAllergens || hasCalories;

  return (
    <Drawer.Root open={isOpen} onOpenChange={handleDrawerOpenChange}>
      <Drawer.Portal>
        <Drawer.Overlay className="fixed inset-0 z-[60] bg-black/60 backdrop-blur-sm" />
        <Drawer.Content className="fixed inset-x-0 bottom-0 z-[60] flex h-[calc(100dvh-4rem)] max-h-[calc(100dvh-4rem)] flex-col overflow-hidden rounded-t-3xl bg-gradient-to-b from-dark-graphite to-charcoal-black outline-none">
          <Drawer.Title className="sr-only">{item.name}</Drawer.Title>
          <div className="mx-auto mt-3 h-1.5 w-12 shrink-0 rounded-full bg-white/20" />

          <div className="relative h-[min(32dvh,12rem)] shrink-0 overflow-hidden sm:h-[min(36dvh,14rem)]">
            <button
              type="button"
              onClick={() => setIsImageFullscreen(true)}
              className="absolute inset-0 z-0 cursor-zoom-in"
              aria-label={item.name}
            >
              <img
                src={item.image}
                alt={item.name}
                className="h-full w-full object-cover"
              />
            </button>
            <div className="pointer-events-none absolute inset-0 bg-gradient-to-t from-charcoal-black/60 to-transparent" />

            <button
              type="button"
              onClick={onClose}
              className="absolute right-4 top-4 z-10 rounded-full bg-charcoal-black/60 p-2.5 backdrop-blur-sm transition-colors hover:bg-charcoal-black/80"
            >
              <X className="h-6 w-6 text-white" />
            </button>

            {item.popular ? (
              <div className="pointer-events-none absolute left-4 top-4 z-10 flex items-center gap-2 rounded-full bg-deep-red/90 px-4 py-2 backdrop-blur-sm">
                <Flame className="h-4 w-4 text-white" />
                <span className="text-sm font-medium text-white">
                  {t("about.popular-choice", "Popular Choice")}
                </span>
              </div>
            ) : null}
          </div>

          <div className="min-h-0 flex-1 overflow-y-auto overscroll-contain">
            <div className="space-y-5 p-5 sm:p-6">
              <div>
                <div className="mb-2 flex items-start justify-between gap-3">
                  <h2 className="text-2xl font-semibold text-warm-cream sm:text-3xl">
                    {item.name}
                  </h2>
                  <span className="whitespace-nowrap text-xl font-semibold text-copper-gold sm:text-2xl">
                    ₺{item.price}
                  </span>
                </div>
                {item.description ? (
                  <p className="text-sm leading-relaxed text-warm-cream/70 sm:text-base">
                    {item.description}
                  </p>
                ) : null}
              </div>

              {hasIngredients ? (
                <div>
                  <h3 className="mb-2 flex items-center gap-2 font-semibold text-warm-cream">
                    <Info className="h-5 w-5 text-copper-gold" />
                    {t("about.ingredients", "Ingredients")}
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {ingredients.map((ingredient, index) => (
                      <span
                        key={index}
                        className="rounded-lg border border-white/10 bg-dark-graphite/50 px-3 py-1.5 text-sm text-warm-cream/80"
                      >
                        {ingredient}
                      </span>
                    ))}
                  </div>
                </div>
              ) : null}

              {hasNutritionInfo ? (
                <div
                  className={`grid gap-4 ${
                    hasAllergens && hasCalories ? "grid-cols-2" : "grid-cols-1"
                  }`}
                >
                  {hasAllergens ? (
                    <div>
                      <h4 className="mb-1 text-sm text-warm-cream/70">
                        {t("about.allergens", "Allergens")}
                      </h4>
                      <p className="text-sm text-warm-cream">{allergens.join(", ")}</p>
                    </div>
                  ) : null}
                  {hasCalories ? (
                    <div>
                      <h4 className="mb-1 text-sm text-warm-cream/70">
                        {t("about.calories", "Calories")}
                      </h4>
                      <p className="text-sm text-warm-cream">{item.calories} kcal</p>
                    </div>
                  ) : null}
                </div>
              ) : null}
            </div>
          </div>

          <div className="shrink-0 border-t border-white/10 bg-charcoal-black/90 p-4 backdrop-blur-sm">
            <button
              type="button"
              disabled={isToggling}
              onClick={() => void toggleProduct(productId)}
              className={`flex w-full items-center justify-center gap-3 rounded-xl px-6 py-3.5 transition-all sm:py-4 disabled:opacity-60 ${
                inAdisyon
                  ? "border border-copper-gold bg-charcoal-black text-copper-gold"
                  : "bg-copper-gold text-charcoal-black hover:bg-copper-gold/90"
              }`}
            >
              <Receipt className="h-5 w-5" />
              <span className="font-semibold">
                {inAdisyon
                  ? t("product-detaile.added-to-order", "Added to order")
                  : t("product-detaile.add-to-order", "Add to order")}
              </span>
            </button>
          </div>
        </Drawer.Content>
      </Drawer.Portal>

      {fullscreenOverlay}
    </Drawer.Root>
  );
}
