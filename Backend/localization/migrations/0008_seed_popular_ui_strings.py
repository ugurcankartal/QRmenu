from django.db import migrations


UI_STRINGS = {
    "about.popular": {
        "help_text": "Ürün kartında popüler rozeti.",
        "translations": {
            "tr": "Popüler",
            "en": "Popular",
        },
    },
    "about.popular-choice": {
        "help_text": "Ürün detay modalında popüler rozeti.",
        "translations": {
            "tr": "Popüler Seçim",
            "en": "Popular Choice",
        },
    },
}


def seed_popular_ui_strings(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    for key_name, config in UI_STRINGS.items():
        key, _ = UiStringKey.objects.get_or_create(
            key=key_name,
            defaults={"help_text": config["help_text"]},
        )

        for code, text in config["translations"].items():
            language = Language.objects.filter(code=code, is_active=True).first()
            if language:
                UiString.objects.update_or_create(
                    language=language,
                    key=key,
                    defaults={"text": text},
                )


def unseed_popular_ui_strings(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0007_seed_product_detail_ui_strings"),
    ]

    operations = [
        migrations.RunPython(seed_popular_ui_strings, unseed_popular_ui_strings),
    ]
