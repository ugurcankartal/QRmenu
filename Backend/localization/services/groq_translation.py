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
from localization.services.groq_translation_progress import GroqTranslationProgress


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


def resolve_source_translations(model, preferred: Language) -> tuple[Language, Any]:
    """Pick source rows for Groq: preferred language, then tr/en, then the fullest set."""
    from django.db.models import Count

    qs = model.objects.filter(language=preferred)
    if qs.exists():
        return preferred, qs

    tried = {preferred.pk}
    for code in ("tr", "en"):
        lang = Language.objects.filter(code=code, is_active=True).exclude(pk__in=tried).first()
        if lang:
            tried.add(lang.pk)
            qs = model.objects.filter(language=lang)
            if qs.exists():
                return lang, qs

    lang_id = (
        model.objects.values("language_id")
        .annotate(c=Count("pk"))
        .order_by("-c")
        .values_list("language_id", flat=True)
        .first()
    )
    if lang_id:
        lang = Language.objects.filter(pk=lang_id).first()
        if lang:
            return lang, model.objects.filter(language=lang)

    return preferred, model.objects.none()


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
    return {"created": 0, "updated": 0, "skipped": 0, "languages": 0, "failed": 0}


def _groq_batch_pause_seconds() -> float:
    raw = os.getenv("GROQ_BATCH_PAUSE_SECONDS", "1")
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 1.0


def _groq_aborted(stats: dict[str, int]) -> bool:
    return bool(stats.get("_abort"))


def public_groq_stats(stats: dict[str, int]) -> dict[str, int]:
    return {key: value for key, value in stats.items() if not str(key).startswith("_")}


def _record_groq_failure(
    exc: Exception,
    *,
    stats: dict[str, int],
    progress: GroqTranslationProgress | None,
    label: str,
) -> None:
    from core.groq_client import GroqRateLimitError

    stats["failed"] += 1
    message = str(exc)
    if progress:
        progress.advance(label=label, error=message)
    if isinstance(exc, GroqRateLimitError) and exc.is_daily_limit:
        stats["_abort"] = True
        stats["_abort_message"] = message


