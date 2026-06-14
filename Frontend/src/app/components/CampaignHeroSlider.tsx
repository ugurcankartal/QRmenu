import { useCallback, useEffect, useState } from "react";
import { motion } from "motion/react";
import { ChevronRight, Flame } from "lucide-react";
import { useNavigate } from "react-router";

import { fetchActiveCampaigns } from "../api/campaigns";
import { useLanguage } from "../context/LanguageContext";
import type { Campaign } from "../types/campaign";
import {
  Carousel,
  CarouselContent,
  CarouselItem,
  type CarouselApi,
} from "./ui/carousel";

const FALLBACK_IMAGE =
  "https://images.unsplash.com/photo-1777502286499-d91d3339be30?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080";

const AUTOPLAY_MS = 8000;

interface CampaignHeroSliderProps {
  campaigns?: Campaign[];
  onActiveCampaignChange?: (campaign: Campaign | null) => void;
  onReady?: (campaigns: Campaign[]) => void;
  showDots?: boolean;
  autoplay?: boolean;
}

function CampaignSlide({
  campaign,
  onExplore,
}: {
  campaign: Campaign;
  onExplore: (campaign: Campaign) => void;
}) {
  const imageSrc = campaign.image_url || FALLBACK_IMAGE;

  return (
    <div className="relative h-[50vh] min-h-[400px] w-full overflow-hidden">
      <div className="absolute inset-0">
        <img
          src={imageSrc}
          alt={campaign.name}
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-charcoal-black/60 via-charcoal-black/40 to-charcoal-black" />
      </div>

      <div className="relative flex h-full flex-col justify-end p-6 pb-12">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          {campaign.name ? (
            <div className="mb-3 flex items-center gap-2">
              <Flame className="h-5 w-5 text-deep-red" />
              <div className="text-sm font-medium uppercase tracking-wider text-copper-gold">
                {campaign.name}
              </div>
            </div>
          ) : null}

          {campaign.description ? (
            <div
              className="campaign-hero-description rich-text-content mb-4 max-w-2xl leading-normal text-warm-cream normal-case [&_*]:normal-case [&_a]:text-copper-gold [&_a]:underline [&_em]:italic [&_p]:m-0 [&_p+p]:mt-2 [&_strong]:font-semibold"
              dangerouslySetInnerHTML={{ __html: campaign.description }}
            />
          ) : null}

          {campaign.badge ? (
            <button
              type="button"
              onClick={() => onExplore(campaign)}
              className="inline-flex items-center gap-2 rounded-full bg-copper-gold px-8 py-4 text-charcoal-black shadow-lg transition-all hover:bg-copper-gold/90 hover:shadow-copper-gold/20"
            >
              <span className="font-semibold">{campaign.badge}</span>
              <ChevronRight className="h-5 w-5" />
            </button>
          ) : null}
        </motion.div>
      </div>
    </div>
  );
}

export function CampaignHeroSlider({
  campaigns: campaignsProp,
  onActiveCampaignChange,
  onReady,
  showDots = true,
  autoplay = true,
}: CampaignHeroSliderProps) {
  const navigate = useNavigate();
  const { languageCode } = useLanguage();
  const [fetchedCampaigns, setFetchedCampaigns] = useState<Campaign[]>([]);
  const [isLoading, setIsLoading] = useState(!campaignsProp);
  const [api, setApi] = useState<CarouselApi>();
  const [selectedIndex, setSelectedIndex] = useState(0);

  const campaigns = campaignsProp ?? fetchedCampaigns;

  useEffect(() => {
    if (campaignsProp) {
      onReady?.(campaignsProp);
      return;
    }

    let cancelled = false;

    async function loadCampaigns() {
      setIsLoading(true);
      try {
        const data = await fetchActiveCampaigns(languageCode);
        if (!cancelled) {
          setFetchedCampaigns(data);
          setSelectedIndex(0);
          onReady?.(data);
        }
      } catch {
        if (!cancelled) {
          setFetchedCampaigns([]);
          onReady?.([]);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    void loadCampaigns();

    return () => {
      cancelled = true;
    };
  }, [campaignsProp, languageCode]);

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
  }, [api, campaigns]);

  useEffect(() => {
    onActiveCampaignChange?.(campaigns[selectedIndex] ?? null);
  }, [campaigns, selectedIndex, onActiveCampaignChange]);

  useEffect(() => {
    if (!api || campaigns.length <= 1 || !autoplay) return;

    const timer = window.setInterval(() => {
      if (api.canScrollNext()) {
        api.scrollNext();
      } else {
        api.scrollTo(0);
      }
    }, AUTOPLAY_MS);

    return () => window.clearInterval(timer);
  }, [api, campaigns.length, autoplay]);

  const goToSlide = useCallback(
    (index: number) => {
      api?.scrollTo(index);
    },
    [api],
  );

  const handleExplore = useCallback(
    (campaign: Campaign) => {
      if (campaign.slug) {
        navigate(`/${campaign.slug}`);
      }
    },
    [navigate],
  );

  if (isLoading) {
    return (
      <section
        data-campaign-hero
        className="relative h-[50vh] min-h-[400px] overflow-hidden bg-charcoal-black"
      >
        <div className="absolute inset-0 animate-pulse bg-charcoal-black/80" />
      </section>
    );
  }

  if (campaigns.length === 0) {
    return null;
  }

  return (
    <section data-campaign-hero className="relative overflow-hidden">
      <Carousel
        setApi={setApi}
        opts={{ loop: campaigns.length > 1 }}
        className="w-full"
      >
        <CarouselContent className="-ml-0">
          {campaigns.map((campaign) => (
            <CarouselItem key={campaign.id} className="basis-full pl-0">
              <CampaignSlide campaign={campaign} onExplore={handleExplore} />
            </CarouselItem>
          ))}
        </CarouselContent>

        {showDots && campaigns.length > 1 ? (
          <div className="absolute bottom-4 left-1/2 z-10 flex -translate-x-1/2 items-center gap-2">
            {campaigns.map((campaign, index) => (
              <button
                key={campaign.id}
                type="button"
                aria-label={`Kampanya ${index + 1}`}
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
        ) : null}
      </Carousel>
    </section>
  );
}
