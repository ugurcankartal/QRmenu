import api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0047_remove_security_models_from_api"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettingstranslation",
            name="about_image",
            field=models.ImageField(
                blank=True,
                help_text="Hakkında sayfası üst banner görseli. Boş bırakılırsa varsayılan dilin görseli kullanılır.",
                null=True,
                upload_to=api.models.settings_about_image_upload_to,
                verbose_name="Hakkında hero görseli",
            ),
        ),
    ]
