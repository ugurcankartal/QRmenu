from django.db import migrations, models


def seed_image_categories(apps, schema_editor):
    ImageCategory = apps.get_model("api", "ImageCategory")
    categories = [
        {
            "code": "products",
            "name": "Ürünler",
            "target": "product",
            "upload_path": "images/products",
            "order": 1,
        },
        {
            "code": "categories",
            "name": "Kategoriler",
            "target": "category",
            "upload_path": "images/categories",
            "order": 2,
        },
    ]
    for data in categories:
        ImageCategory.objects.get_or_create(code=data["code"], defaults=data)


def unseed_image_categories(apps, schema_editor):
    ImageCategory = apps.get_model("api", "ImageCategory")
    ImageCategory.objects.filter(code__in=["products", "categories"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0010_category_image"),
    ]

    operations = [
        migrations.CreateModel(
            name="ImageCategory",
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
                    "code",
                    models.SlugField(
                        help_text="Örn: products, categories",
                        max_length=50,
                        unique=True,
                        verbose_name="Kod",
                    ),
                ),
                ("name", models.CharField(max_length=100, verbose_name="Ad")),
                (
                    "target",
                    models.CharField(
                        choices=[("product", "Ürün"), ("category", "Kategori")],
                        max_length=20,
                        verbose_name="Hedef",
                    ),
                ),
                (
                    "upload_path",
                    models.CharField(
                        help_text="MEDIA köküne göre, örn: images/products",
                        max_length=200,
                        verbose_name="Yükleme klasörü",
                    ),
                ),
                ("is_active", models.BooleanField(default=True, verbose_name="Aktif")),
                ("order", models.PositiveIntegerField(default=0, verbose_name="Sıra")),
            ],
            options={
                "verbose_name": "Görsel kategorisi",
                "verbose_name_plural": "Görsel kategorileri",
                "ordering": ["order", "code"],
            },
        ),
        migrations.RunPython(seed_image_categories, unseed_image_categories),
        migrations.AlterField(
            model_name="category",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="api.models.category_image_upload_to",
                verbose_name="Görsel",
            ),
        ),
        migrations.AlterField(
            model_name="product",
            name="image",
            field=models.ImageField(
                blank=True,
                null=True,
                upload_to="api.models.product_image_upload_to",
                verbose_name="Görsel",
            ),
        ),
    ]
