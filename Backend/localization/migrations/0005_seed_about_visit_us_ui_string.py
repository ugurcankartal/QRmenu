from django.db import migrations


def seed_about_visit_us(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiString = apps.get_model("localization", "UiString")

    key, _ = UiStringKey.objects.get_or_create(
        key="about.visit_us",
        defaults={
            "help_text": "About sayfası iletişim bölümü başlığı.",
        },
    )

    translations = {
        "tr": "Bizi Ziyaret Edin",
        "en": "Visit Us",
    }

    for code, text in translations.items():
        language = Language.objects.filter(code=code, is_active=True).first()
        if language:
            UiString.objects.update_or_create(
                language=language,
                key=key,
                defaults={"text": text},
            )


def unseed_about_visit_us(apps, schema_editor):
    UiStringKey = apps.get_model("localization", "UiStringKey")
    UiStringKey.objects.filter(key="about.visit_us").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0004_language_single_default"),
    ]

    operations = [
        migrations.RunPython(seed_about_visit_us, unseed_about_visit_us),
    ]
