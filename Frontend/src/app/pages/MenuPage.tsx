import { useEffect, useState } from "react";
import { Search } from "lucide-react";
import { CategoryMenuLayout } from "../components/CategoryMenuLayout";
import { useInfiniteProducts } from "../hooks/useInfiniteProducts";
import { useI18n } from "../context/I18nContext";
import { useLanguage } from "../context/LanguageContext";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";

export function MenuPage() {
  const { t } = useI18n();
  const { languageCode } = useLanguage();
  const [searchQuery, setSearchQuery] = useState("");
  const [debouncedSearch, setDebouncedSearch] = useState("");
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);

  useEffect(() => {
    const timer = window.setTimeout(() => {
      setDebouncedSearch(searchQuery);
    }, 300);

    return () => window.clearTimeout(timer);
  }, [searchQuery]);

  const {
    products,
    isLoading,
    isLoadingMore,
    hasMore,
    loadMoreRef,
  } = useInfiniteProducts(languageCode, selectedCategory, debouncedSearch);

  const emptyMessage = debouncedSearch.trim()
    ? `No dishes found matching "${debouncedSearch}"`
    : undefined;

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

      <CategoryMenuLayout
        disabled={Boolean(debouncedSearch.trim())}
        products={products}
        isLoading={isLoading}
        isLoadingMore={isLoadingMore}
        hasMore={hasMore}
        loadMoreRef={loadMoreRef}
        emptyMessage={emptyMessage}
        onSelectedCategoryChange={setSelectedCategory}
      />
    </div>
  );
}
