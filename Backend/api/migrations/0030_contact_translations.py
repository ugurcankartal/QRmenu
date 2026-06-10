from django.db import migrations, models
import django.db.models.deletion


def migrate_contact_translations(apps, schema_editor):
    Contact = apps.get_model("api", "Contact")
    ContactTranslation = apps.get_model("api", "ContactTranslation")
    Language = apps.get_model("localization", "Language")

    default_lang = Language.objects.filter(is_default=True).first()
    if default_lang is None:
        default_lang = Language.objects.filter(code="tr").first()
    if default_lang is None:
        return

    for contact in Contact.objects.all().iterator():
        label = getattr(contact, "label", "") or ""
        value = getattr(contact, "value", "") or ""
        if not value:
            continue
        ContactTranslation.objects.get_or_create(
            contact=contact,
            language=default_lang,
            defaults={
                "label": label,
                "value": value,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0029_campaigns"),
        ("localization", "0004_language_single_default"),
    ]

    operations = [
        migrations.CreateModel(
            name="ContactTranslation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "label",
                    models.CharField(
                        blank=True,
                        help_text="Örn: Ana hat, Şube, Destek",
                        max_length=100,
                        verbose_name="Etiket",
                    ),
                ),
                ("value", models.TextField(verbose_name="Değer")),
                (
                    "contact",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="translations",
                        to="api.contact",
                        verbose_name="İletişim",
                    ),
                ),
                (
                    "language",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="contact_translations",
                        to="localization.language",
                        verbose_name="Dil",
                    ),
                ),
            ],
            options={
                "verbose_name": "İletişim çevirisi",
                "verbose_name_plural": "İletişim çevirileri",
            },
        ),
        migrations.AddConstraint(
            model_name="contacttranslation",
            constraint=models.UniqueConstraint(
                fields=("contact", "language"),
                name="unique_contact_translation_per_language",
            ),
        ),
        migrations.RunPython(migrate_contact_translations, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="contact",
            name="label",
        ),
        migrations.RemoveField(
            model_name="contact",
            name="value",
        ),
    ]
