import { CampaignHeroSlider } from "../components/CampaignHeroSlider";
import { CampaignProductGrid } from "../components/CampaignProductGrid";
import { FeaturedDish } from "../components/FeaturedDish";
import { StickyCategoryNav } from "../components/StickyCategoryNav";
import { ContactValue } from "../components/ContactValue";
import { useCategoryAutoAdvance } from "../hooks/useCategoryAutoAdvance";
import { useInfiniteProducts } from "../hooks/useInfiniteProducts";
import { useLanguage } from "../context/LanguageContext";
import { useSiteSettings } from "../context/SiteSettingsContext";

export function HomePage() {
  const { languageCode } = useLanguage();
  const { resolved, isLoading } = useSiteSettings();
  const { addressContact, contactLabelGroups, workingHours, copyright } = resolved;
  const {
    selectedCategory,
    setSelectedCategory,
    handleRootCategoriesChange,
    handleCategoryEndReached,
  } = useCategoryAutoAdvance();

  const {
    products,
    isLoading: productsLoading,
    isLoadingMore,
    hasMore,
    loadMoreRef,
  } = useInfiniteProducts(languageCode, selectedCategory);

  return (
    <div className="min-h-screen">
      <CampaignHeroSlider />

      <StickyCategoryNav
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        onRootCategoriesChange={handleRootCategoriesChange}
      />

      <CampaignProductGrid
        products={products}
        isLoading={productsLoading}
        isLoadingMore={isLoadingMore}
        hasMore={hasMore}
        loadMoreRef={loadMoreRef}
        onCategoryEndReached={handleCategoryEndReached}
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
