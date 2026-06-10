import { ContactIcon } from "./ContactIcon";
import type { SiteContact } from "../types/siteSettings";
import {
  getContactDisplayContent,
  getContactHref,
  isExternalContactLink,
} from "../utils/contactLinks";

interface ContactValueProps {
  contact: SiteContact;
  className?: string;
}

export function ContactValue({ contact, className = "text-warm-cream/70 text-sm" }: ContactValueProps) {
  const content = getContactDisplayContent(contact);
  const href = getContactHref(contact);

  if (href) {
    return (
      <div className="mb-2 last:mb-0">
        <a
          href={href}
          {...(isExternalContactLink(contact.type)
            ? { target: "_blank", rel: "noopener noreferrer" }
            : {})}
          className={`${className} inline-flex items-center gap-2 hover:text-copper-gold transition-colors`}
        >
          <ContactIcon name={contact.icon} className="w-4 h-4 shrink-0" />
          <span>{content}</span>
        </a>
      </div>
    );
  }

  return (
    <p className={`${className} inline-flex items-center gap-2 mb-2 last:mb-0`}>
      <ContactIcon name={contact.icon} className="w-4 h-4 shrink-0" />
      <span>{content}</span>
    </p>
  );
}
