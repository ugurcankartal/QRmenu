from django.db import migrations, models

import api.models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0011_imagecategory"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="imagecategory",
            name="upload_path",
        ),
        migrations.AddField(
            model_name="imagecategory",
            name="upload_path",
            field=models.ImageField(
                blank=True,
                help_text="Görsel, images/{kod}/ altına kaydedilir.",
                null=True,
                upload_to=api.models.image_category_upload_to,
                verbose_name="Yükleme klasörü",
            ),
        ),
    ]
