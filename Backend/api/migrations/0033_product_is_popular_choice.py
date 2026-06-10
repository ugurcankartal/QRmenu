from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0032_campaign_image"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="is_popular_choice",
            field=models.BooleanField(
                default=False,
                help_text="Ürün detayında popüler seçim rozeti gösterilir.",
                verbose_name="Popüler Seçim",
            ),
        ),
    ]
