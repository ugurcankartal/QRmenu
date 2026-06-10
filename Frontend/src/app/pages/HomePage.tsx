import { useEffect, useMemo, useState } from "react";
import { CampaignHeroSlider } from "../components/CampaignHeroSlider";
import { CampaignProductGrid } from "../components/CampaignProductGrid";
import { FeaturedDish } from "../components/FeaturedDish";
import { StickyCategoryNav } from "../components/StickyCategoryNav";
import { ContactValue } from "../components/ContactValue";
import { filterProductsByCategory } from "../api/categories";
import { fetchProducts } from "../api/products";
import { useLanguage } from "../context/LanguageContext";
import { useSiteSettings } from "../context/SiteSettingsContext";
import type { Category } from "../types/category";
import type { Product } from "../types/product";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";

export function HomePage() {
  const { languageCode } = useLanguage();
  const { resolved, isLoading } = useSiteSettings();
  const { addressContact, contactLabelGroups, workingHours, copyright } = resolved;
  const [products, setProducts] = useState<Product[]>([]);
  const [productsLoading, setProductsLoading] = useState(true);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);

  useEffect(() => {
    let cancelled = false;

    async function loadProducts() {
      setProductsLoading(true);
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
          setProductsLoading(false);
        }
      }
    }

    void loadProducts();

    return () => {
      cancelled = true;
    };
  }, [languageCode]);

  const filteredProducts = useMemo(
    () =>
      filterProductsByCategory(products, categories, selectedCategory),
    [products, categories, selectedCategory],
  );

  return (
    <div className="min-h-screen">
      <CampaignHeroSlider />

      <StickyCategoryNav
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        onCategoriesLoaded={setCategories}
      />

      <CampaignProductGrid
        products={filteredProducts}
        isLoading={productsLoading}
      />

      <FeaturedDish />

      <footer className="mt-16 px-4 py-12 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {contactLabelGroups.map((group) => (
              <div key={group.label}>
                <h4 className="text-copper-gold font-semibold mb-4">
                  {group.label}
                </h4>
                {group.contacts.map((contact) => (
                  <ContactValue key={contact.id} contact={contact} />
                ))}
              </div>
            ))}
            {contactLabelGroups.length === 0 && isLoading && (
              <div>
                <h4 className="text-copper-gold font-semibold mb-4">…</h4>
                <p className="text-warm-cream/70 text-sm">…</p>
              </div>
            )}
            <div>
              <h4 className="text-copper-gold font-semibold mb-4">
                {workingHours.label || (isLoading ? "…" : "Hours")}
              </h4>
              {(workingHours.weekdayDays || workingHours.weekdayHours) && (
                <p className="text-warm-cream/70 text-sm mb-2">
                  {[workingHours.weekdayDays, workingHours.weekdayHours]
                    .filter(Boolean)
                    .join(": ")}
                </p>
              )}
              {(workingHours.weekendDays || workingHours.weekendHours) && (
                <p className="text-warm-cream/70 text-sm mb-2">
                  {[workingHours.weekendDays, workingHours.weekendHours]
                    .filter(Boolean)
                    .join(": ")}
                </p>
              )}
              {workingHours.note && (
                <p className="text-warm-cream/50 text-sm">{workingHours.note}</p>
              )}
            </div>
            <div>
              <h4 className="text-copper-gold font-semibold mb-4">
                {addressContact?.label || (isLoading ? "…" : "Location")}
              </h4>
              <p className="text-warm-cream/70 text-sm">
                {addressContact?.value || (isLoading ? "…" : "")}
              </p>
            </div>
          </div>
          <div className="mt-8 pt-8 border-t border-white/10 text-center">
            <p className="text-warm-cream/50 text-sm">
              {copyright || (isLoading ? "…" : "")}
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
