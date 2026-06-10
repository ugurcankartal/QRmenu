from django.db import migrations


UI_STRINGS = {
    "footer-nav.home": {
        "help_text": "Alt navigasyonda ana sayfa etiketi.",
        "translations": {
            "tr": "Ana Sayfa",
            "en": "Home",
        },
    },
    "footer-nav.menu": {
        "help_text": "Alt navigasyonda menü etiketi.",
        "translations": {
            "tr": "Menü",
            "en": "Menu",
        },
    },
    "footer-nav.adisyon": {
        "help_text": "Alt navigasyonda adisyon/favoriler etiketi.",
        "translations": {
            "tr": "Adisyon",
            "en": "Favorites",
        },
    },
    "footer-nav.about": {
        "help_text": "Alt navigasyonda hakkında etiketi.",
        "translations": {
            "tr": "Hakkında",
            "en": "About",
        },
    },
}


def seed_footer_nav_ui_strings(apps, schema_editor):
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


def unseed_footer_nav_ui_strings(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0010_seed_view_details_ui_string"),
    ]

    operations = [
        migrations.RunPython(
            seed_footer_nav_ui_strings,
            unseed_footer_nav_ui_strings,
        ),
    ]
