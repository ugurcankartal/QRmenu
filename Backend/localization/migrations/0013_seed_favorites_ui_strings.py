from django.db import migrations


UI_STRINGS = {
    "favorites.no-items-yet": {
        "help_text": "Adisyon sayfasında boş liste başlığı.",
        "translations": {
            "tr": "Henüz ürün yok",
            "en": "No items yet",
        },
    },
    "favorites.add-dishes-to-order": {
        "help_text": "Adisyon sayfasında boş liste açıklaması.",
        "translations": {
            "tr": "Menüdeki ürünlerde adisyon ikonuna dokunarak siparişinize ekleyin",
            "en": "Add dishes to your order by tapping the receipt icon on any menu item",
        },
    },
    "favorites.exploremenu": {
        "help_text": "Adisyon sayfasında menüye git butonu metni.",
        "translations": {
            "tr": "Menüyü Keşfet",
            "en": "Explore Menu",
        },
    },
}


def seed_favorites_ui_strings(apps, schema_editor):
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


def unseed_favorites_ui_strings(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0012_seed_no_dishes_ui_string"),
    ]

    operations = [
        migrations.RunPython(
            seed_favorites_ui_strings,
            unseed_favorites_ui_strings,
        ),
    ]
