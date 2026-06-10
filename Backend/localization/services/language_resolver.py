from localization.models import Language


def resolve_active_language(code: str | None) -> Language | None:
    """Pick an active Language: explicit code (incl. BCP47), then default flag, then first by sort_order."""
    if code:
        raw = code.strip().split(";")[0].strip()
        if raw:
            lang = Language.objects.filter(code=raw, is_active=True).first()
            if lang:
                return lang
            short = raw.split("-")[0].lower()
            lang = Language.objects.filter(code=short, is_active=True).first()
            if lang:
                return lang
    return (
        Language.objects.filter(is_active=True, is_default=True).first()
        or Language.objects.filter(is_active=True).order_by("sort_order", "code").first()
    )
