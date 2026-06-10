from django.db import migrations, models

import api.models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0031_contact_icon_link_text"),
    ]

    operations = [
        migrations.AddField(
            model_name="campaign",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to=api.models.campaign_image_upload_to,
                verbose_name="Görsel",
            ),
        ),
    ]
