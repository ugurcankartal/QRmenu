from django.db import migrations


UI_STRINGS = {
    "adisyon.total-price": {
        "help_text": "Adisyon sayfasında liste toplam tutar etiketi.",
        "translations": {
            "tr": "Toplam tutar",
            "en": "Total amount",
        },
    },
    "adisyon.discounted-total-price": {
        "help_text": "Adisyon sayfasında indirimli toplam tutar etiketi.",
        "translations": {
            "tr": "İndirimli toplam tutar",
            "en": "Discounted total",
        },
    },
}


def seed_adisyon_total_ui_strings(apps, schema_editor):
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


def unseed_adisyon_total_ui_strings(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0018_seed_product_detail_added_to_order"),
    ]

    operations = [
        migrations.RunPython(
            seed_adisyon_total_ui_strings,
            unseed_adisyon_total_ui_strings,
        ),
    ]
