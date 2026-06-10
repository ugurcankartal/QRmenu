import { motion } from "motion/react";
import { Receipt, ChevronRight, Minus, Plus, Trash2 } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router";

import { ProductDetailModal } from "../components/ProductDetailModal";
import { useAdisyon } from "../context/AdisyonContext";
import { useI18n } from "../context/I18nContext";
import { useLanguage } from "../context/LanguageContext";
import type { MenuItem } from "../types/menuItem";
import { formatMoneyValue } from "../utils/formatMoney";
import { mapProductToMenuItem } from "../utils/mapProductToMenuItem";

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1555939594-58d7cb561ad1?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080";

export function FavoritesPage() {
  const navigate = useNavigate();
  const { t } = useI18n();
  const { languageCode } = useLanguage();
  const { adisyon, isLoading, updateQuantity, removeItem } = useAdisyon();
  const [selectedItem, setSelectedItem] = useState<MenuItem | null>(null);

  const items = adisyon?.items ?? [];
  const listTotal = adisyon?.total_price ?? "0";
  const discountedTotal = adisyon?.discounted_total_price ?? listTotal;
  const totalSymbol = adisyon?.currency_symbol ?? "₺";
  const hasTotalDiscount = discountedTotal !== listTotal;

  if (isLoading) {
    return (
      <div className="min-h-screen px-4 py-8">
        <div className="max-w-7xl mx-auto">
          <p className="text-warm-cream/60">{t("favorites.loading", "Loading order…")}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen px-4 py-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h2 className="mb-2 text-3xl text-warm-cream">
            {t("footer-nav.adisyon", "Adisyon")}
          </h2>
          <p className="text-warm-cream/60">
            {t("favorites.your-order-list", "Your order list")}
          </p>
        </div>

        {items.length === 0 ? (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex flex-col items-center justify-center py-20 text-center"
          >
            <div className="w-24 h-24 rounded-full bg-dark-graphite/50 flex items-center justify-center mb-6">
              <Receipt className="h-12 w-12 text-copper-gold/50" />
            </div>
            <h3 className="mb-3 text-2xl text-warm-cream">
              {t("favorites.no-items-yet", "No items yet")}
            </h3>
            <p className="mb-8 max-w-md text-warm-cream/60">
              {t(
                "favorites.add-dishes-to-order",
                "Add dishes to your order by tapping the receipt icon on any menu item",
              )}
            </p>
            <button
              onClick={() => navigate("/menu")}
              className="inline-flex items-center gap-2 px-8 py-4 bg-copper-gold text-charcoal-black rounded-full hover:bg-copper-gold/90 transition-all shadow-lg"
            >
              <span className="font-semibold">
                {t("favorites.exploremenu", "Explore Menu")}
              </span>
              <ChevronRight className="w-5 h-5" />
            </button>
          </motion.div>
        ) : (
          <div className="space-y-6">
            <div className="space-y-4">
              {items.map((item) => {
                const menuItem = mapProductToMenuItem(item.product);
                const image = menuItem.image || FALLBACK_IMAGE;
                const symbol = item.currency_symbol ?? "₺";
                const displayPrice = item.campaign_rule
                  ? item.discounted_price
                  : item.price;
                const hasDiscount =
                  item.campaign_rule != null && item.discounted_price !== item.price;

                return (
                  <motion.div
                    key={item.id}
                    initial={{ opacity: 0, y: 12 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="flex gap-4 rounded-2xl border border-white/10 bg-dark-graphite/50 p-4"
                  >
                    <button
                      type="button"
                      onClick={() => setSelectedItem(menuItem)}
                      className="h-24 w-24 shrink-0 overflow-hidden rounded-xl"
                      aria-label={menuItem.name}
                    >
                      <img
                        src={image}
                        alt={menuItem.name}
                        className="h-full w-full object-cover transition-transform hover:scale-105"
                      />
                    </button>
                    <div className="flex min-w-0 flex-1 flex-col justify-between">
                      <div>
                        {item.campaign_badge ? (
                          <span className="mb-1.5 inline-flex items-center rounded-full bg-deep-red/90 px-2.5 py-0.5 text-xs font-medium text-white">
                            {item.campaign_badge}
                          </span>
                        ) : null}
                        <button
                          type="button"
                          onClick={() => setSelectedItem(menuItem)}
                          className="block truncate text-left text-lg font-semibold text-warm-cream transition-colors hover:text-copper-gold"
                        >
                          {menuItem.name}
                        </button>
                        <p className="text-copper-gold font-semibold">
                          {hasDiscount ? (
                            <>
                              <span className="mr-2 text-warm-cream/40 line-through">
                                {symbol}
                                {formatMoneyValue(item.price, languageCode)}
                              </span>
                              <span>
                                {symbol}
                                {formatMoneyValue(displayPrice, languageCode)}
                              </span>
                            </>
                          ) : (
                            <>
                              {symbol}
                              {formatMoneyValue(displayPrice, languageCode)}
                            </>
                          )}
                        </p>
                      </div>
                      <div className="flex items-center justify-between gap-3">
                        <div className="flex items-center gap-2 rounded-full border border-white/10 bg-charcoal-black/40">
                          <button
                            type="button"
                            onClick={() =>
                              void (item.quantity <= 1
                                ? removeItem(item.id)
                                : updateQuantity(item.id, item.quantity - 1))
                            }
                            className="rounded-full p-2 text-warm-cream/80 hover:bg-white/5"
                            aria-label={t("adisyon.decrease", "Decrease")}
                          >
                            <Minus className="h-4 w-4" />
                          </button>
                          <span className="min-w-[1.5rem] text-center text-warm-cream">
                            {item.quantity}
                          </span>
                          <button
                            type="button"
                            onClick={() => void updateQuantity(item.id, item.quantity + 1)}
                            className="rounded-full p-2 text-warm-cream/80 hover:bg-white/5"
                            aria-label={t("adisyon.increase", "Increase")}
                          >
                            <Plus className="h-4 w-4" />
                          </button>
                        </div>
                        <button
                          type="button"
                          onClick={() => void removeItem(item.id)}
                          className="rounded-full p-2 text-warm-cream/50 hover:bg-deep-red/20 hover:text-deep-red"
                          aria-label={t("adisyon.remove", "Remove")}
                        >
                          <Trash2 className="h-5 w-5" />
                        </button>
                      </div>
                    </div>
                  </motion.div>
                );
              })}
            </div>

            <div className="rounded-2xl border border-copper-gold/30 bg-copper-gold/10 p-5">
              <div className="flex items-center justify-between gap-4 text-warm-cream">
                <span className="text-lg">
                  {t("adisyon.bill", "Hesap")}
                </span>
                <p className="text-copper-gold font-semibold">
                  {hasTotalDiscount ? (
                    <>
                      <span className="mr-2 text-warm-cream/40 line-through">
                        {totalSymbol}
                        {formatMoneyValue(listTotal, languageCode)}
                      </span>
                      <span>
                        {totalSymbol}
                        {formatMoneyValue(discountedTotal, languageCode)}
                      </span>
                    </>
                  ) : (
                    <>
                      {totalSymbol}
                      {formatMoneyValue(discountedTotal, languageCode)}
                    </>
                  )}
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {selectedItem ? (
        <ProductDetailModal
          item={selectedItem}
          isOpen
          onClose={() => setSelectedItem(null)}
        />
      ) : null}
    </div>
  );
}
