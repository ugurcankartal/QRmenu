import django.db.models.deletion
from django.db import migrations, models
import mptt.fields


def rebuild_category_tree(apps, schema_editor):
    from api.models import Category

    Category.objects.rebuild()


class Migration(migrations.Migration):
    dependencies = [
        ("api", "0003_category_parent_alter_category_name_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="parent",
            field=mptt.fields.TreeForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="children",
                to="api.category",
            ),
        ),
        migrations.AddField(
            model_name="category",
            name="level",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="lft",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="rght",
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="category",
            name="tree_id",
            field=models.PositiveIntegerField(db_index=True, default=0),
            preserve_default=False,
        ),
        migrations.RunPython(rebuild_category_tree, migrations.RunPython.noop),
    ]
