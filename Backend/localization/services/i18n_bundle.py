from typing import Protocol

from localization.models import UiString
from localization.services.language_resolver import resolve_active_language


class I18nBundleProvider(Protocol):
    def build_bundle(self, language_code: str | None) -> tuple[str | None, dict[str, str]]:
        """Return (resolved_language_code, flat key -> text)."""
        ...


class DatabaseI18nBundleProvider:
    """Loads UI strings from DB (admin-editable)."""

    def build_bundle(self, language_code: str | None) -> tuple[str | None, dict[str, str]]:
        language = resolve_active_language(language_code)
        if language is None:
            return None, {}
        rows = UiString.objects.filter(language=language).select_related("key")
        return language.code, {row.key.key: row.text for row in rows}


default_i18n_bundle_provider = DatabaseI18nBundleProvider()
