from django.db import migrations


def seed_about_all(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    key, _ = UiStringKey.objects.get_or_create(
        key="about.all",
        defaults={
            "help_text": "Kategori navigasyonunda tüm kategoriler seçeneği.",
        },
    )

    translations = {
        "tr": "Hepsi",
        "en": "All",
    }

    for code, text in translations.items():
        language = Language.objects.filter(code=code, is_active=True).first()
        if language:
            UiString.objects.update_or_create(
                language=language,
                key=key,
                defaults={"text": text},
            )


def unseed_about_all(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key="about.all").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0005_seed_about_visit_us_ui_string"),
    ]

    operations = [
        migrations.RunPython(seed_about_all, unseed_about_all),
    ]
