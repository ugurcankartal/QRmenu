import django.db.models.deletion
from django.db import migrations, models


def migrate_chef_recommendation_products(apps, schema_editor):
    ChefRecommendationProduct = apps.get_model("api", "ChefRecommendationProduct")
    table_names = schema_editor.connection.introspection.table_names()
    legacy_table = "api_chefrecommendation_products"
    if legacy_table not in table_names:
        return

    order_by_recommendation = {}
    with schema_editor.connection.cursor() as cursor:
        cursor.execute(
            f"SELECT chefrecommendation_id, product_id FROM {legacy_table} ORDER BY id"
        )
        rows = cursor.fetchall()

    for recommendation_id, product_id in rows:
        order = order_by_recommendation.get(recommendation_id, 0)
        ChefRecommendationProduct.objects.create(
            chef_recommendation_id=recommendation_id,
            product_id=product_id,
            order=order,
        )
        order_by_recommendation[recommendation_id] = order + 1


def unmigrate_chef_recommendation_products(apps, schema_editor):
    ChefRecommendationProduct = apps.get_model("api", "ChefRecommendationProduct")
    ChefRecommendationProduct.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0035_chef_recommendation_products_m2m"),
    ]

    operations = [
        migrations.CreateModel(
            name="ChefRecommendationProduct",
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
                    "order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Küçük değer ön yüzde önce gösterilir.",
                        verbose_name="Öncelik",
                    ),
                ),
                (
                    "chef_recommendation",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="product_links",
                        to="api.chefrecommendation",
                        verbose_name="Şefin önerisi",
                    ),
                ),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="chef_recommendation_links",
                        to="api.product",
                        verbose_name="Ürün",
                    ),
                ),
            ],
            options={
                "verbose_name": "Şefin önerisi ürünü",
                "verbose_name_plural": "Şefin önerisi ürünleri",
                "ordering": ["order", "pk"],
            },
        ),
        migrations.RunPython(
            migrate_chef_recommendation_products,
            unmigrate_chef_recommendation_products,
        ),
        migrations.RemoveField(
            model_name="chefrecommendation",
            name="products",
        ),
        migrations.AddField(
            model_name="chefrecommendation",
            name="products",
            field=models.ManyToManyField(
                blank=True,
                related_name="chef_recommendations",
                through="api.ChefRecommendationProduct",
                to="api.product",
                verbose_name="Ürünler",
            ),
        ),
        migrations.AddConstraint(
            model_name="chefrecommendationproduct",
            constraint=models.UniqueConstraint(
                fields=("chef_recommendation", "product"),
                name="unique_chef_recommendation_product",
            ),
        ),
    ]
