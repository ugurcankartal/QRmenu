from django.db import migrations, models


def ensure_access_groups(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for name in ("admin", "supervisor"):
        Group.objects.get_or_create(name=name)


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0044_seed_content_translations_from_turkish"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="frontend_public_access",
            field=models.BooleanField(
                default=True,
                help_text="Kapalıyken yalnızca admin/supervisor grubundaki kullanıcılar giriş yaparak siteyi görüntüleyebilir.",
                verbose_name="Ön yüz herkese açık",
            ),
        ),
        migrations.RunPython(ensure_access_groups, migrations.RunPython.noop),
    ]
