import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { fetchI18nBundle } from "../api/i18n";
import { useLanguage } from "./LanguageContext";

interface I18nContextValue {
  strings: Record<string, string>;
  isLoading: boolean;
  error: string | null;
  t: (key: string, fallback?: string) => string;
}

const I18nContext = createContext<I18nContextValue | null>(null);

export function I18nProvider({ children }: { children: ReactNode }) {
  const { languageCode } = useLanguage();
  const [strings, setStrings] = useState<Record<string, string>>({});
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadBundle() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchI18nBundle(languageCode || undefined);
        if (!cancelled) {
          setStrings(data.strings ?? {});
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "UI çevirileri yüklenemedi",
          );
          setStrings({});
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadBundle();

    return () => {
      cancelled = true;
    };
  }, [languageCode]);

  const t = useCallback(
    (key: string, fallback?: string) => strings[key] ?? fallback ?? key,
    [strings],
  );

  const value = useMemo<I18nContextValue>(
    () => ({
      strings,
      isLoading,
      error,
      t,
    }),
    [strings, isLoading, error, t],
  );

  return <I18nContext.Provider value={value}>{children}</I18nContext.Provider>;
}

export function useI18n() {
  const context = useContext(I18nContext);
  if (!context) {
    throw new Error("useI18n must be used within I18nProvider");
  }
  return context;
}
