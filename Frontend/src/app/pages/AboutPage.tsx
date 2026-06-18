import { motion } from "motion/react";

import { AboutContactSection } from "../components/AboutContactSection";
import { HighlightIcon } from "../components/HighlightIcon";
import { useSiteSettings } from "../context/SiteSettingsContext";

const FALLBACK_HERO_IMAGE =
  "https://images.unsplash.com/photo-1691078472732-a7cd5037a2a7?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&q=80&w=1080";

const RICH_TEXT_CLASS =
  "rich-text-content leading-relaxed text-warm-cream/70 text-lg normal-case [&_*]:normal-case [&_a]:text-copper-gold [&_a]:underline [&_em]:italic [&_h2]:mb-3 [&_h2]:mt-6 [&_h2]:text-2xl [&_h2]:text-warm-cream [&_h3]:mb-2 [&_h3]:mt-4 [&_h3]:text-xl [&_h3]:text-warm-cream [&_li]:mb-1 [&_ol]:my-4 [&_ol]:list-decimal [&_ol]:pl-6 [&_p]:m-0 [&_p+p]:mt-4 [&_strong]:font-semibold [&_ul]:my-4 [&_ul]:list-disc [&_ul]:pl-6";

export function AboutPage() {
  const { resolved, isLoading } = useSiteSettings();
  const { descriptionTitle, shortDescription, description, highlights, aboutImageUrl } =
    resolved;
  const heroImage = aboutImageUrl || FALLBACK_HERO_IMAGE;

  return (
    <div className="min-h-screen">
      <section className="relative h-64 overflow-hidden">
        <img
          src={heroImage}
          alt={descriptionTitle || resolved.siteTitle || "About"}
          className="h-full w-full object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-b from-charcoal-black/60 to-charcoal-black" />
        <div className="absolute inset-0 flex items-center justify-center">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-3xl px-4 text-center"
          >
            <h2 className="mb-2 text-4xl text-warm-cream">
              {descriptionTitle || (isLoading ? "…" : "")}
            </h2>
            {shortDescription ? (
              <p className="text-lg text-copper-gold">{shortDescription}</p>
            ) : isLoading ? (
              <p className="text-lg text-copper-gold">…</p>
            ) : null}
          </motion.div>
        </div>
      </section>

      {description ? (
        <section className="px-4 py-12">
          <div className="mx-auto max-w-4xl">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              className={RICH_TEXT_CLASS}
              dangerouslySetInnerHTML={{ __html: description }}
            />
          </div>
        </section>
      ) : isLoading ? (
        <section className="px-4 py-12">
          <div className="mx-auto max-w-4xl space-y-4">
            <div className="h-6 animate-pulse rounded bg-dark-graphite/50" />
            <div className="h-6 animate-pulse rounded bg-dark-graphite/50" />
            <div className="h-6 w-2/3 animate-pulse rounded bg-dark-graphite/50" />
          </div>
        </section>
      ) : null}

      {isLoading && highlights.length === 0 ? (
        <section className="px-4 py-12">
          <div className="mx-auto grid max-w-4xl grid-cols-1 gap-6 md:grid-cols-3">
            {Array.from({ length: 3 }).map((_, index) => (
              <div
                key={index}
                className="h-40 animate-pulse rounded-2xl bg-dark-graphite/50"
              />
            ))}
          </div>
        </section>
      ) : highlights.length > 0 ? (
        <section className="px-4 py-12">
          <div className="mx-auto grid max-w-4xl grid-cols-1 gap-6 md:grid-cols-3">
            {highlights.map((highlight, index) => (
              <motion.div
                key={highlight.id}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 }}
                className="rounded-2xl border border-white/10 bg-gradient-to-b from-dark-graphite/70 to-dark-graphite/50 p-6 backdrop-blur-md"
              >
                <HighlightIcon
                  name={highlight.icon}
                  className="mb-4 h-12 w-12 text-copper-gold"
                />
                {highlight.title ? (
                  <h4 className="mb-2 font-semibold text-warm-cream">
                    {highlight.title}
                  </h4>
                ) : null}
                {highlight.description ? (
                  <p className="text-sm text-warm-cream/60">
                    {highlight.description}
                  </p>
                ) : null}
              </motion.div>
            ))}
          </div>
        </section>
      ) : null}

      <AboutContactSection />
    </div>
  );
}
