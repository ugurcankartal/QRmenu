import { useCallback, useEffect, useMemo, useState } from "react";
import { motion } from "motion/react";
import { Award, ChevronRight } from "lucide-react";
import { useNavigate } from "react-router";

import { fetchChefRecommendations } from "../api/chefRecommendations";
import { useI18n } from "../context/I18nContext";
import { useLanguage } from "../context/LanguageContext";
import type { ChefRecommendation } from "../types/chefRecommendation";
import type { Product } from "../types/product";
import {
  getFeaturedProduct,
  getRecommendationProducts,
} from "../utils/chefRecommendation";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from "./ui/carousel";

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1643941217351-bc293885bade?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080";

const AUTOPLAY_MS = 8000;

function formatProductPrice(product: Product): string {
  const amount = Number(product.price);
  const formatted = Number.isFinite(amount)
    ? amount.toLocaleString(undefined, {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
      })
    : product.price;

  const symbol = product.currency_symbol ?? "₺";
  return `${symbol}${formatted}`;
}

function formatPrepTime(
  prepTime: number | null | undefined,
  languageCode: string,
): string {
  if (prepTime == null) {
    return "—";
  }

  return languageCode === "tr" ? `${prepTime} dk` : `${prepTime} mins`;
}

function FeaturedDishSlide({
  recommendation,
  onViewDetails,
}: {
  recommendation: ChefRecommendation;
  onViewDetails: (recommendation: ChefRecommendation) => void;
}) {
  const { t } = useI18n();
  const { languageCode } = useLanguage();
  const featuredProduct = getFeaturedProduct(recommendation);
  const imageSrc = recommendation.image_url || FALLBACK_IMAGE;

  return (
    <div className="grid gap-0 md:grid-cols-2">
      <div className="relative aspect-square overflow-hidden md:aspect-auto">
        <img
          src={imageSrc}
          alt={recommendation.title || featuredProduct?.name || ""}
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-r from-transparent via-transparent to-charcoal-black/60 md:to-charcoal-black" />
      </div>

      <div className="flex flex-col justify-center p-8 md:p-12">
        {recommendation.title ? (
          <div className="mb-4 flex items-center gap-2">
            <Award className="h-6 w-6 text-copper-gold" />
            <span className="text-sm font-medium uppercase tracking-wider text-copper-gold">
              {recommendation.title}
            </span>
          </div>
        ) : null}

        {featuredProduct?.name ? (
          <h3 className="mb-4 text-4xl leading-tight text-warm-cream md:text-5xl">
            {featuredProduct.name}
          </h3>
        ) : null}

        {recommendation.summary ? (
          <p className="mb-6 text-lg leading-relaxed text-warm-cream/80">
            {recommendation.summary}
          </p>
        ) : null}

        {featuredProduct ? (
          <div className="mb-8 flex items-center gap-6">
            <div>
              <p className="mb-1 text-sm text-warm-cream/60">
                {t("about.price", "Price")}
              </p>
              <p className="text-3xl font-semibold text-copper-gold">
                {formatProductPrice(featuredProduct)}
              </p>
            </div>
            <div className="h-12 w-px bg-white/20" />
            <div>
              <p className="mb-1 text-sm text-warm-cream/60">
                {t("about.prep-time", "Prep Time")}
              </p>
              <p className="text-lg font-medium text-warm-cream">
                {formatPrepTime(featuredProduct.prep_time, languageCode)}
              </p>
            </div>
          </div>
        ) : null}

        {recommendation.slug ? (
          <button
            type="button"
            onClick={() => onViewDetails(recommendation)}
            className="inline-flex items-center gap-2 self-start rounded-full bg-copper-gold px-8 py-4 text-charcoal-black shadow-lg transition-all hover:bg-copper-gold/90"
          >
            <span className="font-semibold">
              {t("about.view-details", "View Details")}
            </span>
            <ChevronRight className="h-5 w-5" />
          </button>
        ) : null}
      </div>
    </div>
  );
}

