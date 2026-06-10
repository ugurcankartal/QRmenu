from django.db import migrations

from api.content_translation_maps import (
    TARGET_LANGUAGE_CODES,
    should_preserve_contact_value,
    should_preserve_link_text,
    translate_json_list,
    translate_text,
)


def _target_languages(Language):
    return {
        lang.code: lang
        for lang in Language.objects.filter(
            code__in=TARGET_LANGUAGE_CODES,
            is_active=True,
        )
    }


def _seed_category_translations(apps, languages):
    CategoryTranslation = apps.get_model("api", "CategoryTranslation")
    for tr_row in CategoryTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            CategoryTranslation.objects.update_or_create(
                category_id=tr_row.category_id,
                language=language,
                defaults={
                    "name": translate_text(tr_row.name, code),
                    "title": translate_text(tr_row.title, code),
                    "description": translate_text(tr_row.description, code),
                },
            )


def _seed_product_translations(apps, languages):
    ProductTranslation = apps.get_model("api", "ProductTranslation")
    for tr_row in ProductTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            ProductTranslation.objects.update_or_create(
                product_id=tr_row.product_id,
                language=language,
                defaults={
                    "name": translate_text(tr_row.name, code),
                    "description": translate_text(tr_row.description, code),
                    "ingredients": translate_json_list(tr_row.ingredients, code),
                    "allergens": translate_json_list(tr_row.allergens, code),
                },
            )


def _seed_chef_recommendation_translations(apps, languages):
    ChefRecommendationTranslation = apps.get_model(
        "api", "ChefRecommendationTranslation"
    )
    for tr_row in ChefRecommendationTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            ChefRecommendationTranslation.objects.update_or_create(
                chef_recommendation_id=tr_row.chef_recommendation_id,
                language=language,
                defaults={
                    "title": translate_text(tr_row.title, code),
                    "summary": translate_text(tr_row.summary, code),
                    "description": translate_text(tr_row.description, code),
                },
            )


def _seed_campaign_translations(apps, languages):
    CampaignTranslation = apps.get_model("api", "CampaignTranslation")
    for tr_row in CampaignTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            CampaignTranslation.objects.update_or_create(
                campaign_id=tr_row.campaign_id,
                language=language,
                defaults={
                    "name": translate_text(tr_row.name, code),
                    "description": translate_text(tr_row.description, code),
                    "badge": translate_text(tr_row.badge, code),
                },
            )


def _seed_contact_translations(apps, languages):
    ContactTranslation = apps.get_model("api", "ContactTranslation")
    for tr_row in ContactTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            value = (
                tr_row.value
                if should_preserve_contact_value(tr_row.value)
                else translate_text(tr_row.value, code)
            )
            link_text = (
                tr_row.link_text
                if should_preserve_link_text(tr_row.link_text)
                else translate_text(tr_row.link_text, code)
            )
            ContactTranslation.objects.update_or_create(
                contact_id=tr_row.contact_id,
                language=language,
                defaults={
                    "label": translate_text(tr_row.label, code),
                    "link_text": link_text,
                    "value": value,
                },
            )


def _seed_site_settings_translations(apps, languages):
    SiteSettingsTranslation = apps.get_model("api", "SiteSettingsTranslation")
    for tr_row in SiteSettingsTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            SiteSettingsTranslation.objects.update_or_create(
                settings_id=tr_row.settings_id,
                language=language,
                defaults={
                    "title": translate_text(tr_row.title, code),
                    "keywords": translate_text(tr_row.keywords, code),
                    "description_title": translate_text(
                        tr_row.description_title, code
                    ),
                    "short_description": translate_text(
                        tr_row.short_description, code
                    ),
                    "description": translate_text(tr_row.description, code),
                    "copyright": translate_text(tr_row.copyright, code),
                    "hours_label": translate_text(tr_row.hours_label, code),
                    "weekday_days": translate_text(tr_row.weekday_days, code),
                    "weekday_hours": tr_row.weekday_hours,
                    "weekend_days": translate_text(tr_row.weekend_days, code),
                    "weekend_hours": tr_row.weekend_hours,
                    "hours_note": translate_text(tr_row.hours_note, code),
                },
            )


def _seed_site_highlight_translations(apps, languages):
    SiteHighlightTranslation = apps.get_model("api", "SiteHighlightTranslation")
    for tr_row in SiteHighlightTranslation.objects.filter(language__code="tr"):
        for code, language in languages.items():
            SiteHighlightTranslation.objects.update_or_create(
                highlight_id=tr_row.highlight_id,
                language=language,
                defaults={
                    "title": translate_text(tr_row.title, code),
                    "description": translate_text(tr_row.description, code),
                },
            )


def seed_content_translations_from_turkish(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    languages = _target_languages(Language)
    if not languages:
        return

    _seed_category_translations(apps, languages)
    _seed_product_translations(apps, languages)
    _seed_chef_recommendation_translations(apps, languages)
    _seed_campaign_translations(apps, languages)
    _seed_contact_translations(apps, languages)
    _seed_site_settings_translations(apps, languages)
    _seed_site_highlight_translations(apps, languages)


def unseed_content_translations_from_turkish(apps, schema_editor):
    models_and_fk = [
        ("CategoryTranslation", "category"),
        ("ProductTranslation", "product"),
        ("ChefRecommendationTranslation", "chef_recommendation"),
        ("CampaignTranslation", "campaign"),
        ("ContactTranslation", "contact"),
        ("SiteSettingsTranslation", "settings"),
        ("SiteHighlightTranslation", "highlight"),
    ]
    for model_name, _ in models_and_fk:
        Model = apps.get_model("api", model_name)
        Model.objects.filter(language__code__in=TARGET_LANGUAGE_CODES).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0043_seed_site_highlights"),
        ("localization", "0023_seed_ui_strings_korean"),
    ]

    operations = [
        migrations.RunPython(
            seed_content_translations_from_turkish,
            unseed_content_translations_from_turkish,
        ),
    ]
