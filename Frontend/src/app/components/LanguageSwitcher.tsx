import { useEffect, useRef, useState } from "react";
import { Globe } from "lucide-react";

import { useLanguage } from "../context/LanguageContext";

export function LanguageSwitcher() {
  const {
    languages,
    currentLanguage,
    isLoading,
    error,
    setLanguageCode,
  } = useLanguage();
  const [isOpen, setIsOpen] = useState(false);
  const rootRef = useRef<HTMLDivElement>(null);

  const activeLanguages = languages.filter((language) => language.is_active);

  useEffect(() => {
    if (!isOpen) {
      return;
    }

    function handlePointerDown(event: MouseEvent) {
      if (!rootRef.current?.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }

    document.addEventListener("mousedown", handlePointerDown);
    return () => document.removeEventListener("mousedown", handlePointerDown);
  }, [isOpen]);

  const label = currentLanguage
    ? currentLanguage.code.toUpperCase()
    : isLoading
      ? "…"
      : "—";

  function handleButtonClick() {
    if (activeLanguages.length === 0) {
      return;
    }

    setIsOpen((open) => !open);
  }

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={handleButtonClick}
        disabled={activeLanguages.length === 0 && !isLoading}
        aria-haspopup="listbox"
        aria-expanded={isOpen}
        aria-label={
          currentLanguage
            ? `Dil: ${currentLanguage.name_native}`
            : "Dil seçimi"
        }
        title={error ?? undefined}
        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-dark-graphite/50 text-warm-cream hover:bg-copper-gold/20 transition-colors disabled:opacity-50"
      >
        {currentLanguage?.flag_url ? (
          <img
            src={currentLanguage.flag_url}
            alt=""
            className="w-4 h-4 rounded-sm object-cover"
          />
        ) : (
          <Globe className="w-4 h-4" />
        )}
        <span className="text-sm">{label}</span>
      </button>

      {isOpen && activeLanguages.length > 0 && (
        <ul
          role="listbox"
          aria-label="Diller"
          className="absolute right-0 top-full z-50 mt-2 min-w-[11rem] overflow-hidden rounded-lg border border-white/10 bg-charcoal-black/95 shadow-xl backdrop-blur-xl"
        >
          {activeLanguages.map((language) => {
            const isSelected = currentLanguage?.id === language.id;

            return (
              <li key={language.id} role="option" aria-selected={isSelected}>
                <button
                  type="button"
                  onClick={() => {
                    setLanguageCode(language.code);
                    setIsOpen(false);
                  }}
                  className={`flex w-full items-center gap-2 px-3 py-2 text-left text-sm transition-colors ${
                    isSelected
                      ? "bg-copper-gold/20 text-copper-gold"
                      : "text-warm-cream hover:bg-white/5"
                  }`}
                >
                  {language.flag_url ? (
                    <img
                      src={language.flag_url}
                      alt=""
                      className="h-4 w-4 rounded-sm object-cover"
                    />
                  ) : (
                    <Globe className="h-4 w-4 shrink-0 opacity-70" />
                  )}
                  <span className="font-medium">{language.code.toUpperCase()}</span>
                  <span className="truncate text-warm-cream/70">
                    {language.name_native}
                  </span>
                </button>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}
