from __future__ import annotations

import json
import os
import time
from typing import Any

from django.db import transaction

from api.content_translation_maps import (
    should_preserve_contact_value,
    should_preserve_link_text,
)
from core.groq_client import GroqAPIError, chat_completion, parse_json_response
from localization.models import Language, UiString


def get_default_language() -> Language | None:
    return (
        Language.objects.filter(is_active=True, is_default=True).first()
        or Language.objects.filter(is_active=True, code="tr").first()
        or Language.objects.filter(is_active=True).order_by("sort_order", "code").first()
    )


def get_target_languages(default_language: Language) -> list[Language]:
    return list(
        Language.objects.filter(is_active=True)
        .exclude(pk=default_language.pk)
        .order_by("sort_order", "code")
    )


def _non_empty_fields(row: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in row.items()
        if value not in (None, "", [], {})
    }


def translate_record_batch(
    batch: dict[str, dict[str, Any]],
    *,
    source_language: Language,
    target_language: Language,
    html_fields: frozenset[str] = frozenset(),
    list_fields: frozenset[str] = frozenset(),
    preserve_fields: frozenset[str] = frozenset(),
    context: str = "",
) -> dict[str, dict[str, Any]]:
    if not batch:
        return {}

    rules = [
        "Return ONLY valid JSON.",
        "Top-level keys must exactly match the input record IDs.",
        "Each record must keep the same field names as the input.",
        "Do not add or remove fields.",
        "Preserve brand names, proper nouns, URLs, emails, phone numbers, and @handles unchanged.",
    ]
    if html_fields:
        rules.append(
            f"Preserve HTML tags and attributes in these fields: {', '.join(sorted(html_fields))}."
        )
    if list_fields:
        rules.append(
            f"These fields are JSON arrays; return translated arrays with the same length: {', '.join(sorted(list_fields))}."
        )
    if preserve_fields:
        rules.append(
            f"Copy these fields unchanged from input: {', '.join(sorted(preserve_fields))}."
        )
    if context:
        rules.append(context)

    system_prompt = (
        f"You are a professional translator for a restaurant QR menu application. "
        f"Translate from {source_language.name_native} ({source_language.code}) "
        f"to {target_language.name_native} ({target_language.code}). "
        + " ".join(rules)
    )

    user_prompt = json.dumps(batch, ensure_ascii=False, indent=2)
    content = chat_completion(
        [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
    )
    translated = parse_json_response(content)

    if not isinstance(translated, dict):
        raise GroqAPIError("Groq çeviri yanıtı geçerli bir JSON nesnesi değil.")

    for record_id, fields in batch.items():
        if record_id not in translated:
            raise GroqAPIError(f"Groq yanıtında '{record_id}' kaydı eksik.")
        result_fields = translated[record_id]
        if not isinstance(result_fields, dict):
            raise GroqAPIError(f"Groq yanıtında '{record_id}' alanları geçersiz.")

        for field in preserve_fields:
            if field in fields:
                result_fields[field] = fields[field]

    return translated


def _new_stats() -> dict[str, int]:
    return {"created": 0, "skipped": 0, "languages": 0}


def _groq_batch_size() -> int:
    raw = os.getenv("GROQ_BATCH_SIZE", "4")
    try:
        return max(1, int(raw))
    except ValueError:
        return 4


def _groq_batch_pause_seconds() -> float:
    raw = os.getenv("GROQ_BATCH_PAUSE_SECONDS", "1")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 1.0


def _chunked_records(grouped: dict[str, dict[str, Any]], size: int):
    items = list(grouped.items())
    for index in range(0, len(items), size):
        yield dict(items[index : index + size])


def _existing_parent_ids(model, parent_attr: str, target_language: Language) -> set[int]:
    return set(
        model.objects.filter(language=target_language).values_list(
            f"{parent_attr}_id",
            flat=True,
        )
    )


def _translate_model_batch(
    *,
    source_rows,
    parent_attr: str,
    fields: list[str],
    model,
    unique_attrs: dict[str, Any],
    stats: dict[str, int],
    source_language: Language,
    target_language: Language,
    html_fields: frozenset[str] = frozenset(),
    list_fields: frozenset[str] = frozenset(),
    preserve_fields: frozenset[str] = frozenset(),
    context: str = "",
    row_transform=None,
) -> None:
    grouped: dict[str, dict[str, Any]] = {}
    row_map: dict[str, Any] = {}
    already_translated = _existing_parent_ids(model, parent_attr, target_language)

    for row in source_rows:
        parent_id = getattr(row, parent_attr + "_id")
        if parent_id in already_translated:
            stats["skipped"] += 1
            continue

        record_id = str(parent_id)
        payload = {field: getattr(row, field) for field in fields}
        if row_transform:
            payload = row_transform(row, payload)
        payload = _non_empty_fields(payload)
        if not payload:
            continue
        grouped[record_id] = payload
        row_map[record_id] = row

    if not grouped:
        return

    stats["languages"] += 1
    batch_size = _groq_batch_size()
    pause_seconds = _groq_batch_pause_seconds()
    chunks = list(_chunked_records(grouped, batch_size))

    for chunk_index, chunk in enumerate(chunks):
        translated = translate_record_batch(
            chunk,
            source_language=source_language,
            target_language=target_language,
            html_fields=html_fields,
            list_fields=list_fields,
            preserve_fields=preserve_fields,
            context=context,
        )

        for record_id, field_values in translated.items():
            source_row = row_map[record_id]
            parent_id = getattr(source_row, parent_attr + "_id")
            lookup = {
                **unique_attrs,
                parent_attr + "_id": parent_id,
                "language": target_language,
            }
            defaults = {field: field_values.get(field, "") for field in fields}
            for field in preserve_fields:
                if field in chunk[record_id]:
                    defaults[field] = chunk[record_id][field]
            model.objects.create(**lookup, **defaults)
            stats["created"] += 1

        if pause_seconds and chunk_index < len(chunks) - 1:
            time.sleep(pause_seconds)


def translate_categories(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    from api.models import CategoryTranslation

    stats = _new_stats()
    source_rows = CategoryTranslation.objects.filter(language=source_language)
    for target_language in target_languages:
        _translate_model_batch(
            source_rows=source_rows,
            parent_attr="category",
            fields=["name", "title", "description"],
            model=CategoryTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            context="Category names for a restaurant menu.",
        )
    return stats


def translate_products(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    from api.models import ProductTranslation

    stats = _new_stats()
    source_rows = ProductTranslation.objects.filter(language=source_language)
    for target_language in target_languages:
        _translate_model_batch(
            source_rows=source_rows,
            parent_attr="product",
            fields=["name", "description", "ingredients", "allergens"],
            model=ProductTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            html_fields=frozenset({"description"}),
            list_fields=frozenset({"ingredients", "allergens"}),
            context="Product names and descriptions for a restaurant menu.",
        )
    return stats


def translate_chef_recommendations(
    source_language: Language, target_languages: list[Language]
) -> dict[str, int]:
    from api.models import ChefRecommendationTranslation

    stats = _new_stats()
    source_rows = ChefRecommendationTranslation.objects.filter(language=source_language)
    for target_language in target_languages:
        _translate_model_batch(
            source_rows=source_rows,
            parent_attr="chef_recommendation",
            fields=["title", "summary", "description"],
            model=ChefRecommendationTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            html_fields=frozenset({"description"}),
            context="Chef recommendation content for a restaurant.",
        )
    return stats


def translate_campaigns(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    from api.models import CampaignTranslation

    stats = _new_stats()
    source_rows = CampaignTranslation.objects.filter(language=source_language)
    for target_language in target_languages:
        _translate_model_batch(
            source_rows=source_rows,
            parent_attr="campaign",
            fields=["name", "description", "badge"],
            model=CampaignTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            html_fields=frozenset({"description"}),
            context="Marketing campaign copy for a restaurant.",
        )
    return stats


def translate_contacts(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    from api.models import ContactTranslation

    stats = _new_stats()
    source_rows = ContactTranslation.objects.filter(language=source_language)

    for target_language in target_languages:
        grouped: dict[str, dict[str, Any]] = {}
        row_map = {}
        already_translated = _existing_parent_ids(
            ContactTranslation, "contact", target_language
        )
        for row in source_rows:
            if row.contact_id in already_translated:
                stats["skipped"] += 1
                continue

            record_id = str(row.contact_id)
            payload = {
                "label": row.label,
                "link_text": row.link_text,
                "value": row.value,
            }
            payload = _non_empty_fields(payload)
            preserve_fields = []
            if should_preserve_contact_value(row.value):
                preserve_fields.append("value")
            if should_preserve_link_text(row.link_text):
                preserve_fields.append("link_text")
            if preserve_fields:
                payload["_preserve"] = preserve_fields
            if not payload:
                continue
            grouped[record_id] = {k: v for k, v in payload.items() if k != "_preserve"}
            row_map[record_id] = (row, preserve_fields)

        if not grouped:
            continue

        stats["languages"] += 1
        batch_size = _groq_batch_size()
        pause_seconds = _groq_batch_pause_seconds()
        chunks = list(_chunked_records(grouped, batch_size))

        for chunk_index, chunk in enumerate(chunks):
            translated = translate_record_batch(
                chunk,
                source_language=source_language,
                target_language=target_language,
                preserve_fields=frozenset({"value", "link_text"}),
                context="Contact labels for a restaurant website. Keep URLs, phone numbers, emails, and social handles unchanged.",
            )

            for record_id, field_values in translated.items():
                row, preserve_fields = row_map[record_id]
                defaults = {
                    "label": field_values.get("label", row.label),
                    "link_text": row.link_text if "link_text" in preserve_fields else field_values.get("link_text", row.link_text),
                    "value": row.value if "value" in preserve_fields else field_values.get("value", row.value),
                }
                ContactTranslation.objects.create(
                    contact_id=row.contact_id,
                    language=target_language,
                    **defaults,
                )
                stats["created"] += 1

            if pause_seconds and chunk_index < len(chunks) - 1:
                time.sleep(pause_seconds)

    return stats


def translate_site_settings(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    from api.models import SiteSettingsTranslation

    stats = _new_stats()
    source_rows = SiteSettingsTranslation.objects.filter(language=source_language)
    fields = [
        "title",
        "keywords",
        "description_title",
        "short_description",
        "description",
        "copyright",
        "hours_label",
        "weekday_days",
        "weekday_hours",
        "weekend_days",
        "weekend_hours",
        "hours_note",
    ]
    for target_language in target_languages:
        _translate_model_batch(
            source_rows=source_rows,
            parent_attr="settings",
            fields=fields,
            model=SiteSettingsTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            html_fields=frozenset({"description"}),
            preserve_fields=frozenset({"weekday_hours", "weekend_hours"}),
            context="Site settings and about page content for a restaurant.",
        )
    return stats


def translate_site_highlights(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    from api.models import SiteHighlightTranslation

    stats = _new_stats()
    source_rows = SiteHighlightTranslation.objects.filter(language=source_language)
    for target_language in target_languages:
        _translate_model_batch(
            source_rows=source_rows,
            parent_attr="highlight",
            fields=["title", "description"],
            model=SiteHighlightTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            context="Short highlight bullets for a restaurant homepage.",
        )
    return stats


def translate_ui_strings(source_language: Language, target_languages: list[Language]) -> dict[str, int]:
    stats = _new_stats()
    source_rows = list(
        UiString.objects.filter(language=source_language)
        .select_related("key")
        .order_by("key__key")
    )

    for target_language in target_languages:
        existing_key_ids = set(
            UiString.objects.filter(language=target_language).values_list(
                "key_id",
                flat=True,
            )
        )
        batch = {}
        key_map = {}
        for row in source_rows:
            if row.key_id in existing_key_ids:
                stats["skipped"] += 1
                continue
            if not row.text:
                continue
            batch[row.key.key] = {"text": row.text}
            key_map[row.key.key] = row.key

        if not batch:
            continue

        stats["languages"] += 1
        batch_size = _groq_batch_size()
        pause_seconds = _groq_batch_pause_seconds()
        chunks = list(_chunked_records(batch, batch_size))

        for chunk_index, chunk in enumerate(chunks):
            translated = translate_record_batch(
                chunk,
                source_language=source_language,
                target_language=target_language,
                context="Short UI labels for a restaurant QR menu mobile web app. Keep keys unchanged; translate only the text values.",
            )

            for key_name, field_values in translated.items():
                key = key_map.get(key_name)
                if not key:
                    continue
                text = field_values.get("text", "")
                UiString.objects.create(
                    language=target_language,
                    key=key,
                    text=text,
                )
                stats["created"] += 1

            if pause_seconds and chunk_index < len(chunks) - 1:
                time.sleep(pause_seconds)

    return stats


HANDLERS = {
    "category": translate_categories,
    "product": translate_products,
    "chef_recommendation": translate_chef_recommendations,
    "campaign": translate_campaigns,
    "contact": translate_contacts,
    "site_settings": translate_site_settings,
    "site_highlight": translate_site_highlights,
    "ui_string": translate_ui_strings,
}


@transaction.atomic
def run_groq_translation(handler_name: str) -> dict[str, int]:
    handler = HANDLERS.get(handler_name)
    if handler is None:
        raise ValueError(f"Bilinmeyen çeviri işleyicisi: {handler_name}")

    default_language = get_default_language()
    if default_language is None:
        raise GroqAPIError("Varsayılan dil bulunamadı.")

    target_languages = get_target_languages(default_language)
    if not target_languages:
        raise GroqAPIError("Çevrilecek hedef dil yok.")

    return handler(default_language, target_languages)
