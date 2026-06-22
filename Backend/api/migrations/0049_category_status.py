from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0048_sitesettingstranslation_about_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="status",
            field=models.CharField(
                choices=[("active", "Aktif"), ("inactive", "Deaktif")],
                default="active",
                max_length=20,
                verbose_name="Statü",
            ),
        ),
    ]
