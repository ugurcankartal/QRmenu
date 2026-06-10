from django.db import migrations


UI_STRINGS = {
    "adisyon.bill": {
        "help_text": "Adisyon sayfasında toplam tutar etiketi.",
        "translations": {
            "tr": "Hesap",
            "en": "Bill",
        },
    },
}


def seed_adisyon_bill_ui_string(apps, schema_editor):
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


def unseed_adisyon_bill_ui_string(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key__in=UI_STRINGS.keys()).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0019_seed_adisyon_total_ui_strings"),
    ]

    operations = [
        migrations.RunPython(seed_adisyon_bill_ui_string, unseed_adisyon_bill_ui_string),
    ]
