import { useEffect, useMemo, useState } from "react";
import { motion } from "motion/react";
import { Search } from "lucide-react";
import { StickyCategoryNav } from "../components/StickyCategoryNav";
import { MenuCard } from "../components/MenuCard";
import { filterProductsByCategory } from "../api/categories";
import { fetchProducts } from "../api/products";
import { useI18n } from "../context/I18nContext";
import { useLanguage } from "../context/LanguageContext";
import type { Category } from "../types/category";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";
import { mapProductToMenuItem } from "../utils/mapProductToMenuItem";

export function MenuPage() {
  const { t } = useI18n();
  const { languageCode } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [products, setProducts] = useState<Awaited<ReturnType<typeof fetchProducts>>>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      setIsLoading(true);
      try {
        const data = await fetchProducts(languageCode);
        if (!cancelled) {
          setProducts(data);
        }
      } catch {
        if (!cancelled) {
          setProducts([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadProducts();

    return () => {
      cancelled = true;
    };
  }, [languageCode]);

  const filteredItems = useMemo(() => {
    const categoryFiltered = filterProductsByCategory(
      products,
      categories,
      selectedCategory,
    );
    const items = categoryFiltered.map(mapProductToMenuItem);
    const query = searchQuery.trim().toLowerCase();

    if (!query) {
      return items;
    }

    return items.filter(
      (item) =>
        item.name.toLowerCase().includes(query) ||
        item.description.toLowerCase().includes(query),
    );
  }, [products, categories, selectedCategory, searchQuery]);

  return (
    <div className="min-h-screen">
      <section className="bg-gradient-to-b from-charcoal-black to-transparent px-4 pb-4 pt-6">
        <div className="mx-auto max-w-7xl">
          <h2 className="mb-6 text-3xl text-warm-cream">
            {t("menu.our-menu", "Our Menu")}
          </h2>
          <div className="relative">
            <Search className="absolute left-4 top-1/2 h-5 w-5 -translate-y-1/2 text-warm-cream/50" />
            <input
              type="text"
              placeholder={t("menu.search-dishes", "Search dishes...")}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-2xl border border-white/10 bg-dark-graphite/50 py-4 pl-12 pr-4 text-warm-cream backdrop-blur-md placeholder:text-warm-cream/40 transition-colors focus:border-copper-gold/50 focus:outline-none"
            />
          </div>
        </div>
      </section>

      <StickyCategoryNav
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        onCategoriesLoaded={setCategories}
      />

      <section className="px-4 py-8">
        <div className="mx-auto max-w-7xl">
          {isLoading ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {Array.from({ length: 6 }).map((_, index) => (
                <div
                  key={index}
                  className="aspect-[4/3] animate-pulse rounded-2xl bg-dark-graphite/50"
                />
              ))}
            </div>
          ) : filteredItems.length > 0 ? (
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
              {filteredItems.map((item, index) => (
                <motion.div
                  key={item.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.05 }}
                >
                  <MenuCard item={item} />
                </motion.div>
              ))}
            </div>
          ) : (
            <div className="py-20 text-center">
              <p className="text-lg text-warm-cream/60">
                {searchQuery.trim()
                  ? `No dishes found matching "${searchQuery}"`
                  : t(
                      "about.no-dishes-found-in-this-category",
                      "No dishes found in this category.",
                    )}
              </p>
            </div>
          )}
        </div>
      </section>
    </div>
  );
}