export function FeaturedDish() {
  const navigate = useNavigate();
  const { languageCode } = useLanguage();
  const [recommendations, setRecommendations] = useState<ChefRecommendation[]>(
    [],
  );
  const [isLoading, setIsLoading] = useState(true);
  const [api, setApi] = useState<CarouselApi>();
  const [selectedIndex, setSelectedIndex] = useState(0);

  useEffect(() => {
    let cancelled = false;

    async function loadRecommendations() {
      setIsLoading(true);
      try {
        const data = await fetchChefRecommendations(languageCode);
        if (!cancelled) {
          setRecommendations(data);
          setSelectedIndex(0);
        }
      } catch {
        if (!cancelled) {
          setRecommendations([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadRecommendations();

    return () => {
      cancelled = true;
    };
  }, [languageCode]);

  useEffect(() => {
    if (!api) return;

    const onSelect = () => {
      setSelectedIndex(api.selectedScrollSnap());
    };

    onSelect();
    api.on("select", onSelect);
    api.on("reInit", onSelect);

    return () => {
      api.off("select", onSelect);
      api.off("reInit", onSelect);
    };
  }, [api, recommendations]);

  useEffect(() => {
    if (!api || recommendations.length <= 1) return;

    const timer = window.setInterval(() => {
      if (api.canScrollNext()) {
        api.scrollNext();
      } else {
        api.scrollTo(0);
      }
    }, AUTOPLAY_MS);

    return () => window.clearInterval(timer);
  }, [api, recommendations.length]);

  const goToSlide = useCallback(
    (index: number) => {
      api?.scrollTo(index);
    },
    [api],
  );

  const handleViewDetails = useCallback(
    (recommendation: ChefRecommendation) => {
      if (recommendation.slug) {
        navigate(`/${recommendation.slug}`);
      }
    },
    [navigate],
  );

  const visibleRecommendations = useMemo(
    () =>
      recommendations.filter(
        (recommendation) => getRecommendationProducts(recommendation).length > 0,
      ),
    [recommendations],
  );

  if (isLoading) {
    return (
      <section className="mt-8 px-4 py-12">
        <div className="mx-auto max-w-7xl">
          <div className="h-[420px] animate-pulse rounded-3xl bg-dark-graphite/60" />
        </div>
      </section>
    );
  }

  if (visibleRecommendations.length === 0) {
    return null;
  }

  const hasMultiple = visibleRecommendations.length > 1;

  return (
    <section className="mt-8 px-4 py-12">
      <div className="mx-auto max-w-7xl">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="relative overflow-hidden rounded-3xl border border-copper-gold/30 bg-gradient-to-br from-dark-graphite to-charcoal-black shadow-2xl"
        >
          {hasMultiple ? (
            <Carousel setApi={setApi} opts={{ loop: true }} className="w-full">
              <CarouselContent className="-ml-0">
                {visibleRecommendations.map((recommendation) => (
                  <CarouselItem
                    key={recommendation.id}
                    className="basis-full pl-0"
                  >
                    <FeaturedDishSlide
                      recommendation={recommendation}
                      onViewDetails={handleViewDetails}
                    />
                  </CarouselItem>
                ))}
              </CarouselContent>

              <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 items-center gap-2">
                {visibleRecommendations.map((recommendation, index) => (
                  <button
                    key={recommendation.id}
                    type="button"
                    aria-label={`Şefin önerisi ${index + 1}`}
                    aria-current={selectedIndex === index ? "true" : undefined}
                    onClick={() => goToSlide(index)}
                    className={`h-2 rounded-full transition-all ${
                      selectedIndex === index
                        ? "w-6 bg-copper-gold"
                        : "w-2 bg-warm-cream/50 hover:bg-warm-cream/80"
                    }`}
                  />
                ))}
              </div>
            </Carousel>
          ) : (
            <FeaturedDishSlide
              recommendation={visibleRecommendations[0]}
              onViewDetails={handleViewDetails}
            />
          )}
        </motion.div>
      </div>
    </section>
  );
}
