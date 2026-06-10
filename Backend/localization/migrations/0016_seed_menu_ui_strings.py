from django.db import migrations


UI_STRINGS = {
    "menu.our-menu": {
        "help_text": "Menü sayfası başlığı.",
        "translations": {
            "tr": "Menümüz",
            "en": "Our Menu",
        },
    },
    "menu.search-dishes": {
        "help_text": "Menü sayfası arama alanı placeholder metni.",
        "translations": {
            "tr": "Yemek ara...",
            "en": "Search dishes...",
        },
    },
}


def seed_menu_ui_strings(apps, schema_editor):
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


def unseed_menu_ui_strings(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0015_seed_about_follow_us_ui_string"),
    ]

    operations = [
        migrations.RunPython(
            seed_menu_ui_strings,
            unseed_menu_ui_strings,
        ),
    ]
