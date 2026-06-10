import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { fetchLanguages } from "../api/languages";
import {
  LANGUAGE_STORAGE_KEY,
  LANGUAGE_USER_PICKED_KEY,
} from "../config";
import type { Language } from "../types/language";

interface LanguageContextValue {
  languages: Language[];
  currentLanguage: Language | null;
  languageCode: string;
  isLoading: boolean;
  error: string | null;
  setLanguageCode: (code: string) => void;
  cycleLanguage: () => void;
}

const LanguageContext = createContext<LanguageContextValue | null>(null);

function getActiveLanguages(languages: Language[]): Language[] {
  return languages.filter((language) => language.is_active);
}

function pickInitialLanguage(languages: Language[]): Language | null {
  const active = getActiveLanguages(languages);
  if (active.length === 0) {
    return null;
  }

  const userPicked = localStorage.getItem(LANGUAGE_USER_PICKED_KEY) === "1";
  const stored = localStorage.getItem(LANGUAGE_STORAGE_KEY);

  if (userPicked && stored) {
    const storedMatch = active.find(
      (language) => language.code.toLowerCase() === stored.toLowerCase(),
    );
    if (storedMatch) {
      return storedMatch;
    }
  }

  return active.find((language) => language.is_default) ?? active[0];
}

function rememberLanguageChoice(language: Language) {
  localStorage.setItem(LANGUAGE_STORAGE_KEY, language.code);
  localStorage.setItem(LANGUAGE_USER_PICKED_KEY, "1");
}

export function LanguageProvider({ children }: { children: ReactNode }) {
  const [languages, setLanguages] = useState<Language[]>([]);
  const [currentLanguage, setCurrentLanguage] = useState<Language | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadLanguages() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchLanguages();
        if (cancelled) {
          return;
        }

        setLanguages(data);
        setCurrentLanguage((previous) => {
          if (previous) {
            const stillValid = data.find((language) => language.id === previous.id);
            if (stillValid) {
              return stillValid;
            }
          }
          return pickInitialLanguage(data);
        });
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error ? loadError.message : "Diller yüklenemedi",
          );
          setLanguages([]);
          setCurrentLanguage(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadLanguages();

    return () => {
      cancelled = true;
    };
  }, []);

  useEffect(() => {
    if (currentLanguage) {
      localStorage.setItem(LANGUAGE_STORAGE_KEY, currentLanguage.code);
    }
  }, [currentLanguage]);

  const setLanguageCode = useCallback(
    (code: string) => {
      const match = languages.find(
        (language) =>
          language.is_active &&
          language.code.toLowerCase() === code.toLowerCase(),
      );
      if (match) {
        rememberLanguageChoice(match);
        setCurrentLanguage(match);
      }
    },
    [languages],
  );

  const cycleLanguage = useCallback(() => {
    const active = getActiveLanguages(languages);
    if (active.length === 0) {
      return;
    }

    if (!currentLanguage) {
      const initial = pickInitialLanguage(active);
      if (initial) {
        setCurrentLanguage(initial);
      }
      return;
    }

    const currentIndex = active.findIndex(
      (language) => language.id === currentLanguage.id,
    );
    const nextIndex = currentIndex >= 0 ? (currentIndex + 1) % active.length : 0;
    const nextLanguage = active[nextIndex];
    rememberLanguageChoice(nextLanguage);
    setCurrentLanguage(nextLanguage);
  }, [currentLanguage, languages]);

  const value = useMemo<LanguageContextValue>(
    () => ({
      languages,
      currentLanguage,
      languageCode: currentLanguage?.code ?? "",
      isLoading,
      error,
      setLanguageCode,
      cycleLanguage,
    }),
    [
      languages,
      currentLanguage,
      isLoading,
      error,
      setLanguageCode,
      cycleLanguage,
    ],
  );

  return (
    <LanguageContext.Provider value={value}>{children}</LanguageContext.Provider>
  );
}

export function useLanguage() {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error("useLanguage must be used within LanguageProvider");
  }
  return context;
}