def _field_value_for_compare(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    return value


def _needs_groq_translation(
    source_row,
    target_row,
    fields: list[str],
    preserve_fields: frozenset[str] = frozenset(),
) -> bool:
    """True when missing or when target text still matches source (seed/stub rows)."""
    if target_row is None:
        return True

    has_content = False
    for field in fields:
        if field in preserve_fields:
            continue
        source_val = _field_value_for_compare(getattr(source_row, field, None) or "")
        if source_val in (None, "", [], {}):
            continue
        has_content = True
        target_val = _field_value_for_compare(getattr(target_row, field, None) or "")
        if target_val != source_val:
            return False
    return has_content


def _collect_pending_records(
    *,
    source_rows,
    parent_attr: str,
    fields: list[str],
    model,
    target_language: Language,
    stats: dict[str, int],
    row_transform=None,
    preserve_fields: frozenset[str] = frozenset(),
) -> list[tuple[Any, str, dict[str, Any]]]:
    pending: list[tuple[Any, str, dict[str, Any]]] = []

    for row in source_rows:
        parent_id = getattr(row, parent_attr + "_id")
        existing = model.objects.filter(
            **{f"{parent_attr}_id": parent_id, "language": target_language}
        ).first()
        if existing and not _needs_groq_translation(row, existing, fields, preserve_fields):
            stats["skipped"] += 1
            continue

        record_id = str(parent_id)
        payload = {field: getattr(row, field) for field in fields}
        if row_transform:
            payload = row_transform(row, payload)
        payload = _non_empty_fields(payload)
        if not payload:
            stats["skipped"] += 1
            continue
        pending.append((row, record_id, payload))

    return pending


def _translate_pending_records(
    *,
    pending: list[tuple[Any, str, dict[str, Any]]],
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
    copy_fields_from_source: frozenset[str] = frozenset(),
    context: str = "",
    progress: GroqTranslationProgress | None = None,
    progress_label: str = "",
) -> None:
    if not pending:
        return

    stats["languages"] += 1
    pause_seconds = _groq_batch_pause_seconds()

    for index, (source_row, record_id, payload) in enumerate(pending):
        if _groq_aborted(stats):
            return
        label = f"{progress_label} → {target_language.code} (#{record_id})"
        try:
            translated = translate_record_batch(
                {record_id: payload},
                source_language=source_language,
                target_language=target_language,
                html_fields=html_fields,
                list_fields=list_fields,
                preserve_fields=preserve_fields,
                context=context,
            )
            field_values = translated[record_id]
            with transaction.atomic():
                parent_id = getattr(source_row, parent_attr + "_id")
                lookup = {
                    **unique_attrs,
                    parent_attr + "_id": parent_id,
                    "language": target_language,
                }
                defaults = {field: field_values.get(field, "") for field in fields}
                for field in preserve_fields:
                    if field in payload:
                        defaults[field] = payload[field]
                for field in copy_fields_from_source:
                    val = getattr(source_row, field, None)
                    if val:
                        defaults[field] = val
                _, created = model.objects.update_or_create(**lookup, defaults=defaults)
                if created:
                    stats["created"] += 1
                else:
                    stats["updated"] += 1
            if progress:
                progress.advance(label=label)
        except (GroqAPIError, ValueError, TypeError, KeyError) as exc:
            _record_groq_failure(exc, stats=stats, progress=progress, label=label)
            if _groq_aborted(stats):
                return

        if pause_seconds and index < len(pending) - 1 and not _groq_aborted(stats):
            time.sleep(pause_seconds)


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
    copy_fields_from_source: frozenset[str] = frozenset(),
    context: str = "",
    row_transform=None,
    progress: GroqTranslationProgress | None = None,
    progress_label: str = "",
    dry_run: bool = False,
) -> int:
    if stats.get("_abort"):
        return 0

    pending = _collect_pending_records(
        source_rows=source_rows,
        parent_attr=parent_attr,
        fields=fields,
        model=model,
        target_language=target_language,
        stats=stats if not dry_run else _new_stats(),
        row_transform=row_transform,
        preserve_fields=preserve_fields,
    )
    if dry_run:
        return len(pending)

    _translate_pending_records(
        pending=pending,
        parent_attr=parent_attr,
        fields=fields,
        model=model,
        unique_attrs=unique_attrs,
        stats=stats,
        source_language=source_language,
        target_language=target_language,
        html_fields=html_fields,
        list_fields=list_fields,
        preserve_fields=preserve_fields,
        copy_fields_from_source=copy_fields_from_source,
        context=context,
        progress=progress,
        progress_label=progress_label,
    )
    return 0


def _contact_translatable_fields(row) -> tuple[dict[str, Any], list[str]]:
    payload: dict[str, Any] = {}
    preserve_fields: list[str] = []

    if row.label:
        payload["label"] = row.label

    if row.link_text:
        if should_preserve_link_text(row.link_text):
            preserve_fields.append("link_text")
        else:
            payload["link_text"] = row.link_text

    if row.value:
        if should_preserve_contact_value(row.value):
            preserve_fields.append("value")
        else:
            payload["value"] = row.value

    return payload, preserve_fields


def _collect_pending_contacts(source_rows, target_language, stats) -> list[tuple[Any, str, dict[str, Any], list[str]]]:
    from api.models import ContactTranslation

    pending: list[tuple[Any, str, dict[str, Any], list[str]]] = []

    for row in source_rows:
        existing = ContactTranslation.objects.filter(
            contact_id=row.contact_id,
            language=target_language,
        ).first()
        if existing and not _needs_groq_translation(
            row,
            existing,
            ["label", "link_text", "value"],
        ):
            stats["skipped"] += 1
            continue

        payload, preserve_fields = _contact_translatable_fields(row)
        if not payload and not preserve_fields and not row.label and not row.link_text and not row.value:
            stats["skipped"] += 1
            continue

        pending.append((row, str(row.contact_id), payload, preserve_fields))

    return pending


