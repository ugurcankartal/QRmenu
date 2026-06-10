from django.db import migrations, models


def sync_category_orders(apps, schema_editor):
    Category = apps.get_model("api", "Category")
    parent_ids = Category.objects.values_list("parent_id", flat=True).distinct()
    for parent_id in parent_ids:
        siblings = list(
            Category.objects.filter(parent_id=parent_id)
            .order_by("tree_id", "lft")
            .only("pk", "order")
        )
        updates = []
        for index, category in enumerate(siblings):
            if category.order != index:
                category.order = index
                updates.append(category)
        if updates:
            Category.objects.bulk_update(updates, ["order"])


class Migration(migrations.Migration):

    dependencies = [
        ("api", "0006_category_translations"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="order",
            field=models.PositiveIntegerField(default=0, editable=False),
        ),
        migrations.RunPython(sync_category_orders, migrations.RunPython.noop),
    ]
