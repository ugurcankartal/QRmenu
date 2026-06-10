from django.db import migrations, models


def ensure_single_default_language(apps, schema_editor):
    Language = apps.get_model("localization", "Language")
    defaults = list(
        Language.objects.filter(is_default=True).order_by("sort_order", "code")
    )
    if len(defaults) <= 1:
        return
    keep = defaults[0]
    Language.objects.filter(is_default=True).exclude(pk=keep.pk).update(
        is_default=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ("localization", "0003_language_flag"),
    ]

    operations = [
        migrations.AlterField(
            model_name="language",
            name="is_default",
            field=models.BooleanField(
                default=False,
                help_text="Aynı anda yalnızca bir dil varsayılan olabilir.",
                verbose_name="Varsayılan",
            ),
        ),
        migrations.RunPython(
            ensure_single_default_language,
            migrations.RunPython.noop,
        ),
    ]
