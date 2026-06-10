import type { LucideIcon } from "lucide-react";
import {
  Facebook,
  Globe,
  Instagram,
  Link,
  Linkedin,
  Mail,
  MapPin,
  MessageCircle,
  Music,
  Phone,
  Printer,
  Twitter,
  Youtube,
} from "lucide-react";

const ICON_MAP: Record<string, LucideIcon> = {
  Phone,
  Printer,
  Mail,
  MapPin,
  Instagram,
  Facebook,
  Twitter,
  MessageCircle,
  Youtube,
  Linkedin,
  Music,
  Globe,
  Link,
};

interface ContactIconProps {
  name: string;
  className?: string;
}

export function ContactIcon({ name, className }: ContactIconProps) {
  const Icon = ICON_MAP[name] ?? Link;
  return <Icon className={className} aria-hidden="true" />;
}

export function normalizeContactUrl(value: string): string {
  const trimmed = value.trim();
  if (trimmed.toLowerCase().startsWith("www.")) {
    return `https://${trimmed}`;
  }
  return trimmed;
}