def _translate_contacts_for_language(
    *,
    source_rows,
    target_language: Language,
    source_language: Language,
    stats: dict[str, int],
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> int:
    from api.models import ContactTranslation

    pending = _collect_pending_contacts(source_rows, target_language, stats if not dry_run else _new_stats())
    if dry_run:
        return len(pending)

    if not pending:
        return 0

    stats["languages"] += 1
    pause_seconds = _groq_batch_pause_seconds()

    for index, (row, record_id, payload, dynamic_preserve) in enumerate(pending):
        if _groq_aborted(stats):
            return 0
        label = f"Iletisim → {target_language.code} (#{record_id})"
        preserve = frozenset(dynamic_preserve)

        try:
            if payload:
                translated = translate_record_batch(
                    {record_id: payload},
                    source_language=source_language,
                    target_language=target_language,
                    preserve_fields=preserve,
                    context=(
                        "Contact labels for a restaurant website. "
                        "Keep URLs, phone numbers, emails, and social handles unchanged."
                    ),
                )
                field_values = translated[record_id]
                defaults = {}
                for field in ("label", "link_text", "value"):
                    if field in preserve:
                        defaults[field] = getattr(row, field)
                    elif field in payload:
                        defaults[field] = field_values.get(field, getattr(row, field))
                    else:
                        defaults[field] = getattr(row, field)
            else:
                defaults = {
                    "label": row.label,
                    "link_text": row.link_text,
                    "value": row.value,
                }

            with transaction.atomic():
                _, created = ContactTranslation.objects.update_or_create(
                    contact_id=row.contact_id,
                    language=target_language,
                    defaults=defaults,
                )
                if created:
                    stats["created"] += 1
                else:
                    stats["updated"] += 1
            if progress:
                progress.advance(label=label)
        except (GroqAPIError, ValueError, TypeError, KeyError) as exc:
            _record_groq_failure(exc, stats=stats, progress=progress, label=label)
            if _groq_aborted(stats):
                return 0

        if pause_seconds and index < len(pending) - 1 and not _groq_aborted(stats):
            time.sleep(pause_seconds)

    return 0


def count_handler_work(
    handler_name: str,
    source_language: Language,
    target_languages: list[Language],
) -> int:
    handler = HANDLERS[handler_name]
    result = handler(source_language, target_languages, dry_run=True)
    return int(result) if isinstance(result, int) else 0


def translate_categories(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import CategoryTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(CategoryTranslation, source_language)
    if not source_rows.exists():
        return 0 if dry_run else stats
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
            source_rows=source_rows,
            parent_attr="category",
            fields=["name", "title", "description"],
            model=CategoryTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            context="Category names for a restaurant menu.",
            progress=progress,
            progress_label="Kategori",
            dry_run=dry_run,
        )
    return total if dry_run else stats


def translate_products(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import ProductTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(ProductTranslation, source_language)
    if not source_rows.exists():
        return 0 if dry_run else stats
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
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
            progress=progress,
            progress_label="Urun",
            dry_run=dry_run,
        )
    return total if dry_run else stats


def translate_chef_recommendations(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import ChefRecommendationTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(
        ChefRecommendationTranslation, source_language
    )
    if not source_rows.exists():
        return 0 if dry_run else stats
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
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
            progress=progress,
            progress_label="Sef onerisi",
            dry_run=dry_run,
        )
    return total if dry_run else stats


def translate_campaigns(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import CampaignTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(CampaignTranslation, source_language)
    if not source_rows.exists():
        return 0 if dry_run else stats
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
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
            progress=progress,
            progress_label="Kampanya",
            dry_run=dry_run,
        )
    return total if dry_run else stats


def translate_contacts(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import ContactTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(ContactTranslation, source_language)
    if not source_rows.exists():
        return 0 if dry_run else stats
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        if dry_run:
            total += _translate_contacts_for_language(
                source_rows=source_rows,
                target_language=target_language,
                source_language=source_language,
                stats=stats,
                dry_run=True,
            )
        else:
            _translate_contacts_for_language(
                source_rows=source_rows,
                target_language=target_language,
                source_language=source_language,
                stats=stats,
                progress=progress,
            )
    return total if dry_run else stats


def translate_site_settings(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import SiteSettingsTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(
        SiteSettingsTranslation, source_language
    )
    if not source_rows.exists():
        return 0 if dry_run else stats
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
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
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
            copy_fields_from_source=frozenset({"favicon", "logo"}),
            context="Site settings and about page content for a restaurant.",
            progress=progress,
            progress_label="Site ayari",
            dry_run=dry_run,
        )
    return total if dry_run else stats


def translate_site_highlights(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    from api.models import SiteHighlightTranslation

    stats = stats or _new_stats()
    source_language, source_rows = resolve_source_translations(
        SiteHighlightTranslation, source_language
    )
    if not source_rows.exists():
        return 0 if dry_run else stats
    total = 0
    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        total += _translate_model_batch(
            source_rows=source_rows,
            parent_attr="highlight",
            fields=["title", "description"],
            model=SiteHighlightTranslation,
            unique_attrs={},
            stats=stats,
            source_language=source_language,
            target_language=target_language,
            context="Short highlight bullets for a restaurant homepage.",
            progress=progress,
            progress_label="One cikan",
            dry_run=dry_run,
        )
    return total if dry_run else stats


def translate_ui_strings(
    source_language: Language,
    target_languages: list[Language],
    *,
    stats: dict[str, int] | None = None,
    progress: GroqTranslationProgress | None = None,
    dry_run: bool = False,
) -> dict[str, int] | int:
    stats = stats or _new_stats()
    source_language, source_qs = resolve_source_translations(UiString, source_language)
    source_rows = list(
        source_qs.select_related("key").order_by("key__key")
    )
    if not source_rows:
        return 0 if dry_run else stats
    total = 0

    for target_language in target_languages:
        if _groq_aborted(stats):
            break
        pending: list[tuple[Any, str, dict[str, Any]]] = []
        key_map = {}
        for row in source_rows:
            existing = UiString.objects.filter(
                language=target_language,
                key=row.key,
            ).first()
            if existing and not _needs_groq_translation(row, existing, ["text"]):
                stats["skipped"] += 1
                continue
            if not row.text:
                stats["skipped"] += 1
                continue
            pending.append((row, row.key.key, {"text": row.text}))
            key_map[row.key.key] = row.key

        if dry_run:
            total += len(pending)
            continue

        if not pending:
            continue

        stats["languages"] += 1
        pause_seconds = _groq_batch_pause_seconds()
        for index, (row, key_name, payload) in enumerate(pending):
            if _groq_aborted(stats):
                break
            label = f"UI metni → {target_language.code} ({key_name})"
            try:
                translated = translate_record_batch(
                    {key_name: payload},
                    source_language=source_language,
                    target_language=target_language,
                    context=(
                        "Short UI labels for a restaurant QR menu mobile web app. "
                        "Keep keys unchanged; translate only the text values."
                    ),
                )
                text = translated[key_name].get("text", "")
                with transaction.atomic():
                    _, created = UiString.objects.update_or_create(
                        language=target_language,
                        key=key_map[key_name],
                        defaults={"text": text},
                    )
                    if created:
                        stats["created"] += 1
                    else:
                        stats["updated"] += 1
                if progress:
                    progress.advance(label=label)
            except (GroqAPIError, ValueError, TypeError, KeyError) as exc:
                _record_groq_failure(exc, stats=stats, progress=progress, label=label)
                if _groq_aborted(stats):
                    break

            if pause_seconds and index < len(pending) - 1 and not _groq_aborted(stats):
                time.sleep(pause_seconds)

        if _groq_aborted(stats):
            break

    return total if dry_run else stats


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


def run_groq_translation(
    handler_name: str,
    *,
    progress: GroqTranslationProgress | None = None,
) -> dict[str, int]:
    handler = HANDLERS.get(handler_name)
    if handler is None:
        raise ValueError(f"Bilinmeyen çeviri işleyicisi: {handler_name}")

    default_language = get_default_language()
    if default_language is None:
        raise GroqAPIError("Varsayılan dil bulunamadi.")

    target_languages = get_target_languages(default_language)
    if not target_languages:
        raise GroqAPIError("Çevrilecek hedef dil yok.")

    if progress:
        total = count_handler_work(handler_name, default_language, target_languages)
        progress.init(total)

    stats = _new_stats()
    handler(
        default_language,
        target_languages,
        stats=stats,
        progress=progress,
        dry_run=False,
    )
    return stats
