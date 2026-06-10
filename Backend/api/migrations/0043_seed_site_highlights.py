from django.db import migrations


HIGHLIGHTS = [
    {
        "icon": "Award",
        "order": 0,
        "translations": {
            "tr": {
                "title": "Ödüllü",
                "description": "İstanbul'un en iyi Türk restoranlarından biri olarak tanınıyoruz",
            },
            "en": {
                "title": "Award Winning",
                "description": "Recognized as one of Istanbul's finest Turkish restaurants",
            },
        },
    },
    {
        "icon": "Clock",
        "order": 1,
        "translations": {
            "tr": {
                "title": "Her Gün Taze",
                "description": "Tüm malzemeler her sabah yerel pazarlardan taze olarak temin edilir",
            },
            "en": {
                "title": "Fresh Daily",
                "description": "All ingredients sourced fresh every morning from local markets",
            },
        },
    },
    {
        "icon": "MapPin",
        "order": 2,
        "translations": {
            "tr": {
                "title": "Merkezi Konum",
                "description": "Tarihi Sultanahmet Meydanı bölgesinde yer alıyoruz",
            },
            "en": {
                "title": "Prime Location",
                "description": "Located in the historic Sultanahmet Square district",
            },
        },
    },
]


def seed_site_highlights(apps, schema_editor):
    SiteSettings = apps.get_model("api", "SiteSettings")
    SiteHighlight = apps.get_model("api", "SiteHighlight")
    SiteHighlightTranslation = apps.get_model("api", "SiteHighlightTranslation")
    Language = apps.get_model("localization", "Language")

    settings = SiteSettings.objects.filter(is_active=True).order_by("-updated_at").first()
    if not settings:
        return

    if SiteHighlight.objects.filter(settings=settings).exists():
        return

    for item in HIGHLIGHTS:
        highlight = SiteHighlight.objects.create(
            settings=settings,
            icon=item["icon"],
            order=item["order"],
            is_active=True,
        )
        for code, text in item["translations"].items():
            language = Language.objects.filter(code=code, is_active=True).first()
            if language:
                SiteHighlightTranslation.objects.create(
                    highlight=highlight,
                    language=language,
                    title=text["title"],
                    description=text["description"],
                )


def unseed_site_highlights(apps, schema_editor):
    SiteHighlight = apps.get_model("api", "SiteHighlight")
    SiteHighlight.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0042_site_highlight"),
        ("localization", "0002_seed_languages"),
    ]

    operations = [
        migrations.RunPython(seed_site_highlights, unseed_site_highlights),
    ]
