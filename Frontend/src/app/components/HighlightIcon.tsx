import {
  Award,
  Clock,
  Heart,
  MapPin,
  Sparkles,
  Star,
  Users,
  type LucideIcon,
} from "lucide-react";

import { ContactIcon } from "./ContactIcon";

const HIGHLIGHT_ICON_MAP: Record<string, LucideIcon> = {
  Award,
  Clock,
  MapPin,
  Sparkles,
  Heart,
  Star,
  Users,
};

interface HighlightIconProps {
  name: string;
  className?: string;
}

export function HighlightIcon({ name, className }: HighlightIconProps) {
  const Icon = HIGHLIGHT_ICON_MAP[name];
  if (Icon) {
    return <Icon className={className} aria-hidden="true" />;
  }
  return <ContactIcon name={name} className={className} />;
}
