import {
  createContext,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";

import { fetchSiteSettings } from "../api/siteSettings";
import { useLanguage } from "./LanguageContext";
import type {
  ContactLabelGroup,
  ResolvedSiteHighlight,
  ResolvedSiteSettings,
  ResolvedWorkingHours,
  SiteContact,
  SiteHighlight,
  SiteSettings,
  SiteSettingsTranslation,
} from "../types/siteSettings";

interface SiteSettingsContextValue {
  settings: SiteSettings | null;
  resolved: ResolvedSiteSettings;
  isLoading: boolean;
  error: string | null;
}

const SiteSettingsContext = createContext<SiteSettingsContextValue | null>(null);

const EMPTY_WORKING_HOURS: ResolvedWorkingHours = {
  label: "",
  weekdayDays: "",
  weekdayHours: "",
  weekendDays: "",
  weekendHours: "",
  note: "",
};

const EMPTY_RESOLVED: ResolvedSiteSettings = {
  siteName: "",
  siteTitle: "",
  descriptionTitle: "",
  shortDescription: "",
  description: "",
  highlights: [],
  logoUrl: null,
  faviconUrl: null,
  copyright: "",
  addressContact: null,
  contactLabelGroups: [],
  workingHours: EMPTY_WORKING_HOURS,
};

function resolveContactTranslation(
  contact: SiteContact,
  languageCode: string,
): SiteContact {
  if (!contact.translations?.length) {
    return contact;
  }

  const normalizedCode = languageCode.toLowerCase();
  const exact = contact.translations.find(
    (translation) => translation.language.toLowerCase() === normalizedCode,
  );
  const fallback = contact.translations[0];
  const selected = exact ?? fallback;

  if (!selected) {
    return contact;
  }

  return {
    ...contact,
    label: selected.label || contact.label,
    link_text: selected.link_text || contact.link_text,
    value: selected.value || contact.value,
    display_text:
      contact.type === "address"
        ? selected.value || contact.value
        : (selected.link_text || contact.link_text)?.trim() ||
          selected.value ||
          contact.display_text ||
          contact.value,
    is_link: contact.is_link,
    icon: contact.icon,
  };
}

function pickPrimaryAddressContact(
  contacts: SiteContact[] | undefined,
  languageCode: string,
): SiteContact | null {
  if (!contacts?.length) {
    return null;
  }

  const addressContacts = contacts
    .filter((contact) => contact.type === "address")
    .map((contact) => resolveContactTranslation(contact, languageCode))
    .sort((left, right) => left.priority - right.priority || left.id - right.id);

  return addressContacts[0] ?? null;
}

function buildContactLabelGroups(
  contacts: SiteContact[] | undefined,
  languageCode: string,
): ContactLabelGroup[] {
  if (!contacts?.length) {
    return [];
  }

  const grouped = new Map<string, SiteContact[]>();

  contacts
    .filter((contact) => contact.type !== "address")
    .map((contact) => resolveContactTranslation(contact, languageCode))
    .sort((left, right) => left.priority - right.priority || left.id - right.id)
    .forEach((contact) => {
      const label = contact.label?.trim() || contact.type;
      const existing = grouped.get(label) ?? [];
      existing.push(contact);
      grouped.set(label, existing);
    });

  return Array.from(grouped.entries()).map(([label, labelContacts]) => ({
    label,
    contacts: labelContacts,
  }));
}

function resolveTranslation(
  settings: SiteSettings,
  languageCode: string,
): SiteSettingsTranslation | null {
  const normalizedCode = languageCode.toLowerCase();

  if (normalizedCode) {
    const exact = settings.translations.find(
      (translation) => translation.language.toLowerCase() === normalizedCode,
    );
    if (exact) {
      return exact;
    }
  }

  return settings.translations[0] ?? null;
}

function resolveHighlight(
  highlight: SiteHighlight,
  languageCode: string,
): ResolvedSiteHighlight {
  const normalizedCode = languageCode.toLowerCase();
  const exact = highlight.translations?.find(
    (translation) => translation.language.toLowerCase() === normalizedCode,
  );
  const fallback = highlight.translations?.[0];

  return {
    id: highlight.id,
    icon: highlight.icon,
    order: highlight.order,
    title: exact?.title ?? fallback?.title ?? highlight.title ?? "",
    description:
      exact?.description ??
      fallback?.description ??
      highlight.description ??
      "",
  };
}

function buildHighlights(
  highlights: SiteHighlight[] | undefined,
  languageCode: string,
): ResolvedSiteHighlight[] {
  if (!highlights?.length) {
    return [];
  }

  return highlights
    .map((highlight) => resolveHighlight(highlight, languageCode))
    .sort((left, right) => left.order - right.order || left.id - right.id);
}

function buildWorkingHours(
  settings: SiteSettings,
  translation: SiteSettingsTranslation | null,
): ResolvedWorkingHours {
  return {
    label: translation?.hours_label ?? settings.hours_label ?? "",
    weekdayDays: translation?.weekday_days ?? settings.weekday_days ?? "",
    weekdayHours: translation?.weekday_hours ?? settings.weekday_hours ?? "",
    weekendDays: translation?.weekend_days ?? settings.weekend_days ?? "",
    weekendHours: translation?.weekend_hours ?? settings.weekend_hours ?? "",
    note: translation?.hours_note ?? settings.hours_note ?? "",
  };
}

function buildResolved(
  settings: SiteSettings | null,
  languageCode: string,
): ResolvedSiteSettings {
  if (!settings) {
    return EMPTY_RESOLVED;
  }

  const translation = resolveTranslation(settings, languageCode);

  return {
    siteName: settings.name,
    siteTitle: translation?.title ?? settings.title ?? "",
    descriptionTitle:
      translation?.description_title ?? settings.description_title ?? "",
    shortDescription:
      translation?.short_description ?? settings.short_description ?? "",
    description: translation?.description ?? settings.description ?? "",
    highlights: buildHighlights(settings.highlights, languageCode),
    logoUrl: translation?.logo_url ?? settings.logo_url,
    faviconUrl: translation?.favicon_url ?? settings.favicon_url,
    copyright: translation?.copyright ?? settings.copyright ?? "",
    addressContact: pickPrimaryAddressContact(settings.contacts, languageCode),
    contactLabelGroups: buildContactLabelGroups(settings.contacts, languageCode),
    workingHours: buildWorkingHours(settings, translation),
  };
}

export function SiteSettingsProvider({ children }: { children: ReactNode }) {
  const { languageCode } = useLanguage();
  const [settings, setSettings] = useState<SiteSettings | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function loadSettings() {
      setIsLoading(true);
      setError(null);

      try {
        const data = await fetchSiteSettings(languageCode || undefined);
        if (!cancelled) {
          setSettings(data);
        }
      } catch (loadError) {
        if (!cancelled) {
          setError(
            loadError instanceof Error
              ? loadError.message
              : "Site ayarları yüklenemedi",
          );
          setSettings(null);
        }
      } finally {
        if (!cancelled) {
          setIsLoading(false);
        }
      }
    }

    loadSettings();

    return () => {
      cancelled = true;
    };
  }, [languageCode]);

  const resolved = useMemo(
    () => buildResolved(settings, languageCode),
    [settings, languageCode],
  );

  useEffect(() => {
    if (resolved.faviconUrl) {
      let link = document.querySelector<HTMLLinkElement>("link[rel='icon']");
      if (!link) {
        link = document.createElement("link");
        link.rel = "icon";
        document.head.appendChild(link);
      }
      link.href = resolved.faviconUrl;
    }
  }, [resolved.faviconUrl]);

  const value = useMemo<SiteSettingsContextValue>(
    () => ({
      settings,
      resolved,
      isLoading,
      error,
    }),
    [settings, resolved, isLoading, error],
  );

  return (
    <SiteSettingsContext.Provider value={value}>
      {children}
    </SiteSettingsContext.Provider>
  );
}

export function useSiteSettings() {
  const context = useContext(SiteSettingsContext);
  if (!context) {
    throw new Error("useSiteSettings must be used within SiteSettingsProvider");
  }
  return context;
}
