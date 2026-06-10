import { normalizeContactUrl } from "../components/ContactIcon";
import type { SiteContact } from "../types/siteSettings";

export const SOCIAL_CONTACT_TYPES = new Set([
  "instagram",
  "facebook",
  "twitter",
  "linkedin",
  "youtube",
  "tiktok",
  "whatsapp",
  "website",
]);

function normalizePhoneHref(value: string): string {
  const digits = value.replace(/[^\d+]/g, "");
  return digits ? `tel:${digits}` : "";
}

export function getContactHref(contact: SiteContact): string | null {
  const value = contact.value?.trim();
  if (!value) {
    return null;
  }

  switch (contact.type) {
    case "phone":
    case "fax":
      return normalizePhoneHref(value);
    case "email":
      return `mailto:${value}`;
    default:
      return contact.is_link ? normalizeContactUrl(value) : null;
  }
}

export function isExternalContactLink(type: string): boolean {
  return type !== "phone" && type !== "email" && type !== "fax";
}

export function getContactDisplayContent(contact: SiteContact): string {
  if (contact.type === "address") {
    return contact.value;
  }
  return contact.display_text || contact.value;
}
