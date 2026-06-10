from django.db import migrations


UI_STRINGS = {
    "product-detaile.add-to-order": {
        "help_text": "Ürün detay modalında adisyona ekle butonu metni.",
        "translations": {
            "tr": "Adisyona Ekle",
            "en": "Add to order",
        },
    },
}


def seed_product_detail_add_to_order(apps, schema_editor):
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


def unseed_product_detail_add_to_order(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0016_seed_menu_ui_strings"),
    ]

    operations = [
        migrations.RunPython(
            seed_product_detail_add_to_order,
            unseed_product_detail_add_to_order,
        ),
    ]
