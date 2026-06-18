export interface SiteSettingsTranslation {
  language: string;
  title: string;
  keywords: string;
  description_title: string;
  short_description: string;
  description: string;
  copyright: string;
  hours_label: string;
  weekday_days: string;
  weekday_hours: string;
  weekend_days: string;
  weekend_hours: string;
  hours_note: string;
  favicon_url: string | null;
  logo_url: string | null;
  about_image_url: string | null;
}

export interface SiteHighlightTranslation {
  language: string;
  title: string;
  description: string;
}

export interface SiteHighlight {
  id: number;
  icon: string;
  order: number;
  title: string;
  description: string;
  translations: SiteHighlightTranslation[];
}

export interface SiteContactTranslation {
  language: string;
  label: string;
  link_text: string;
  value: string;
}

export interface SiteContact {
  id: number;
  type: string;
  icon: string;
  label: string;
  link_text: string;
  value: string;
  display_text: string;
  is_link: boolean;
  priority: number;
  translations: SiteContactTranslation[];
}

export interface ContactLabelGroup {
  label: string;
  contacts: SiteContact[];
}

export interface SiteSettings {
  id: number;
  name: string;
  title: string;
  keywords: string;
  description_title: string;
  short_description: string;
  description: string;
  copyright: string;
  hours_label: string;
  weekday_days: string;
  weekday_hours: string;
  weekend_days: string;
  weekend_hours: string;
  hours_note: string;
  favicon_url: string | null;
  logo_url: string | null;
  about_image_url: string | null;
  translations: SiteSettingsTranslation[];
  contacts: SiteContact[];
  highlights: SiteHighlight[];
}

export interface ResolvedWorkingHours {
  label: string;
  weekdayDays: string;
  weekdayHours: string;
  weekendDays: string;
  weekendHours: string;
  note: string;
}

export interface ResolvedSiteHighlight {
  id: number;
  icon: string;
  title: string;
  description: string;
  order: number;
}

export interface ResolvedSiteSettings {
  siteName: string;
  siteTitle: string;
  descriptionTitle: string;
  shortDescription: string;
  description: string;
  highlights: ResolvedSiteHighlight[];
  logoUrl: string | null;
  faviconUrl: string | null;
  aboutImageUrl: string | null;
  copyright: string;
  addressContact: SiteContact | null;
  contactLabelGroups: ContactLabelGroup[];
  workingHours: ResolvedWorkingHours;
}
