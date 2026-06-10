from django.db import migrations


UI_STRINGS = {
    "about.no-dishes-found-in-this-category": {
        "help_text": "Seçili kategoride ürün bulunamadığında gösterilen mesaj.",
        "translations": {
            "tr": "Bu kategoride yemek bulunamadı.",
            "en": "No dishes found in this category.",
        },
    },
}


def seed_no_dishes_ui_string(apps, schema_editor):
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


def unseed_no_dishes_ui_string(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0011_seed_footer_nav_ui_strings"),
    ]

    operations = [
        migrations.RunPython(
            seed_no_dishes_ui_string,
            unseed_no_dishes_ui_string,
        ),
    ]
