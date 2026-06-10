from django.db import migrations


UI_STRINGS = {
    "about.price": {
        "help_text": "Şefin önerisi bölümünde fiyat etiketi.",
        "translations": {
            "tr": "Fiyat",
            "en": "Price",
        },
    },
    "about.prep-time": {
        "help_text": "Şefin önerisi bölümünde hazırlama süresi etiketi.",
        "translations": {
            "tr": "Hazırlama Süresi",
            "en": "Prep Time",
        },
    },
}


def seed_featured_dish_ui_strings(apps, schema_editor):
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


def unseed_featured_dish_ui_strings(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0008_seed_popular_ui_strings"),
    ]

    operations = [
        migrations.RunPython(
            seed_featured_dish_ui_strings,
            unseed_featured_dish_ui_strings,
        ),
    ]
