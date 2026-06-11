import { useEffect, useMemo, useState } from "react";
import { Navigate, useParams } from "react-router";

import { filterProductsByCategory } from "../api/categories";
import { fetchChefRecommendationBySlug } from "../api/chefRecommendations";
import { fetchCampaignBySlug } from "../api/campaigns";
import { CampaignHeroSlider } from "../components/CampaignHeroSlider";
import { CampaignProductGrid } from "../components/CampaignProductGrid";
import { StickyCategoryNav } from "../components/StickyCategoryNav";
import { useLanguage } from "../context/LanguageContext";
import type { Campaign } from "../types/campaign";
import type { Category } from "../types/category";
import {
  ALL_CATEGORIES,
  type ActiveCategory,
} from "../types/categorySelection";
import type { ChefRecommendation } from "../types/chefRecommendation";
import { ChefRecommendationPage } from "./ChefRecommendationPage";
import { isSeoDocumentPath, SeoDocumentView } from "./SeoDocumentView";

type SlugPageType = "loading" | "campaign" | "chef" | "notfound";

export function SlugPage() {
  const { slug } = useParams<{ slug: string }>();

  if (slug && isSeoDocumentPath(`/${slug}`)) {
    return <SeoDocumentView />;
  }
  const { languageCode } = useLanguage();
  const [pageType, setPageType] = useState<SlugPageType>("loading");
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [recommendation, setRecommendation] = useState<ChefRecommendation | null>(
    null,
  );

  useEffect(() => {
    if (!slug) {
      setPageType("notfound");
      return;
    }

    let cancelled = false;
    const currentSlug = slug;

    async function loadSlugPage() {
      setPageType("loading");
      setCampaign(null);
      setRecommendation(null);

      try {
        const campaignData = await fetchCampaignBySlug(currentSlug, languageCode);
        if (cancelled) return;

        if (campaignData) {
          setCampaign(campaignData);
          setPageType("campaign");
          return;
        }

        const chefData = await fetchChefRecommendationBySlug(
          currentSlug,
          languageCode,
        );
        if (cancelled) return;

        if (chefData) {
          setRecommendation(chefData);
          setPageType("chef");
          return;
        }

        setPageType("notfound");
      } catch {
        if (!cancelled) {
          setPageType("notfound");
        }
      }
    }

    void loadSlugPage();

    return () => {
      cancelled = true;
    };
  }, [slug, languageCode]);

  if (pageType === "notfound") {
    return <Navigate to="/" replace />;
  }

  if (pageType === "loading") {
    return (
      <div className="min-h-screen">
        <section className="relative h-[50vh] min-h-[400px] overflow-hidden bg-charcoal-black">
          <div className="absolute inset-0 animate-pulse bg-charcoal-black/80" />
        </section>
        <CampaignProductGrid products={[]} isLoading />
      </div>
    );
  }

  if (pageType === "campaign" && campaign) {
    return <CampaignSlugView campaign={campaign} />;
  }

  if (pageType === "chef" && recommendation) {
    return <ChefRecommendationPage recommendation={recommendation} />;
  }

  return null;
}

function CampaignSlugView({ campaign }: { campaign: Campaign }) {
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] =
    useState<ActiveCategory>(ALL_CATEGORIES);

  const filteredProducts = useMemo(
    () =>
      filterProductsByCategory(
        campaign.products,
        categories,
        selectedCategory,
      ),
    [campaign.products, categories, selectedCategory],
  );

  return (
    <div className="min-h-screen">
      <CampaignHeroSlider
        campaigns={[campaign]}
        showDots={false}
        autoplay={false}
      />
      <StickyCategoryNav
        products={campaign.products}
        selectedCategory={selectedCategory}
        onCategoryChange={setSelectedCategory}
        onCategoriesLoaded={setCategories}
      />
      <CampaignProductGrid products={filteredProducts} />
    </div>
  );
}
