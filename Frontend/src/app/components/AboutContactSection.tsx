import { useMemo } from "react";
import { Clock } from "lucide-react";

import { useSiteSettings } from "../context/SiteSettingsContext";
import { useI18n } from "../context/I18nContext";
import type { ContactLabelGroup, SiteContact } from "../types/siteSettings";
import {
  getContactDisplayContent,
  getContactHref,
  isExternalContactLink,
  SOCIAL_CONTACT_TYPES,
} from "../utils/contactLinks";
import { ContactIcon } from "./ContactIcon";

function ContactDetailRow({
  icon,
  label,
  contacts,
}: {
  icon: string;
  label: string;
  contacts: SiteContact[];
}) {
  return (
    <div className="flex items-start gap-4">
      <div className="p-3 rounded-xl bg-dark-graphite/50">
        <ContactIcon name={icon} className="w-6 h-6 text-copper-gold" />
      </div>
      <div>
        <h4 className="text-warm-cream font-semibold mb-1">{label}</h4>
        {contacts.map((contact) => {
          const content = getContactDisplayContent(contact);
          const href = getContactHref(contact);
          const lines = content.split(/\r?\n/).filter(Boolean);

          if (href) {
            return (
              <a
                key={contact.id}
                href={href}
                {...(isExternalContactLink(contact.type)
                  ? { target: "_blank", rel: "noopener noreferrer" }
                  : {})}
                className="block text-warm-cream/70 hover:text-copper-gold transition-colors mb-1 last:mb-0"
              >
                {content}
              </a>
            );
          }

          return lines.map((line, index) => (
            <p
              key={`${contact.id}-${index}`}
              className="text-warm-cream/70 mb-1 last:mb-0"
            >
              {line}
            </p>
          ));
        })}
      </div>
    </div>
  );
}

function filterDetailGroups(groups: ContactLabelGroup[]): ContactLabelGroup[] {
  return groups
    .map((group) => ({
      ...group,
      contacts: group.contacts.filter(
        (contact) => !SOCIAL_CONTACT_TYPES.has(contact.type),
      ),
    }))
    .filter((group) => group.contacts.length > 0);
}

export function AboutContactSection() {
  const { t, isLoading: isI18nLoading } = useI18n();
  const { resolved, isLoading } = useSiteSettings();
  const { addressContact, contactLabelGroups, workingHours } = resolved;

  const detailGroups = useMemo(
    () => filterDetailGroups(contactLabelGroups),
    [contactLabelGroups],
  );

  const socialContacts = useMemo(
    () =>
      contactLabelGroups
        .flatMap((group) => group.contacts)
        .filter((contact) => SOCIAL_CONTACT_TYPES.has(contact.type))
        .sort((left, right) => left.priority - right.priority || left.id - right.id),
    [contactLabelGroups],
  );

  return (
    <section className="px-4 py-12">
      <div className="max-w-4xl mx-auto">
        <h3 className="text-2xl text-warm-cream mb-8 text-center">
          {isI18nLoading ? "…" : t("about.visit_us", "Visit Us")}
        </h3>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <div className="space-y-6">
            {addressContact && (
              <ContactDetailRow
                icon={addressContact.icon || "MapPin"}
                label={addressContact.label || "Location"}
                contacts={[addressContact]}
              />
            )}

            {detailGroups.map((group) => (
              <ContactDetailRow
                key={group.label}
                icon={group.contacts[0]?.icon || "Link"}
                label={group.label}
                contacts={group.contacts}
              />
            ))}

            {isLoading && !addressContact && detailGroups.length === 0 && (
              <p className="text-warm-cream/70">…</p>
            )}
          </div>

          <div className="space-y-6">
            {(workingHours.label ||
              workingHours.weekdayDays ||
              workingHours.weekdayHours ||
              workingHours.weekendDays ||
              workingHours.weekendHours) && (
              <div className="p-6 rounded-2xl bg-gradient-to-b from-dark-graphite/70 to-dark-graphite/50 backdrop-blur-md border border-white/10">
                <h4 className="text-warm-cream font-semibold mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5 text-copper-gold" />
                  {workingHours.label || "Opening Hours"}
                </h4>
                <div className="space-y-3">
                  {(workingHours.weekdayDays || workingHours.weekdayHours) && (
                    <div className="flex justify-between gap-4">
                      <span className="text-warm-cream/70">
                        {workingHours.weekdayDays}
                      </span>
                      <span className="text-warm-cream">{workingHours.weekdayHours}</span>
                    </div>
                  )}
                  {(workingHours.weekendDays || workingHours.weekendHours) && (
                    <div className="flex justify-between gap-4">
                      <span className="text-warm-cream/70">
                        {workingHours.weekendDays}
                      </span>
                      <span className="text-warm-cream">{workingHours.weekendHours}</span>
                    </div>
                  )}
                  {workingHours.note && (
                    <p className="text-warm-cream/50 text-sm pt-2">{workingHours.note}</p>
                  )}
                </div>
              </div>
            )}

            {socialContacts.length > 0 && (
              <div>
                <h4 className="mb-4 font-semibold text-warm-cream">
                  {t("about.follow-us", "Follow Us")}
                </h4>
                <div className="flex flex-wrap gap-3">
                  {socialContacts.map((contact) => {
                    const href = getContactHref(contact);
                    const label = contact.display_text || contact.label || contact.type;

                    if (!href) {
                      return (
                        <div
                          key={contact.id}
                          className="p-3 rounded-xl bg-dark-graphite/50"
                          title={label}
                        >
                          <ContactIcon
                            name={contact.icon}
                            className="w-6 h-6 text-copper-gold"
                          />
                        </div>
                      );
                    }

                    return (
                      <a
                        key={contact.id}
                        href={href}
                        target="_blank"
                        rel="noopener noreferrer"
                        title={label}
                        className="p-3 rounded-xl bg-dark-graphite/50 hover:bg-copper-gold/20 transition-colors"
                      >
                        <ContactIcon
                          name={contact.icon}
                          className="w-6 h-6 text-copper-gold"
                        />
                      </a>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </section>
  );
}
