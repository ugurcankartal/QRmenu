from django.db import migrations


LANGUAGES = [
    ("it", "Italiano", 3),
    ("fr", "Français", 4),
    ("es", "Español", 5),
    ("ja", "日本語", 6),
    ("zh", "中文", 7),
    ("ru", "Русский", 8),
    ("ar", "العربية", 9),
]


def seed_additional_languages(apps, schema_editor):
    Language = apps.get_model("localization", "Language")

    for code, name_native, sort_order in LANGUAGES:
        Language.objects.get_or_create(
            code=code,
            defaults={
                "name_native": name_native,
                "is_active": True,
                "is_default": False,
                "sort_order": sort_order,
            },
        )


def unseed_additional_languages(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    Language.objects.filter(code__in=[code for code, _, _ in LANGUAGES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0020_seed_adisyon_bill_ui_string"),
    ]

    operations = [
        migrations.RunPython(seed_additional_languages, unseed_additional_languages),
    ]
