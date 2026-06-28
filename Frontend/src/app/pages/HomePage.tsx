import { useState } from "react";
import { CampaignHeroSlider } from "../components/CampaignHeroSlider";
import { CampaignProductGrid } from "../components/CampaignProductGrid";
import { FeaturedDish } from "../components/FeaturedDish";
import { ContactValue } from "../components/ContactValue";
import { StickyCategoryNav } from "../components/StickyCategoryNav";
import { useInfiniteProducts } from "../hooks/useInfiniteProducts";
import { useLanguage } from "../context/LanguageContext";
import { useSiteSettings } from "../context/SiteSettingsContext";
import type { ResolvedWorkingHours } from "../types/siteSettings";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";

function hasWorkingHoursContent(workingHours: ResolvedWorkingHours): boolean {
  return Boolean(
    workingHours.label?.trim() ||
      workingHours.weekdayDays?.trim() ||
      workingHours.weekdayHours?.trim() ||
      workingHours.weekendDays?.trim() ||
      workingHours.weekendHours?.trim() ||
      workingHours.note?.trim(),
  );
}

export function HomePage() {
  const { languageCode } = useLanguage();
  const { resolved, isLoading } = useSiteSettings();
  const { addressContact, contactLabelGroups, workingHours, copyright } = resolved;
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);

  const {
    products,
    isLoading: productsLoading,
    isLoadingMore,
    hasMore,
    loadMoreRef,
  } = useInfiniteProducts(languageCode, selectedCategory);

  const showWorkingHours = isLoading || hasWorkingHoursContent(workingHours);
  const showAddress =
    isLoading ||
    Boolean(addressContact?.label?.trim() || addressContact?.value?.trim());
  const showCopyright = isLoading || Boolean(copyright?.trim());
  const showFooter =
    contactLabelGroups.length > 0 ||
    showWorkingHours ||
    showAddress ||
    showCopyright;

  return (
    <div className="min-h-screen">
      <CampaignHeroSlider />

      <StickyCategoryNav
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
      />
      <CampaignProductGrid
        categoryKey={selectedCategory}
        products={products}
        isLoading={productsLoading}
        isLoadingMore={isLoadingMore}
        hasMore={hasMore}
        loadMoreRef={loadMoreRef}
      />

      <FeaturedDish />

      {showFooter ? (
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

              {showWorkingHours ? (
                <div>
                  {workingHours.label?.trim() || isLoading ? (
                    <h4 className="text-copper-gold font-semibold mb-4">
                      {workingHours.label?.trim() || (isLoading ? "…" : "")}
                    </h4>
                  ) : null}
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
                  {workingHours.note?.trim() ? (
                    <p className="text-warm-cream/50 text-sm">
                      {workingHours.note}
                    </p>
                  ) : null}
                </div>
              ) : null}

              {showAddress ? (
                <div>
                  {addressContact?.label?.trim() || isLoading ? (
                    <h4 className="text-copper-gold font-semibold mb-4">
                      {addressContact?.label?.trim() || (isLoading ? "…" : "")}
                    </h4>
                  ) : null}
                  {addressContact?.value?.trim() ? (
                    <p className="text-warm-cream/70 text-sm">
                      {addressContact.value}
                    </p>
                  ) : isLoading ? (
                    <p className="text-warm-cream/70 text-sm">…</p>
                  ) : null}
                </div>
              ) : null}
            </div>

            {showCopyright ? (
              <div className="mt-8 pt-8 border-t border-white/10 text-center">
                <p className="text-warm-cream/50 text-sm">
                  {copyright?.trim() || (isLoading ? "…" : "")}
                </p>
              </div>
            ) : null}
          </div>
        </footer>
      ) : null}
    </div>
  );
}
