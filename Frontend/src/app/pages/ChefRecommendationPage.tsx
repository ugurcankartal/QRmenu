import { useMemo, useState } from "react";
import { Award } from "lucide-react";

import { filterProductsByCategory } from "../api/categories";
import { CampaignProductGrid } from "../components/CampaignProductGrid";
import { StickyCategoryNav } from "../components/StickyCategoryNav";
import type { Category } from "../types/category";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";
import type { ChefRecommendation } from "../types/chefRecommendation";
import { getRecommendationProducts } from "../utils/chefRecommendation";

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1643941217351-bc293885bade?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080";

const RICH_TEXT_CLASS =
  "rich-text-content leading-relaxed text-warm-cream/90 normal-case [&_*]:normal-case [&_a]:text-copper-gold [&_a]:underline [&_em]:italic [&_h2]:mb-3 [&_h2]:mt-6 [&_h2]:text-2xl [&_h2]:text-warm-cream [&_h3]:mb-2 [&_h3]:mt-4 [&_h3]:text-xl [&_h3]:text-warm-cream [&_li]:mb-1 [&_ol]:my-4 [&_ol]:list-decimal [&_ol]:pl-6 [&_p]:m-0 [&_p+p]:mt-4 [&_strong]:font-semibold [&_ul]:my-4 [&_ul]:list-disc [&_ul]:pl-6";

interface ChefRecommendationPageProps {
  recommendation: ChefRecommendation;
}

export function ChefRecommendationPage({
  recommendation,
}: ChefRecommendationPageProps) {
  const products = getRecommendationProducts(recommendation);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);
  const imageSrc = recommendation.image_url || FALLBACK_IMAGE;

  const filteredProducts = useMemo(
    () => filterProductsByCategory(products, categories, selectedCategory),
    [products, categories, selectedCategory],
  );

  return (
    <div className="min-h-screen">
      <section>
        <div className="relative h-[40vh] min-h-[320px] w-full overflow-hidden">
          <img
            src={imageSrc}
            alt={recommendation.title}
            className="h-full w-full object-cover"
          />
          <div className="absolute inset-0 bg-gradient-to-b from-charcoal-black/30 via-charcoal-black/50 to-charcoal-black" />
          <div className="absolute inset-x-0 bottom-0 p-6 pb-10 md:p-10">
            {recommendation.title ? (
              <div className="mb-3 flex items-center gap-2">
                <Award className="h-6 w-6 text-copper-gold" />
                <span className="text-sm font-medium uppercase tracking-wider text-copper-gold">
                  {recommendation.title}
                </span>
              </div>
            ) : null}
            {recommendation.summary ? (
              <p className="max-w-3xl text-lg leading-relaxed text-warm-cream/90 md:text-xl">
                {recommendation.summary}
              </p>
            ) : null}
          </div>
        </div>

        {recommendation.description ? (
          <div className="px-4 py-10 md:py-14">
            <div
              className={`mx-auto max-w-3xl ${RICH_TEXT_CLASS}`}
              dangerouslySetInnerHTML={{ __html: recommendation.description }}
            />
          </div>
        ) : null}
      </section>

      <StickyCategoryNav
        products={products}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        onCategoriesLoaded={setCategories}
      />
      <CampaignProductGrid
        categoryKey={selectedCategory}
        products={filteredProducts}
      />
    </div>
  );
}
